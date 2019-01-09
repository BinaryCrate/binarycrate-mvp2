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
from binarycrate import editor
import cavorite_tests.fakejs as js
from cavorite import callbacks, ajaxget, timeouts, Router, t, c
from collections import defaultdict
import uuid
from mock import Mock, MagicMock
import json
from binarycrate.editor import BCProjectTree, BCPFolder, BCPFile, ContextMenuFormItems
from binarycrate.controls import codemirror, Form
from utils import IterateVirtualDOM, AnyVirtualDOM, get_matching_vnode, style_to_dict, get_vnode_by_id, get_vnode_by_css_class, get_matching_vnodes
import cavorite.bootstrap.modals
from binarycrate.editor import HANDLE_NONE, HANDLE_TOPLEFT, HANDLE_TOPRIGHT, HANDLE_BOTTOMLEFT, HANDLE_BOTTOMRIGHT
from binarycrate.controls.bcform import get_form_item_property, FormItemPropType
from binarycrate.controls import bcform
import tempfile
from backports.tempfile import TemporaryDirectory
import os
from cavorite.HTML import *
from binarycrate import historygraphfrontend
import sys
import pytest
import binarycrate.frontend_utils


class TestEditor(object):
    def get_BCPFile_title(self, node):
        assert type(node) == BCPFile
        assert len(node.get_children()) == 1
        first_child = node.get_children()[0]
        assert first_child.get_tag_name().lower() == 'a'
        assert len(first_child.get_children()) == 1
        text_node = first_child.get_children()[0]
        assert type(text_node) == t
        return text_node.text

    def get_tree_important_nodes(self, tree):
        # This function exists because we want to get the versions of nodes after a mount_redraw
        #root_folder = tree.get_children()[0]
        #folder = root_folder.get_children()[0]
        #return root_folder, root_folder.get_children()[1], folder, folder.get_children()[2].get_children()[0]
        root_folder = tree.get_children()[0]
        hello_world = root_folder.folder_children[1]
        folder = root_folder.folder_children[0]
        hello_folder = folder.folder_children[0]
        return root_folder, hello_world, folder, hello_folder

    def test_editor_displays_folder_structure(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        def dummy_uuid_editor():
            return uuid.UUID('236a5a73-0ffd-4329-95c0-9deaa95830f4')
        project_id = 'e1e37287-9127-46cb-bddb-4a1a825a5d8e'

        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(editor.modals, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(Router, 'router', Mock())
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(editor, 'get_uuid', dummy_uuid_editor)

        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.globals.cavorite_ajaxGet = Mock()

        result = defaultdict(int)

        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }
        # SImulate the first screen draw before there is anything loaded

        tree = node.get_project_tree()

        assert type(tree) == BCProjectTree
        root_folder = tree.get_children()
        assert len(root_folder) == 0

        # Simulate the query which is sent after the screen is drawn
        node.query_project()

        js.globals.cavorite_ajaxGet.assert_called_with('/api/projects/image-list/' + project_id + '/', str(dummy_uuid()))


        monkeypatch.setattr(node, 'mount_redraw', Mock())

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '', # Test when we get a completely empty result may be necessary for some transitional things
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30}]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': True,
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

        # Test that the text in form_items is translated in Python dicts
        for de in editor.project['directory_entry']:
            if de['id'] != '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a':
                assert de['form_items'] == []
            else:
                assert de['form_items'] == [{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": True}]

        tree = node.get_project_tree()

        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)

        assert type(tree) == BCProjectTree
        #root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 2
        assert type(root_folder.folder_children[0]) == BCPFolder
        assert root_folder.folder_children[0].de['name'] == 'folder'
        #hello_world = root_folder.folder_children[1]
        assert type(hello_world) == BCPFile
        assert self.get_BCPFile_title(hello_world) == 'hello_world.py'
        #folder = root_folder.folder_children[0]
        #hello_folder = folder.folder_children[0]
        assert type(hello_folder) == BCPFile
        assert self.get_BCPFile_title(hello_folder) == '* hello_folder.py'

        assert root_folder.get_display_title() == '/'
        assert folder.get_display_title() == 'folder'

        # Test no content set
        assert len(node.code_mirror.get_children()) == 1
        assert type(node.code_mirror.get_children()[0]) == t
        assert node.code_mirror.get_children()[0].text() == ''

        node.code_mirror.editor = Mock(setValue=Mock())
        hello_world.on_click(None)
        #node.code_mirror.editor.setValue.assert_called_with(hello_world_content)

        # Test content set from clicked file
        assert len(node.code_mirror.get_children()) == 1
        assert type(node.code_mirror.get_children()[0]) == t
        assert node.code_mirror.get_children()[0].text() == hello_world_content

        # Click folder should blank the text
        node.code_mirror.editor = Mock(setValue=Mock())
        folder.on_click(None)
        assert node.code_mirror.editor.setValue.call_count == 0
        assert len(node.code_mirror.get_children()) == 1
        assert type(node.code_mirror.get_children()[0]) == t
        assert node.code_mirror.get_children()[0].text() == ''
        folder.on_click(None)

        node.code_mirror.editor = Mock(setValue=Mock())
        hello_folder.on_click(None)
        #node.code_mirror.editor.setValue.assert_called_with(hello_folder_content)

        assert len(node.code_mirror.get_children()) == 1
        assert type(node.code_mirror.get_children()[0]) == t
        assert node.code_mirror.get_children()[0].text() == hello_folder_content

        hello_world.on_click(None)
        # Click on hello_world and check that the UI updates correctly
        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        assert node.selected_de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'
        assert node.selected_file_de == node.selected_de
        assert 'file-active' in hello_world.get_attribs().get('class', '')
        a_hello_world = hello_world.get_children()[0]
        assert a_hello_world.get_tag_name() == 'a'
        assert 'file-active' in a_hello_world.get_attribs().get('class', '')
        label_folder = folder.get_children()[0]
        assert label_folder.get_tag_name() == 'label'
        assert 'file-active' not in label_folder.get_attribs().get('class', '')
        checkbox_folder = folder.get_children()[1]
        assert checkbox_folder.get_tag_name() == 'input'
        assert 'checked' not in checkbox_folder.get_attribs()

        folder.on_click(None)
        # Click on folder and check that the UI updates correctly
        tree = node.get_project_tree()
        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        assert node.selected_de['id'] == 'c1a4bc81-1ade-4c55-b457-81e59b785b01'
        assert node.selected_file_de == None
        assert 'file-active' not in hello_world.get_attribs().get('class', '')
        a_hello_world = hello_world.get_children()[0]
        assert a_hello_world.get_tag_name() == 'a'
        assert 'file-active' not in a_hello_world.get_attribs().get('class', '')
        label_folder = folder.get_children()[0]
        assert label_folder.get_tag_name() == 'label'
        assert 'file-active' in label_folder.get_attribs().get('class', '')
        checkbox_folder = folder.get_children()[1]
        assert checkbox_folder.get_tag_name() == 'input'
        assert 'checked' in checkbox_folder.get_attribs()

        hello_world.on_click(None)
        # Click on hello_world and check that the UI updates correctly That is the selected changes but not the fact that folder is checked (ie folded out)
        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        assert node.selected_de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'
        assert 'file-active' in hello_world.get_attribs().get('class', '')
        a_hello_world = hello_world.get_children()[0]
        assert a_hello_world.get_tag_name() == 'a'
        assert 'file-active' in a_hello_world.get_attribs().get('class', '')
        label_folder = folder.get_children()[0]
        assert label_folder.get_tag_name() == 'label'
        assert 'file-active' not in label_folder.get_attribs().get('class', '')
        checkbox_folder = folder.get_children()[1]
        assert checkbox_folder.get_tag_name() == 'input'
        assert 'checked' in checkbox_folder.get_attribs()

        js.return_get_element_by_id = {'preview': Mock(getBoundingClientRect=Mock(return_value=Mock(left=0, top=0)))}

        hello_world2_content = "print('Hello world2')"
        mock_code_mirrow_get_value = Mock(side_effect=lambda: hello_world2_content)
        node.code_mirror.editor = Mock(getValue=mock_code_mirrow_get_value)

        #editor.code_mirror_changed = Mock()

        node.code_mirror.onchange_codemirror(None)
        #editor.code_mirror_changed.assert_called_with(hello_world2_content)
        assert node.selected_file_de['content'] == hello_world2_content

        # Test we send the correct thing when we change the default file
        #editor.selected_de = [de for de in editor.project['directory_entry'] if de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'][0]
        node.set_current_file_as_default(Mock())

        # Test we send the correct stuff when we add a new button
        node.contextmenu_x = 100
        node.contextmenu_y = 100
        node.new_button(Mock(clientX=100, clientY=100))

        js.globals.cavorite_ajaxPut.reset_mock()

        node.save_project(None)
        calls = [(a[0][0], a[0][2]) for a in js.globals.cavorite_ajaxPut.call_args_list]

        assert len(calls) == len(editor.project['directory_entry']) - 1 # We don't send the root folder
        was_found = False
        was_found2 = False
        for url, data in calls:
            if url == '/api/projects/directoryentry/ae935c72-cf56-48ed-ab35-575cb9a983ea/':
                assert len(data) == 7
                assert data['id'] == node.selected_de['id']
                assert data['name'] == node.selected_de['name']
                assert data['is_file'] == node.selected_de['is_file']
                assert data['content'] == hello_world2_content
                assert data['parent_id'] == node.selected_de['parent_id']
                assert data['is_default'] == True
                assert json.loads(data['form_items']) == json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": true}]')
                was_found = True
            if url == '/api/projects/directoryentry/6a05e63e-6db4-4898-a3eb-2aad50dd5f9a/':
                assert len(data) == 7
                assert data['name'] == 'hello_folder.py'
                assert data['is_default'] == False
                was_found2 = True

        assert was_found
        assert was_found2


    def test_editor_new_line(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        def dummy_uuid_editor():
            return uuid.UUID('236a5a73-0ffd-4329-95c0-9deaa95830f4')
        project_id = 'e1e37287-9127-46cb-bddb-4a1a825a5d8e'

        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(editor.modals, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(Router, 'router', Mock())
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(editor, 'get_uuid', dummy_uuid_editor)

        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.globals.cavorite_ajaxGet = Mock()

        result = defaultdict(int)

        editor.project.clear()

        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }
        # SImulate the first screen draw before there is anything loaded

        tree = node.get_project_tree()

        assert type(tree) == BCProjectTree
        root_folder = tree.get_children()
        print('root_folde=',root_folder)
        assert len(root_folder) == 0

        # Simulate the query which is sent after the screen is drawn
        node.query_project()

        js.globals.cavorite_ajaxGet.assert_called_with('/api/projects/image-list/' + project_id + '/', str(dummy_uuid()))


        monkeypatch.setattr(node, 'mount_redraw', Mock())

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '', # Test when we get a completely empty result may be necessary for some transitional things
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30}]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': True,
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

        # Test that the text in form_items is translated in Python dicts
        for de in editor.project['directory_entry']:
            if de['id'] != '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a':
                assert de['form_items'] == []
            else:
                assert de['form_items'] == [{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": True}]

        tree = node.get_project_tree()

        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)

        assert type(tree) == BCProjectTree
        #root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 2
        assert type(root_folder.folder_children[0]) == BCPFolder
        assert root_folder.folder_children[0].de['name'] == 'folder'
        #hello_world = root_folder.folder_children[1]
        assert type(hello_world) == BCPFile
        assert self.get_BCPFile_title(hello_world) == 'hello_world.py'
        #folder = root_folder.folder_children[0]
        #hello_folder = folder.folder_children[0]
        assert type(hello_folder) == BCPFile
        assert self.get_BCPFile_title(hello_folder) == '* hello_folder.py'

        assert root_folder.get_display_title() == '/'
        assert folder.get_display_title() == 'folder'

        # Test no content set
        assert len(node.code_mirror.get_children()) == 1
        assert type(node.code_mirror.get_children()[0]) == t
        assert node.code_mirror.get_children()[0].text() == ''

        node.code_mirror.editor = Mock(setValue=Mock())
        hello_world.on_click(None)
        #node.code_mirror.editor.setValue.assert_called_with(hello_world_content)

        # Test content set from clicked file
        assert len(node.code_mirror.get_children()) == 1
        assert type(node.code_mirror.get_children()[0]) == t
        assert node.code_mirror.get_children()[0].text() == hello_world_content

        # Click folder should blank the text
        node.code_mirror.editor = Mock(setValue=Mock())
        folder.on_click(None)
        assert node.code_mirror.editor.setValue.call_count == 0
        assert len(node.code_mirror.get_children()) == 1
        assert type(node.code_mirror.get_children()[0]) == t
        assert node.code_mirror.get_children()[0].text() == ''
        folder.on_click(None)

        node.code_mirror.editor = Mock(setValue=Mock())
        hello_folder.on_click(None)
        #node.code_mirror.editor.setValue.assert_called_with(hello_folder_content)

        assert len(node.code_mirror.get_children()) == 1
        assert type(node.code_mirror.get_children()[0]) == t
        assert node.code_mirror.get_children()[0].text() == hello_folder_content

        hello_world.on_click(None)
        # Click on hello_world and check that the UI updates correctly
        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        assert node.selected_de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'
        assert node.selected_file_de == node.selected_de
        assert 'file-active' in hello_world.get_attribs().get('class', '')
        a_hello_world = hello_world.get_children()[0]
        assert a_hello_world.get_tag_name() == 'a'
        assert 'file-active' in a_hello_world.get_attribs().get('class', '')
        label_folder = folder.get_children()[0]
        assert label_folder.get_tag_name() == 'label'
        assert 'file-active' not in label_folder.get_attribs().get('class', '')
        checkbox_folder = folder.get_children()[1]
        assert checkbox_folder.get_tag_name() == 'input'
        assert 'checked' not in checkbox_folder.get_attribs()

        folder.on_click(None)
        # Click on folder and check that the UI updates correctly
        tree = node.get_project_tree()
        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        assert node.selected_de['id'] == 'c1a4bc81-1ade-4c55-b457-81e59b785b01'
        assert node.selected_file_de == None
        assert 'file-active' not in hello_world.get_attribs().get('class', '')
        a_hello_world = hello_world.get_children()[0]
        assert a_hello_world.get_tag_name() == 'a'
        assert 'file-active' not in a_hello_world.get_attribs().get('class', '')
        label_folder = folder.get_children()[0]
        assert label_folder.get_tag_name() == 'label'
        assert 'file-active' in label_folder.get_attribs().get('class', '')
        checkbox_folder = folder.get_children()[1]
        assert checkbox_folder.get_tag_name() == 'input'
        assert 'checked' in checkbox_folder.get_attribs()

        hello_world.on_click(None)
        # Click on hello_world and check that the UI updates correctly That is the selected changes but not the fact that folder is checked (ie folded out)
        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        assert node.selected_de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'
        assert 'file-active' in hello_world.get_attribs().get('class', '')
        a_hello_world = hello_world.get_children()[0]
        assert a_hello_world.get_tag_name() == 'a'
        assert 'file-active' in a_hello_world.get_attribs().get('class', '')
        label_folder = folder.get_children()[0]
        assert label_folder.get_tag_name() == 'label'
        assert 'file-active' not in label_folder.get_attribs().get('class', '')
        checkbox_folder = folder.get_children()[1]
        assert checkbox_folder.get_tag_name() == 'input'
        assert 'checked' in checkbox_folder.get_attribs()

        js.return_get_element_by_id = {'preview': Mock(getBoundingClientRect=Mock(return_value=Mock(left=0, top=0)))}

        hello_world2_content = "print('Hello world2')"
        mock_code_mirrow_get_value = Mock(side_effect=lambda: hello_world2_content)
        node.code_mirror.editor = Mock(getValue=mock_code_mirrow_get_value)

        #editor.code_mirror_changed = Mock()

        node.code_mirror.onchange_codemirror(None)
        #editor.code_mirror_changed.assert_called_with(hello_world2_content)
        assert node.selected_file_de['content'] == hello_world2_content

        # Test we send the correct thing when we change the default file
        #editor.selected_de = [de for de in editor.project['directory_entry'] if de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'][0]
        node.set_current_file_as_default(Mock())

        # Test we send the correct stuff when we add a new button
        node.new_line(Mock(clientX=100, clientY=100))

        js.globals.cavorite_ajaxPut.reset_mock()

        node.save_project(None)
        calls = [(a[0][0], a[0][2]) for a in js.globals.cavorite_ajaxPut.call_args_list]

        assert len(calls) == len(editor.project['directory_entry']) - 1 # We don't send the root folder
        was_found = False
        was_found2 = False
        for url, data in calls:
            if url == '/api/projects/directoryentry/ae935c72-cf56-48ed-ab35-575cb9a983ea/':
                assert len(data) == 7
                assert data['id'] == node.selected_de['id']
                assert data['name'] == node.selected_de['name']
                assert data['is_file'] == node.selected_de['is_file']
                assert data['content'] == hello_world2_content
                assert data['parent_id'] == node.selected_de['parent_id']
                assert data['is_default'] == True
                assert json.loads(data['form_items']) == json.loads('[{"x2": 150, "name": "line1", "y1": 100, "x1": 100, "type": "line", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "y2": 150, "visible": true, "stroke": "rgb(0,0,0)", "stroke_width": 5}]')
                was_found = True
            if url == '/api/projects/directoryentry/6a05e63e-6db4-4898-a3eb-2aad50dd5f9a/':
                assert len(data) == 7
                assert data['name'] == 'hello_folder.py'
                assert data['is_default'] == False
                was_found2 = True

        assert was_found
        assert was_found2


    def test_editor_can_add_new_files(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        project_id = 'e1e37287-9127-46cb-bddb-4a1a825a5d8e'

        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(Router, 'router', Mock())
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        result = defaultdict(int)

        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }

        tree = node.get_project_tree()

        monkeypatch.setattr(node, 'mount_redraw', Mock())

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

        tree = node.get_project_tree()

        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        #root_folder = tree.get_children()[0]
        #folder = root_folder.get_children()[0]
        #return root_folder, root_folder.get_children()[1], folder, folder.get_children()[2].get_children()[0]

        assert type(tree) == BCProjectTree
        #root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 2
        assert type(root_folder.folder_children[0]) == BCPFolder
        assert root_folder.folder_children[0].de['name'] == 'folder'
        #hello_world = root_folder.folder_children[1]
        assert type(hello_world) == BCPFile
        assert self.get_BCPFile_title(hello_world) == 'hello_world.py'
        #folder = root_folder.folder_children[0]
        #hello_folder = folder.folder_children[0]
        assert type(hello_folder) == BCPFile
        assert self.get_BCPFile_title(hello_folder) == 'hello_folder.py'

        assert root_folder.get_display_title() == '/'
        assert folder.get_display_title() == 'folder'

        virtual_node = node._build_virtual_dom()
        #add_folder_link = get_matching_vnode(virtual_node, lambda vnode: get_vnode_by_css_class(vnode, 'fa fa-1x fa-folder-o'))

        editor.js.globals.window.alert = Mock()
        hello_world.on_click(Mock())
        #add_folder_link.get_attribs()['onclick'](Mock())
        node.display_new_file_modal(Mock())

        editor.js.globals.window.alert.assert_not_called()

        editor.js.globals.window.alert = Mock()
        root_folder.on_click(Mock())
        node.display_new_file_modal(Mock())

        editor.js.globals.window.alert.assert_not_called()

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'newFile':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['newFile_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtFileName":
                            node.value = ''
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        node.mount_redraw = Mock()

        virtual_node = node._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        # Call the modal handler
        rendered_modal = node._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'newFile': rendered_modal}

        def setup_mock_modal_callback(node, file_name):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtFileName':
                node.value = file_name

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'hello_file.py2'))

        editor.js.globals.window.alert = Mock()

        result['newFile_OK_handler'](Mock())

        editor.js.globals.window.alert.assert_called_with('Error: python files must end with .py')

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'hello_file.py'))

        result['newFile_OK_handler'](Mock())

        rendered = node._render(None)

        def setup_mock_modal_callback_was_added(node, file_name):
            if isinstance(node, js.MockElement) and node.tagName == 'a' and node.children.length == 1:
                #print('setup_mock_modal_callback_was_added node=', node)
                child = node.children.item(0)
                if isinstance(child, js.MockTextNode):
                    #print('setup_mock_modal_callback_was_added child=', str(child))
                    if  str(child) == file_name:
                        result['new_file_found'] = True

        js.IterateElements(rendered, lambda node: setup_mock_modal_callback_was_added(node, 'hello_file.py'))

        assert result['new_file_found']

        root_de = [de for de in editor.project['directory_entry'] if de['parent_id'] is None][0]
        new_file = [de for de in editor.project['directory_entry'] if de['name'] == 'hello_file.py'][0]

        assert node.selected_de == new_file
        assert node.selected_file_de == new_file

        folder.on_click(None)

        # Call the modal handler
        rendered_modal = node._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'newFile': rendered_modal}

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'hello_subfile.py'))

        #print('test_editor result[newFile_OK_handler]=', result['newFile_OK_handler'])
        result['newFile_OK_handler'](Mock())

        folder_de = [de for de in editor.project['directory_entry'] if de['name'] == 'folder'][0]
        hello_subfile_de = [de for de in editor.project['directory_entry'] if de['name'] == 'hello_subfile.py'][0]

        rendered = node._render(None)

        result['new_file_found'] = False

        js.IterateElements(rendered, lambda node: setup_mock_modal_callback_was_added(node, 'hello_subfile.py'))

        assert result['new_file_found']

        assert folder_de['id'] == hello_subfile_de['parent_id']

    def test_editor_can_add_new_folders(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        project_id = 'e1e37287-9127-46cb-bddb-4a1a825a5d8e'

        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(Router, 'router', Mock())
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        result = defaultdict(int)

        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }

        tree = node.get_project_tree()

        monkeypatch.setattr(node, 'mount_redraw', Mock())

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

        tree = node.get_project_tree()

        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        #root_folder = tree.get_children()[0]
        #folder = root_folder.get_children()[0]
        #return root_folder, root_folder.get_children()[1], folder, folder.get_children()[2].get_children()[0]

        assert type(tree) == BCProjectTree
        #root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 2
        assert type(root_folder.folder_children[0]) == BCPFolder
        assert root_folder.folder_children[0].de['name'] == 'folder'
        #hello_world = root_folder.folder_children[1]
        assert type(hello_world) == BCPFile
        assert self.get_BCPFile_title(hello_world) == 'hello_world.py'
        #folder = root_folder.folder_children[0]
        #hello_folder = folder.folder_children[0]
        assert type(hello_folder) == BCPFile
        assert self.get_BCPFile_title(hello_folder) == 'hello_folder.py'

        assert root_folder.get_display_title() == '/'
        assert folder.get_display_title() == 'folder'

        virtual_node = node._build_virtual_dom()
        #add_folder_link = get_matching_vnode(virtual_node, lambda vnode: get_vnode_by_css_class(vnode, 'fa fa-1x fa-folder-o'))

        editor.js.globals.window.alert = Mock()
        hello_world.on_click(Mock())
        #add_folder_link.get_attribs()['onclick'](Mock())
        node.display_new_folder_modal(Mock())

        editor.js.globals.window.alert.assert_called_with('Error: You must select a folder to insert this folder in')

        editor.js.globals.window.alert = Mock()
        root_folder.on_click(Mock())
        node.display_new_folder_modal(Mock())

        editor.js.globals.window.alert.assert_not_called()

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'newFolder':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['newFolder_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtFolderName":
                            node.value = ''
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        node.mount_redraw = Mock()

        virtual_node = node._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        # Call the modal handler
        rendered_modal = node._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'newFolder': rendered_modal}

        def setup_mock_modal_callback(node, file_name):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtFolderName':
                print('setup_mock_modal_callback settings node file_name to=', file_name)
                node.value = file_name

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'folder2'))

        #print('test_editor result[newFile_OK_handler]=', result['newFile_OK_handler'])
        result['newFolder_OK_handler'](Mock())

        rendered = node._render(None)

        def setup_mock_modal_callback_was_added(node, folder_name):
            if isinstance(node, js.MockElement) and node.tagName == 'label' and node.children.length == 1:
                #print('setup_mock_modal_callback_was_added node=', node)
                child = node.children.item(0)
                if isinstance(child, js.MockTextNode):
                    print('setup_mock_modal_callback_was_added child=', str(child))
                    if  str(child) == folder_name:
                        result['new_folder_found'] = True

        js.IterateElements(rendered, lambda node: setup_mock_modal_callback_was_added(node, 'folder2'))

        assert result['new_folder_found']

        root_de = [de for de in editor.project['directory_entry'] if de['parent_id'] is None][0]
        folder2_de = [de for de in editor.project['directory_entry'] if de['name'] == 'folder2'][0]

        folder.on_click(None)

        # Call the modal handler
        rendered_modal = node._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'newFolder': rendered_modal}

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'folder3'))

        #print('test_editor result[newFile_OK_handler]=', result['newFile_OK_handler'])
        result['newFolder_OK_handler'](Mock())

        folder3_de = [de for de in editor.project['directory_entry'] if de['name'] == 'folder3'][0]
        #hello_subfile_de = [de for de in editor.project['directory_entry'] if de['name'] == 'hello_subfile.py'][0]

        rendered = node._render(None)

        result['new_folder_found'] = False

        js.IterateElements(rendered, lambda node: setup_mock_modal_callback_was_added(node, 'folder3'))

        assert result['new_folder_found']

        folder_de = [de for de in editor.project['directory_entry'] if de['name'] == 'folder'][0]
        assert folder3_de['parent_id'] == folder_de['id']

    def test_editor_can_delete_files(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        project_id = 'e1e37287-9127-46cb-bddb-4a1a825a5d8e'

        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(Router, 'router', Mock())
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        result = defaultdict(int)

        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }

        tree = node.get_project_tree()

        monkeypatch.setattr(node, 'mount_redraw', Mock())

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

        tree = node.get_project_tree()

        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        #root_folder = tree.get_children()[0]
        #folder = root_folder.get_children()[0]
        #return root_folder, root_folder.get_children()[1], folder, folder.get_children()[2].get_children()[0]

        assert type(tree) == BCProjectTree
        #root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 2
        assert type(root_folder.folder_children[0]) == BCPFolder
        assert root_folder.folder_children[0].de['name'] == 'folder'
        #hello_world = root_folder.folder_children[1]
        assert type(hello_world) == BCPFile
        assert self.get_BCPFile_title(hello_world) == 'hello_world.py'
        #folder = root_folder.folder_children[0]
        #hello_folder = folder.folder_children[0]
        assert type(hello_folder) == BCPFile
        assert self.get_BCPFile_title(hello_folder) == 'hello_folder.py'

        hello_world.on_click(Mock())

        node.delete_selected_de(Mock())

        assert editor.project['deleted_directory_entries'] == ['ae935c72-cf56-48ed-ab35-575cb9a983ea']

        tree = node.get_project_tree()
        assert type(tree) == BCProjectTree
        root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 1
        assert type(root_folder.folder_children[0]) == BCPFolder
        assert root_folder.folder_children[0].de['name'] == 'folder'

    def test_editor_can_delete_folder(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        project_id = 'e1e37287-9127-46cb-bddb-4a1a825a5d8e'

        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(Router, 'router', Mock())
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        result = defaultdict(int)

        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }

        tree = node.get_project_tree()

        monkeypatch.setattr(node, 'mount_redraw', Mock())

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

        tree = node.get_project_tree()

        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        #root_folder = tree.get_children()[0]
        #folder = root_folder.get_children()[0]
        #return root_folder, root_folder.get_children()[1], folder, folder.get_children()[2].get_children()[0]

        assert type(tree) == BCProjectTree
        #root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 2
        assert type(root_folder.folder_children[0]) == BCPFolder
        assert root_folder.folder_children[0].de['name'] == 'folder'
        #hello_world = root_folder.folder_children[1]
        assert type(hello_world) == BCPFile
        assert self.get_BCPFile_title(hello_world) == 'hello_world.py'
        #folder = root_folder.folder_children[0]
        #hello_folder = folder.folder_children[0]
        assert type(hello_folder) == BCPFile
        assert self.get_BCPFile_title(hello_folder) == 'hello_folder.py'

        folder.on_click(Mock())

        node.delete_selected_de(Mock())

        assert set(editor.project['deleted_directory_entries']) == {'c1a4bc81-1ade-4c55-b457-81e59b785b01', '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a'}

        tree = node.get_project_tree()
        assert type(tree) == BCProjectTree
        root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 1
        assert type(root_folder.folder_children[0]) == BCPFile
        assert root_folder.folder_children[0].de['name'] == 'hello_world.py'


