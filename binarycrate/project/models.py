# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.db import models
import uuid
from mptt.models import MPTTModel, TreeForeignKey

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


class Project(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=1000)
    type = models.IntegerField()
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
        assert False

    def get_url(self):
        # Returns an URL that the file can be downloaded from. Could be a local url or a S3 bucket URL
        # In production the Nginx web server will be redirected to download this file
        return ''


        
