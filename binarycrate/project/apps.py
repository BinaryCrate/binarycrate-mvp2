# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig
from django.db.models import signals



class ProjectConfig(AppConfig):
    name = 'project'

    def ready(self):
        from . import receivers
        signals.post_save.connect(
            receivers.save_de_content, sender='project.DirectoryEntry',
            dispatch_uid='project.DirectoryEntry.save')

        signals.post_init.connect(
            receivers.load_de_content, sender='project.DirectoryEntry',
            dispatch_uid='project.DirectoryEntry.init')

        signals.post_save.connect(
            receivers.create_html_files, sender='project.Project',
            dispatch_uid='project.Project.save')
