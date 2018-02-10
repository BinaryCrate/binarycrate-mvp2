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

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        #print('DirectoryEntry content.setter value=', value)
        self._content = value

    class MPTTMeta:
        order_insertion_by = ['name']

    def __init__(self, *args, **kwargs):
        self._content = ''
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

    
