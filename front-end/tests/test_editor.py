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
from binarycrate.controls import codemirror

class TestEditor(object):
    def test_editor_displays_folder_structure(self, monkeypatch):
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

        js.globals.cavorite_ajaxGet.assert_called_with('/api/projects/' + project_id, str(dummy_uuid()))


        #assert False
        #pass

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
                        'parent_id': None
                       },
                       # A file in the root directory
                       {'id': 'ae935c72-cf56-48ed-ab35-575cb9a983ea',
                        'name': 'hello_world.py',
                        'is_file': True,
                        'content': hello_world_content,
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054'
                       },
                       # A folder in the root directory
                       {'id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01',
                        'name': 'folder',
                        'is_file': False, 
                        'content': '', 
                        'parent_id': 'df6b6e0f-f796-40f3-9b97-df7a20899054'
                       },
                       # A file in the 'folder' folder
                       {'id': '6a05e63e-6db4-4898-a3eb-2aad50dd5f9a',
                        'name': 'hello_folder.py',
                        'is_file': True,
                        'content': hello_folder_content,
                        'parent_id': 'c1a4bc81-1ade-4c55-b457-81e59b785b01'
                       },
                     ]
                    }
        node.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)

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

        def get_tree_important_nodes(tree):
            # This function exists because we want to get the versions of nodes after a mount_redraw
            root_folder = tree.get_children()
            folder = root_folder[0]
            return root_folder, root_folder[1], folder, folder.get_children()[2].get_children()[0]

        root_folder, hello_world, folder, hello_folder = get_tree_important_nodes(tree)

        assert type(tree) == BCProjectTree
        #root_folder = tree.get_children()
        assert len(root_folder) == 2
        assert type(root_folder[0]) == BCPFolder
        assert root_folder[0].de['name'] == 'folder'
        #hello_world = root_folder[1]
        assert type(hello_world) == BCPFile
        assert get_BCPFile_title(hello_world) == 'hello_world.py'
        #folder = root_folder[0]
        #hello_folder = folder.get_children()[2].get_children()[0]
        assert type(hello_folder) == BCPFile
        assert get_BCPFile_title(hello_folder) == 'hello_folder.py'

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

        # Click folder doesn't update the text
        node.code_mirror.editor = Mock(setValue=Mock())
        folder.on_click(None)
        assert node.code_mirror.editor.setValue.call_count == 0
        assert len(node.code_mirror.get_children()) == 1
        assert type(node.code_mirror.get_children()[0]) == t
        assert node.code_mirror.get_children()[0].text() == hello_world_content
        folder.on_click(None)

        node.code_mirror.editor = Mock(setValue=Mock())
        hello_folder.on_click(None)
        #node.code_mirror.editor.setValue.assert_called_with(hello_folder_content)

        assert len(node.code_mirror.get_children()) == 1
        assert type(node.code_mirror.get_children()[0]) == t
        assert node.code_mirror.get_children()[0].text() == hello_folder_content

        hello_world.on_click(None)
        # Click on hello_world and check that the UI updates correctly
        root_folder, hello_world, folder, hello_folder = get_tree_important_nodes(tree)
        assert node.selected_de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'
        assert 'file-active' in hello_world.get_attribs().get('class', '')
        a_hello_world = hello_world.get_children()[0]
        assert a_hello_world.tag == 'a'
        assert 'file-active' in a_hello_world.get_attribs().get('class', '')
        label_folder = folder.get_children()[0]
        assert label_folder.tag == 'label'
        assert 'file-active' not in label_folder.get_attribs().get('class', '')
        checkbox_folder = folder.get_children()[1]
        assert checkbox_folder.tag == 'input'
        assert 'checked' not in checkbox_folder.get_attribs()

        folder.on_click(None)
        # Click on folder and check that the UI updates correctly
        tree = node.get_project_tree()
        root_folder, hello_world, folder, hello_folder = get_tree_important_nodes(tree)
        assert node.selected_de['id'] == 'c1a4bc81-1ade-4c55-b457-81e59b785b01'
        assert 'file-active' not in hello_world.get_attribs().get('class', '')
        a_hello_world = hello_world.get_children()[0]
        assert a_hello_world.tag == 'a'
        assert 'file-active' not in a_hello_world.get_attribs().get('class', '')
        label_folder = folder.get_children()[0]
        assert label_folder.tag == 'label'
        assert 'file-active' in label_folder.get_attribs().get('class', '')
        checkbox_folder = folder.get_children()[1]
        assert checkbox_folder.tag == 'input'
        assert 'checked' in checkbox_folder.get_attribs()
        
        hello_world.on_click(None)
        # Click on hello_world and check that the UI updates correctly That is the selected changes but not the fact that folder is checked (ie folded out)
        root_folder, hello_world, folder, hello_folder = get_tree_important_nodes(tree)
        assert node.selected_de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'
        assert 'file-active' in hello_world.get_attribs().get('class', '')
        a_hello_world = hello_world.get_children()[0]
        assert a_hello_world.tag == 'a'
        assert 'file-active' in a_hello_world.get_attribs().get('class', '')
        label_folder = folder.get_children()[0]
        assert label_folder.tag == 'label'
        assert 'file-active' not in label_folder.get_attribs().get('class', '')
        checkbox_folder = folder.get_children()[1]
        assert checkbox_folder.tag == 'input'
        assert 'checked' in checkbox_folder.get_attribs()

        js.return_get_element_by_id = {'preview': Mock()}

        hello_world2_content = "print('Hello world2')"
        mock_code_mirrow_get_value = Mock(side_effect=lambda: hello_world2_content)
        node.code_mirror.editor = Mock(getValue=mock_code_mirrow_get_value)

        #editor.code_mirror_changed = Mock()

        node.code_mirror.onchange_codemirror(None)
        #editor.code_mirror_changed.assert_called_with(hello_world2_content)
        assert node.selected_file_de['content'] == hello_world2_content

        editor.save_project(None)
        calls = [(a[0][0], a[0][2]) for a in js.globals.cavorite_ajaxPut.call_args_list]

        assert len(calls) == len(editor.project['directory_entry']) - 1 # We don't send the root folder
        was_found = False
        for url, data in calls:
            if url == '/api/projects/directoryentry/ae935c72-cf56-48ed-ab35-575cb9a983ea/':
                assert data == {'id': node.selected_de['id'],
                                 'name': node.selected_de['name'],
                                 'is_file': node.selected_de['is_file'],
                                 'content': node.selected_de['content'],
                                 'parent_id': node.selected_de['parent_id'],
                                }
                was_found = True

        assert was_found


        
