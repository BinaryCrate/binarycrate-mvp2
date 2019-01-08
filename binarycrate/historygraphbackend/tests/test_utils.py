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
from rest_framework.test import APITestCase
from historygraph import DocumentCollection, Document, fields
from historygraphbackend.api.serializers import HistoryGraphWriteSerializer
from historygraphbackend.utils import get_unknown_edges, get_start_node1, get_start_node2


class HistoryGraphFilterSingleDocumentTestCase(APITestCase):
    def setUp(self):
        # Create a document and make some changes
        class Covers(Document):
            covers = fields.IntRegister()
            table = fields.IntRegister()
        self.dc1 = DocumentCollection()
        self.dc1.register(Covers)
        self.test = Covers()
        self.dc1.add_document_object(self.test)
        self.test.covers = 1
        self.clockhash1 = self.test._clockhash
        self.test.covers = 2

        historyedges2 = [{'documentid': e.documentid,
                'documentclassname': e.documentclassname,
                'classname': e.__class__.__name__,
                'endnodeid': e.get_end_node(),
                'startnode1id':get_start_node1(e),
                'startnode2id': get_start_node2(e),
                'propertyownerid': e.propertyownerid,
                'propertyname': e.propertyname,
                'propertyvalue': e.propertyvalue,
                'propertytype': e.propertytype,
                'nonce': e.nonce,
                'transaction_id': e.transaction_hash,
                'documentcollectionid': self.dc1.id}
                for e in self.test.history.get_all_edges()]
        serializer = HistoryGraphWriteSerializer(data=historyedges2, many=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

    def test_get_all_edges_if_nothing_known(self):
        l = get_unknown_edges(self.dc1.id, {})
        self.assertEqual(len(l), 2)
        self.assertEqual({e.endnodeid for e in l},
                         {self.clockhash1, self.test._clockhash})

    def test_get_no_edges_if_everything_known(self):
        l = get_unknown_edges(self.dc1.id,
                              {self.test.id: self.test._clockhash})
        self.assertEqual(len(l), 0)

    def test_get_some_edges_if_partially_known(self):
        l = get_unknown_edges(self.dc1.id,
                              {self.test.id: self.clockhash1})
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].endnodeid, self.test._clockhash)

class HistoryGraphFilterMultipleDocumentTestCase(APITestCase):
    def setUp(self):
        def save_historygraph(historygraph, documentcollectionid):
            historyedges2 = [{'documentid': e.documentid,
                    'documentclassname': e.documentclassname,
                    'classname': e.__class__.__name__,
                    'endnodeid': e.get_end_node(),
                    'startnode1id':get_start_node1(e),
                    'startnode2id': get_start_node2(e),
                    'propertyownerid': e.propertyownerid,
                    'propertyname': e.propertyname,
                    'propertyvalue': e.propertyvalue,
                    'propertytype': e.propertytype,
                    'nonce': e.nonce,
                    'transaction_id': e.transaction_hash,
                    'documentcollectionid': documentcollectionid}
                    for e in historygraph.get_all_edges()]
            serializer = HistoryGraphWriteSerializer(data=historyedges2, many=True)
            self.assertTrue(serializer.is_valid(), serializer.errors)
            serializer.save()

        # Create a document and make some changes
        class Covers(Document):
            covers = fields.IntRegister()
            table = fields.IntRegister()
        self.dc1 = DocumentCollection()
        self.dc1.register(Covers)
        self.test = Covers()
        self.dc1.add_document_object(self.test)
        self.test.covers = 1
        self.clockhash1 = self.test._clockhash
        self.test.covers = 2
        save_historygraph(self.test.history, self.dc1.id)

        self.dc2 = DocumentCollection()
        self.dc2.register(Covers)
        self.test2 = Covers()
        self.dc2.add_document_object(self.test2)
        self.test2.covers = 3
        self.clockhash2 = self.test2._clockhash
        self.test2.covers = 4
        self.test3 = Covers()
        self.dc2.add_document_object(self.test3)
        self.test3.covers = 5
        self.clockhash3 = self.test3._clockhash
        self.test3.covers = 6
        save_historygraph(self.test2.history, self.dc2.id)
        save_historygraph(self.test3.history, self.dc2.id)


    def test_get_all_edges_if_nothing_known(self):
        l = get_unknown_edges(self.dc1.id, {})
        self.assertEqual(len(l), 2)
        self.assertEqual({e.endnodeid for e in l},
                         {self.clockhash1, self.test._clockhash})

    def test_get_no_edges_if_everything_known(self):
        l = get_unknown_edges(self.dc1.id,
                              {self.test.id: self.test._clockhash})
        self.assertEqual(len(l), 0)

    def test_get_some_edges_if_partially_known(self):
        l = get_unknown_edges(self.dc1.id,
                              {self.test.id: self.clockhash1})
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].endnodeid, self.test._clockhash)

    def test_get_some_edges_if_some_partially_known_others_unknown(self):
        l = get_unknown_edges(self.dc2.id,
                              {self.test2.id: self.clockhash2})
        self.assertEqual(len(l), 3)
        self.assertEqual({e.endnodeid for e in l},
                         {self.test2._clockhash, self.clockhash3, self.test3._clockhash})
