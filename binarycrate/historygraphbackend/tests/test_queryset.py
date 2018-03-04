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

