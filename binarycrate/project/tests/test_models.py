# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from rest_framework.test import APITestCase
from project.models import Project, DirectoryEntry, Image
import uuid
import tempfile
import shutil
import os
from django.conf import settings
from accounts.factories import UserFactory


class TestModels(APITestCase):

    def test_initialising_new_model_has_empty_string_content(self):
        de = DirectoryEntry.objects.create(name='hello_world.py', is_file=True)
        assert de.content == ''
        assert de.form_items == '[]'

    def test_saving_and_reloading_preserves_content(self):
        de = DirectoryEntry.objects.create(name='hello_world.py', is_file=True)
        de.content = "print('Hello world')"
        de.form_items = "[{'id': '2f991f85-fea5-466f-ab79-58b5241729e7'}]"
        de.is_default = True
        de.save()

        with open(settings.PROJECT_FILES_ROOT + '/' + str(de.id), 'r') as project_file:
            file_content = project_file.read()

        with open(settings.PROJECT_FILES_ROOT + '/' + str(de.id) + '-form-items', 'r') as project_file:
            form_items_file_content = project_file.read()

        assert de.content == file_content
        assert de.form_items == form_items_file_content

        de2 = DirectoryEntry.objects.get(id=de.id)
        assert de.content == de2.content
        assert de.form_items == de2.form_items
        assert de.is_default == de2.is_default


class TestImageModel(APITestCase):
    def test_image_saving_saves_the_file(self):
        u = UserFactory()
        de = DirectoryEntry.objects.create(name='', is_file=False)
        project = Project.objects.create(name='Test 1', type=0, public=False,
                       root_folder=de, owner=u)
        image = Image.objects.create(name='Natural-red-apple.jpg', project=project)

        with open(os.path.join(settings.BASE_DIR, 'project', 'tests', 'assets', 'Natural-red-apple.jpg'), 'rb') as f:
            image.save_file(f)

        with open(settings.PROJECT_FILES_ROOT + '/images-{0}/{1}'.format(project.id, image.id), 'rb') as saved_file:
            with open(os.path.join(settings.BASE_DIR, 'project', 'tests', 'assets', 'Natural-red-apple.jpg'), 'rb') as original_file:
                saved_content = saved_file.read()
                original_content = original_file.read()

                assert saved_content == original_content

        assert image.get_url() == '/images/images-{0}/{1}.jpg'.format(project.id, image.id)
        


