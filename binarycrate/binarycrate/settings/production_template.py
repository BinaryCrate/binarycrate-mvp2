# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
from .base import *

ALLOWED_HOSTS = ['*']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'HOST': '',
        'USER': '',
        'CONN_MAX_AGE': 600,
    }
}



