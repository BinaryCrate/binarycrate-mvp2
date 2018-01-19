# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
#from myproject.apps.core.models import Account
from project.models import Project, DirectoryEntry
import uuid


class ProjectListTestCase(APITestCase):
    def setUp(self):
        self.project_id = uuid.uuid4()
        de = DirectoryEntry.objects.create(name='', is_file=False)
        Project.objects.create(id=self.project_id, name='Test 1', type=0, public=True,
                               root_folder=de)

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
        Ensure we can list the projects
        """
        self.assertEqual(Project.objects.count(), 1)
        url = reverse('api:project-detail', kwargs={'pk':str(self.project_id)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'id': str(self.project_id), 'name': 'Test 1', 'type': 0,
                                         'public': True})

