# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from project.models import Project, DirectoryEntry
import uuid
from accounts.factories import UserFactory
from rest_framework.test import APIClient


# From https://gist.github.com/href/1319371
from collections import namedtuple
DirectoryEntryDict = namedtuple('DirectoryEntryDict', ['id', 'name', 'is_file', 'parent_id', 'content', 'form_items', 'is_default'])
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

    def test_project_post_creates_project(self):
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-list')
        project_id = str(uuid.uuid4())
        data = {'name':'Test 2', 'type':0, 'public':False }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)

    def test_put_project_detail(self):
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

    def test_delete_project_detail(self):
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
                          'parent_id': None,
                          'is_default': False,
                         }),
                         convert({'id': str(self.de_hello_world.id),
                          'name': self.de_hello_world.name,
                          'is_file': self.de_hello_world.is_file,
                          'content': self.de_hello_world.content,
                          'form_items': '[]',
                          'parent_id': str(self.de_rootfolder.id),
                          'is_default': True,
                         }),
                         convert({'id': str(self.de_folder.id),
                          'name': self.de_folder.name,
                          'is_file': self.de_folder.is_file,
                          'content': '',
                          'form_items': '[]',
                          'parent_id': str(self.de_rootfolder.id),
                          'is_default': False,
                         }),
                         convert({'id': str(self.de_hello_folder.id),
                          'name': self.de_hello_folder.name,
                          'is_file': self.de_hello_folder.is_file,
                          'content': self.de_hello_folder.content,
                          'form_items': '[]',
                          'parent_id': str(self.de_folder.id),
                          'is_default': False,
                         }),
                         })

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
                          'is_default': True,
                         }
        response = self.client.put(url, data, format='json')
        #print('response.content=', response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DirectoryEntry.objects.get(id=self.de_hello_world.id).content, "print('Hello world2')")
        self.assertEqual(DirectoryEntry.objects.get(id=self.de_hello_world.id).form_items, "[{'id': '37ce1ec8-84dc-4b5e-8a09-9411c5007a0'}]")
        self.assertEqual(DirectoryEntry.objects.get(id=self.de_hello_world.id).is_default, True)

    def test_put_can_create_a_new_directory_entry(self):
        data = {'id': str(uuid.uuid4()),
                          'name': 'Hello world2',
                          'is_file': True,
                          'content': "print('Hello world4')",
                          'parent_id': str(self.de_rootfolder.id),
                          'form_items': "[{'id': '37ce1ec8-84dc-4b5e-8a09-9411c5007a0'}]",
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
                          'parent_id': None,
                          'is_default': False,
                         }),
                         convert({'id': str(self.de_hello_world.id),
                          'name': self.de_hello_world.name,
                          'is_file': self.de_hello_world.is_file,
                          'content': self.de_hello_world.content,
                          'form_items': '[]',
                          'parent_id': str(self.de_rootfolder.id),
                          'is_default': True,
                         }),
                         convert({'id': str(self.de_folder.id),
                          'name': self.de_folder.name,
                          'is_file': self.de_folder.is_file,
                          'content': '',
                          'form_items': '[]',
                          'parent_id': str(self.de_rootfolder.id),
                          'is_default': False,
                         }),
                         convert({'id': str(self.de_hello_folder.id),
                          'name': self.de_hello_folder.name,
                          'is_file': self.de_hello_folder.is_file,
                          'content': self.de_hello_folder.content,
                          'form_items': '[]',
                          'parent_id': str(self.de_folder.id),
                          'is_default': False,
                         }),
                         })


