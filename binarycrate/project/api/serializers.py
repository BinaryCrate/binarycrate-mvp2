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
        fields = ('id', 'name', 'is_file', 'parent_id', 'content',
                  'form_items', 'form_properties', 'is_default')
        extra_kwargs = {'is_default': {'required': True}}

class ProjectGetSerializer(serializers.ModelSerializer):
    directory_entry = DirectoryEntrySerializer(many=True,
                                               source='get_directory_entries')

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
