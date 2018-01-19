# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from ..models import Project
from ..serializers import ProjectSerializer
from rest_framework import mixins
from rest_framework import generics


#class ProjectList(generics.ListCreateAPIView):
class ProjectList(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


#class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
class ProjectDetail(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


