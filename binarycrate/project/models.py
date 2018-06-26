# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

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

    class MPTTMeta:
        order_insertion_by = ['name']

    def __init__(self, *args, **kwargs):
        self._content = ''
        self._form_items = '[]'
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
