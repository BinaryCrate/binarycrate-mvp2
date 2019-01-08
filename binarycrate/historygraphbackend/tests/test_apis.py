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
from accounts.factories import UserFactory
from historygraphbackend.models import HistoryEdge
import uuid
from django.urls import reverse
from rest_framework import status
import json
from historygraph import Document, fields, DocumentCollection
from historygraphbackend.utils import get_start_node1, get_start_node2
from historygraphbackend.api.serializers import HistoryGraphWriteSerializer


class HistoryGraphGetTestCase(APITestCase):
    def setUp(self):
        self.dcid1 = uuid.uuid4()
        self.dcid2 = uuid.uuid4()

        HistoryEdge.objects.create(documentcollectionid=self.dcid1,
                                   documentid='A',
                                   documentclassname='B',
                                   classname='C',
                                   endnodeid=str(uuid.uuid4()),
                                   startnode1id='D',
                                   startnode2id='E',
                                   propertyownerid='F',
                                   propertyname='G',
                                   propertyvalue='H',
                                   propertytype='I')
        HistoryEdge.objects.create(documentcollectionid=self.dcid2,
                                   documentid='A1',
                                   documentclassname='B1',
                                   classname='C1',
                                   endnodeid=str(uuid.uuid4()),
                                   startnode1id='D1',
                                   startnode2id='E1',
                                   propertyownerid='F1',
                                   propertyname='G1',
                                   propertyvalue='H1',
                                   propertytype='I1')
        HistoryEdge.objects.create(documentcollectionid=self.dcid2,
                                   documentid='A2',
                                   documentclassname='B2',
                                   classname='C2',
                                   endnodeid=str(uuid.uuid4()),
                                   startnode1id='D2',
                                   startnode2id='E2',
                                   propertyownerid='F2',
                                   propertyname='G2',
                                   propertyvalue='H2',
                                   propertytype='I2')


    def test_get_historygraph(self):
        """
        Ensure we can list a projects history graph edges if we are logged in
        """
        u = UserFactory()
        self.client.force_authenticate(user=u)

        self.assertEqual(HistoryEdge.objects.count(), 3)

        url = reverse('api:historygraph-list', kwargs=
                      {'documentcollectionid': str(self.dcid1)})
        data = [ ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data['immutableobjects'], [])
        historyedges = response.data['history']
        self.assertEqual(len(historyedges), 1)
        #self.assertEqual(historyedges[0]['documentcollectionid'], str(self.dcid1))
        self.assertEqual(historyedges[0][0], 'A')
        self.assertEqual(historyedges[0][1], 'B')
        self.assertEqual(historyedges[0][2], 'C')
        #self.assertEqual(historyedges[0][3], 'D')
        self.assertEqual(historyedges[0][4], 'D')
        self.assertEqual(historyedges[0][5], 'E')
        self.assertEqual(historyedges[0][6], 'F')
        self.assertEqual(historyedges[0][7], 'G')
        self.assertEqual(historyedges[0][8], 'H')

        def get_response_data_set(response_data, k):
            return {d[k] for d in response_data}

        url = reverse('api:historygraph-list', kwargs=
                      {'documentcollectionid': str(self.dcid2)})
        data = [ ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data['immutableobjects'], [])
        historyedges = response.data['history']
        self.assertEqual(len(historyedges), 2)
        #self.assertEqual(get_response_data_set(historyedges, 'documentcollectionid'), {str(self.dcid2)})
        self.assertEqual(get_response_data_set(historyedges, 0), {'A1', 'A2'})
        self.assertEqual(get_response_data_set(historyedges, 1), {'B1', 'B2'})
        self.assertEqual(get_response_data_set(historyedges, 2), {'C1', 'C2' })
        #self.assertEqual(get_response_data_set(historyedges, 3), {'D1', 'D2' })
        self.assertEqual(get_response_data_set(historyedges, 4), {'D1', 'D2' })
        self.assertEqual(get_response_data_set(historyedges, 5), {'E1', 'E2' })
        self.assertEqual(get_response_data_set(historyedges, 6), {'F1', 'F2'})
        self.assertEqual(get_response_data_set(historyedges, 7), {'G1', 'G2'})
        self.assertEqual(get_response_data_set(historyedges, 8), {'H1', 'H2'})

    def test_login_is_required(self):
        url = reverse('api:historygraph-list',
                      kwargs={'documentcollectionid': str(self.dcid1)})
        data = [ ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(str(self.dcid1) in response.content)

    def test_get_unknown_historygraph(self):
        """
        Ensure we can list an empty list if there are no historygraph edges available
        """
        u = UserFactory()
        self.client.force_authenticate(user=u)

        url = reverse('api:historygraph-list',
                      kwargs={'documentcollectionid': str(uuid.uuid4())})
        data = [ ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['history']), 0)

    def test_post_creates_historygraph_edges(self):
        u = UserFactory()
        self.client.force_authenticate(user=u)

        url = reverse('api:historygraph-post',
                      kwargs={'documentcollectionid': str(self.dcid2)})
        project_id = str(uuid.uuid4())
        self.assertEqual(HistoryEdge.objects.count(), 3)
        """
        historyedges = [{'documentcollectionid':str(self.dcid2),
                 'documentid':'A4',
                 'documentclassname':'B4',
                 'classname':'C4',
                 'endnodeid':str(uuid.uuid4()),
                 'startnode1id':'D4',
                 'startnode2id':'E4',
                 'propertyownerid':'F4',
                 'propertyname':'G4',
                 'propertyvalue':'H4',
                 'propertytype':'I4',
                 'transaction_id':'J4'},
                {'documentcollectionid':str(self.dcid2),
                 'documentid':'A5',
                 'documentclassname':'B5',
                 'classname':'C5',
                 'endnodeid':str(uuid.uuid4()),
                 'startnode1id':'D5',
                 'startnode2id':'E5',
                 'propertyownerid':'F5',
                 'propertyname':'G5',
                 'propertyvalue':'H5',
                 'propertytype':'I5',
                 'transaction_id':'J5'}]
        """
        historyedges = [('A4',
                 'B4',
                 'C4',
                 str(uuid.uuid4()),
                 'D4',
                 'E4',
                 'F4',
                 'G4',
                 'H4',
                 'I4',
                 'J4',
                 'K4'),
                ('A5',
                 'B5',
                 'C5',
                 str(uuid.uuid4()),
                 'D5',
                 'E5',
                 'F5',
                 'G5',
                 'H5',
                 'I5',
                 'J5',
                 'K5')]
        data = {'history': json.dumps(historyedges), 'immutableobjects': json.dumps([])}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HistoryEdge.objects.count(), 5)

        classnames = {edge.classname for edge in HistoryEdge.objects.by_document_collection_id(self.dcid2)}
        self.assertIn('C4', classnames)
        self.assertIn('C5', classnames)

    def test_post_historygraph_edges_requires_login(self):
        url = reverse('api:historygraph-post',
                      kwargs={'documentcollectionid': str(self.dcid2)})
        project_id = str(uuid.uuid4())
        self.assertEqual(HistoryEdge.objects.count(), 3)
        data = [{'documentcollectionid':str(self.dcid2),
                 'documentid':'A4',
                 'documentclassname':'B4',
                 'classname':'C4',
                 'endnodeid':str(uuid.uuid4()),
                 'startnode1id':'D4',
                 'startnode2id':'E4',
                 'propertyownerid':'F4',
                 'propertyname':'G4',
                 'propertyvalue':'H4',
                 'propertytype':'I4'},
                {'documentcollectionid':str(self.dcid2),
                 'documentid':'A5',
                 'documentclassname':'B5',
                 'classname':'C5',
                 'endnodeid':str(uuid.uuid4()),
                 'startnode1id':'D5',
                 'startnode2id':'E5',
                 'propertyownerid':'F5',
                 'propertyname':'G5',
                 'propertyvalue':'H5',
                 'propertytype':'I5'}]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_post_historygraph_edges_duplicates_are_ignored(self):
        u = UserFactory()
        self.client.force_authenticate(user=u)

        url = reverse('api:historygraph-post',
                      kwargs={'documentcollectionid': str(self.dcid2)})
        project_id = str(uuid.uuid4())
        self.assertEqual(HistoryEdge.objects.count(), 3)
        endnodeid = str(uuid.uuid4())
        """
        historyedges = [{'documentcollectionid':str(self.dcid2),
                 'documentid':'A4',
                 'documentclassname':'B4',
                 'classname':'C4',
                 'endnodeid':endnodeid,
                 'startnode1id':'D4',
                 'startnode2id':'E4',
                 'propertyownerid':'F4',
                 'propertyname':'G4',
                 'propertyvalue':'H4',
                 'propertytype':'I4',
                 'transaction_id':'J4'},
                {'documentcollectionid':str(self.dcid2),
                 'documentid':'A4',
                 'documentclassname':'B4',
                 'classname':'C4',
                 'endnodeid':endnodeid,
                 'startnode1id':'D4',
                 'startnode2id':'E4',
                 'propertyownerid':'F4',
                 'propertyname':'G4',
                 'propertyvalue':'H4',
                 'propertytype':'I4',
                 'transaction_id':'J4'}]
        """
        historyedges = [('A4',
                 'B4',
                 'C4',
                 endnodeid,
                 'D4',
                 'E4',
                 'F4',
                 'G4',
                 'H4',
                 'I4',
                 'J4',
                 'K4'),
                ('A4',
                 'B4',
                 'C4',
                 endnodeid,
                 'D4',
                 'E4',
                 'F4',
                 'G4',
                 'H4',
                 'I4',
                 'J4',
                 'K4')]
        data = {'history': json.dumps(historyedges), 'immutableobjects': json.dumps([])}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HistoryEdge.objects.count(), 4)

        classnames = {edge.classname for edge in HistoryEdge.objects.by_document_collection_id(self.dcid2)}
        self.assertIn('C4', classnames)
        self.assertNotIn('C5', classnames)

    def test_can_delete_all_edges_by_document_id(self):
        u = UserFactory()
        self.client.force_authenticate(user=u)
        url = reverse('api:historygraph-post', kwargs=
                      {'documentcollectionid': str(self.dcid2)})
        self.assertEqual(HistoryEdge.objects.count(), 3)
        data = {}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(HistoryEdge.objects.count(), 1)
        self.assertEqual(HistoryEdge.objects.first().documentcollectionid, self.dcid1)

class HistoryGraphFilteredGetTestCase(APITestCase):
    def test_return_subset_of_edges(self):
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

        u = UserFactory()
        self.client.force_authenticate(user=u)
        url = reverse('api:historygraph-list', kwargs=
                      {'documentcollectionid': str(self.dc2.id)})
        data = [{'documentid':self.test2.id, 'clockhash':self.clockhash2} ]
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data['immutableobjects'], [])
        historyedges = response.data['history']
        self.assertEqual(len(historyedges), 3)
        self.assertEqual({e[3] for e in historyedges},
                         {self.test2._clockhash, self.clockhash3,
                          self.test3._clockhash})
