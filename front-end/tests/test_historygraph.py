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
from binarycrate import historygraphfrontend
import uuid
from historygraph import DocumentCollection, Document
from historygraph import fields
import cavorite_tests.fakejs as js
from cavorite import ajaxget
from mock import Mock
import json


class Score(Document):
    current_count = fields.IntCounter()


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
        mock_download_commplete_callback = Mock()

        historygraphfrontend.initialise_document_collection(project_id, mock_download_commplete_callback)
        assert isinstance(historygraphfrontend.documentcollection, DocumentCollection)
        assert historygraphfrontend.documentcollection.id == project_id
        historygraphfrontend.documentcollection.register(Score)

        js.globals.cavorite_ajaxPost = Mock()
        historygraphfrontend.download_document_collection()
        js.globals.cavorite_ajaxPost.assert_called_with(
            '/api/historygraph/' + str(project_id) + '/list/',
            str(dummy_uuid()), {u'hashes': '[]'})
        assert historygraphfrontend.documentcollection_download_ready == False

        response = {'history': [], 'immutableobjects': []}
        mock_download_commplete_callback.assert_not_called()
        historygraphfrontend.historygraph_ajaxget_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)
        mock_download_commplete_callback.assert_called_once()
        mock_download_commplete_callback = None
        assert historygraphfrontend.documentcollection_download_ready == True

        score = Score(None)
        historygraphfrontend.documentcollection.add_document_object(score)
        assert score.current_count.get() == 0
        score.current_count.add(1)
        assert score.current_count.get() == 1

        js.globals.cavorite_ajaxPost = Mock()
        historygraphfrontend.post_document_collection()
        #js.globals.cavorite_ajaxPost.assert_called_with('/api/historygraph/' + str(project_id) + '/', str(dummy_uuid()))
        #js.globals.cavorite_ajaxPost.assert_called()
        assert js.globals.cavorite_ajaxPost.call_count == 1
        assert js.globals.cavorite_ajaxPost.call_args[0][0] == '/api/historygraph/' + str(project_id) + '/write/'
        dc_edges = js.globals.cavorite_ajaxPost.call_args[0][2]
        assert len(dc_edges) == 2
        assert len(json.loads(dc_edges['immutableobjects'])) == 0
        assert len(json.loads(dc_edges['history'])) == 1

        historygraphfrontend.initialise_document_collection(project_id, None)
        historygraphfrontend.documentcollection.register(Score)
        js.globals.cavorite_ajaxPost = Mock()
        historygraphfrontend.download_document_collection()
        js.globals.cavorite_ajaxPost.assert_called_with(
            '/api/historygraph/' + str(project_id) + '/list/',
            str(dummy_uuid()), {u'hashes': '[]'})
        dc_edges2 = {'history': json.loads(dc_edges['history']), 'immutableobjects': json.loads(dc_edges['immutableobjects'])}
        historygraphfrontend.historygraph_ajaxget_handler(Mock(status=200, responseText=json.dumps(dc_edges2)),
                                              dc_edges2)

        scores = historygraphfrontend.documentcollection.get_by_class(Score)

        assert len(scores) == 1
        assert scores[0].id == score.id
        assert scores[0].current_count.get() == 1

        # Test that reloading when we already have edges just works
        js.globals.cavorite_ajaxPost = Mock()
        historygraphfrontend.download_document_collection()
        js.globals.cavorite_ajaxPost.assert_called_once()
        assert js.globals.cavorite_ajaxPost.call_args[0][0] == \
            '/api/historygraph/' + str(project_id) + '/list/'
        assert js.globals.cavorite_ajaxPost.call_args[0][1] == str(dummy_uuid())
        payload = js.globals.cavorite_ajaxPost.call_args[0][2]
        assert len(payload) == 1
        hashes = json.loads(payload['hashes'])
        assert len(hashes) == 1
        assert hashes == [{'documentid':scores[0].id,
                             'clockhash': scores[0]._clockhash}]

        historygraphfrontend.historygraph_ajaxget_handler(Mock(status=200, responseText=json.dumps(dc_edges2)),
                                              dc_edges2)

        scores = historygraphfrontend.documentcollection.get_by_class(Score)

        assert len(scores) == 1
        assert scores[0].id == score.id
        assert scores[0].current_count.get() == 1
