# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from ..models import Project
from .serializers import ProjectGetSerializer, ProjectPostSerializer
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
from rest_framework import status


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class ProjectList(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        user = self.request.user
        #return Project.objects.none()
        return Project.objects.filter(owner=user)

    def get(self, request, format=None):
        projects = self.get_queryset()
        serializer = ProjectGetSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProjectPostSerializer(data=request.data)
        if serializer.is_valid():
            de = DirectoryEntry.objects.create(name='', is_file=False)
            serializer.save(owner=self.request.user, root_folder=de)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        #print('ProjectDetail project.owner=',project.owner)
        #print('ProjectDetail request.user=',request.user)
        if project.owner != request.user:
            raise PermissionDenied()
        serializer = ProjectGetSerializer(project)
        return Response(serializer.data)


