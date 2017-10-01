from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import resolve
from accounts.factories import UserFactory


class LandingPageTestCase(TestCase):
    def test_redirects_to_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/accounts/login/?next=/')

