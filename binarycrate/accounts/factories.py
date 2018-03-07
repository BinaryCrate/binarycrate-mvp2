# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import factory


class UserFactory(factory.django.DjangoModelFactory):

    email = factory.Sequence(lambda n: '{}@users.example.com'.format(n))

    class Meta(object):
        django_get_or_create = ['email']
        model = 'accounts.User'
