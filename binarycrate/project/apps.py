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

from __future__ import absolute_import, print_function, unicode_literals

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
            receivers.save_project, sender='project.Project',
            dispatch_uid='project.Project.save')
