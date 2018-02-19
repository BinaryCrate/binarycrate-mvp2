# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from binarycrate import editor
import cavorite_tests.fakejs as js
from cavorite import callbacks, ajaxget, timeouts, Router, t, c
from collections import defaultdict
import uuid
from mock import Mock
import json
from binarycrate.editor import BCProjectTree, BCPFolder, BCPFile, ContextMenu
from binarycrate.controls import codemirror
from utils import IterateVirtualDOM, AnyVirtualDOM, get_matching_vnode, style_to_dict
import cavorite.bootstrap.modals


class TestEditor(object):
    def get_BCPFile_title(self, node):
        assert type(node) == BCPFile
        assert len(node.get_children()) == 1
        first_child = node.get_children()[0]
        assert first_child.tag.lower() == 'a'
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
        assert self.get_BCPFile_title(hello_folder) == 'hello_folder.py'

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
        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
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
        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
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
        root_folder, hello_world, folder, hello_folder = self.get_tree_important_nodes(tree)
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
                                 'form_items': list(),
                                }
                was_found = True

        assert was_found


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
        

        #node.add_new_folder_handler(Mock())

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'newFile':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'tag'):
                        if vnode.tag == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['newFile_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.tag == 'input' and vnode.get_attribs().get('id') == "txtFileName":
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

        js.IterateElements(rendered_modal, lambda node: setup_mock_modal_callback(node, 'hello_file.py'))

        #print('test_editor result[newFile_OK_handler]=', result['newFile_OK_handler'])
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
        

        #node.add_new_folder_handler(Mock())

        def mock_element_iterator_callback(vnode):
            if hasattr(vnode, 'get_attribs') and vnode.get_attribs().get('id') == 'newFolder':

                def mock_element_iterator_callback2(vnode):
                    if hasattr(vnode, 'tag'):
                        if vnode.tag == 'button' and vnode.get_attribs().get('class') == "btn btn-primary":
                            result['newFolder_OK_handler'] = vnode.get_attribs()['onclick']
                        if vnode.tag == 'input' and vnode.get_attribs().get('id') == "txtFolderName":
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
                    #print('setup_mock_modal_callback_was_added child=', str(child))
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
        

class TestContextMenu(object):
    def test_context_menu_appears(self, monkeypatch):
        monkeypatch.setattr(Router, 'ResetHashChange', Mock())
        monkeypatch.setattr(editor.cavorite, 'js', js)
        monkeypatch.setattr(editor, 'js', js)
        monkeypatch.setattr(timeouts, 'js', js)

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
        view.projects_api_ajax_result_handler(Mock(status=200, responseText=json.dumps(response)),
                                              response)
        view.selected_de = [de for de in editor.project['directory_entry'] if de['id'] == 'ae935c72-cf56-48ed-ab35-575cb9a983ea'][0]

        assert len(view.selected_de['form_items']) == 0

        view.mount_redraw = Mock()
        assert view.context_menu is None
        Router.router.ResetHashChange.reset_mock()
        view.contextmenu_preview(Mock(pageX=10, pageY=10))
        assert type(view.context_menu) == ContextMenu
        assert len(view.context_menu.menu_items) == 1
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
        assert button['y'] == 20
        assert button['width'] == 100
        assert button['height'] == 30
        assert button['caption'] == 'Button'
        assert button['name'] == 'button1'

        def is_nvode_button(vnode):
            if hasattr(vnode, 'tag') is False:
                return None
            if vnode.tag != 'button':
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
        preview_node.get_attribs()['onmousedown'](Mock())
        assert view.selected_item == ''
        
        vnode_button.get_attribs()['onmousedown'](Mock())
        assert view.selected_item == button['id']
        assert view.mouse_is_down == True
    
        # Lift the mouse button up and check we are still selected
        preview_node.get_attribs()['onmouseup'](Mock())
        assert view.selected_item == button['id']
        assert view.mouse_is_down == False

        # Click again
        vnode_button.get_attribs()['onmousedown'](Mock())
        assert view.selected_item == button['id']
        assert view.mouse_is_down == True

        #Move the mouse and check the button moves
        Router.router.global_mouse_x = 500
        Router.router.global_mouse_y = 500

        Router.router.on_body_mousemove(Mock(clientX=520, clientY=530))

        assert button['x'] == 30
        assert button['y'] == 50
        vnode_button = get_matching_vnode(view, is_nvode_button)
        assert style_to_dict(vnode_button.get_attribs()['style'])['left'] == str(button['x'])
        assert style_to_dict(vnode_button.get_attribs()['style'])['top'] == str(button['y'])

        # Check moving the mouse with nothing selected does nothing
        preview_node.get_attribs()['onmousedown'](Mock())
        assert view.selected_item == ''
        assert view.mouse_is_down == True

        Router.router.on_body_mousemove(Mock(clientX=550, clientY=550))

        assert button['x'] == 30
        assert button['y'] == 50
        vnode_button = get_matching_vnode(view, is_nvode_button)
        assert style_to_dict(vnode_button.get_attribs()['style'])['left'] == str(button['x'])
        assert style_to_dict(vnode_button.get_attribs()['style'])['top'] == str(button['y'])

