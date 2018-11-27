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
from django.test import TestCase
from django.urls import reverse
import uuid
from accounts.factories import UserFactory
from project.models import Project, DirectoryEntry
from django.conf import settings


class TestSharedProjectView(TestCase):
    def setUp(self):
        self.project_id = uuid.uuid4()
        self.user = UserFactory(username='user2@binarycrate.com',email='user2@binarycrate.com')
        self.de_rootfolder = DirectoryEntry.objects.create(name='', is_file=False)
        self.project = Project.objects.create(id=self.project_id, name='Test 2', type=0, public=True,
                               root_folder=self.de_rootfolder, owner=self.user)
        self.de_hello_world = DirectoryEntry.objects.create(parent=self.de_rootfolder, name='hello_world.py', is_file=True)
        self.de_hello_world.content = "print('Hello world')"
        self.de_hello_world.is_default = True
        self.de_hello_world.save()
        self.de_folder = DirectoryEntry.objects.create(parent=self.de_rootfolder, name='folder', is_file=False)
        self.de_hello_folder = DirectoryEntry.objects.create(parent=self.de_folder, name='hello_folder.py', is_file=True)
        self.de_hello_folder.content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""
        self.de_hello_folder.save()

    def test_renders_if_exists(self):
        response = self.client.get(reverse('share:shared_project',
                                   kwargs={'project_id': self.project_id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.decode('utf-8').find(
                         str(self.project_id)) > 0)
        self.assertTrue(response.content.decode('utf-8').find(
                         'boot_bc_shared_project.py') > 0)
        self.assertIn(settings.BUILD_NUMBER, response.content)

    def test_404_if_doesnt_exist(self):
        response = self.client.get(reverse('share:shared_project',
                                   kwargs={'project_id': uuid.uuid4()}))
        self.assertEqual(response.status_code, 404)

    def test_404_if_not_public(self):
        self.project.public = False
        self.project.save()
        response = self.client.get(reverse('share:shared_project',
                                   kwargs={'project_id': self.project_id}))
        self.assertEqual(response.status_code, 404)
