# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from binarycrate.celery import app as celery


#TODO: This task is included for example purposes for how to write them these debug tasks should be removed once real tasks are created
@celery.task()
def debug_task(val):
    print('Request: {0}'.format(val))

