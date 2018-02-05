# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.core.files.storage import FileSystemStorage
from django.conf import settings


project_media_storage = FileSystemStorage(
    location=settings.PROJECT_FILES_ROOT)

