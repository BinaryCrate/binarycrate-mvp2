# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from .models import Project
from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'type', 'public')
