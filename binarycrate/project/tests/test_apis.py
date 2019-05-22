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
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from project.models import Project, DirectoryEntry, Image
import uuid
from accounts.factories import UserFactory
from rest_framework.test import APIClient
import pytest

import os
from django.conf import settings


# TODO: This (DirectoryEntryDict) appears to be balloonian code - it should be deleted
# From https://gist.github.com/href/1319371
from collections import namedtuple
DirectoryEntryDict = namedtuple('DirectoryEntryDict', ['id', 'name',
                                'is_file', 'parent_id', 'content',
                                'form_items', 'form_properties', 'is_default'])
def convert(dictionary):
    return DirectoryEntryDict(**dictionary)


class ProjectListTestCase(APITestCase):
    def setUp(self):
        self.project_id = uuid.uuid4()
        u = UserFactory()
        de = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id, name='Test 1', type=0, public=False,
                               root_folder=de, owner=u)
        self.client.force_authenticate(user=u)

    def test_list_projects(self):
        """
        Ensure we can list the projects
        """
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-list')
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.project_id))
        self.assertEqual(response.data[0]['name'], 'Test 1')
        self.assertEqual(response.data[0]['type'], 0)
        self.assertEqual(response.data[0]['public'], False)


    def test_project_detail(self):
        """
        Ensure we can view individual projects
        """
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.project_id))
        self.assertEqual(response.data['name'], 'Test 1')
        self.assertEqual(response.data['type'], 0)
        self.assertEqual(response.data['public'], False)

    def test_project_post_creates_python_project(self):
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-list')
        project_id = str(Project.objects.first().id)
        data = {'name':'Test 2', 'type':0, 'public':False }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertNotEqual(response.data['id'], project_id)
        self.assertIn(response.data['id'], set([str(p.id) for p in Project.objects.all()]))

    def test_put_python_project_detail(self):
        """
        Ensure we can view individual projects
        """
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id)})
        data = { 'id': str(self.project_id), 'name': 'Test 1a', 'type': 0,
                 'public': False}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.first().name, 'Test 1a')

    def test_delete_python_project_detail(self):
        """
        Ensure we can delete individual projects
        """
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id)})
        data = { }
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)


class ProjectMustLogin(APITestCase):
    # If the user is not logged in they get 403 errors
    def setUp(self):
        self.project_id = uuid.uuid4()
        u = UserFactory()
        de = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id, name='Test 1', type=0, public=False,
                               root_folder=de, owner=u)

    def test_list_projects(self):
        """
        Ensure we can list the projects
        """
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-list')
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(str(self.project_id) in response.content)


    def test_project_detail(self):
        """
        Ensure we can view individual projects
        """
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(str(self.project_id) in response.content)

    def test_project_post_must_login(self):
        url = reverse('api:project-list')
        project_id = str(uuid.uuid4())
        data = { 'id': project_id, 'name':'Test 2', 'type':0, 'public':False }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(str(self.project_id) in response.content)

    def test_put_project_detail_must_login(self):
        """
        Ensure a user can only change their  projects
        """
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id)})
        data = { 'id': str(self.project_id), 'name': 'Test 1a', 'type': 0,
                 'public': False}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.first().name, 'Test 1')

    def test_delete_project_detail_must_login(self):
        """
        Ensure we can delete individual projects
        """
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id)})
        data = { }
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.first().name, 'Test 1')

