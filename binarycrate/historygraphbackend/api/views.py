# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
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
from historygraphbackend.models import HistoryEdge
from .serializers import HistoryGraphSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class HistoryGraphView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_queryset(self, documentcollectionid):
        return HistoryEdge.objects.by_document_collection_id(documentcollectionid)

    def get(self, request, documentcollectionid, format=None):
        edges = self.get_queryset(documentcollectionid)
        serializer = HistoryGraphSerializer(edges, many=True)
        return Response({'history': serializer.data, 'immutableobjects': []})

    def post(self, request, documentcollectionid, format=None):
        data = request.data['history'] # Ignore immutable objects for now
        serializer = HistoryGraphSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

