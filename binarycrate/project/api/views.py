# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from ..models import Project, Image
from .serializers import (ProjectGetSerializer, ProjectPostSerializer,
                          DirectoryEntrySerializer, ImagePostSerializer,
                          ImageGetSerializer, ImagePutSerializer)
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
from rest_framework.mixins import UpdateModelMixin
import copy
from django.http import Http404
from .permissions import IsReadOnlyOrAuthenticated


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class ProjectList(APIView):
    #permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        user = self.request.user
        #return Project.objects.none()
        return Project.objects.filter(owner=user)

    def get(self, request, format=None):
        if self.request.user.is_anonymous:
            raise PermissionDenied()
        projects = self.get_queryset()
        serializer = ProjectGetSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProjectPostSerializer(data=request.data)
        if serializer.is_valid():
            de = DirectoryEntry.objects.create(name='', is_file=False)
            if self.request.user.is_anonymous:
                owner = None
            else:
                owner = self.request.user
            project = serializer.save(owner=owner, root_folder=de)
            self.request.session['project_id'] = str(project.pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    permission_classes = (IsReadOnlyOrAuthenticated, )
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        if not project.public and project.owner != request.user:
            raise PermissionDenied()
        serializer = ProjectGetSerializer(project)
        return Response(serializer.data)

    def delete(self, request,pk, format=None):
        project = self.get_object(pk)
        if project.owner != request.user:
            raise PermissionDenied()
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        project = self.get_object(pk)
        if project.owner != request.user:
            raise PermissionDenied()
        serializer = ProjectPostSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DirectoryEntryDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_object(self, pk):
        try:
            return DirectoryEntry.objects.get(pk=pk)
        except DirectoryEntry.DoesNotExist:
            raise Http404

    def get_or_create_object(self, pk):
        try:
            return DirectoryEntry.objects.get(pk=pk)
        except DirectoryEntry.DoesNotExist:
            return DirectoryEntry(id=pk, is_file=True)

    def put(self, request, pk, format=None):
        de = self.get_or_create_object(pk)
        #print('DirectoryEntryDetail de=', de)
        serializer = DirectoryEntrySerializer(de, data=request.data)
        if serializer.is_valid():
            de = serializer.save()
            de.content = request.data['content'] # TODO: Add some validation here
            de.form_items = request.data['form_items'] # TODO: Add some validation here
            if request.data['parent_id'] is None:
                de.parent = None
            else:
                de.parent = DirectoryEntry.objects.get(id=request.data['parent_id'])
            de.save()
            #print('DirectoryEntryDetail de=', de)
            response_data = copy.copy(serializer.validated_data)
            response_data['content'] = de.content
            response_data['form_items'] = de.form_items
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        de = self.get_object(pk)
        de.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ImageUploadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        serializer = ImagePostSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.validated_data['project']
            if project.owner != request.user:
                raise PermissionDenied()
            image = serializer.save()
            image.save_file(serializer.validated_data['file_data'])
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail' : 'Invalid data.'})

class ImageEditView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_object(self, pk):
        try:
            return Image.objects.get(pk=pk)
        except Image.DoesNotExist:
            raise Http404


    def delete(self, request, pk, *args, **kwargs):
        image = self.get_object(pk)
        if image.project.owner != request.user:
            raise PermissionDenied()
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, *args, **kwargs):
        image = self.get_object(pk)
        serializer = ImagePutSerializer(data=request.data)
        if serializer.is_valid():
            if image.project.owner != request.user:
                raise PermissionDenied()
            image.name = serializer.validated_data['name']
            image.save()
            return Response(status=status.HTTP_200_OK, data={})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail' : 'Invalid data.'})

class ImageListView(APIView):
    """
    List all images belong to a project
    """
    permission_classes = (IsReadOnlyOrAuthenticated, )
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_object(self, project):
        try:
            return Project.objects.get(pk=project)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, project, format=None):
        project = self.get_object(project)
        images = Image.objects.filter(project=project)
        if not project.public and project.owner != request.user:
            raise PermissionDenied()
        serializer = ImageGetSerializer(images, many=True)
        return Response(serializer.data)
