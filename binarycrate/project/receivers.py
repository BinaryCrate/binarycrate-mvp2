# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from binarycrate.storage import project_media_storage
from cStringIO import StringIO
from .models import Project, ProjectTypes

def save_de_content(sender, instance, created, raw, **kwargs):
    #print ('save_de_content called instance._content=',instance._content)
    if raw is False:
        project_media_storage.delete(str(instance.id))
        project_media_storage.save(str(instance.id), StringIO(instance._content))
        project_media_storage.delete(str(instance.id) + '-form-items')
        project_media_storage.save(str(instance.id) + '-form-items', StringIO(instance._form_items))


def load_de_content(sender, instance, **kwargs):
    if project_media_storage.exists(str(instance.id)):
        with project_media_storage.open(str(instance.id), 'r') as project_file:
            instance._content = project_file.read()
            #print('load_de_content instance._content=', instance._content)
    if project_media_storage.exists(str(instance.id) + '-form-items'):
        with project_media_storage.open(str(instance.id) + '-form-items', 'r') as project_file:
            instance._form_items = project_file.read()

def create_html_files(sender, instance, created, raw, **kwargs):
    if created is True:
        if instance.type == 1:
            instance.create_files()
