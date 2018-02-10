# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from ..models import Project, DirectoryEntry
from rest_framework import serializers


class DirectoryEntrySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super(DirectoryEntrySerializer, self).to_representation(instance)
        if ret['parent_id'] is not None:
            ret['parent_id'] = str(ret['parent_id'])
        return ret

    class Meta:
        model = DirectoryEntry
        fields = ('id', 'name', 'is_file', 'parent_id', 'content')

class ProjectGetSerializer(serializers.ModelSerializer):
    directory_entry = DirectoryEntrySerializer(many=True, source='get_directory_entries')

    class Meta:
        model = Project
        fields = ('id', 'name', 'type', 'public', 'directory_entry')

class ProjectPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'type', 'public')
