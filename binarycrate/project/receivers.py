# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from binarycrate.storage import project_media_storage
from cStringIO import StringIO


def save_de_content(sender, instance, created, raw, **kwargs):
    if raw is False:
        project_media_storage.delete(str(instance.id))
        project_media_storage.save(str(instance.id), StringIO(instance.content))


def load_de_content(sender, instance, **kwargs):
    if project_media_storage.exists(str(instance.id)):
        with project_media_storage.open(str(instance.id), 'r') as project_file:
            instance.content = project_file.read()
        
