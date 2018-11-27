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
from django.test.client import RequestFactory
from django.core.urlresolvers import resolve, reverse
from accounts.factories import UserFactory
from accounts.models import User
from django.conf import settings


class LandingPageTestCase(TestCase):
    def test_redirects_to_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/accounts/login/?next=/')

    def test_logged_in_gets_correct_page(self):
        # Create a non-admin user.
        self.user = User.objects.create_user('a@a.com', 'userpass')
        self.client.login(username='a@a.com', password='userpass')

        #Check if the content is valid
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        response.render()
        self.assertIn(b"pypyjs", response.content)
        self.assertIn(settings.BUILD_NUMBER, response.content)
        # Check we are loading the correct boot file
        self.assertIn('bootbc.py', response.content)
