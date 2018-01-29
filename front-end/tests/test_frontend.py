# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from binarycrate import dashboard
import cavorite_tests.fakejs as js
from cavorite import callbacks
from collections import defaultdict
import uuid


class TestDashboard(object):
    def test_shows_projects_from_service(self, monkeypatch):
        monkeypatch.setattr(dashboard.cavorite, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        callbacks.initialise_global_callbacks()

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

        dashboard.projects_api_result_fn([{'id': uuid.uuid4(), 'name': 'Mark\'s Project', 'type': 0, 'public': True}])

        rendered_node = node._render(None)
        js.IterateElements(rendered_node, mock_element_iterator_callback)

        assert result['marks_project'] == 1

