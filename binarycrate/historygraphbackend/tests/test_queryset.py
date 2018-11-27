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

from __future__ import absolute_import, print_function, unicode_literals
from rest_framework.test import APITestCase
import uuid
from historygraphbackend.models import HistoryEdge


class TestEdgeQueryset(APITestCase):
    def test_can_filter_by_documentcollection_id(self):
        dcid1 = uuid.uuid4()
        dcid2 = uuid.uuid4()

        HistoryEdge.objects.create(documentcollectionid=dcid1, documentid='AAA', endnodeid=str(uuid.uuid4()))
        HistoryEdge.objects.create(documentcollectionid=dcid2, documentid='BBB', endnodeid=str(uuid.uuid4()))

        qs = HistoryEdge.objects.by_document_collection_id(dcid1)
        assert qs.count() == 1
        assert qs.first().documentid == 'AAA'

    def test_can_filter_by_endnodeid(self):
        dcid1 = uuid.uuid4()
        endnodeid1 = uuid.uuid4()
        endnodeid2 = uuid.uuid4()

        HistoryEdge.objects.create(documentcollectionid=dcid1, documentid='AAA', endnodeid=endnodeid1)
        HistoryEdge.objects.create(documentcollectionid=dcid1, documentid='BBB', endnodeid=endnodeid2)

        qs = HistoryEdge.objects.by_endnodeid(endnodeid1)
        assert qs.count() == 1
        assert qs.first().documentid == 'AAA'
