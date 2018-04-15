# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.db import models
from django.contrib.auth.models import AbstractUser
from . import managers


class User(AbstractUser):
    email = models.EmailField('email address', max_length=254, unique=True,
                              db_index=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Should not include USERNAME_FIELD

    objects = managers.UserManager()

