# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from binarycrate import dashboard
import cavorite_tests.fakejs as js
from cavorite import callbacks, ajaxget, timeouts
from collections import defaultdict
import uuid
from mock import Mock
import json


class TestDashboard(object):
    def test_shows_projects_from_service(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('531cb169-91f4-4102-9a0a-2cd5e9659071')

        monkeypatch.setattr(dashboard.cavorite, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.globals.cavorite_ajaxGet = Mock()

        result = defaultdict(int)

        def mock_element_iterator_callback(node):
            if isinstance(node, js.MockElement)  and node.tagName == 'div' and node.getAttribute('class') == 'wrimagecard-topimage_title':
                p_children = [c for c in node.children if c.tagName == 'p']
                assert len(p_children) == 1
                p = p_children[0]
                assert len(p.children) == 1
                text_node = p.children[0]
                assert isinstance(text_node, js.MockTextNode)
                if str(text_node) == 'Mark\'s Project':
                    result['marks_project'] += 1
                

        node = dashboard.dashboard_view()
        # Simulate the query which is sent after the screen is drawn
        node.query_projects()

        js.globals.cavorite_ajaxGet.assert_called_with('/api/projects/', str(dummy_uuid()))

        monkeypatch.setattr(node, 'mount_redraw', Mock())

        response = [{'id': str(uuid.uuid4()), 'name': 'Mark\'s Project', 'type': 0, 'public': True}]
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)), response)

        rendered_node = node._render(None)
        js.IterateElements(rendered_node, mock_element_iterator_callback)

        assert result['marks_project'] == 1

