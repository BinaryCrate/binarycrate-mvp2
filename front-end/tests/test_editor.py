# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from binarycrate import editor
import cavorite_tests.fakejs as js
from cavorite import callbacks, ajaxget, timeouts, Router, t
from collections import defaultdict
import uuid
from mock import Mock
import json
from binarycrate.editor import BCProjectTree, BCPFolder, BCPFile


class TestEditor(object):
    def test_editor_displays_folder_structure(self, monkeypatch):
        def dummy_uuid():
            return uuid.UUID('d7114859-3a2f-4701-967a-fb66fd60b963')
        project_id = 'e1e37287-9127-46cb-bddb-4a1a825a5d8e'

        monkeypatch.setattr(editor.cavorite, 'js', js)
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
            pass
            #if isinstance(node, js.MockElement)  and node.tagName == 'div' and node.getAttribute('class') == 'wrimagecard-topimage_title':
            #    p_children = [c for c in node.children.l if c.tagName == 'p']
            #    assert len(p_children) == 1
            #    p = p_children[0]
            #    assert len(p.children.l) == 1
            #    text_node = p.children.item(0)
            #    assert isinstance(text_node, js.MockTextNode)
            #    if str(text_node) == 'Mark\'s Project':
            #        result['marks_project'] += 1
                

        node = editor.editor_view()
        node.url_kwargs = { 'project_id': project_id }
        # SImulate the first screen draw before there is anything loaded

        tree = node.get_project_tree()

        assert type(tree) == BCProjectTree
        root_folder = tree.get_children()
        assert len(root_folder) == 0

        # Simulate the query which is sent after the screen is drawn
        node.query_project()

        js.globals.cavorite_ajaxGet.assert_called_with('/api/projects/' + project_id, str(dummy_uuid()))


        #assert False
        #pass

        monkeypatch.setattr(node, 'mount_redraw', Mock())

        hello_world_content = "print('Hello world')"
        hello_folder_content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""

        response = {'id': '4b352f3a-752f-4769-8537-880be4e99ce0', 'name': 'Mark\'s Project', 'type': 0, 'public': True, 'directory_entry':
                     [
                       # Root directory
                       {'id': 'df6b6e0f-f796-40f3-9b97-df7a20899054', 'name': '', 'is_file': False, 'content': '', 'parent_id': None},
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea', 'name': 'hello_world.py', 'is_file': True, 'content': hello_world_content, 'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054'},
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01', 'name': 'folder', 'is_file': False, 'content': '', 'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054'},
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a', 'name': 'hello_folder.py', 'is_file': True, 'content': hello_folder_content, 'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01'},
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)), response)

        tree = node.get_project_tree()

        def get_BCPFile_title(node):
            assert type(node) == BCPFile
            assert len(node.get_children()) == 1
            first_child = node.get_children()[0]
            assert first_child.tag.lower() == 'a'
            assert len(first_child.get_children()) == 1
            text_node = first_child.get_children()[0]
            assert type(text_node) == t
            return text_node.text

        assert type(tree) == BCProjectTree
        root_folder = tree.get_children()
        assert len(root_folder) == 2
        assert type(root_folder[0]) == BCPFolder
        assert root_folder[0].title == 'folder'
        assert type(root_folder[1]) == BCPFile
        assert get_BCPFile_title(root_folder[1]) == 'hello_world.py'
        folder = root_folder[0]
        assert type(folder.get_children()[2].get_children()[0]) == BCPFile
        assert get_BCPFile_title(folder.get_children()[2].get_children()[0]) == 'hello_folder.py'