class ProjectCannotAccessOtherUserTestCase(APITestCase):
    def setUp(self):
        self.project_id1 = uuid.uuid4()
        self.project_id2 = uuid.uuid4()
        self.user1 = UserFactory(username='user1@binarycrate.com',email='user1@binarycrate.com')
        self.user2 = UserFactory(username='user2@binarycrate.com',email='user2@binarycrate.com')
        de1 = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id1, name='Test 1', type=0, public=False,
                               root_folder=de1, owner=self.user1)
        self.de_rootfolder = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id2, name='Test 2', type=0, public=False,
                               root_folder=self.de_rootfolder, owner=self.user2)
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

        self.client.force_authenticate(user=self.user2)

    def test_list_projects(self):
        """
        Ensure we can list the projects
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-list')
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.project_id2))
        self.assertEqual(response.data[0]['name'], 'Test 2')
        self.assertEqual(response.data[0]['type'], 0)
        self.assertEqual(response.data[0]['public'], False)


    def test_project_detail_cannot_access_other_users_projects(self):
        """
        Ensure we can view individual projects
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id1)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(str(self.project_id2) in response.content)

    def test_project_detail_can_access_my_projects(self):
        """
        Ensure we can view individual projects
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id2)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.project_id2))
        self.assertEqual(response.data['name'], 'Test 2')
        self.assertEqual(response.data['type'], 0)
        self.assertEqual(response.data['public'], False)
        processed_directory_entries = {convert(d) for d in response.data['directory_entry']}
        self.assertEqual(processed_directory_entries, {
                         convert({'id': str(self.de_rootfolder.id),
                          'name': self.de_rootfolder.name,
                          'is_file': self.de_rootfolder.is_file,
                          'content': '',
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': None,
                          'is_default': False,
                         }),
                         convert({'id': str(self.de_hello_world.id),
                          'name': self.de_hello_world.name,
                          'is_file': self.de_hello_world.is_file,
                          'content': self.de_hello_world.content,
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': str(self.de_rootfolder.id),
                          'is_default': True,
                         }),
                         convert({'id': str(self.de_folder.id),
                          'name': self.de_folder.name,
                          'is_file': self.de_folder.is_file,
                          'content': '',
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': str(self.de_rootfolder.id),
                          'is_default': False,
                         }),
                         convert({'id': str(self.de_hello_folder.id),
                          'name': self.de_hello_folder.name,
                          'is_file': self.de_hello_folder.is_file,
                          'content': self.de_hello_folder.content,
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': str(self.de_folder.id),
                          'is_default': False,
                         }),
                         })

    def test_put_project_detail_cannot_change_another_users_project(self):
        """
        Ensure a user can only change their  projects
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id1)})
        data = { 'id': str(self.project_id1), 'name': 'Test 1a', 'type': 0,
                 'public': False}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual({'Test 1', 'Test 2'}, {p.name for p in Project.objects.all()})

    def test_delete_project_detail_cannot_delete_another_users_project(self):
        """
        Ensure we can delete individual projects
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id1)})
        data = { }
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual({'Test 1', 'Test 2'}, {p.name for p in Project.objects.all()})

class ProjectCanSaveTestCase(APITestCase):
    def setUp(self):
        self.project_id1 = uuid.uuid4()
        self.project_id2 = uuid.uuid4()
        self.user1 = UserFactory(username='user1@binarycrate.com',email='user1@binarycrate.com')
        self.user2 = UserFactory(username='user2@binarycrate.com',email='user2@binarycrate.com')
        de1 = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id1, name='Test 1', type=0, public=False,
                               root_folder=de1, owner=self.user1)
        self.de_rootfolder = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id2, name='Test 2', type=0, public=False,
                               root_folder=self.de_rootfolder, owner=self.user2)
        self.de_hello_world = DirectoryEntry.objects.create(parent=self.de_rootfolder, name='hello_world.py', is_file=True)
        self.de_hello_world.content = "print('Hello world')"
        self.de_hello_world.form_items = "[{'id': '2f991f85-fea5-466f-ab79-58b5241729e7'}]"
        self.de_hello_world.save()
        self.de_folder = DirectoryEntry.objects.create(parent=self.de_rootfolder, name='folder', is_file=False)
        self.de_hello_folder = DirectoryEntry.objects.create(parent=self.de_folder, name='hello_folder.py', is_file=True)
        self.de_hello_folder.content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""
        self.de_hello_folder.save()

        self.client.force_authenticate(user=self.user2)

    def test_put_updates_a_directory_entry(self):
        url = reverse('api:directoryentry-detail', kwargs={'pk':str(self.de_hello_world.id)})
        data = {'id': str(self.de_hello_world.id),
                          'name': self.de_hello_world.name,
                          'is_file': self.de_hello_world.is_file,
                          'content': "print('Hello world2')",
                          'parent_id': str(self.de_rootfolder.id),
                          'form_items': "[{'id': '37ce1ec8-84dc-4b5e-8a09-9411c5007a0'}]",
                          'form_properties': "{'width': '200', 'height': '400'}",
                          'is_default': True,
                         }
        response = self.client.put(url, data, format='json')
        #print('response.content=', response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DirectoryEntry.objects.get(id=self.de_hello_world.id).content, "print('Hello world2')")
        self.assertEqual(DirectoryEntry.objects.get(id=self.de_hello_world.id).form_items, "[{'id': '37ce1ec8-84dc-4b5e-8a09-9411c5007a0'}]")
        self.assertEqual(DirectoryEntry.objects.get(id=self.de_hello_world.id).is_default, True)
        self.assertEqual(DirectoryEntry.objects.get(id=self.de_hello_world.id).form_properties, "{'width': '200', 'height': '400'}")

    def test_put_can_create_a_new_directory_entry(self):
        data = {'id': str(uuid.uuid4()),
                          'name': 'Hello world2',
                          'is_file': True,
                          'content': "print('Hello world4')",
                          'parent_id': str(self.de_rootfolder.id),
                          'form_items': "[{'id': '37ce1ec8-84dc-4b5e-8a09-9411c5007a0'}]",
                          'form_properties': "{'width': '200', 'height': '400'}",
                          'is_default': True,
                         }
        url = reverse('api:directoryentry-detail', kwargs={'pk':data['id']})
        response = self.client.put(url, data, format='json')
        #print('response.content=', response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DirectoryEntry.objects.get(id=data['id']).content, "print('Hello world4')")
        self.assertEqual(DirectoryEntry.objects.get(id=data['id']).form_items, "[{'id': '37ce1ec8-84dc-4b5e-8a09-9411c5007a0'}]")
        self.assertEqual(str(DirectoryEntry.objects.get(id=data['id']).parent_id), data['parent_id'])
        self.assertEqual(DirectoryEntry.objects.get(id=data['id']).is_default, True)
        self.assertEqual(DirectoryEntry.objects.get(id=data['id']).form_properties, "{'width': '200', 'height': '400'}")

    def test_delete_a_directory_entry(self):
        url = reverse('api:directoryentry-detail', kwargs={'pk':str(self.de_hello_world.id)})
        data = { }
        response = self.client.delete(url, data, format='json')
        #print('response.content=', response.content)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DirectoryEntry.objects.filter(name='hello_world.py').count(), 0)

class PublicAccessOtherUserTestCase(APITestCase):
    def setUp(self):
        self.project_id1 = uuid.uuid4()
        self.project_id2 = uuid.uuid4()
        self.user1 = UserFactory(username='user1@binarycrate.com',email='user1@binarycrate.com')
        self.user2 = UserFactory(username='user2@binarycrate.com',email='user2@binarycrate.com')
        de1 = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id1, name='Test 1', type=0, public=True,
                               root_folder=de1, owner=self.user1)
        self.de_rootfolder = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id2, name='Test 2', type=0, public=False,
                               root_folder=self.de_rootfolder, owner=self.user2)
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

        self.client.force_authenticate(user=self.user2)

    def test_list_projects(self):
        """
        Ensure we can list the projects. Even though a project is public another should not be able
        to see to in their list
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-list')
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.project_id2))
        self.assertEqual(response.data[0]['name'], 'Test 2')
        self.assertEqual(response.data[0]['type'], 0)
        self.assertEqual(response.data[0]['public'], False)


    def test_project_detail_can_access_other_users_projects(self):
        """
        Ensure we can access public projects if we know the pk
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id1)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.project_id1))
        self.assertEqual(response.data['name'], 'Test 1')
        self.assertEqual(response.data['type'], 0)
        self.assertEqual(response.data['public'], True)

    def test_project_detail_other_user_can_access_my_projects(self):
        """
        Ensure we can view individual projects
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id2)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.project_id2))
        self.assertEqual(response.data['name'], 'Test 2')
        self.assertEqual(response.data['type'], 0)
        self.assertEqual(response.data['public'], False)
        processed_directory_entries = {convert(d) for d in response.data['directory_entry']}
        self.assertEqual(processed_directory_entries, {
                         convert({'id': str(self.de_rootfolder.id),
                          'name': self.de_rootfolder.name,
                          'is_file': self.de_rootfolder.is_file,
                          'content': '',
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': None,
                          'is_default': False,
                         }),
                         convert({'id': str(self.de_hello_world.id),
                          'name': self.de_hello_world.name,
                          'is_file': self.de_hello_world.is_file,
                          'content': self.de_hello_world.content,
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': str(self.de_rootfolder.id),
                          'is_default': True,
                         }),
                         convert({'id': str(self.de_folder.id),
                          'name': self.de_folder.name,
                          'is_file': self.de_folder.is_file,
                          'content': '',
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': str(self.de_rootfolder.id),
                          'is_default': False,
                         }),
                         convert({'id': str(self.de_hello_folder.id),
                          'name': self.de_hello_folder.name,
                          'is_file': self.de_hello_folder.is_file,
                          'content': self.de_hello_folder.content,
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': str(self.de_folder.id),
                          'is_default': False,
                         }),
                         })

