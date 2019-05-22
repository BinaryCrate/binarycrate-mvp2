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

# This file contains tests to test the integration with redbaron

from __future__ import absolute_import, print_function, unicode_literals
from binarycrate import editor
import cavorite_tests.fakejs as js
from cavorite import callbacks, ajaxget, timeouts, Router, t, c
from mock import Mock
from binarycrate.controls import codemirror
from collections import defaultdict
from binarycrate.editor import BCProjectTree, BCPFolder, BCPFile
import uuid
import json
from .utils import get_tree_important_nodes, get_BCPFile_title
import datetime


class TestEditorRedBaron(object):
    def test_waits_are_correct(self, monkeypatch):
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
        js.globals.document.program_output = js.MockJSArray()

        js.globals.cavorite_ajaxGet = Mock()

        result = defaultdict(int)

        editor.project.clear()
        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }
        # SImulate the first screen draw before there is anything loaded

        tree = node.get_project_tree()

        root_folder = tree.get_children()

        # Simulate the query which is sent after the screen is drawn
        node.query_project()

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
                        'form_properties': '{}',
                        'parent_id': None,
                        'is_default': False,
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'form_items': '[]',
                        'form_properties': '{}',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False,
                        'content': '',
                        'form_items': '[]',
                        'form_properties': '{}',
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054',
                        'is_default': False,
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'form_items': '[{"width": 100, "name": "button1", "caption": "Button", "y": 100, "x": 100, "type": "button", "id": "236a5a73-0ffd-4329-95c0-9deaa95830f4", "height": 30}]',
                        'form_properties': '{"width": "200", "height": "400"}',
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'is_default': True,
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

        tree = node.get_project_tree()

        root_folder, hello_world, folder, hello_folder = get_tree_important_nodes(tree)

        node.code_mirror.editor = Mock(setValue=Mock())
        hello_world.on_click(None)

        js.return_get_element_by_id = {'preview': Mock(getBoundingClientRect=Mock(return_value=Mock(left=0, top=0)))}

        hello_world2_content = "print('Hello world2')"
        mock_code_mirror_get_value = Mock(side_effect=lambda: hello_world2_content)
        node.code_mirror.editor = Mock(getValue=mock_code_mirror_get_value)

        # Test that we call the query function
        node.query_file_functions = Mock()

        node.code_mirror.onchange_codemirror(None)
        node.query_file_functions.assert_called_once()

        hello_world2_content = "print('Hello world3')"
        # Test that we call the query function
        node.query_file_functions = Mock()

        node.code_mirror.onchange_codemirror(None)
        node.query_file_functions.assert_not_called()

        # Test that we call the query function if the last update was more than
        # 5 seconds ago
        hello_world2_content = "print('Hello world4')"
        node.last_file_method_cache_update = datetime.datetime.now() - \
            datetime.timedelta(0, 10)
        node.query_file_functions = Mock()

        node.code_mirror.onchange_codemirror(None)
        node.query_file_functions.assert_called_once()
