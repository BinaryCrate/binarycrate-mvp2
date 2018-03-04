# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from rest_framework.test import APITestCase
from accounts.factories import UserFactory
from historygraphbackend.models import HistoryEdge
import uuid
from django.urls import reverse
from historygraphbackend.models import HistoryEdge
from rest_framework import status


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

        url = reverse('api:historygraph-list', kwargs={'documentcollectionid': str(self.dcid1)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['documentcollectionid'], str(self.dcid1))
        self.assertEqual(response.data[0]['documentid'], 'A')
        self.assertEqual(response.data[0]['documentclassname'], 'B')
        self.assertEqual(response.data[0]['classname'], 'C')
        self.assertEqual(response.data[0]['startnode1id'], 'D')
        self.assertEqual(response.data[0]['startnode2id'], 'E')
        self.assertEqual(response.data[0]['propertyownerid'], 'F')
        self.assertEqual(response.data[0]['propertyname'], 'G')
        self.assertEqual(response.data[0]['propertyvalue'], 'H')
        self.assertEqual(response.data[0]['propertytype'], 'I')

        def get_response_data_set(response_data, k):
            return {d[k] for d in response.data}

        url = reverse('api:historygraph-list', kwargs={'documentcollectionid': str(self.dcid2)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(get_response_data_set(response.data, 'documentcollectionid'), {str(self.dcid2)})
        self.assertEqual(get_response_data_set(response.data, 'documentid'), {'A1', 'A2'})
        self.assertEqual(get_response_data_set(response.data, 'documentclassname'), {'B1', 'B2'})
        self.assertEqual(get_response_data_set(response.data, 'classname'), {'C1', 'C2' })
        self.assertEqual(get_response_data_set(response.data, 'startnode1id'), {'D1', 'D2' })
        self.assertEqual(get_response_data_set(response.data, 'startnode2id'), {'E1', 'E2' })
        self.assertEqual(get_response_data_set(response.data, 'propertyownerid'), {'F1', 'F2' })
        self.assertEqual(get_response_data_set(response.data, 'propertyname'), {'G1', 'G2'})
        self.assertEqual(get_response_data_set(response.data, 'propertyvalue'), {'H1', 'H2'})
        self.assertEqual(get_response_data_set(response.data, 'propertytype'), {'I1', 'I2'})

    def test_login_is_required(self):
        url = reverse('api:historygraph-list', kwargs={'documentcollectionid': str(self.dcid1)})
        data = { }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(str(self.dcid1) in response.content)

