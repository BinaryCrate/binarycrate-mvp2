# -*- coding: utf-8 -*-
# BinaryCrate -  BinaryCrate an in browser python IDE. Design to make learning coding easy.
# Copyright (C) 2018 BinaryCrate Pty Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, print_function, unicode_literals
from rest_framework.test import APITestCase
from project.models import Project, DirectoryEntry, Image, ProjectTypes
import uuid
import tempfile
import shutil
import os
from django.conf import settings
from accounts.factories import UserFactory

#added additional imports from test apis
from django.urls import reverse
from rest_framework import status
from accounts.factories import UserFactory
from rest_framework.test import APIClient


class TestModels(APITestCase):

    def test_initialising_new_model_has_empty_string_content(self):
        de = DirectoryEntry.objects.create(name='hello_world.py', is_file=True)
        assert de.content == ''
        assert de.form_items == '[]'
        assert de.form_properties == '{}'

    def test_saving_and_reloading_preserves_content(self):
        de = DirectoryEntry.objects.create(name='hello_world.py', is_file=True)
        de.content = "print('Hello world')"
        de.form_items = "[{'id': '2f991f85-fea5-466f-ab79-58b5241729e7'}]"
        de.form_properties = "{'width': '200', 'height': '400'}"
        de.is_default = True
        de.save()

        with open(settings.PROJECT_FILES_ROOT + '/' + str(de.id), 'r') as project_file:
            file_content = project_file.read()

        with open(settings.PROJECT_FILES_ROOT + '/' + str(de.id) + '-form-items', 'r') as project_file:
            form_items_file_content = project_file.read()

        with open(settings.PROJECT_FILES_ROOT + '/' + str(de.id) + '-form-properties', 'r') as project_file:
            form_properties_file_content = project_file.read()

        assert de.content == file_content
        assert de.form_items == form_items_file_content
        assert de.form_properties == form_properties_file_content

        de2 = DirectoryEntry.objects.get(id=de.id)
        assert de.content == de2.content
        assert de.form_items == de2.form_items
        assert de.is_default == de2.is_default
        assert de.form_properties == de2.form_properties


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



class TestPythonProject(APITestCase):
        def test_python_project_correct_type(self):
            self.project_id = uuid.uuid4()
            u = UserFactory()
            de = DirectoryEntry.objects.create(name='', is_file=False)
            Project.objects.create(id=self.project_id, name='Test Python', type=ProjectTypes.python.value, public=False,
                                   root_folder=de, owner=u)

            self.assertEqual(Project.objects.count(), 1)
            p = Project.objects.all().first()
            self.assertEqual(p.type, 0)

            self.assertEqual(set(p.get_directory_entries().values_list('name', flat=True)), {''})

class TestWebpageProject(APITestCase):
    def test_creating_webpage_project_type(self):
            self.project_id = uuid.uuid4()
            u = UserFactory()
            de = DirectoryEntry.objects.create(name='', is_file=False)
            Project.objects.create(id=self.project_id, name='Test Webpage', type=ProjectTypes.webpage.value, public=False,
                                   root_folder=de, owner=u)

            self.assertEqual(Project.objects.count(), 1)
            self.assertEqual(Project.objects.all().first().type, 1)

class TestWebpageFiles(APITestCase):
    def test_webpage_files_created_in_root(self):
            self.project_id = uuid.uuid4()
            u = UserFactory()
            de = DirectoryEntry.objects.create(name='', is_file=False)
            p = Project.objects.create(id=self.project_id, name='Test Webpage', type=ProjectTypes.webpage.value, public=False,
                                   root_folder=de, owner=u)

            self.assertEqual(Project.objects.count(), 1)
            self.assertEqual(Project.objects.all().first().type, 1)

            #Checks that new files are not re-created upon saving project
            p.save()
            p.save()

            print(p.get_directory_entries().values_list('name', flat=True))
            p.save()
            self.assertEqual(p.get_directory_entries().count(), 4)
            self.assertEqual(set(p.get_directory_entries().values_list('name', flat=True)),
            {u'', u'scripts.js', u'index.html', u'styles.css'})


class TestPythonWithStorageProject(APITestCase):
        def test_python_project_correct_type(self):
            self.project_id = uuid.uuid4()
            u = UserFactory()
            de = DirectoryEntry.objects.create(name='', is_file=False)
            Project.objects.create(id=self.project_id, name='Test Python',
                                type=ProjectTypes.python_with_storage.value, public=False,
                                   root_folder=de, owner=u)

            self.assertEqual(Project.objects.count(), 1)
            p = Project.objects.all().first()
            self.assertEqual(p.type, 2)

            print('Dir entries=', p.get_directory_entries().values_list('name', flat=True))
            self.assertEqual(set(p.get_directory_entries().values_list('name', flat=True)),
                {'', 'documents.py'})

            de = p.get_directory_entries().get(name='documents.py')
            self.assertEqual(de.content, """from __future__ import absolute_import, unicode_literals, print_function
from binarycrate import historygraphfrontend
from historygraph import Document, DocumentObject
from historygraph import fields
import inspect
import copy

# Don't change anything above this line
# Your Document definition go here





# Don't change anything below this line
for c in copy.copy(globals().values()):
    if inspect.isclass(c) and issubclass(c, DocumentObject) and c != Document and c != DocumentObject:
        historygraphfrontend.documentcollection.register(c)

historygraphfrontend.download_document_collection()
""")
