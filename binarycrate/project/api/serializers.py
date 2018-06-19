# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from ..models import Project, DirectoryEntry, Image
from rest_framework import serializers
import copy


class DirectoryEntrySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super(DirectoryEntrySerializer, self).to_representation(instance)
        if ret['parent_id'] is not None:
            ret['parent_id'] = str(ret['parent_id'])
        return ret

    class Meta:
        model = DirectoryEntry
        fields = ('id', 'name', 'is_file', 'parent_id', 'content', 'form_items', 'is_default')
        extra_kwargs = {'is_default': {'required': True}} 

class ProjectGetSerializer(serializers.ModelSerializer):
    directory_entry = DirectoryEntrySerializer(many=True, source='get_directory_entries')

    class Meta:
        model = Project
        fields = ('id', 'name', 'type', 'public', 'directory_entry')

class ProjectPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'type', 'public')


class ImagePostSerializer(serializers.ModelSerializer):
    file_data = serializers.FileField()

    def create(self, validated_data):
        validated_data = copy.copy(validated_data)
        del validated_data['file_data']
        return super(ImagePostSerializer, self).create(validated_data)

    class Meta:
        model = Image
        fields = ('name', 'project', 'file_data')
    
class ImageGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'name', 'image_url')

class ImagePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('name',)

