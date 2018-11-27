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


def save_project(sender, instance, created, raw, **kwargs):
    if created is True:
        if instance.type == 1:
            instance.create_files()
    from .models import DirectoryEntry, ProjectTypes
    if raw is False and created is True and instance.type == ProjectTypes.python_with_storage.value:
        DirectoryEntry.objects.create(name='documents.py', is_file=True,
            parent=instance.get_directory_entries().first(),
            content="""from __future__ import absolute_import, unicode_literals, print_function
from binarycrate import historygraphfrontend
from historygraph import Document, DocumentObject
from historygraph import fields
import inspect
import copy

# Don't change anything above this line
# Your Document definition go here





# Don't change anything below this line
for c in copy.copy(globals().values()):
    if inspect.isclass(c) and issubclass(c, DocumentObject) and c != Document and c != DocumentObject:
        historygraphfrontend.documentcollection.register(c)

historygraphfrontend.download_document_collection()
""")
