# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from historygraphbackend.models import HistoryEdge
from rest_framework import serializers


class HistoryGraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryEdge
        fields = ('documentcollectionid', 'documentid', 'documentclassname',
                  'classname', 'endnodeid', 'startnode1id', 'startnode2id',
                  'propertyownerid', 'propertyname', 'propertyvalue', 'propertytype', 'nonce')
        extra_kwargs = {'startnode2id': {'required': True}} 

    def create(self, validated_data):
        #TODO: There is no meaningful validation of submit HistoryGraph edges. Pls fix
        if HistoryEdge.objects.by_endnodeid(validated_data['endnodeid']).count() == 0:
            # Duplicate HistoryEdges are ignored
            return super(HistoryGraphSerializer, self).create(validated_data)
        else:
            return HistoryEdge.objects.by_endnodeid(validated_data['endnodeid']).get()

