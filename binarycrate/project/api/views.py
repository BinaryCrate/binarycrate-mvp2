# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from ..models import Project
from .serializers import ProjectSerializer
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
#from .permissions import IsOwner
from project.models import DirectoryEntry
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class ProjectList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(owner=user)

    def perform_create(self, serializer):
        de = DirectoryEntry.objects.create(name='', is_file=False)
        serializer.save(owner=self.request.user, root_folder=de)

    serializer_class = ProjectSerializer


class ProjectDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        if project.owner != request.user:
            raise PermissionDenied()
        serializer = ProjectSerializer(project)
        return Response(serializer.data)