class TestContextMenuFormItems(object):
    def test_context_menu_appears(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()

        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        view.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)
        view.selected_de = [de for de in editor.project['directory_entry'] if de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'][0]

        assert len(view.selected_de['form_items']) == 0

        view.mount_redraw = Mock()
        assert view.context_menu is None
        Router.router.ResetHashChange.reset_mock()
        view.contextmenu_preview(Mock(pageX=10, pageY=10))
        assert type(view.context_menu) == ContextMenuFormItems
        assert len(view.context_menu.menu_items) >= 1
        assert view.context_menu.menu_items[0][0] == 'New Button'
        assert callable(view.context_menu.menu_items[0][1])
        view.mount_redraw.assert_called()
        Router.router.ResetHashChange.assert_called()

        Router.router.ResetHashChange.reset_mock()
        view.mount_redraw.reset_mock()
        js.return_get_element_by_id = {'preview': Mock(getBoundingClientRect=Mock(return_value=Mock(left=0, top=0)))}
        assert view.selected_item == ''
        view.new_button(Mock(clientX=10, clientY=20))
        assert view.context_menu is None
        view.mount_redraw.assert_called()
        Router.router.ResetHashChange.assert_called()

        assert len(view.selected_de['form_items']) == 1
        button = view.selected_de['form_items'][0]
        assert button['type'] == 'button'
        assert button['x'] == 10
        assert button['y'] == 10
        assert button['width'] == 100
        assert button['height'] == 30
        assert button['caption'] == 'Button'
        assert button['name'] == 'button1'

        def is_nvode_button(vnode):
            if hasattr(vnode, 'get_tag_name') is False:
                return None
            if vnode.get_tag_name() != 'button':
                return None
            l = vnode.get_children()
            if len(l) != 1:
                return None
            child = l[0]
            if type(child) == t and child.text == 'Button':
                return vnode
            else:
                return None

        vnode_button = get_matching_vnode(view, is_nvode_button)
        assert vnode_button is not None
        assert view.selected_item == button['id']
        assert style_to_dict(vnode_button.get_attribs()['style'])['left'] == str(button['x'])
        assert style_to_dict(vnode_button.get_attribs()['style'])['top'] == str(button['y'])

        def find_preview(vnode):
            if not hasattr(vnode, 'get_attribs'):
                return False
            return vnode.get_attribs().get('id', '') == 'preview-svg'

        preview_node = get_matching_vnode(view, find_preview)
        assert preview_node is not None
        preview_node.get_attribs()['onmousedown'](Mock(button=0))
        assert view.selected_item == ''

        vnode_button.get_attribs()['onmousedown'](Mock(button=0))
        assert view.selected_item == button['id']
        assert view.mouse_is_down == True

        # Lift the mouse button up and check we are still selected
        preview_node.get_attribs()['onmouseup'](Mock())
        assert view.selected_item == button['id']
        assert view.mouse_is_down == False

        # Test clicking with the right mouse button selects an item but doesnt allow us to drag it
        # First deselect it
        preview_node = get_matching_vnode(view, find_preview)
        assert preview_node is not None
        preview_node.get_attribs()['onmousedown'](Mock(button=0))
        assert view.selected_item == ''

        # Then click with the right hand mouse button
        vnode_button.get_attribs()['onmousedown'](Mock(button=1))
        assert view.selected_item == button['id']
        assert view.mouse_is_down == False

        # Click again
        vnode_button.get_attribs()['onmousedown'](Mock(button=0))
        assert view.selected_item == button['id']
        assert view.mouse_is_down == True

        #Move the mouse and check the button moves
        Router.router.global_mouse_x = 500
        Router.router.global_mouse_y = 500

        Router.router.on_body_mousemove(Mock(clientX=520, clientY=530))

        assert button['x'] == 30
        assert button['y'] == 40
        assert button['width'] == 100
        assert button['height'] == 30
        vnode_button = get_matching_vnode(view, is_nvode_button)
        assert style_to_dict(vnode_button.get_attribs()['style'])['left'] == str(button['x'])
        assert style_to_dict(vnode_button.get_attribs()['style'])['top'] == str(button['y'])

        # Check moving the mouse with nothing selected does nothing
        preview_node.get_attribs()['onmousedown'](Mock(button=0))
        assert view.selected_item == ''
        assert view.mouse_is_down == True

        Router.router.on_body_mousemove(Mock(clientX=550, clientY=550))

        assert button['x'] == 30
        assert button['y'] == 40
        assert button['width'] == 100
        assert button['height'] == 30
        vnode_button = get_matching_vnode(view, is_nvode_button)
        assert style_to_dict(vnode_button.get_attribs()['style'])['left'] == str(button['x'])
        assert style_to_dict(vnode_button.get_attribs()['style'])['top'] == str(button['y'])

        # Test clicking on handles selects them and allows us to resize the button
        vnode_button.get_attribs()['onmousedown'](Mock(button=0))
        assert view.selected_item == button['id']
        assert view.mouse_is_down == True
        assert view.selected_handler == HANDLE_NONE
        vnode_button.get_attribs()['onmouseup'](Mock())
        assert view.selected_item == button['id']
        assert view.mouse_is_down == False

        # Click the top left handle and move the mouse
        vnode_handle = get_vnode_by_id(view, 'handle-top-left')
        vnode_handle.get_attribs()['onmousedown'](Mock(button=0))
        assert view.selected_item == button['id']
        assert view.mouse_is_down == True
        assert view.selected_handler == HANDLE_TOPLEFT

        Router.router.on_body_mousemove(Mock(clientX=540, clientY=540))
        assert button['x'] == 20
        assert button['y'] == 30
        assert button['width'] == 110
        assert button['height'] == 40

        vnode_handle.get_attribs()['onmouseup'](Mock())
        assert view.selected_item == button['id']
        assert view.mouse_is_down == False
        assert view.selected_handler == HANDLE_NONE

        # Click the top right handle and move the mouse
        vnode_handle = get_vnode_by_id(view, 'handle-top-right')
        vnode_handle.get_attribs()['onmousedown'](Mock(button=0))
        assert view.selected_item == button['id']
        assert view.mouse_is_down == True
        assert view.selected_handler == HANDLE_TOPRIGHT

        Router.router.on_body_mousemove(Mock(clientX=550, clientY=545))
        assert button['x'] == 20
        assert button['y'] == 35
        assert button['width'] == 120
        assert button['height'] == 35

        vnode_handle.get_attribs()['onmouseup'](Mock())
        assert view.selected_item == button['id']
        assert view.mouse_is_down == False
        assert view.selected_handler == HANDLE_NONE

        # Click the bottom right handle and move the mouse
        vnode_handle = get_vnode_by_id(view, 'handle-bottom-right')
        vnode_handle.get_attribs()['onmousedown'](Mock(button=0))
        assert view.selected_item == button['id']
        assert view.mouse_is_down == True
        assert view.selected_handler == HANDLE_BOTTOMRIGHT

        Router.router.on_body_mousemove(Mock(clientX=565, clientY=555))
        assert button['x'] == 20
        assert button['y'] == 35
        assert button['width'] == 135
        assert button['height'] == 45

        vnode_handle.get_attribs()['onmouseup'](Mock())
        assert view.selected_item == button['id']
        assert view.mouse_is_down == False
        assert view.selected_handler == HANDLE_NONE

        # Click the bottom left handle and move the mouse
        vnode_handle = get_vnode_by_id(view, 'handle-bottom-left')
        vnode_handle.get_attribs()['onmousedown'](Mock(button=0))
        assert view.selected_item == button['id']
        assert view.mouse_is_down == True
        assert view.selected_handler == HANDLE_BOTTOMLEFT

        Router.router.on_body_mousemove(Mock(clientX=555, clientY=550))
        assert button['x'] == 10
        assert button['y'] == 35
        assert button['width'] == 145
        assert button['height'] == 40

        vnode_handle.get_attribs()['onmouseup'](Mock())
        assert view.selected_item == button['id']
        assert view.mouse_is_down == False
        assert view.selected_handler == HANDLE_NONE

        view.mount_redraw = Mock()
        assert view.context_menu is None
        Router.router.ResetHashChange.reset_mock()
        vnode_button.get_attribs()['oncontextmenu'](Mock())
        assert type(view.context_menu) == ContextMenuFormItems
        assert len(view.context_menu.menu_items) >= 1

        assert 'Change caption' ==  view.context_menu.menu_items[0][0]
        assert 'Change height' ==   view.context_menu.menu_items[1][0]
        assert 'Change name' ==     view.context_menu.menu_items[2][0]
        assert 'Change visible' ==  view.context_menu.menu_items[3][0]
        assert 'Change width' ==    view.context_menu.menu_items[4][0]
        assert 'Change x' ==        view.context_menu.menu_items[5][0]
        assert 'Change y' ==        view.context_menu.menu_items[6][0]

        assert view.context_menu.menu_items[-1][0] == 'Delete'
        assert callable(view.context_menu.menu_items[-1][1])
        view.mount_redraw.assert_called()
        Router.router.ResetHashChange.assert_called()
        view.context_menu.menu_items[-1][1](Mock())

        vnode_button = get_matching_vnode(view, is_nvode_button)
        assert vnode_button is None

    def test_context_menu_can_change_parameters(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()

        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        view.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)
        view.selected_de = [de for de in editor.project['directory_entry'] if de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'][0]

        view.mount_redraw = Mock()
        Router.router.ResetHashChange.reset_mock()
        view.contextmenu_preview(Mock(pageX=10, pageY=10))

        Router.router.ResetHashChange.reset_mock()
        view.mount_redraw.reset_mock()
        js.return_get_element_by_id = {'preview': Mock(getBoundingClientRect=Mock(return_value=Mock(left=0, top=0)))}
        view.new_button(Mock(clientX=10, clientY=20))

        button = view.selected_de['form_items'][0]

        def is_nvode_button(vnode, button_title):
            if hasattr(vnode, 'get_tag_name') is False:
                return None
            if vnode.get_tag_name() != 'button':
                return None
            l = vnode.get_children()
            if len(l) != 1:
                return None
            child = l[0]
            if type(child) == t and child.text == button_title:
                return vnode
            else:
                return None

        vnode_button = get_matching_vnode(view, lambda vnode: is_nvode_button(vnode, 'Button'))

        view.mount_redraw = Mock()
        Router.router.ResetHashChange.reset_mock()
        vnode_button.get_attribs()['oncontextmenu'](Mock())

        assert 'Change caption' ==  view.context_menu.menu_items[0][0]
        assert callable(view.context_menu.menu_items[0][1])
        view.mount_redraw.assert_called()
        Router.router.ResetHashChange.assert_called()
        view.context_menu.menu_items[0][1](Mock())

        result = dict()

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'changeProperty':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['changeProperty_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtValue":
                            result['default_value'] = vnode.get_attribs().get('value', '')
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        view.mount_redraw = Mock()

        virtual_node = view._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        assert result['default_value'] == 'Button'

        # Call the modal handler
        rendered_modal = view._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'changeProperty': rendered_modal}

        def setup_mock_modal_callback(node, file_name):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtValue':
                node.value = file_name

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'Fastasico!'))

        #print('test_editor result[changeProperty_OK_handler]=', result['changeProperty_OK_handler'])
        result['changeProperty_OK_handler'](Mock())

        rendered = view._render(None)

        vnode_button = get_matching_vnode(view, lambda vnode: is_nvode_button(vnode, 'Fastasico!'))
        assert vnode_button is not None

        view.program_is_running = True

        rendered = view._render(None)

        vnode_button = get_matching_vnode(view, lambda vnode: is_nvode_button(vnode, 'Fastasico!'))
        assert vnode_button is None

    def test_context_menu_can_change_boolean_parameter(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()

        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        view.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)
        view.selected_de = [de for de in editor.project['directory_entry'] if de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'][0]

        view.mount_redraw = Mock()
        Router.router.ResetHashChange.reset_mock()
        view.contextmenu_preview(Mock(pageX=10, pageY=10))

        Router.router.ResetHashChange.reset_mock()
        view.mount_redraw.reset_mock()
        js.return_get_element_by_id = {'preview': Mock(getBoundingClientRect=Mock(return_value=Mock(left=0, top=0)))}
        view.new_checkbox(Mock(clientX=10, clientY=20))

        checkbox = view.selected_de['form_items'][0]

        def is_nvode_checkbox(vnode):
            if hasattr(vnode, 'get_tag_name') is False:
                return None
            if vnode.get_tag_name() != 'input':
                return None
            if vnode.get_attribs().get('type', '') != 'checkbox':
                return None
            #print('vnode called tag=input type=checkbox form_item=', vnode.get_attribs().get('form_item', ''))
            if vnode.get_attribs().get('form_item', '') != 'True':
                return None
            return vnode

        vnode_checkbox = get_matching_vnode(view, lambda vnode: is_nvode_checkbox(vnode))

        view.mount_redraw = Mock()
        Router.router.ResetHashChange.reset_mock()
        vnode_checkbox.get_attribs()['oncontextmenu'](Mock())

        assert 'Change value' ==  view.context_menu.menu_items[3][0]
        assert callable(view.context_menu.menu_items[3][1])
        view.mount_redraw.assert_called()
        Router.router.ResetHashChange.assert_called()
        view.context_menu.menu_items[3][1](Mock())

        result = dict()

        def mock_element_iterator_callback(vnode):
            #if hasattr(vnode, 'get_attribs'):
            #    print('mock_element_iterator_callback called vnodeid=', vnode.get_attribs().get('id'))
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'changePropertyBoolean':
                #print('mock_element_iterator_callback changeBooleanProperty found')

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['changePropertyBoolean_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "chkValue":
                            #print('mock_element_iterator_callback  vnode.checked=',vnode.get_attribs().get('checked', ''))
                            result['default_value'] = vnode.get_attribs().get('checked', '') == 'checked'
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        view.mount_redraw = Mock()

        virtual_node = view._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        assert result['default_value'] == False

        # Call the modal handler
        rendered_modal = view._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'changePropertyBoolean': rendered_modal}

        def setup_mock_modal_callback(node, checked):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'chkValue':
                node.checked = checked

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, True))

        #print('test_editor result[changeProperty_OK_handler]=', result['changeProperty_OK_handler'])
        result['changePropertyBoolean_OK_handler'](Mock())

        rendered = view._build_virtual_dom()

        vnode_checkbox = get_matching_vnode(rendered, lambda vnode: is_nvode_checkbox(vnode))
        assert vnode_checkbox.get_attribs()['checked'] == 'checked'

    def test_context_menu_can_change_color_parameter(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()

        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        view.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)
        view.selected_de = [de for de in editor.project['directory_entry'] if de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'][0]

        view.mount_redraw = Mock()
        Router.router.ResetHashChange.reset_mock()
        view.contextmenu_preview(Mock(pageX=10, pageY=10))

        Router.router.ResetHashChange.reset_mock()
        view.mount_redraw.reset_mock()
        js.return_get_element_by_id = {'preview': Mock(getBoundingClientRect=Mock(return_value=Mock(left=0, top=0)))}
        view.new_rectangle(Mock(clientX=10, clientY=20))

        checkbox = view.selected_de['form_items'][0]

        def is_nvode_rect(vnode):
            if hasattr(vnode, 'get_tag_name') is False:
                return None
            if vnode.get_tag_name() != 'rect':
                return None
            #if vnode.get_attribs().get('type', '') != 'checkbox':
            #    return None
            #print('vnode called tag=input type=checkbox form_item=', vnode.get_attribs().get('form_item', ''))
            #if vnode.get_attribs().get('form_item', '') != 'True':
            #    return None
            return vnode

        vnode_rect = get_matching_vnode(view, lambda vnode: is_nvode_rect(vnode))

        view.mount_redraw = Mock()
        Router.router.ResetHashChange.reset_mock()
        vnode_rect.get_attribs()['oncontextmenu'](Mock())

        fill_index = 0
        #print('menu items=', [view.context_menu.menu_items[i][0] for i in range(len(view.context_menu.menu_items))])
        assert 'Change fill' ==  view.context_menu.menu_items[fill_index][0]
        assert callable(view.context_menu.menu_items[fill_index][1])
        view.mount_redraw.assert_called()
        Router.router.ResetHashChange.assert_called()
        view.context_menu.menu_items[fill_index][1](Mock())

        result = dict()

        def mock_element_iterator_callback(vnode):
            #if hasattr(vnode, 'get_attribs'):
            #    print('mock_element_iterator_callback called vnodeid=', vnode.get_attribs().get('id'))
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'changePropertyColor':
                #print('mock_element_iterator_callback changeBooleanProperty found')

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['changePropertyColor_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "chkEmpty":
                            result['color_empty'] = vnode.get_attribs().get('checked', '') == 'checked'
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtRed":
                            result['color_red'] = vnode.get_attribs().get('value', '')
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtGreen":
                            result['color_green'] = vnode.get_attribs().get('value', '')
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtBlue":
                            result['color_blue'] = vnode.get_attribs().get('value', '')
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        view.mount_redraw = Mock()

        virtual_node = view._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        assert result['color_empty'] == True

        # Call the modal handler
        rendered_modal = view._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'changePropertyColor': rendered_modal}

        def setup_mock_modal_callback(node, empty, red, green, blue):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'chkEmpty':
                #print('setup_mock_modal_callback setting chkEmpty=', empty)
                node.checked = empty
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtRed':
                node.value = red
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtGreen':
                node.value = green
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtBlue':
                node.value = blue

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, False, '255', '0', '0'))

        result['changePropertyColor_OK_handler'](Mock())

        rendered = view._build_virtual_dom()

        vnode_rect = get_matching_vnode(rendered, lambda vnode: is_nvode_rect(vnode))
        assert vnode_rect.get_attribs()['fill'] == 'rgb(255,0,0)'

        vnode_rect.get_attribs()['oncontextmenu'](Mock())
        fill_index = 0
        #print('menu items=', [view.context_menu.menu_items[i][0] for i in range(len(view.context_menu.menu_items))])
        assert 'Change fill' ==  view.context_menu.menu_items[fill_index][0]
        assert callable(view.context_menu.menu_items[fill_index][1])
        view.mount_redraw.assert_called()
        Router.router.ResetHashChange.assert_called()
        view.context_menu.menu_items[fill_index][1](Mock())

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, True, '', '', ''))

        result['changePropertyColor_OK_handler'](Mock())

        rendered = view._build_virtual_dom()

        vnode_rect = get_matching_vnode(rendered, lambda vnode: is_nvode_rect(vnode))
        assert vnode_rect.get_attribs()['fill'] == 'none'

    def test_multiple_new_buttons_have_unique_names(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()

        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        view.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)
        view.selected_de = [de for de in editor.project['directory_entry'] if de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'][0]

        view.mount_redraw = Mock()
        Router.router.ResetHashChange.reset_mock()
        view.contextmenu_preview(Mock(pageX=10, pageY=10))

        Router.router.ResetHashChange.reset_mock()
        view.mount_redraw.reset_mock()
        js.return_get_element_by_id = {'preview': Mock(getBoundingClientRect=Mock(return_value=Mock(left=0, top=0)))}
        view.new_button(Mock(clientX=10, clientY=20))
        view.new_button(Mock(clientX=20, clientY=30))

        button = view.selected_de['form_items'][0]

        def is_nvode_button(vnode, button_title):
            if hasattr(vnode, 'get_tag_name') is False:
                return None
            if vnode.get_tag_name() != 'button':
                return None
            l = vnode.get_children()
            if len(l) != 1:
                return None
            child = l[0]
            if type(child) == t and child.text == button_title:
                return vnode
            else:
                return None

        vnode_buttons = get_matching_vnodes(view, lambda vnode: is_nvode_button(vnode, 'Button'))
        assert len(vnode_buttons) == 2

        assert len(view.selected_de['form_items']) == 2

        for fi in view.selected_de['form_items']:
            assert fi['type'] == 'button'

        assert {fi['name'] for fi in view.selected_de['form_items']} == {'button1', 'button2'}

        button2_fi = [fi for fi in view.selected_de['form_items'] if fi['name'] == 'button2'][0]

        view.mount_redraw = Mock()
        Router.router.ResetHashChange.reset_mock()
        vnode_button = vnode_buttons[1]
        vnode_button.get_attribs()['oncontextmenu'](Mock())

        name_index = 2
        assert 'Change name' ==  view.context_menu.menu_items[name_index][0]
        assert callable(view.context_menu.menu_items[name_index][1])
        view.mount_redraw.assert_called()
        Router.router.ResetHashChange.assert_called()
        view.context_menu.menu_items[name_index][1](Mock())

        #assert False

        result = dict()

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'changeProperty':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['changeProperty_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtValue":
                            result['default_value'] = vnode.get_attribs().get('value', '')
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        view.mount_redraw = Mock()

        virtual_node = view._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        assert result['default_value'] == 'button2'

        # Call the modal handler
        rendered_modal = view._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'changeProperty': rendered_modal}

        def setup_mock_modal_callback(node, control_name):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtValue':
                node.value = control_name

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'button1'))

        #print('test_editor result[changeProperty_OK_handler]=', result['changeProperty_OK_handler'])
        editor.js.globals.window.alert = Mock()
        result['changeProperty_OK_handler'](Mock())

        editor.js.globals.window.alert.assert_called_with('Error: Another control with that name already exists')
        assert {fi['name'] for fi in view.selected_de['form_items']} == {'button1', 'button2'}

