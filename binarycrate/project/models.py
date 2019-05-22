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

from django.db import models
import uuid
from mptt.models import MPTTModel, TreeForeignKey
from binarycrate.storage import project_media_storage
from common.utils import ChoiceEnum

class DirectoryEntry(MPTTModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=1000)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    is_file = models.BooleanField()
    is_default = models.BooleanField(default=False)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def form_items(self):
        return self._form_items

    @form_items.setter
    def form_items(self, value):
        self._form_items = value

    @property
    def form_properties(self):
        return self._form_properties

    @form_properties.setter
    def form_properties(self, value):
        self._form_properties = value

    class MPTTMeta:
        order_insertion_by = ['name']

    def __init__(self, *args, **kwargs):
        self._content = ''
        self._form_items = '[]'
        self._form_properties = '{}'
        super(DirectoryEntry, self).__init__(*args, **kwargs)

class ProjectTypes(ChoiceEnum):
    python = 0
    webpage = 1
    python_with_storage = 2

class Project(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=1000)
    type = models.IntegerField(choices=ProjectTypes.choices())
    root_folder = models.OneToOneField(DirectoryEntry)
    public = models.BooleanField()
    owner = models.ForeignKey('accounts.User')

    def get_directory_entries(self):
        return self.root_folder.get_descendants(include_self=True)

    def create_files(self):
        DirectoryEntry.objects.create(parent=self.root_folder, name='index.html', is_file=True)
        DirectoryEntry.objects.create(parent=self.root_folder, name='styles.css', is_file=True)
        DirectoryEntry.objects.create(parent=self.root_folder, name='scripts.js', is_file=True)

class Image(models.Model):
    # Represents an image uploaded by a user
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=1000)
    project = models.ForeignKey(Project, related_name='images')

    def save_file(self, f):
        # f = a file handle or compatible object which we will read in from to save the file to disk or an S3 bucket
        filename = self.get_file_name()
        project_media_storage.delete(filename)
        project_media_storage.save(filename, f)

    def get_file_name(self):
        # Returns the name of the file
        return 'images-{0}/{1}'.format(self.project.id, self.id)

    def get_file_extension(self):
        i = self.name.rfind('.')
        assert i >= 0
        return self.name[i:]

    def get_url(self):
        # Returns an URL that the file can be downloaded from. Could be a local url or a S3 bucket URL
        # In production the Nginx web server will be redirected to download this file
        return '/images/images-{0}/{1}{2}'.format(self.project.id, self.id, self.get_file_extension())


    @property
    def image_url(self):
        return self.get_url()
