# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from project.models import Project, DirectoryEntry
import uuid
from accounts.factories import UserFactory
from rest_framework.test import APIClient


class ProjectListTestCase(APITestCase):
    def setUp(self):
        self.project_id = uuid.uuid4()
        u = UserFactory()
        de = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id, name='Test 1', type=0, public=True,
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
        self.assertEqual(response.data, [{'id': str(self.project_id), 'name': 'Test 1', 'type': 0,
                                         'public': True}])


    def test_project_detail(self):
        """
        Ensure we can view individual projects
        """
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'id': str(self.project_id), 'name': 'Test 1', 'type': 0,
                                         'public': True})

    def test_project_post_creates_project(self):
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-list')
        project_id = str(uuid.uuid4())
        data = {'name':'Test 2', 'type':0, 'public':True }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)



class ProjectMustLogin(APITestCase):
    # If the user is not logged in they get 403 errors
    def setUp(self):
        self.project_id = uuid.uuid4()
        u = UserFactory()
        de = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id, name='Test 1', type=0, public=True,
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
        data = { 'id': project_id, 'name':'Test 2', 'type':0, 'public':True }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(str(self.project_id) in response.content)
    
class ProjectCannotAccessOtherUserTestCase(APITestCase):
    def setUp(self):
        self.project_id1 = uuid.uuid4()
        self.project_id2 = uuid.uuid4()
        self.user1 = UserFactory(username='user1@binarycrate.com',email='user1@binarycrate.com')
        self.user2 = UserFactory(username='user2@binarycrate.com',email='user2@binarycrate.com')
        de = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id1, name='Test 1', type=0, public=True,
                               root_folder=de, owner=self.user1)
        de = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id2, name='Test 2', type=0, public=True,
                               root_folder=de, owner=self.user2)
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
        self.assertEqual(response.data, [{'id': str(self.project_id2), 'name': 'Test 2', 'type': 0,
                                         'public': True}])


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
        self.assertEqual(response.data, {'id': str(self.project_id2), 'name': 'Test 2', 'type': 0,
                                         'public': True})



