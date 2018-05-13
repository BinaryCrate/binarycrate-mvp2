# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from binarycrate import dashboard
import cavorite_tests.fakejs as js
from cavorite import callbacks, ajaxget, timeouts, Router
from collections import defaultdict
import uuid
from mock import Mock
import json
import cavorite.bootstrap.modals
from utils import IterateVirtualDOM


class TestDashboard(object):
    def test_shows_projects_from_service(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('531cb169-91f4-4102-9a0a-2cd5e9659071')

        monkeypatch.setattr(dashboard.cavorite, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(Router, 'router', Mock())
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.globals.cavorite_ajaxGet = Mock()

        result = defaultdict(int)

        def mock_element_iterator_callback(node):
            if isinstance(node, js.MockElement)  and node.tagName == 'div' and node.getAttribute('class') == 'wrimagecard-topimage_title':
                p_children = [c for c in node.children.l if c.tagName == 'p']
                assert len(p_children) == 1
                p = p_children[0]
                assert len(p.children.l) == 1
                text_node = p.children.item(0)
                assert isinstance(text_node, js.MockTextNode)
                if str(text_node) == 'Mark\'s Project':
                    result['marks_project'] += 1
                

        node = dashboard.dashboard_view()
        node.mount_redraw = Mock()
        # Simulate the query which is sent after the screen is drawn
        node.query_projects()

        js.globals.cavorite_ajaxGet.assert_called_with('/api/projects/', str(dummy_uuid()))

        monkeypatch.setattr(node, 'mount_redraw', Mock())

        response = [{'id': str(uuid.uuid4()), 'name': 'Mark\'s Project', 'type': 0, 'public': True}]
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)), response)

        rendered_node = node._render(None)
        js.IterateElements(rendered_node, mock_element_iterator_callback)

        assert result['marks_project'] == 1

    def test_calls_ajax_post_correctly(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('531cb169-91f4-4102-9a0a-2cd5e9659071')

        monkeypatch.setattr(dashboard.cavorite, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(dashboard, 'js', js)
        monkeypatch.setattr(dashboard.modals, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.globals.cavorite_ajaxGet = Mock()
        js.globals.cavorite_ajaxPost = Mock()
        Router.router = Mock()

        result = dict()

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'createNew':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['createNew_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtProjectName":
                            node.value = 'Porject2'
                        if vnode.get_tag_name() == 'select' and vnode.get_attribs().get('id') == "selectProjectType":
                            node.value = 'Porject2'
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        node = dashboard.dashboard_view()
        node.mount_redraw = Mock()

        virtual_node = node._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        # Call the modal handler
        rendered_modal = node._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'createNew': rendered_modal}

        def setup_mock_modal_callback(node):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtProjectName':
                node.value = 'Test 2'
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'selectProjectType':
                node.value = 0

        js.IterateElements(rendered_modal, setup_mock_modal_callback)

        result['createNew_OK_handler'](Mock())

        js.globals.cavorite_ajaxPost.assert_called_with('/api/projects/', str(dummy_uuid()), {'name':'Test 2', 'type':0, 'public':True })

        node.projects_api_ajax_post_result_handler(Mock(status=200, responseText=json.dumps('OK')), 'OK')

        js.globals.cavorite_ajaxGet.assert_called_with('/api/projects/', str(dummy_uuid()))

    def test_calls_ajax_put_rename_correctly(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('531cb169-91f4-4102-9a0a-2cd5e9659071')

        monkeypatch.setattr(dashboard.cavorite, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(dashboard, 'js', js)
        monkeypatch.setattr(dashboard.modals, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.globals.cavorite_ajaxGet = Mock()
        js.globals.cavorite_ajaxPut = Mock()

        Router.router = Mock()

        result = dict()

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('data-target') == '#renameProj':
                result['renameProj_popupmenu_handler'] = vnode.get_attribs().get('onclick')

            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'renameProj':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['renameProj_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtProjectName":
                            node.value = 'Porject2'
                        if vnode.get_tag_name() == 'select' and vnode.get_attribs().get('id') == "selectProjectType":
                            node.value = 0
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        project_id = str(uuid.uuid4())
        dashboard.projects = [{'id': project_id, 'name': 'Mark\'s Project', 'type': 0, 'public': True}]

        node = dashboard.dashboard_view()
        node.mount_redraw = Mock()

        virtual_node = node._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        # Call the modal handler
        rendered_modal = node._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'renameProj': rendered_modal}

        def setup_mock_modal_callback(node):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtProjectName':
                node.value = 'Test 2'
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'selectProjectType':
                node.value = 0

        js.IterateElements(rendered_modal, setup_mock_modal_callback)

        result['renameProj_popupmenu_handler'](Mock())
        result['renameProj_OK_handler'](Mock())

        js.globals.cavorite_ajaxPut.assert_called_with('/api/projects/' + project_id + '/', str(dummy_uuid()), {'id': project_id, 'name':'Test 2', 'type': 0, 'public':True })

        node.projects_api_ajax_put_result_handler(Mock(status=200, responseText=json.dumps('OK')), 'OK')

        js.globals.cavorite_ajaxGet.assert_called_with('/api/projects/', str(dummy_uuid()))

