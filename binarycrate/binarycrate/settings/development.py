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

from __future__ import absolute_import, unicode_literals, print_function
import os
from .base import *

ALLOWED_HOSTS = ['*']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*q)qs493d1wcmmv3v#z3lz5dy8^#8c&q+w-%79d!w#lh379*47'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Email

# Uncomment to use the standard debugging email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#Uncomment to test email sending with sendgrid
#EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"

#TODO: Make this a parameter we can pass on the command line to fab/docker
#SENDGRID_API_KEY = "xxx"

#SENDGRID_SANDBOX_MODE_IN_DEBUG = False

#SENDGRID_ECHO_TO_STDOUT = True
