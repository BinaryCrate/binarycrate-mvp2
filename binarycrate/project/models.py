# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.db import models
import uuid
from mptt.models import MPTTModel, TreeForeignKey
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
    htmlcss = 1

class Project(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=1000)
    type = models.IntegerField(choices=ProjectTypes.choices())
    root_folder = models.OneToOneField(DirectoryEntry)
    public = models.BooleanField()
    owner = models.ForeignKey('accounts.User')

    def get_directory_entries(self):
        return self.root_folder.get_descendants(include_self=True)
