from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import resolve, reverse
from accounts.factories import UserFactory
from accounts.models import User


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