class TestFormItems(object):
    def gen_check_form_item_generic_properties(self, form_item_type):
        assert get_form_item_property(form_item_type)['x'] == FormItemPropType.INT
        assert get_form_item_property(form_item_type)['y'] == FormItemPropType.INT
        assert get_form_item_property(form_item_type)['width'] == FormItemPropType.INT
        assert get_form_item_property(form_item_type)['height'] == FormItemPropType.INT
        assert get_form_item_property(form_item_type)['name'] == FormItemPropType.STRING

    def gen_check_svg_form_item_generic_properties(self, form_item_type):
        self.gen_check_form_item_generic_properties(form_item_type)
        assert get_form_item_property(form_item_type)['stroke_width'] == FormItemPropType.INT
        assert get_form_item_property(form_item_type)['stroke'] == FormItemPropType.COLOR
        assert get_form_item_property(form_item_type)['fill'] == FormItemPropType.COLOR

    def test_form_item_line_properties(self):
        #Lines are different to the other types
        assert 'x' not in get_form_item_property('line')
        assert 'y' not in get_form_item_property('line')
        assert 'width' not in get_form_item_property('line')
        assert 'height' not in get_form_item_property('line')

        assert get_form_item_property('line')['x1'] == FormItemPropType.INT
        assert get_form_item_property('line')['y1'] == FormItemPropType.INT
        assert get_form_item_property('line')['x2'] == FormItemPropType.INT
        assert get_form_item_property('line')['y2'] == FormItemPropType.INT
        assert get_form_item_property('line')['name'] == FormItemPropType.STRING
        assert get_form_item_property('line')['stroke_width'] == FormItemPropType.INT
        assert get_form_item_property('line')['stroke'] == FormItemPropType.COLOR

    def test_form_item_button_properties(self):
        self.gen_check_form_item_generic_properties('button')
        assert get_form_item_property('button')['caption'] == FormItemPropType.STRING
        self.gen_check_form_item_generic_properties('label')
        assert get_form_item_property('label')['caption'] == FormItemPropType.STRING
        self.gen_check_form_item_generic_properties('frame')
        assert get_form_item_property('frame')['caption'] == FormItemPropType.STRING
        self.gen_check_form_item_generic_properties('checkbox')
        assert get_form_item_property('checkbox')['caption'] == FormItemPropType.STRING
        self.gen_check_form_item_generic_properties('textbox')
        assert get_form_item_property('textbox')['text'] == FormItemPropType.STRING
        self.gen_check_form_item_generic_properties('image')
        assert get_form_item_property('image')['src'] == FormItemPropType.STRING
        self.gen_check_form_item_generic_properties('checkbox')
        assert get_form_item_property('checkbox')['value'] == FormItemPropType.BOOLEAN

    def test_form_items_name(self):
        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                     ]
                   }
        editor.project = response

        view = editor.EditorView()
        view.selected_de = response['directory_entry'][0]
        assert view.get_next_name('button') == 'button1'

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                     ]
                   }
        editor.project = response
        view.selected_de = response['directory_entry'][0]

        response['directory_entry'][0]['form_items'] = [{'name': 'button1'}]
        assert view.get_next_name('button') == 'button2'


