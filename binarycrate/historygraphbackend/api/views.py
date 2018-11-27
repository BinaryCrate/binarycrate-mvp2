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
import json


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
        #serializer = HistoryGraphSerializer(edges, many=True)
        history = [(str(edge.documentid),
                str(edge.documentclassname),
                str(edge.classname),
                str(edge.endnodeid),
                str(edge.startnode1id),
                str(edge.startnode2id),
                str(edge.propertyownerid),
                str(edge.propertyname),
                str(edge.propertyvalue),
                str(edge.propertytype),
                str(edge.nonce)) for edge in edges]
        return Response({'history': history, 'immutableobjects': []})

    def post(self, request, documentcollectionid, format=None):
        #print('HistoryGraphView post received=', request.data)
        #print('HistoryGraphView post received history=', request.data['history'])
        #print('HistoryGraphView post received type history=', type(request.data['history']))
        #print('HistoryGraphView post received imutableobjects=', request.data['immutableobjects'])
        #print('HistoryGraphView post received type imutableobjects=', type(request.data['immutableobjects']))
        historyedges = json.loads(request.data['history']) # Ignore immutable objects for now
        historyedges2 = [{'documentid': t[0],
                'documentclassname': t[1],
                'classname': t[2],
                'endnodeid': t[3],
                'startnode1id': t[4],
                'startnode2id': t[5],
                'propertyownerid': t[6],
                'propertyname': t[7],
                'propertyvalue': t[8],
                'propertytype': t[9],
                'nonce': t[10], 'documentcollectionid': documentcollectionid} for t in historyedges if HistoryEdge.objects.by_endnodeid(t[3]).count() == 0]
        #print('HistoryGraphView post received historyedges2=', historyedges2)
        serializer = HistoryGraphSerializer(data=historyedges2, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
