# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from binarycrate import historygraphfrontend
import uuid
from historygraph import DocumentCollection, Document, FieldIntCounter
import cavorite_tests.fakejs as js
from cavorite import ajaxget
from mock import Mock
import json


class Score(Document):
    current_count = FieldIntCounter()


class TestHistoryGraph(object):
    # This class tests the history graph frontend functionality
    def test_history_graph(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        ajaxget.initialise_ajaxget_callbacks()

        historygraphfrontend.documentcollection = None
        project_id = uuid.uuid4()
        historygraphfrontend.initialise_document_collection(project_id)
        assert isinstance(historygraphfrontend.documentcollection, DocumentCollection)
        assert historygraphfrontend.documentcollection.id == project_id
        historygraphfrontend.documentcollection.Register(Score)

        js.globals.cavorite_ajaxGet = Mock()
        historygraphfrontend.download_document_collection()
        js.globals.cavorite_ajaxGet.assert_called_with('/api/historygraph/' + str(project_id) + '/', str(dummy_uuid()))
        assert historygraphfrontend.documentcollection_download_ready == False

        response = {'history': [], 'immutableobjects': []}
        historygraphfrontend.historygraph_ajaxget_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)
        assert historygraphfrontend.documentcollection_download_ready == True

        score = Score(None)
        historygraphfrontend.documentcollection.AddDocumentObject(score)
        assert score.current_count.get() == 0
        score.current_count.add(1)
        assert score.current_count.get() == 1

        js.globals.cavorite_ajaxPost = Mock()
        historygraphfrontend.post_document_collection()
        #js.globals.cavorite_ajaxPost.assert_called_with('/api/historygraph/' + str(project_id) + '/', str(dummy_uuid()))
        #js.globals.cavorite_ajaxPost.assert_called()
        assert js.globals.cavorite_ajaxPost.call_count == 1
        dc_edges = js.globals.cavorite_ajaxPost.call_args[0][2]
        assert len(dc_edges) == 2
        assert len(json.loads(dc_edges['immutableobjects'])) == 0
        assert len(json.loads(dc_edges['history'])) == 1

        historygraphfrontend.initialise_document_collection(project_id)
        historygraphfrontend.documentcollection.Register(Score)
        js.globals.cavorite_ajaxGet = Mock()
        historygraphfrontend.download_document_collection()
        js.globals.cavorite_ajaxGet.assert_called_with('/api/historygraph/' + str(project_id) + '/', str(dummy_uuid()))
        dc_edges2 = {'history': json.loads(dc_edges['history']), 'immutableobjects': json.loads(dc_edges['immutableobjects'])}
        historygraphfrontend.historygraph_ajaxget_handler(Mock(status=200, responseText=json.dumps(dc_edges2)),
                                              dc_edges2)

        scores = historygraphfrontend.documentcollection.GetByClass(Score)

        assert len(scores) == 1
        assert scores[0].id == score.id
        assert scores[0].current_count.get() == 1

        # Test that reloading when we already have edges just works
        js.globals.cavorite_ajaxGet = Mock()
        historygraphfrontend.download_document_collection()
        js.globals.cavorite_ajaxGet.assert_called_with('/api/historygraph/' + str(project_id) + '/', str(dummy_uuid()))
        historygraphfrontend.historygraph_ajaxget_handler(Mock(status=200, responseText=json.dumps(dc_edges2)),
                                              dc_edges2)

        scores = historygraphfrontend.documentcollection.GetByClass(Score)

        assert len(scores) == 1
        assert scores[0].id == score.id
        assert scores[0].current_count.get() == 1



