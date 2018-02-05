# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from rest_framework.test import APITestCase
from project.models import Project, DirectoryEntry
import uuid
import tempfile
import shutil
import os
from django.conf import settings


class TestModels(APITestCase):

    def test_initialising_new_model_has_empty_string_content(self):
        de = DirectoryEntry.objects.create(name='hello_world.py', is_file=True)
        assert de.content == ''

    def test_saving_and_reloading_preserves_content(self):
        de = DirectoryEntry.objects.create(name='hello_world.py', is_file=True)
        de.content = "print('Hello world')"
        de.save()

        with open(settings.PROJECT_FILES_ROOT + '/' + str(de.id), 'r') as project_file:
            file_content = project_file.read()

        assert de.content == file_content

        de2 = DirectoryEntry.objects.get(id=de.id)
        assert de.content == de2.content

