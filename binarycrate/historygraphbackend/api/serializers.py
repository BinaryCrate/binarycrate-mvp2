# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from historygraphbackend.models import HistoryEdge
from rest_framework import serializers


class HistoryGraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryEdge
        fields = ('documentcollectionid', 'documentid', 'documentclassname',
                  'classname', 'endnodeid', 'startnode1id', 'startnode2id',
                  'propertyownerid', 'propertyname', 'propertyvalue', 'propertytype')

