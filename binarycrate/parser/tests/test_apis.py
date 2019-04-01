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
from django.urls import reverse
from rest_framework import status
from accounts.factories import UserFactory


class ParserTestCase(APITestCase):
    def setUp(self):
        u = UserFactory()
        self.client.force_authenticate(user=u)

    def test_simple_parse_example(self):
        url = reverse('api:parser-get-member-functions')
        data = {'content': """class MyForm(Form):
    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        self.name = ""
""" }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], ["__init__", 2])


    def test_parse_class_with_two_functions(self):
        url = reverse('api:parser-get-member-functions')
        data = {'content': """class MyForm(Form):
    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        self.name = ""

    def button1_onclick(self, e):
        pass
""" }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0], ["__init__", 2])
        self.assertEqual(response.data[1], ["button1_onclick", 6])


class AddFunctionToClassTestCase(APITestCase):
    def setUp(self):
        u = UserFactory()
        self.client.force_authenticate(user=u)

    def test_simple_add_member_function(self):
        url = reverse('api:parser-add-member-function')
        data = {'content': """class MyForm(Form):
    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        self.name = ""
""",
        'function_name': 'button1_onclick',
        'newfunction': """def button1_onclick(self, e):
    pass
"""}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data['content'], """class MyForm(Form):
    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        self.name = ""
    def button1_onclick(self, e):
        pass
""")
        self.assertEqual(response.data['new_functions'], [["__init__", 2],
                         ["button1_onclick", 5]])
