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

from historygraphbackend.models import HistoryEdge
from rest_framework import serializers


class HistoryGraphWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryEdge
        fields = ('documentcollectionid', 'documentid', 'documentclassname',
                  'classname', 'endnodeid', 'startnode1id', 'startnode2id',
                  'propertyownerid', 'propertyname', 'propertyvalue',
                  'propertytype', 'nonce', 'transaction_id')
        extra_kwargs = {'startnode2id': {'required': True}}

    def create(self, validated_data):
        #TODO: There is no meaningful validation of submit HistoryGraph edges. Pls fix
        if HistoryEdge.objects.by_endnodeid(validated_data['endnodeid']).count() == 0:
            # Duplicate HistoryEdges are ignored
            return super(HistoryGraphWriteSerializer, self).create(validated_data)
        else:
            return HistoryEdge.objects.by_endnodeid(validated_data['endnodeid']).get()
