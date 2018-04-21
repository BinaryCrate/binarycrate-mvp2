# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a user."""
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creates and saves a user with ``is_superuser`` set to ``True```."""
        return self.create_user(email, password, is_staff=True,
                                is_superuser=True, **extra_fields)