class TestRunningAProgram(object):
    def test_files_are_loaded_into_virtual_file_system(self, monkeypatch):
        # Test the default module directory location is correct
        assert editor.python_module_dir == '/lib/pypyjs/lib_pypy/'

        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        old_python_module_dir = editor.python_module_dir
        with TemporaryDirectory() as temp_dir:
            assert os.path.isdir(temp_dir)
            editor.python_module_dir = temp_dir + '/'
            body = js.globals.document.body
            error_404_page = c("div", [c("p", "No match 404 error"),
                                       c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
            view = editor.EditorView()
            r = Router({r'^$': view},
                        error_404_page, body)
            r.route()
            view.mount_redraw = Mock()
            hello_world_content = "print('Hello world')"
            hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

            response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                        'name': 'Mark\'s Project',
                        'type': 0,
                        'public': True,
                        'directory_entry':
                         [
                           # Root directory
                           {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                            'name': '',
                            'is_file': False,
                            'content': '',
                            'form_items': '[]',
                            'parent_id': None,
                            'is_default': False,
                           },
                           # A file in the root directory
                           {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                            'name': 'hello_world.py',
                            'is_file': True,
                            'content': hello_world_content,
                            'form_items': '[]',
                            'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                            'is_default': True,
                           },
                           # A folder in the root directory
                           {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                            'name': 'folder',
                            'is_file': False,
                            'content': '',
                            'form_items': '[]',
                            'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                            'is_default': False,
                           },
                           # A file in the 'folder' folder
                           {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                            'name': 'hello_folder.py',
                            'is_file': True,
                            'content': hello_folder_content,
                            'form_items': '[]',
                            'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                            'is_default': False,
                           },
                         ]
                        }
            view.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                                  response)

            view.write_program_to_virtual_file_system()

            with open(temp_dir + '/hello_world.py', 'r') as project_file:
                file_content = project_file.read()
            assert file_content == hello_world_content

            with open(temp_dir + '/folder/hello_folder.py', 'r') as project_file:
                file_content = project_file.read()
            assert file_content == hello_folder_content

        editor.python_module_dir = old_python_module_dir

    def test_process_file_location(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()
        view.mount_redraw = Mock()

        editor.python_module_dir = '/lib/pypyjs/lib_pypy/'
        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
print('Hello folder i={}'.format(i))
"""
        editor.project = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": true}]'),
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': True,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': [],
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }

        class TestForm1(Form):
            file_location = '/lib/pypyjs/lib_pypy/hello_world.py'

        t1 = TestForm1(editorview=view)
        assert t1.get_file_location() == 'hello_world.py'

        class TestForm2(Form):
            file_location = '/lib/pypyjs/lib_pypy/folder/hello_folder.py'

        t2 = TestForm2(editorview=view)
        assert t2.get_file_location() == 'folder/hello_folder.py'

        form_items = t1.get_form_items()

        assert len(form_items) == 1
        fi = form_items[0]
        assert fi['width'] == 100
        assert fi['name'] == 'button1'

    def test_running_program_adds_form_to_form_stack(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()
        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
print('Hello folder i={}'.format(i))
"""
        editor.project = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": false}]'),
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': True,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': [],
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }

        view.images = [{'id': '4a88ff77-5969-40b8-a1da-8fefc5477f44', 'name': 'space-rocket.jpg'},
                         {'id': '4ee4576a-c5f8-450b-bf8f-3a77f87632f3', 'name': 'my-image.jpg'}]

        assert len(view.form_stack) == 0
        js.return_get_element_by_id = {'secondary-output': Mock()}

        class TestForm2(Form):
            file_location = '/lib/pypyjs/lib_pypy/folder/hello_folder.py'

        class TestForm1(Form):
            file_location = '/lib/pypyjs/lib_pypy/hello_world.py'

            def open_child(self):
                TestForm2(self)

        form_classes = [TestForm1]
        view.get_default_module_form_classes = Mock(return_value=form_classes)
        view.write_program_to_virtual_file_system = Mock()

        # Test dashboard link is inthe Dom before we run the project
        result = defaultdict(bool)
        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'text') and vnode.text == 'Dashboard':
                result['dashboard_found'] = True
            if hasattr(vnode, 'text') and vnode.text == 'Debug':
                result['debug_found'] = True
            if hasattr(vnode, 'text') and vnode.text == ' Run':
                result['run_found'] = True
            if hasattr(vnode, 'text') and vnode.text == 'Stop':
                result['stop_found'] = True
        view.mount_redraw = Mock()

        virtual_node = view._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        assert result['dashboard_found'] == True
        assert result['debug_found'] == True
        assert result['run_found'] == True
        assert result['stop_found'] == False

        # Test a control marked as visible = False is still visible when not running
        view.selected_de = view.get_project()['directory_entry'][0]
        assert len(view.get_selected_de_form_controls()) == 1

        view.cleanup_project = Mock()
        view.save_project = Mock()
        view.run_project(Mock())

        # Assert we save the project when run is called
        view.save_project.assert_called_once()

        # Test that while the program is running we cannot see the Dashboard Link
        assert view.program_is_running == True

        result = defaultdict(bool)
        view.mount_redraw = Mock()

        virtual_node = view._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        assert result['dashboard_found'] == False
        assert result['debug_found'] == False
        assert result['run_found'] == False
        assert result['stop_found'] == True

        assert len(view.form_stack) == 1
        assert isinstance(view.form_stack[-1].button1, bcform.Button)

        d = {'count': 0}
        def dummy_handler(e):
            d['count'] += 1

        # Test we can add a dynamic button to the form
        form = view.form_stack[-1]
        # Test a control marked as visible = False is not visible when running
        assert len(form.get_form_control_elements()) == 1

        assert len(form.get_form_controls()) == 1
        form.add_control(bcform.Button({'x': 1, 'y': 1, 'width': 100,
                                        'height': 80, 'caption': '2nd Button',
                                        'name':'bill', 'visible': True,
                                        'onclick': dummy_handler}))
        assert len(form.get_form_control_elements()) == 2 # The dynamically added button should be visible but not the static
        assert len(form.get_form_controls()) == 2
        # Mark the static button as visible and verify it appear
        static_button_form_item = form.get_form_controls()[0]
        assert static_button_form_item.visible == False
        static_button_form_item.visible = True
        assert len(form.get_form_control_elements()) == 3 # Both buttons should now be visible

        static_button = form.get_form_control_elements()[0]
        dynamic_button = form.get_form_control_elements()[1]
        form.handle_onclick = Mock()
        static_button.get_attribs()['onclick'](Mock())
        form.handle_onclick.assert_called_once()
        form.handle_onclick = Mock()
        assert d['count'] == 0
        dynamic_button.get_attribs()['onclick'](Mock())
        assert d['count'] == 1
        form.handle_onclick.assert_not_called()
        form.remove_dynamic_controls()
        assert len(form.get_form_controls()) == 1

        view.form_stack[-1].on_historygraph_download_complete = Mock()
        view.form_stack[-1].on_historygraph_download_complete.assert_not_called()
        #js.globals.cavorite_setTimeout = Mock()
        old_timeout = timeouts.set_timeout
        timeouts.set_timeout = Mock()
        assert view.historygraph_download_timeout is None
        view.on_historygraph_download_complete()
        view.form_stack[-1].on_historygraph_download_complete.assert_called_once()
        #js.globals.cavorite_setTimeout.assert_called_once()
        timeouts.set_timeout.assert_called_once()
        assert view.historygraph_download_timeout is not None
        #print('timeouts.set_timeout.call_args=', timeouts.set_timeout.call_args)
        #print('timeouts.set_timeout.call_args[0][0]=', timeouts.set_timeout.call_args[0][0])
        # Test that calling the timeout callback resets the timeout value
        timeout_callback = timeouts.set_timeout.call_args[0][0]
        #print('view.historygraph_download_timeout=',view.historygraph_download_timeout)
        #assert False
        timeout_callback()
        assert view.historygraph_download_timeout is None
        timeouts.set_timeout = old_timeout

        # Assert we can add a new form to the form stack
        view.form_stack[-1].open_child()
        assert len(view.form_stack) == 2
        assert type(view.form_stack[-1]) == TestForm2

        # Assert we can close the form on the top of the stack
        view.form_stack[0].on_child_form_closed = Mock()
        view.form_stack[-1].close()
        assert len(view.form_stack) == 1
        view.form_stack[0].on_child_form_closed.assert_called()

        # Assert we can access the list of preloaded images
        form = view.form_stack[0]
        assert form.get_preloaded_images() == view.images
        assert form.get_preloaded_image_id('space-rocket.jpg') == \
            '4a88ff77-5969-40b8-a1da-8fefc5477f44'
        with pytest.raises(AssertionError):
            form.get_preloaded_image_id('invalid.jpg')

        # Assert mouse moves are received by the form
        preview = Mock()
        preview.getBoundingClientRect = Mock(return_value=MagicMock(left=2, top=10))
        js.return_get_element_by_id = {'preview': preview}
        form = view.form_stack[0]
        form.on_body_mousemove = Mock()
        e = Mock()
        e.configure_mock(clientX=100, clientY=100)
        view.on_body_mousemove(e, 10, 10)
        form.on_body_mousemove.assert_called_with(98, 90)

        # Assert mouse clicks on no specific control are received by the form
        form = view.form_stack[0]
        form.on_body_click = Mock()
        view.on_body_click(Mock())
        form.on_body_click.assert_called_with()

        result = defaultdict(bool)
        # Test the timeout is cleared if it is set
        view.historygraph_download_timeout = Mock()
        old_clear_timeout = editor.timeouts.clear_timeout
        editor.timeouts.clear_timeout = Mock()
        view.stop_project(Mock())
        assert view.program_is_running == False
        assert view.form_stack == []
        assert js.globals.document.print_to_secondary_output == False
        timeouts.clear_timeout.assert_called_once()
        view.mount_redraw = Mock()
        editor.timeouts.clear_timeout = old_clear_timeout

        virtual_node = view._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        assert result['dashboard_found'] == True
        assert result['debug_found'] == True
        assert result['run_found'] == True
        assert result['stop_found'] == False



    def test_running_program_can_access_timeouts(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('531cb169-91f4-4102-9a0a-2cd5e9659071')

        reset_hash_change_mock = Mock()
        monkeypatch.setattr(Router, 'ResetHashChange', reset_hash_change_mock)
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(timeouts, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()
        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
print('Hello folder i={}'.format(i))
"""
        editor.project = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": true}]'),
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': True,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': [],
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }

        assert len(view.form_stack) == 0
        js.return_get_element_by_id = {'secondary-output': Mock()}

        counter = dict()
        counter['count'] = 0

        class TestForm1(Form):
            file_location = '/lib/pypyjs/lib_pypy/hello_world.py'

            def timeout_handler(self):
                counter['count'] += 1

            def fire_timeout(self):
                return self.set_timeout(self.timeout_handler, 1000)

        form_classes = [TestForm1]
        view.get_default_module_form_classes = Mock(return_value=form_classes)
        view.write_program_to_virtual_file_system = Mock()
        view.cleanup_project = Mock()
        view.save_project = Mock()
        view.run_project(Mock())
        assert view.program_is_running == True

        assert len(timeouts.global_timeout_callbacks) == 1
        assert len(timeouts.global_timeout_val_to_id) == 1
        assert len(timeouts.global_timeout_id_to_val) == 1
        form = view.form_stack[-1]
        assert len(form._active_timeouts) == 0
        val = form.fire_timeout()
        assert set(timeouts.global_timeout_callbacks.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_timeout_id_to_val.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_timeout_val_to_id.keys()) == {val}
        assert len(form._active_timeouts) == 1

        assert counter['count'] == 0

        view.mount_redraw = Mock()
        assert reset_hash_change_mock.call_count == 2
        js.globals.document.cavorite_timeouthandler(str(dummy_uuid()))

        view.mount_redraw.assert_called()
        assert reset_hash_change_mock.call_count == 3

        assert counter['count'] == 1
        assert len(timeouts.global_timeout_callbacks) == 0
        assert len(timeouts.global_timeout_val_to_id) == 0
        assert len(timeouts.global_timeout_id_to_val) == 0
        assert len(form._active_timeouts) == 0

    def test_stopping_program_can_clears_timeouts(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('531cb169-91f4-4102-9a0a-2cd5e9659071')

        reset_hash_change_mock = Mock()
        monkeypatch.setattr(Router, 'ResetHashChange', reset_hash_change_mock)
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(timeouts, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()
        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
print('Hello folder i={}'.format(i))
"""
        editor.project = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": true}]'),
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': True,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': [],
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }

        assert len(view.form_stack) == 0
        js.return_get_element_by_id = {'secondary-output': Mock()}

        counter = dict()
        counter['count'] = 0

        class TestForm1(Form):
            file_location = '/lib/pypyjs/lib_pypy/hello_world.py'

            def timeout_handler(self):
                counter['count'] += 1

            def fire_timeout(self):
                return self.set_timeout(self.timeout_handler, 1000)

        form_classes = [TestForm1]
        view.get_default_module_form_classes = Mock(return_value=form_classes)
        view.write_program_to_virtual_file_system = Mock()
        view.cleanup_project = Mock()
        view.save_project = Mock()
        view.run_project(Mock())
        assert view.program_is_running == True

        assert len(timeouts.global_timeout_callbacks) == 1
        assert len(timeouts.global_timeout_val_to_id) == 1
        assert len(timeouts.global_timeout_id_to_val) == 1
        form = view.form_stack[-1]
        assert len(form._active_timeouts) == 0
        val = form.fire_timeout()
        assert set(timeouts.global_timeout_callbacks.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_timeout_id_to_val.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_timeout_val_to_id.keys()) == {val}
        assert len(form._active_timeouts) == 1

        view.historygraph_download_timeout = None
        old_clear_timeout = editor.timeouts.clear_timeout
        editor.timeouts.clear_timeout = Mock()
        view.stop_project(Mock())
        assert len(form._active_timeouts) == 0
        # The 2 calls are fromt he other timeout in this program
        assert timeouts.clear_timeout.call_count == 1
        editor.timeouts.clear_timeout = old_clear_timeout

    def test_running_program_can_clear_timeouts(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('531cb169-91f4-4102-9a0a-2cd5e9659071')

        reset_hash_change_mock = Mock()
        monkeypatch.setattr(Router, 'ResetHashChange', reset_hash_change_mock)
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(timeouts, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()
        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
print('Hello folder i={}'.format(i))
"""
        editor.project = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": true}]'),
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': True,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': [],
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }

        assert len(view.form_stack) == 0
        js.return_get_element_by_id = {'secondary-output': Mock()}

        counter = dict()
        counter['count'] = 0

        class TestForm1(Form):
            file_location = '/lib/pypyjs/lib_pypy/hello_world.py'

            def timeout_handler(self):
                counter['count'] += 1

            def fire_timeout(self):
                return self.set_timeout(self.timeout_handler, 1000)

        form_classes = [TestForm1]
        view.get_default_module_form_classes = Mock(return_value=form_classes)
        view.write_program_to_virtual_file_system = Mock()
        view.cleanup_project = Mock()
        view.save_project = Mock()
        view.run_project(Mock())
        assert view.program_is_running == True

        assert len(timeouts.global_timeout_callbacks) == 1
        assert len(timeouts.global_timeout_val_to_id) == 1
        assert len(timeouts.global_timeout_id_to_val) == 1
        val = view.form_stack[-1].fire_timeout()
        assert set(timeouts.global_timeout_callbacks.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_timeout_id_to_val.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_timeout_val_to_id.keys()) == {val}

        assert counter['count'] == 0

        view.mount_redraw = Mock()
        assert reset_hash_change_mock.call_count == 2
        #js.globals.document.cavorite_timeouthandler(str(dummy_uuid()))
        view.form_stack[-1].clear_timeout(val)

        assert view.mount_redraw.call_count == 0
        assert reset_hash_change_mock.call_count == 2

        assert counter['count'] == 0
        assert len(timeouts.global_timeout_callbacks) == 0
        assert len(timeouts.global_timeout_val_to_id) == 0
        assert len(timeouts.global_timeout_id_to_val) == 0

    def test_running_program_can_access_intervals(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('531cb169-91f4-4102-9a0a-2cd5e9659071')

        reset_hash_change_mock = Mock()
        monkeypatch.setattr(Router, 'ResetHashChange', reset_hash_change_mock)
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(timeouts, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()
        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
print('Hello folder i={}'.format(i))
"""
        editor.project = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": true}]'),
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': True,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': [],
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }

        assert len(view.form_stack) == 0
        js.return_get_element_by_id = {'secondary-output': Mock()}

        counter = dict()
        counter['count'] = 0

        class TestForm1(Form):
            file_location = '/lib/pypyjs/lib_pypy/hello_world.py'

            def timeout_handler(self):
                counter['count'] += 1

            def fire_interval(self):
                return self.set_interval(self.timeout_handler, 1000)

        form_classes = [TestForm1]
        view.get_default_module_form_classes = Mock(return_value=form_classes)
        view.write_program_to_virtual_file_system = Mock()
        view.cleanup_project = Mock()
        view.save_project = Mock()
        view.run_project(Mock())
        assert view.program_is_running == True

        assert len(timeouts.global_interval_callbacks) == 0
        assert len(timeouts.global_interval_val_to_id) == 0
        assert len(timeouts.global_interval_id_to_val) == 0
        form = view.form_stack[-1]
        assert len(form._active_intervals) == 0
        val = form.fire_interval()
        assert set(timeouts.global_interval_callbacks.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_interval_id_to_val.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_interval_val_to_id.keys()) == {val}
        assert len(form._active_intervals) == 1

        assert counter['count'] == 0

        view.mount_redraw = Mock()
        assert reset_hash_change_mock.call_count == 2
        js.globals.document.cavorite_intervalhandler(str(dummy_uuid()))

        view.mount_redraw.assert_called()
        assert reset_hash_change_mock.call_count == 3

        assert counter['count'] == 1
        assert set(timeouts.global_interval_callbacks.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_interval_id_to_val.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_interval_val_to_id.keys()) == {val}
        assert len(form._active_intervals) == 1

        val = view.form_stack[-1].clear_interval(val)

        assert counter['count'] == 1
        assert len(timeouts.global_interval_callbacks) == 0
        assert len(timeouts.global_interval_val_to_id) == 0
        assert len(timeouts.global_interval_id_to_val) == 0
        assert len(form._active_intervals) == 0

    def test_stopping_program_clears_intervals(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('531cb169-91f4-4102-9a0a-2cd5e9659071')

        reset_hash_change_mock = Mock()
        monkeypatch.setattr(Router, 'ResetHashChange', reset_hash_change_mock)
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(timeouts, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()
        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
print('Hello folder i={}'.format(i))
"""
        editor.project = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": true}]'),
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': True,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': [],
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }

        assert len(view.form_stack) == 0
        js.return_get_element_by_id = {'secondary-output': Mock()}

        counter = dict()
        counter['count'] = 0

        class TestForm1(Form):
            file_location = '/lib/pypyjs/lib_pypy/hello_world.py'

            def timeout_handler(self):
                counter['count'] += 1

            def fire_interval(self):
                return self.set_interval(self.timeout_handler, 1000)

        form_classes = [TestForm1]
        view.get_default_module_form_classes = Mock(return_value=form_classes)
        view.write_program_to_virtual_file_system = Mock()
        view.cleanup_project = Mock()
        view.save_project = Mock()
        view.run_project(Mock())
        assert view.program_is_running == True

        assert len(timeouts.global_interval_callbacks) == 0
        assert len(timeouts.global_interval_val_to_id) == 0
        assert len(timeouts.global_interval_id_to_val) == 0
        form = view.form_stack[-1]
        assert len(form._active_intervals) == 0
        val = form.fire_interval()
        assert set(timeouts.global_interval_callbacks.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_interval_id_to_val.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_interval_val_to_id.keys()) == {val}
        assert len(form._active_intervals) == 1

        assert counter['count'] == 0

        view.mount_redraw = Mock()
        assert reset_hash_change_mock.call_count == 2
        js.globals.document.cavorite_intervalhandler(str(dummy_uuid()))

        view.mount_redraw.assert_called()
        assert reset_hash_change_mock.call_count == 3

        assert counter['count'] == 1
        assert set(timeouts.global_interval_callbacks.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_interval_id_to_val.keys()) == {str(dummy_uuid())}
        assert set(timeouts.global_interval_val_to_id.keys()) == {val}
        assert len(form._active_intervals) == 1

        view.stop_project(Mock())

        assert len(form._active_intervals) == 0


    def test_running_with_storage_program_initialises_historygraph(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        mock_download_document_collection = Mock()
        monkeypatch.setattr(historygraphfrontend, 'download_document_collection', mock_download_document_collection)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()
        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
print('Hello folder i={}'.format(i))
"""
        documents_content = """from __future__ import absolute_import, unicode_literals, print_function
from binarycrate import historygraphfrontend
from historygraph import Document, DocumentObject
from historygraph import fields
import inspect
import copy

# Don't change anything above this line
# Your Document definition go here





# Don't change anything below this line
for c in copy.copy(globals().values()):
    if inspect.isclass(c) and issubclass(c, DocumentObject) and c != Document and c != DocumentObject:
        historygraphfrontend.documentcollection.register(c)

historygraphfrontend.download_document_collection()
"""
        editor.project = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 2,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30}]'),
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': True,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': [],
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                       # A the documents.py file in the root directory
                       {'id': '5f1b86d7-58ae-46e5-ad1f-775b7c561e7b',
                        'name': 'documents.py',
                        'is_file': True,
                        'content': documents_content,
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': True,
                       },
                     ]
                    }

        assert len(view.form_stack) == 0

        #class TestForm1(Form):
        #    file_location = '/lib/pypyjs/lib_pypy/hello_world.py'

        #form_classes = [TestForm1]
        #view.get_default_module_form_classes = Mock(return_value=form_classes)
        #view.write_program_to_virtual_file_system = Mock()

        js.return_get_element_by_id = {'secondary-output': Mock()}

        old_python_module_dir = editor.python_module_dir
        with TemporaryDirectory() as temp_dir:
            assert os.path.isdir(temp_dir)
            editor.python_module_dir = temp_dir + '/'
            sys.path.append(editor.python_module_dir)
            mock_download_document_collection.assert_not_called()
            view.write_program_to_virtual_file_system()
            view.cleanup_project = Mock()
            view.save_project = Mock()
            view.run_project(Mock())
            assert view.program_is_running == False

            mock_download_document_collection.assert_called_once()
            assert sys.path[-1] == editor.python_module_dir
            sys.path.pop()
            assert sys.path[-1] != editor.python_module_dir
        editor.python_module_dir = old_python_module_dir

    def test_running_without_storage_program_doesnt_initialise_historygraph(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        mock_download_document_collection = Mock()
        monkeypatch.setattr(historygraphfrontend, 'download_document_collection', mock_download_document_collection)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()
        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
print('Hello folder i={}'.format(i))
"""
        editor.project = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30}]'),
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': True,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': [],
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }

        assert len(view.form_stack) == 0

        js.return_get_element_by_id = {'secondary-output': Mock()}

        old_python_module_dir = editor.python_module_dir
        with TemporaryDirectory() as temp_dir:
            assert os.path.isdir(temp_dir)
            editor.python_module_dir = temp_dir + '/'
            sys.path.append(editor.python_module_dir)
            mock_download_document_collection.assert_not_called()
            view.write_program_to_virtual_file_system()
            view.cleanup_project = Mock()
            view.save_project = Mock()
            view.run_project(Mock())
            assert view.program_is_running == False

            mock_download_document_collection.assert_not_called()
            assert sys.path[-1] == editor.python_module_dir
            sys.path.pop()
            assert sys.path[-1] != editor.python_module_dir
        editor.python_module_dir = old_python_module_dir

    def test_running_program_without_default_file_causes_an_error(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()
        view.mount_redraw = Mock()

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
print('Hello folder i={}'.format(i))
"""
        editor.project = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': json.loads('[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30, "visible": true}]'),
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': [],
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': [],
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }

        assert len(view.form_stack) == 0

        class TestForm1(Form):
            file_location = '/lib/pypyjs/lib_pypy/hello_world.py'

        form_classes = [TestForm1]
        view.get_default_module_form_classes = Mock(return_value=form_classes)
        view.write_program_to_virtual_file_system = Mock()
        editor.js.globals.window.alert = Mock()
        js.return_get_element_by_id = {'secondary-output': Mock()}

        view.cleanup_project = Mock()
        view.save_project = Mock()
        view.run_project(Mock())
        assert view.program_is_running == True


        editor.js.globals.window.alert.assert_called_with('Error: You must select one of the files as the default to run')

        #assert len(view.form_stack) == 1
        #assert isinstance(view.form_stack[-1].button1, dict)

    def test_context_menu_can_change_preloaded_image_parameter(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)
        #monkeypatch.setattr(binarycrate.controls.codemirror, 'js', js)

        callbacks.initialise_global_callbacks()
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        js.return_get_elements_by_class_name = {'CodeMirror': Mock(length=0)}
        js.return_get_element_by_id = {'code': Mock()}
        codemirror.global_change_callback_handler = Mock()

        body = js.globals.document.body
        error_404_page = c("div", [c("p", "No match 404 error"),
                                   c("p", [c("a", {"href": "/#!"}, "Back to main page")])])
        view = editor.EditorView()
        r = Router({r'^$': view},
                    error_404_page, body)
        r.route()

        view.mount_redraw = Mock()


        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }

        response_images = [{'id': '4a88ff77-5969-40b8-a1da-8fefc5477f44', 'name': 'space-rocket.jpg'},
                           {'id': '4ee4576a-c5f8-450b-bf8f-3a77f87632f3', 'name': 'my-image.jpg'}]

        view.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)
        view.images_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response_images)),
                                              response_images)
        view.selected_de = [de for de in editor.project['directory_entry'] if de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'][0]

        view.mount_redraw = Mock()
        Router.router.ResetHashChange.reset_mock()
        view.contextmenu_preview(Mock(pageX=10, pageY=10))

        Router.router.ResetHashChange.reset_mock()
        view.mount_redraw.reset_mock()
        js.return_get_element_by_id = {'preview': Mock(getBoundingClientRect=Mock(return_value=Mock(left=0, top=0)))}
        view.new_image(Mock(clientX=10, clientY=20))

        virtual_dom = view._build_virtual_dom()

        def is_nvode_image(vnode):
            if hasattr(vnode, 'get_tag_name') is False:
                return None
            if vnode.get_tag_name() != 'img':
                return None
            #if vnode.get_attribs().get('type', '') != 'checkbox':
            #    return None
            #print('vnode called tag=input type=checkbox form_item=', vnode.get_attribs().get('form_item', ''))
            #if vnode.get_attribs().get('form_item', '') != 'True':
            #    return None
            return vnode

        vnode_image = get_matching_vnode(virtual_dom, lambda vnode: is_nvode_image(vnode))

        view.mount_redraw = Mock()
        Router.router.ResetHashChange.reset_mock()
        vnode_image.get_attribs()['oncontextmenu'](Mock())

        fill_index = 2
        #print('menu items=', [view.context_menu.menu_items[i][0] for i in range(len(view.context_menu.menu_items))])
        assert 'Change preloaded_image' ==  view.context_menu.menu_items[fill_index][0]
        assert callable(view.context_menu.menu_items[fill_index][1])
        view.mount_redraw.assert_called()
        Router.router.ResetHashChange.assert_called()
        view.context_menu.menu_items[fill_index][1](Mock())

        result = dict()
        result['available_images'] = []

        def mock_element_iterator_callback(vnode):
            #if hasattr(vnode, 'get_attribs'):
            #    print('mock_element_iterator_callback called vnodeid=', vnode.get_attribs().get('id'))
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'changePropertyPreloadedImage':
                #print('mock_element_iterator_callback changeBooleanProperty found')

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        #print('mock_element_iterator_callback2 vnode.tag=', vnode.tag)
                        #print('mock_element_iterator_callback2 vnode.get_attribs().get(\'id\')=', vnode.get_attribs().get('id'))
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['changePropertyPreloadedImage_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'select' and vnode.get_attribs().get('id') == "selChosenImage":
                            result['chosen_image'] = vnode.get_attribs().get('value', '')
                        if vnode.get_tag_name() == 'option':
                            result['available_images'] += [ vnode.get_children()[0].text ]
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        view.mount_redraw = Mock()

        virtual_node = view._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        assert result['chosen_image'] == ''
        assert result['available_images'] == ['(none)', 'space-rocket.jpg', 'my-image.jpg']

        # Call the modal handler
        rendered_modal = view._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'changePropertyPreloadedImage': rendered_modal}

        def setup_mock_modal_callback(node, choice):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'selChosenImage':
                #print('setup_mock_modal_callback setting selChosenImage=', choice)
                # Verify that the select element contains options from the server
                assert node.options.length == 3
                assert node.options.item(0).getAttribute('value') == ''
                assert node.options.item(0).children.item(0)._text == '(none)'
                assert node.options.item(1).getAttribute('value') == '4a88ff77-5969-40b8-a1da-8fefc5477f44'
                assert node.options.item(1).children.item(0)._text == 'space-rocket.jpg'
                assert node.options.item(2).getAttribute('value') == '4ee4576a-c5f8-450b-bf8f-3a77f87632f3'
                assert node.options.item(2).children.item(0)._text == 'my-image.jpg'
                node.value = choice

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, '4ee4576a-c5f8-450b-bf8f-3a77f87632f3'))

        result['changePropertyPreloadedImage_OK_handler'](Mock())

        rendered = view._build_virtual_dom()

        vnode_image = get_matching_vnode(rendered, lambda vnode: is_nvode_image(vnode))
        assert vnode_image.get_attribs()['preloaded_image'] == '4ee4576a-c5f8-450b-bf8f-3a77f87632f3'
        assert vnode_image.get_attribs()['src'] == '/images/images-4b352f3a-752f-4769-8537-880be4e99ce0/4ee4576a-c5f8-450b-bf8f-3a77f87632f3.jpg'

        vnode_image.get_attribs()['oncontextmenu'](Mock())
        fill_index = 2
        #print('menu items=', [view.context_menu.menu_items[i][0] for i in range(len(view.context_menu.menu_items))])
        assert 'Change preloaded_image' ==  view.context_menu.menu_items[fill_index][0]
        assert callable(view.context_menu.menu_items[fill_index][1])
        view.mount_redraw.assert_called()
        Router.router.ResetHashChange.assert_called()
        view.context_menu.menu_items[fill_index][1](Mock())

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, ''))

        result['changePropertyPreloadedImage_OK_handler'](Mock())

        rendered = view._build_virtual_dom()

        vnode_rect = get_matching_vnode(rendered, lambda vnode: is_nvode_image(vnode))
        assert vnode_rect.get_attribs()['preloaded_image'] == ''
        assert vnode_rect.get_attribs()['src'] == ''

