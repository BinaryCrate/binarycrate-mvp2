# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import cavorite
import cavorite.bootstrap.modals
from binarycrate import anonymous
from cavorite import callbacks, ajaxget, timeouts, Router
import cavorite_tests.fakejs as js
from mock import Mock
from utils import IterateVirtualDOM
import uuid
import json


class TestAnonymousProject(object):
    def test_pops_up_new_project_dialog(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('820885b9-f53b-4ea0-8240-af4ec7fca032')

        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(anonymous.cavorite, 'js', js)
        monkeypatch.setattr(anonymous.modals, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(Router, 'router', Mock())

        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        view = anonymous.anonymous_project_view()

        result = dict()

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'createNew':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['createNew_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtProjectName":
                            vnode.value = 'Porject2'
                        if vnode.get_tag_name() == 'select' and vnode.get_attribs().get('id') == "selectProjectType":
                            vnode.value = 'Porject2'
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        view.mount_redraw = Mock()

        virtual_node = view._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        assert 'createNew_OK_handler' in result

        # Call the modal handler
        rendered_modal = view._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'createNew': rendered_modal}

        def setup_mock_modal_callback(node):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtProjectName':
                node.value = 'Test 2'
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'selectProjectType':
                node.value = 0

        js.IterateElements(rendered_modal, setup_mock_modal_callback)

        result['createNew_OK_handler'](Mock())

        js.globals.cavorite_ajaxPost.assert_called_with('/api/projects/', str(dummy_uuid()), {'name':'Test 2', 'type':0, 'public':True })

        js.globals.cavorite_ajaxGet = Mock()
        view.projects_api_ajax_post_result_handler(Mock(status=200, responseText=json.dumps('OK')), 'OK')

        js.globals.cavorite_ajaxGet.assert_called_with('/api/projects/', str(dummy_uuid()))

        response = [{'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                            'name': 'Mark\'s Project',
                            'type': 0,
                            'public': True,
                    }]

        js.globals.cavorite_ajaxGet = Mock()
        view.mount_redraw = Mock()
        view.projects_result_handler(Mock(status=200,responseText=json.dumps(response)), response)
        view.mount_redraw.assert_called()
        view.project_view.query_project()

        assert len(view.get_children()) == 1
        assert view.get_children()[0] == view.project_view

        js.globals.cavorite_ajaxGet.assert_called_with('/api/projects/image-list/4b352f3a-752f-4769-8537-880be4e99ce0/', str(dummy_uuid()))
