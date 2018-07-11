# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import os
from celery import Celery
from django.conf import settings


# http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'binarycrate.settings.celery')


app = Celery('binarycrate')

app.config_from_object('django.conf:settings', namespace='CELERY')
#app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.autodiscover_tasks()