class PublicAccessNotLoggedInUserTestCase(APITestCase):
    def setUp(self):
        self.project_id1 = uuid.uuid4()
        self.project_id2 = uuid.uuid4()
        self.user1 = UserFactory(username='user1@binarycrate.com',email='user1@binarycrate.com')
        self.user2 = UserFactory(username='user2@binarycrate.com',email='user2@binarycrate.com')
        de1 = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id1, name='Test 1', type=0, public=False,
                               root_folder=de1, owner=self.user1)
        self.de_rootfolder = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id2, name='Test 2', type=0, public=True,
                               root_folder=self.de_rootfolder, owner=self.user2)
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

    def test_list_projects(self):
        """
        Ensure we can list the projects. Even though a project is public another should not be able
        to see to in their list
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-list')
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(str(self.project_id1) in response.content)
        self.assertFalse(str(self.project_id2) in response.content)


    def test_project_detail_can_access_other_users_projects(self):
        """
        Ensure we can access public projects if we know the pk
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id2)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.project_id2))
        self.assertEqual(response.data['name'], 'Test 2')
        self.assertEqual(response.data['type'], 0)
        self.assertEqual(response.data['public'], True)

    def test_project_detail_can_access_public_projects(self):
        """
        Ensure we can view individual projects
        """
        self.assertEqual(Project.objects.count(), 2)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id2)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.project_id2))
        self.assertEqual(response.data['name'], 'Test 2')
        self.assertEqual(response.data['type'], 0)
        self.assertEqual(response.data['public'], True)
        processed_directory_entries = {convert(d) for d in response.data['directory_entry']}
        self.assertEqual(processed_directory_entries, {
                         convert({'id': str(self.de_rootfolder.id),
                          'name': self.de_rootfolder.name,
                          'is_file': self.de_rootfolder.is_file,
                          'content': '',
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': None,
                          'is_default': False,
                         }),
                         convert({'id': str(self.de_hello_world.id),
                          'name': self.de_hello_world.name,
                          'is_file': self.de_hello_world.is_file,
                          'content': self.de_hello_world.content,
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': str(self.de_rootfolder.id),
                          'is_default': True,
                         }),
                         convert({'id': str(self.de_folder.id),
                          'name': self.de_folder.name,
                          'is_file': self.de_folder.is_file,
                          'content': '',
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': str(self.de_rootfolder.id),
                          'is_default': False,
                         }),
                         convert({'id': str(self.de_hello_folder.id),
                          'name': self.de_hello_folder.name,
                          'is_file': self.de_hello_folder.is_file,
                          'content': self.de_hello_folder.content,
                          'form_items': '[]',
                          'form_properties': '{}',
                          'parent_id': str(self.de_folder.id),
                          'is_default': False,
                         }),
                         })