class TestNewFileContentPythonProject(object):
    def test_new_file_standard_python(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        project_id = 'e1e37287-9127-46cb-bddb-4a1a825a5d8e'

        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(Router, 'router', Mock())
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        result = defaultdict(int)

        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }

        tree = node.get_project_tree()

        monkeypatch.setattr(node, 'mount_redraw', Mock())

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

        tree = node.get_project_tree()

        #root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        #root_folder = tree.get_children()[0]
        #folder = root_folder.get_children()[0]
        #return root_folder, root_folder.get_children()[1], folder, folder.get_children()[2].get_children()[0]

        """
        assert type(tree) == BCProjectTree
        #root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 2
        assert type(root_folder.folder_children[0]) == BCPFolder
        assert root_folder.folder_children[0].de['name'] == 'folder'
        #hello_world = root_folder.folder_children[1]
        assert type(hello_world) == BCPFile
        assert self.get_BCPFile_title(hello_world) == 'hello_world.py'
        #folder = root_folder.folder_children[0]
        #hello_folder = folder.folder_children[0]
        assert type(hello_folder) == BCPFile
        assert self.get_BCPFile_title(hello_folder) == 'hello_folder.py'

        assert root_folder.get_display_title() == '/'
        assert folder.get_display_title() == 'folder'
        """
        virtual_node = node._build_virtual_dom()
        #add_folder_link = get_matching_vnode(virtual_node, lambda vnode: get_vnode_by_css_class(vnode, 'fa fa-1x fa-folder-o'))

        editor.js.globals.window.alert = Mock()
        #hello_world.on_click(Mock())
        #add_folder_link.get_attribs()['onclick'](Mock())
        #node.display_new_file_modal(Mock())

        #editor.js.globals.window.alert.assert_called_with('Error: You must select a folder to insert this file in')

        editor.js.globals.window.alert = Mock()
        #root_folder.on_click(Mock())
        node.display_new_file_modal(Mock())

        editor.js.globals.window.alert.assert_not_called()

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'newFile':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['newFile_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtFileName":
                            node.value = ''
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        node.mount_redraw = Mock()

        virtual_node = node._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        # Call the modal handler
        rendered_modal = node._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'newFile': rendered_modal}

        def setup_mock_modal_callback(node, file_name):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtFileName':
                node.value = file_name

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'travel.py'))

        #print('test_editor result[newFile_OK_handler]=', result['newFile_OK_handler'])
        result['newFile_OK_handler'](Mock())

        assert len(node.get_project()['directory_entry']) == 5
        new_de = [de for de in node.get_project()['directory_entry'] if de['name'] == 'travel.py'][0]

        assert new_de['content'] == """from __future__ import unicode_literals, absolute_import, print_function
"""

    def test_new_file_graphical_python(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        project_id = 'e1e37287-9127-46cb-bddb-4a1a825a5d8e'

        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(Router, 'router', Mock())
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        result = defaultdict(int)

        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }

        tree = node.get_project_tree()

        monkeypatch.setattr(node, 'mount_redraw', Mock())

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 0,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

        tree = node.get_project_tree()

        #root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        #root_folder = tree.get_children()[0]
        #folder = root_folder.get_children()[0]
        #return root_folder, root_folder.get_children()[1], folder, folder.get_children()[2].get_children()[0]

        """
        assert type(tree) == BCProjectTree
        #root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 2
        assert type(root_folder.folder_children[0]) == BCPFolder
        assert root_folder.folder_children[0].de['name'] == 'folder'
        #hello_world = root_folder.folder_children[1]
        assert type(hello_world) == BCPFile
        assert self.get_BCPFile_title(hello_world) == 'hello_world.py'
        #folder = root_folder.folder_children[0]
        #hello_folder = folder.folder_children[0]
        assert type(hello_folder) == BCPFile
        assert self.get_BCPFile_title(hello_folder) == 'hello_folder.py'

        assert root_folder.get_display_title() == '/'
        assert folder.get_display_title() == 'folder'
        """
        virtual_node = node._build_virtual_dom()
        #add_folder_link = get_matching_vnode(virtual_node, lambda vnode: get_vnode_by_css_class(vnode, 'fa fa-1x fa-folder-o'))

        editor.js.globals.window.alert = Mock()
        #hello_world.on_click(Mock())
        #add_folder_link.get_attribs()['onclick'](Mock())
        #node.display_new_file_modal(Mock())

        #editor.js.globals.window.alert.assert_called_with('Error: You must select a folder to insert this file in')

        editor.js.globals.window.alert = Mock()
        #root_folder.on_click(Mock())
        node.display_new_file_modal(Mock())

        editor.js.globals.window.alert.assert_not_called()

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'newFile':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['newFile_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtFileName":
                            node.value = ''
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        node.mount_redraw = Mock()

        virtual_node = node._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        # Call the modal handler
        rendered_modal = node._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'newFile': rendered_modal}

        def setup_mock_modal_callback(node, file_name):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtFileName':
                node.value = file_name
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'selFileType':
                node.value = 'graphical-py-file'

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'travel.py'))

        #print('test_editor result[newFile_OK_handler]=', result['newFile_OK_handler'])
        result['newFile_OK_handler'](Mock())

        assert len(node.get_project()['directory_entry']) == 5
        new_de = [de for de in node.get_project()['directory_entry'] if de['name'] == 'travel.py'][0]

        print(new_de['content'])
        assert new_de['content'] == """from __future__ import unicode_literals, absolute_import, print_function
from binarycrate.controls import Form

class Travel(Form):
    file_location = __file__
"""

    def test_new_file_graphical_python_historygraph(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        project_id = 'e1e37287-9127-46cb-bddb-4a1a825a5d8e'

        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(callbacks, 'js', js)
        monkeypatch.setattr(ajaxget, 'js', js)
        monkeypatch.setattr(ajaxget, 'get_uuid', dummy_uuid)
        monkeypatch.setattr(timeouts, 'js', js)
        monkeypatch.setattr(Router, 'router', Mock())
        monkeypatch.setattr(codemirror, 'js', js)
        monkeypatch.setattr(cavorite.bootstrap.modals, 'js', js)
        monkeypatch.setattr(cavorite.svg, 'js', js)
        monkeypatch.setattr(binarycrate.frontend_utils, 'js', js)
        callbacks.initialise_global_callbacks()
        ajaxget.initialise_ajaxget_callbacks()
        timeouts.initialise_timeout_callbacks()

        result = defaultdict(int)

        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }

        tree = node.get_project_tree()

        monkeypatch.setattr(node, 'mount_redraw', Mock())

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0',
                    'name': 'Mark\'s Project',
                    'type': 2,
                    'public': True,
                    'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'name': '',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[]',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': False,
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

        tree = node.get_project_tree()

        #root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
        #root_folder = tree.get_children()[0]
        #folder = root_folder.get_children()[0]
        #return root_folder, root_folder.get_children()[1], folder, folder.get_children()[2].get_children()[0]

        """
        assert type(tree) == BCProjectTree
        #root_folder = tree.get_children()[0]
        assert type(root_folder) == BCPFolder
        assert root_folder.get_is_checked()
        assert len(root_folder.folder_children) == 2
        assert type(root_folder.folder_children[0]) == BCPFolder
        assert root_folder.folder_children[0].de['name'] == 'folder'
        #hello_world = root_folder.folder_children[1]
        assert type(hello_world) == BCPFile
        assert self.get_BCPFile_title(hello_world) == 'hello_world.py'
        #folder = root_folder.folder_children[0]
        #hello_folder = folder.folder_children[0]
        assert type(hello_folder) == BCPFile
        assert self.get_BCPFile_title(hello_folder) == 'hello_folder.py'

        assert root_folder.get_display_title() == '/'
        assert folder.get_display_title() == 'folder'
        """
        virtual_node = node._build_virtual_dom()
        #add_folder_link = get_matching_vnode(virtual_node, lambda vnode: get_vnode_by_css_class(vnode, 'fa fa-1x fa-folder-o'))

        editor.js.globals.window.alert = Mock()
        #hello_world.on_click(Mock())
        #add_folder_link.get_attribs()['onclick'](Mock())
        #node.display_new_file_modal(Mock())

        #editor.js.globals.window.alert.assert_called_with('Error: You must select a folder to insert this file in')

        editor.js.globals.window.alert = Mock()
        #root_folder.on_click(Mock())
        node.display_new_file_modal(Mock())

        editor.js.globals.window.alert.assert_not_called()

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'newFile':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'get_tag_name'):
                        if vnode.get_tag_name() == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['newFile_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.get_tag_name() == 'input' and vnode.get_attribs().get('id') == "txtFileName":
                            node.value = ''
                IterateVirtualDOM(vnode, mock_element_iterator_callback2)

        node.mount_redraw = Mock()

        virtual_node = node._build_virtual_dom()
        IterateVirtualDOM(virtual_node, mock_element_iterator_callback)

        # Call the modal handler
        rendered_modal = node._render(None)
        cavorite.bootstrap.modals.js.return_get_element_by_id = {'newFile': rendered_modal}

        def setup_mock_modal_callback(node, file_name):
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'txtFileName':
                node.value = file_name
            if isinstance(node, js.MockElement) and node.getAttribute('id') == 'selFileType':
                node.value = 'graphical-py-file'

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'travel.py'))

        #print('test_editor result[newFile_OK_handler]=', result['newFile_OK_handler'])
        result['newFile_OK_handler'](Mock())

        assert len(node.get_project()['directory_entry']) == 5
        new_de = [de for de in node.get_project()['directory_entry'] if de['name'] == 'travel.py'][0]

        print(new_de['content'])
        assert new_de['content'] == """from __future__ import unicode_literals, absolute_import, print_function
from binarycrate.controls import Form
from binarycrate.historygraphfrontend import documentcollection as dc

class Travel(Form):
    file_location = __file__
"""
