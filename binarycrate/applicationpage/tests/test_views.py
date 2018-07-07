# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import resolve, reverse
from accounts.factories import UserFactory
from accounts.models import User
from django.conf import settings
import uuid


class ApplicationPageTestCase(TestCase):
    def test_anonymous_login_displays_the_correct_page(self):
        #Check if the content is valid
        response = self.client.get('/app/')
        self.assertEqual(response.status_code, 200)
        response.render()
        self.assertIn(b"pypyjs", response.content)
        self.assertIn(settings.BUILD_NUMBER, response.content)
        # Check we are loading the correct boot file
        self.assertIn('bootbc_anonymous_user.py', response.content)
        assert response.context['is_anonymous'] == 'true'
        self.assertIn('data-is-anonymous=\'true\'', response.content)
        self.assertIn('data-anonymous-project-id=\'\'', response.content)

    def test_logged_in_gets_correct_page(self):
        # Create a non-admin user.
        self.user = User.objects.create_user('a@a.com', 'userpass')
        self.client.login(username='a@a.com', password='userpass')

        #Check if the content is valid
        response = self.client.get('/app/')
        self.assertEqual(response.status_code, 200)
        response.render()
        self.assertIn(b"pypyjs", response.content)
        self.assertIn(settings.BUILD_NUMBER, response.content)
        # Check we are loading the correct boot file
        self.assertIn('bootbc.py', response.content)
        assert response.context['is_anonymous'] == 'false'
        self.assertIn('data-is-anonymous=\'false\'', response.content)

    def test_anonymous_login_includes_the_correct_project_id(self):
        #Check if the content is valid
        project_id = str(uuid.uuid4())
        session = self.client.session
        session['project_id'] = project_id
        session.save()
        response = self.client.get('/app/')
        self.assertEqual(response.status_code, 200)
        response.render()
        self.assertIn(b"pypyjs", response.content)
        self.assertIn(settings.BUILD_NUMBER, response.content)
        # Check we are loading the correct boot file
        self.assertIn('bootbc_anonymous_user.py', response.content)
        assert response.context['is_anonymous'] == 'true'
        self.assertIn('data-is-anonymous=\'true\'', response.content)
        self.assertIn('data-anonymous-project-id=\'' + project_id + '\'', response.content)