class ProjectImageTestCase(APITestCase):
    def setUp(self):
        self.project_id = uuid.uuid4()
        u = UserFactory()
        de = DirectoryEntry.objects.create(name='', is_file=False)
        self.project = Project.objects.create(id=self.project_id, name='Test 1', type=0, public=False,
                               root_folder=de, owner=u)
        self.client.force_authenticate(user=u)

    def test_upload_image(self):
        # Upload the file and test we don't get an error
        assert Image.objects.all().count() == 0
        with open(os.path.join(settings.BASE_DIR, 'project', 'tests', 'assets', 'Natural-red-apple.jpg'), 'rb') as f:
            response = self.client.post(reverse('api:image-upload'), {'name': 'Natural-red-apple.jpg', 'project': str(self.project.id),
                                          'file_data': f}, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            assert Image.objects.all().count() == 1

        url = reverse('api:image-list', kwargs={'project':str(self.project_id)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data
        assert len(results) == 1
        result = results[0]
        assert result['name'] == 'Natural-red-apple.jpg'
        assert result['image_url'] == '/images/images-{0}/{1}.jpg'.format(self.project.id, result['id'])

        with open(settings.PROJECT_FILES_ROOT + '/images-{0}/{1}'.format(self.project.id, result['id']), 'rb') as saved_file:
            with open(os.path.join(settings.BASE_DIR, 'project', 'tests', 'assets', 'Natural-red-apple.jpg'), 'rb') as original_file:
                saved_content = saved_file.read()
                original_content = original_file.read()

                assert saved_content == original_content

                response = self.client.get(result['image_url'], follow=True)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                assert saved_content == response.content

    def test_delete_uploaded_image(self):
        # Upload the file and test we don't get an error
        assert Image.objects.all().count() == 0
        with open(os.path.join(settings.BASE_DIR, 'project', 'tests', 'assets', 'Natural-red-apple.jpg'), 'rb') as f:
            response = self.client.post(reverse('api:image-upload'), {'name': 'Natural-red-apple.jpg', 'project': str(self.project.id),
                                          'file_data': f}, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            assert Image.objects.all().count() == 1

        response = self.client.delete(reverse('api:image-edit', kwargs={'pk': str(Image.objects.first().pk)}), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        assert Image.objects.all().count() == 0

    def test_rename_uploaded_image(self):
        # Upload the file and test we don't get an error
        assert Image.objects.all().count() == 0
        with open(os.path.join(settings.BASE_DIR, 'project', 'tests', 'assets', 'Natural-red-apple.jpg'), 'rb') as f:
            response = self.client.post(reverse('api:image-upload'), {'name': 'Natural-red-apple.jpg', 'project': str(self.project.id),
                                          'file_data': f}, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            assert Image.objects.all().count() == 1

        response = self.client.put(reverse('api:image-edit', kwargs={'pk': str(Image.objects.first().pk)}), {'name': 'Natural-red-pear.jpg'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert Image.objects.all().count() == 1
        assert {i.name for i in Image.objects.all()} == {'Natural-red-pear.jpg'}


class ProjectImageNotLoggedInTestCase(APITestCase):
    def setUp(self):
        self.project_id = uuid.uuid4()
        u = UserFactory()
        de = DirectoryEntry.objects.create(name='', is_file=False)
        self.project = Project.objects.create(id=self.project_id, name='Test 1', type=0, public=False,
                               root_folder=de, owner=u)

    def test_upload_image(self):
        # Test we get an error if not logged in and the uplaod fails
        assert Image.objects.all().count() == 0
        with open(os.path.join(settings.BASE_DIR, 'project', 'tests', 'assets', 'Natural-red-apple.jpg'), 'rb') as f:
            response = self.client.post('/api/projects/image/', {'name': 'Natural-red-apple.jpg', 'project': str(self.project.id),
                                          'file_data': f}, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            assert Image.objects.all().count() == 0

    def test_delete_image(self):
        Image.objects.create(project=self.project, name='hello.jpg')

        assert Image.objects.all().count() == 1
        response = self.client.delete(reverse('api:image-edit', kwargs={'pk': str(Image.objects.first().pk)}), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assert Image.objects.all().count() == 1

    def test_rename_image(self):
        Image.objects.create(project=self.project, name='hello.jpg')

        assert Image.objects.all().count() == 1
        response = self.client.put(reverse('api:image-edit', kwargs={'pk': str(Image.objects.first().pk)}), {'name': 'Natural-red-pear.jpg'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assert Image.objects.all().count() == 1
        assert {i.name for i in Image.objects.all()} == {'hello.jpg'}

class ProjectFilesTestCase(APITestCase):
    def setUp(self):
        self.project_id1 = uuid.uuid4()
        self.project_id2 = uuid.uuid4()
        self.user1 = UserFactory(username='user1@binarycrate.com', email='user1@binarycrate.com')

        self.de1 = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id1, name='Python Test', type=0, public=True,
                               root_folder=self.de1, owner=self.user1)
        self.pyfile = DirectoryEntry.objects.create(parent=self.de1, name='pyfile.py',
                                                    is_file=True)
        self.pyfile.is_default = True
        self.pyfile.save()

        self.de2 = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id2, name='HTML Test', type=1, public=True,
                               root_folder=self.de2, owner=self.user1)
        #Note: 3 files are automatically spawned upon creation of Webpage project

        self.client.force_authenticate(user=self.user1)

    # Users are allowed to delete python projects
    def test_delete_python_files(self):
        """
        Ensure Python projects can be deleted
        """
        self.assertEqual(DirectoryEntry.objects.filter(name='pyfile.py').count(), 1)
        url = reverse('api:directoryentry-detail', kwargs={'pk': str(self.pyfile.id)})
        data = {}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DirectoryEntry.objects.filter(name='pyfile.py').count(), 0)

    # User gets 405 error when attempting to delete html project files
    def test_delete_html_files(self):
        """
        Ensure HTML project files cannot be deleted, error 405 'method not allowed' returned
        """
        self.assertEqual(DirectoryEntry.objects.filter(name='index.html').count(), 1)
        html = DirectoryEntry.objects.get(name='index.html')
        url = reverse('api:directoryentry-detail', kwargs={'pk':str(html.id)})
        data = {}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(DirectoryEntry.objects.filter(name='index.html').count(), 1)

    # User gets 405 error when attempting to create html project file
    def test_create_html_files(self):
        """Ensure HTML project files cannot be created, error 405 returned"""
        data = {'id': str(uuid.uuid4()),
                'name': 'file.html',
                'is_file': True,
                'content': "print('Hello world4')",
                'parent_id': str(self.de2.id),
                'form_items': "[{'id': '197239de-0b08-49ca-8419-33907d8be3c0'}]",
                'is_default': True,
                }
        url = reverse('api:directoryentry-detail', kwargs={'pk': data['id']})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(DirectoryEntry.objects.filter(name='file.html').count(), 0)

    #Users can update content and form_items of html project files
    def test_update_html_files(self):
        """Ensure put can update fields except name of HTML project files"""
        html = DirectoryEntry.objects.get(name='index.html') #This file is created automatically
        url = reverse('api:directoryentry-detail', kwargs={'pk': str(html.id)})
        data = {'id': str(html.id),
                'name': "index.html",
                'is_file': html.is_file,
                'content': "print('Hello world123')",
                'parent_id': str(self.de2.id),
                'form_items': "[{'id': '37ce1ec8-84dc-4b5e-8a09-9411c5007a0'}]",
                'is_default': html.is_default,
                }
        response = self.client.put(url, data, format='json')
        # print('response.content=', response.content)
        print(html.name)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DirectoryEntry.objects.filter(name='index.html').count(), 1)
        self.assertEqual(DirectoryEntry.objects.get(id=html.id).content, "print('Hello world123')")
        self.assertEqual(DirectoryEntry.objects.get(id=html.id).form_items,
                         "[{'id': '37ce1ec8-84dc-4b5e-8a09-9411c5007a0'}]")

    def test_rename_html_file(self):
        "Return error 405 when attempting to rename HTML project files"
        html = DirectoryEntry.objects.get(name='index.html') #This file is created automatically
        url = reverse('api:directoryentry-detail', kwargs={'pk': str(html.id)})
        data = {'id': str(html.id),
                'name': "newname.html",
                'is_file': html.is_file,
                'content': "print('Hello world2')",
                'parent_id': str(self.de2.id),
                'form_items': "[{'id': '37ce1ec8-84dc-4b5e-8a09-9411c5007a0'}]",
                'is_default': True,
                }
        response = self.client.put(url, data, format='json')
        # print('response.content=', response.content)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(DirectoryEntry.objects.filter(name='newname.html').count(), 0)
        self.assertEqual(DirectoryEntry.objects.filter(name='index.html').count(), 1)
        self.assertEqual(DirectoryEntry.objects.get(id=html.id).content, '')
        self.assertEqual(DirectoryEntry.objects.get(id=html.id).form_items,
                         str(html.form_items))

class ProjectImageOtherUserTestCase(APITestCase):
    def setUp(self):
        self.project_id = uuid.uuid4()
        u = UserFactory(username='user1@binarycrate.com',email='user1@binarycrate.com')
        u2 = UserFactory(username='user2@binarycrate.com',email='user2@binarycrate.com')
        de = DirectoryEntry.objects.create(name='', is_file=False)
        self.project = Project.objects.create(id=self.project_id, name='Test 1', type=0, public=False,
                               root_folder=de, owner=u)
        self.client.force_authenticate(user=u2)

    def test_upload_image(self):
        # Test we get an error if logged in as a different user
        assert Image.objects.all().count() == 0
        with open(os.path.join(settings.BASE_DIR, 'project', 'tests', 'assets', 'Natural-red-apple.jpg'), 'rb') as f:
            response = self.client.post('/api/projects/image/', {'name': 'Natural-red-apple.jpg', 'project': str(self.project.id),
                                          'file_data': f}, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            assert Image.objects.all().count() == 0

    def test_delete_image(self):
        Image.objects.create(project=self.project, name='hello.jpg')

        assert Image.objects.all().count() == 1
        response = self.client.delete(reverse('api:image-edit', kwargs={'pk': str(Image.objects.first().pk)}), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assert Image.objects.all().count() == 1

    def test_rename_image(self):
        Image.objects.create(project=self.project, name='hello.jpg')

        assert Image.objects.all().count() == 1
        response = self.client.put(reverse('api:image-edit', kwargs={'pk': str(Image.objects.first().pk)}), {'name': 'Natural-red-pear.jpg'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assert Image.objects.all().count() == 1
        assert {i.name for i in Image.objects.all()} == {'hello.jpg'}
