from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import resolve


class LandingPageTestCase(TestCase):
    def test_redirects_to_login(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        view, args, kwargs = resolve('/')
        # There should be no args or kwargs
        self.assertEqual(len(args), 0)
        self.assertEqual(len(kwargs), 0)
        response = view(request)
        self.assertRedirects(response, '/accounts/login')

