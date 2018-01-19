# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from ..models import Project
from .serializers import ProjectSerializer
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from .permissions import IsOwner


#class ProjectList(generics.ListCreateAPIView):
class ProjectList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(owner=user)

    serializer_class = ProjectSerializer


#class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
class ProjectDetail(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


