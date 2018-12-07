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

from __future__ import unicode_literals, absolute_import, print_function
import cavorite
from cavorite import c, t, Router, callbacks, timeouts, get_current_hash, get_uuid
from cavorite.HTML import *

try:
    import js
except ImportError:
    js = None
import copy
from .controls import CodeMirrorHandlerVNode
import uuid
from .navigation import BCChrome, navitem
import cavorite.bootstrap.modals as modals
from cavorite.bootstrap.modals import ModalTrigger, Modal
from cavorite.ajaxget import ajaxget, ajaxput, ajaxdelete
import json
from operator import itemgetter
from collections import defaultdict
from cavorite.svg import svg
import re
import os
from binarycrate.controls import Form
import inspect
from binarycrate import historygraphfrontend
import binarycrate
from .urllib import urlencode
import bs4
from bs4 import BeautifulSoup
from .uploadmodal import UploadModal
from binarycrate.controls.bcform import get_form_item_property, FormItemPropType
from types import ModuleType
import sys
from binarycrate.controls import ContextMenu


HANDLE_NONE = 0
HANDLE_TOPLEFT = 1
HANDLE_TOPRIGHT = 2
HANDLE_BOTTOMRIGHT = 4
HANDLE_BOTTOMLEFT = 3

python_module_dir = '/lib/pypyjs/lib_pypy/'

project = {}

original_modules = set()

project_files = [] #All the project files we have written to the virtual file system

example_html = """<!doctype html>
<html>
  <head>
    <meta charset=utf-8>
    <title>HTML5 Demo</title>
    <style>p {font-family: monospace;}</style>
  </head>
  <body>
    <p>Canvas pane goes here:</p>
    <canvas id=pane width=300 height=200></canvas>
    <script>
      var canvas = document.getElementById('pane');
      var context = canvas.getContext('2d');
      context.fillStyle = 'rgb(250,0,0)';
      context.fillRect(10, 10, 55, 50);
      context.fillStyle = 'rgba(0, 0, 250, 0.5)';
      context.fillRect(30, 30, 55, 50);
    </script>
  </body>
</html>"""


def merge_dicts(d1, d2):
    ret = copy.copy(d1)
    ret.update(d2)
    return ret


class BCProjectTree(ol):
    def __init__(self, children):
        super(BCProjectTree, self).__init__({'class': 'tree'}, children)


class BCPFolder(li):
    def __init__(self, de, folder_children, editor_view):
        self.editor_view = editor_view
        self.de = de
        self.folder_children = folder_children
        self.id = str(uuid.uuid4())
        ##super(BCPFolder, self).__init__({'class': 'file-active'})
        super(BCPFolder, self).__init__()

    def get_is_checked(self):
        if self.de['parent_id'] is None:
            return True
        else:
            return self.editor_view.folder_state[self.de['id']]

    def get_display_title(self):
        return self.de['name'] if self.de['parent_id'] is not None else '/'

    def get_children(self):
        input_attribs = {'type': 'checkbox', 'id':self.id, 'onclick': self.on_click, 'oncontextmenu': self.on_contextmenu}
        label_attribs = {'for': self.id, 'oncontextmenu': self.on_contextmenu}
        if self.get_is_checked():
            input_attribs.update({'checked': 'checked'})
        if self.get_is_active():
            label_attribs.update({'class': 'file-active'})
        return [label(label_attribs, self.get_display_title()),
                html_input(input_attribs),
                ol(self.folder_children)]

    def get_is_active(self):
        return self.editor_view.selected_de == self.de

    def on_click(self, e):
        self.editor_view.folder_state[self.de['id']] = not self.editor_view.folder_state[self.de['id']]
        self.editor_view.selected_de = self.de
        self.editor_view.selected_file_de = None
        self.editor_view.selected_item = ''
        self.editor_view.mount_redraw()
        self.editor_view.update_html_preview()
        Router.router.ResetHashChange()

    def delete_file(self, e):
        print('delete_file called')
        #e.stopPropagation()
        #e.preventDefault()
        self.editor_view.delete_selected_de(e)

    def on_contextmenu(self, e):
        posx, posy = ContextMenu.xy_from_e(e)
        self.editor_view.context_menu = ContextMenu(self, posx, posy, (
                                        ('Delete Folder', self.delete_file),
                                        ))
        self.editor_view.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def close_context_menu(self, e):
        print("close_context_menu called")
        self.editor_view.context_menu = None
        self.editor_view.mount_redraw()
        Router.router.ResetHashChange()

class BCPFile(li):
    def __init__(self, de, code_mirror, editor_view):
        self.de = de
        self.code_mirror = code_mirror
        self.editor_view = editor_view
        super(BCPFile, self).__init__({'class': 'file'})

    def get_children(self):
        href = str(js.globals.window.location.href)
        if href.find('#') < 0:
            href = '#'
        a_attribs = {'href': href, 'onclick': self.on_click, 'oncontextmenu': self.on_contextmenu}
        if self.get_is_active():
            a_attribs.update({'class': 'file-active'})
        return [
            a(a_attribs, ('* ' if self.de['is_default'] else '') + self.de['name'])
        ]

    def get_attribs(self):
        ret = super(BCPFile, self).get_attribs()
        if self.get_is_active():
            ret.update({'class': 'file file-active'})
        return ret

    def get_is_active(self):
        return self.editor_view.selected_de == self.de

    def on_click(self, e):
        self.editor_view.selected_de = self.de
        self.editor_view.selected_file_de = self.de
        self.editor_view.selected_item = ''
        self.editor_view.mount_redraw()
        self.editor_view.update_html_preview()
        Router.router.ResetHashChange()

    def rename_file(self, e):
        print('rename_file called')
        #e.stopPropagation()
        #e.preventDefault()
        self.editor_view.context_menu = None
        self.editor_view.mount_redraw()
        Router.router.ResetHashChange()
        self.editor_view.display_rename_file_modal(e)

    def delete_file(self, e):
        print('delete_file called')
        #e.stopPropagation()
        #e.preventDefault()
        self.editor_view.delete_selected_de(e)

    def set_default(self, e):
        print('set_default called')
        #e.stopPropagation()
        #e.preventDefault()
        self.editor_view.set_current_file_as_default(e)

    def on_contextmenu(self, e):
        posx, posy = ContextMenu.xy_from_e(e)
        self.editor_view.context_menu = ContextMenu(self, posx, posy, (
                                        ('Rename File', self.rename_file),
                                        ('Delete File', self.delete_file),
                                        ('Set as Default', self.set_default),
                                        ))
        self.editor_view.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def close_context_menu(self, e):
        self.editor_view.context_menu = None
        self.editor_view.mount_redraw()
        Router.router.ResetHashChange()


def sub_menu_handler(e):
    jquery = js.globals['$']
    jquery(e.target).next('div').toggle();
    e.stopPropagation()
    e.preventDefault()


def drop_down_menu(title, members):
    return div({'class': "dropdown nav-item shapes__dropdown dropdown-menu-header"}, [
        html_button({'class': "btn dropdown-toggle crt-btn", 'type': "button", 'id': "dropdownMenuButton",
                     'data-toggle': "dropdown", 'aria-haspopup': "true", 'aria-expanded': "false"}, title),
        div({'class': "dropdown-menu", 'aria-labelledby': "dropdownMenuButton"}, members)
    ])


def drop_down_item(title, icon_class, click_handler):
    attribs = {'class': "dropdown-item", 'href': get_current_hash()}
    if click_handler is not None:
        attribs['onclick'] = click_handler
    else:
        def dummy_click_handler(e):
            e.stopPropagation()
            e.preventDefault()

        attribs['onclick'] = dummy_click_handler
    return a(attribs, [
        i({'class': "fa fa-1x " + icon_class, 'aria-hidden':"true"}),
        t(' ' + title),
    ])


def drop_down_submenu(title, icon_class, members):
    return div({'class': "dropdown-submenu"}, [
        a({'class': "dropdown-item", 'href': "#", 'onclick': sub_menu_handler}, [
            i({'class': "fa fa-1x " + icon_class, 'aria-hidden': "true"}),
            t(title),
        ]),
        div({'class': "dropdown-menu"}, members)
    ])


def test_click_handler(e):
    js.globals.window.alert('Hello click handler build number {}'.format(binarycrate.BUILD_NUMBER))
    e.stopPropagation()
    e.preventDefault()

class ContextMenuFormItems(nav):
    def __init__(self, posx, posy, menu_items, *args, **kwargs):
        self.menu_items = menu_items
        super(ContextMenuFormItems, self).__init__({'class': "context-menu", 'style': 'left: {}px; top:{}px'.format(posx, posy)}, *args, **kwargs)

    def get_children(self):
        menu_items = [
            li({'class': "context-menu__item"}, [
                a({'href': get_current_hash(), 'class': "context-menu__link", 'onclick': mi[1]}, [
                    # i({'class': 'fa fa-eye'}),
                    t(mi[0]),
                ]),
            ]) for mi in self.menu_items]

        return [
            ul({'class': 'context-menu__items'}, menu_items),
        ]


class EditorView(BCChrome):
    def save_project(self, e):
        print('save_project called')

        def dummy_put_result_handler(xmlhttp, response):
            self.save_progress -= 1

        def dummy_delete_result_handler(xmlhttp, response):
            self.save_progress -= 1

        for de in project['directory_entry']:
            if de['name'] != '':  # Don't try to save the root folder
                de_copy = copy.copy(de)
                #print('de_copy[form_items]=', de_copy['form_items'])
                de_copy['form_items'] = json.dumps(de_copy['form_items'])
                ajaxput('/api/projects/directoryentry/' + de['id'] + '/', de_copy, dummy_put_result_handler)
                self.save_progress += 1
        for de_id in project['deleted_directory_entries']:
            ajaxdelete('/api/projects/directoryentry/' + de_id + '/', dummy_delete_result_handler)
            self.save_progress += 1

    def delete_selected_de(self, e):
        if self.selected_de == None:
            return
        global project

        def get_items_to_delete(de, todelete):
            todelete.insert(0, de['id'])
            if de['is_file'] is False:
                for de2 in project['directory_entry']:
                    if de2['parent_id'] == de['id']:
                        get_items_to_delete(de2, todelete)

        items_to_delete = list()
        get_items_to_delete(self.selected_de, items_to_delete)
        project['directory_entry'] = [de for de in project['directory_entry'] if de['id'] not in items_to_delete]
        project['deleted_directory_entries'].extend(items_to_delete)
        self.selected_de = None
        self.mount_redraw()
        Router.router.ResetHashChange()

    def write_program_to_virtual_file_system(self, parent_id=None, extra_path=''):
        # print('write_program_to_virtual_file_system called')
        global project
        if parent_id is None:
            # print('write_program_to_virtual_file_system 1')
            de = [de for de in project['directory_entry'] if de['parent_id'] is None][0]
            self.write_program_to_virtual_file_system(de['id'])
        else:
            # print('write_program_to_virtual_file_system 2')
            des = [de for de in project['directory_entry'] if de['parent_id'] == parent_id]
            # print('write_program_to_virtual_file_system 3')
            for de in des:
                if de['is_file'] is False:
                    # print('write_program_to_virtual_file_system 4')
                    try:
                        os.stat(python_module_dir + extra_path + de['name'] + '/')
                    except:
                        os.mkdir(python_module_dir + extra_path + de['name'] + '/')
                    self.write_program_to_virtual_file_system(de['id'], extra_path + de['name'] + '/')
                    # print('write_program_to_virtual_file_system 5')
                else:
                    # print('write_program_to_virtual_file_system 6')
                    # print('write_program_to_virtual_file_system de[content]', de['content'])
                    # print('write_program_to_virtual_file_system type(de[content])', type(de['content']))
                    with open(python_module_dir + extra_path + de['name'], "w+") as fl:
                         fl.write(de['content'].encode('utf-8'))
                         global project_files
                         project_files.append(python_module_dir + extra_path + de['name'])
                    #print('write_program_to_virtual_file_system 7')

    def get_default_directory_entry(self):
        des = [de for de in project['directory_entry'] if de['is_default']]
        if len(des) == 0:
            return None
        else:
            return des[0]

    def get_default_module_form_classes(self):
        #TODO: There are no unit tests for inspecting the module and pulling out the forms please create
        def reload_recursively(mod):
            if not isinstance(mod, ModuleType):
                return
            #print('found mod= ', mod)
            #print('found dir(mod)= ', dir(mod))
            for mod2 in dir(mod):
                #print('mod2=', mod2)
                if mod2 not in sys.builtin_module_names and \
                   mod2 != '__builtin__'  and mod2 != '__builtins__':
                    reload_recursively(getattr(mod, mod2))
            #print('reloading mod= ', mod)
            reload(mod)

        #de = [de for de in project['directory_entry'] if de['is_default']][0]
        de = self.get_default_directory_entry()
        if de is None:
            return []
        if project['type'] == 2:
            documents_imported_module = __import__('documents') #TODO: Make it impossible to rename or delete the documents file from the root of the proejct
        file_name = de['name'][:de['name'].find('.')]
        imported_module = __import__(file_name)
        class_name = file_name[0].upper() + file_name[1:]
        if class_name in dir(imported_module):
            # First look for a class with the given name
            return [getattr(imported_module, class_name)]

        #print('EditorView run_project dir(imported_module)=', dir(imported_module))
        # If we don't have a class with a match name and there are only one class return it
        classes = [getattr(imported_module, name) for name in dir(imported_module)
                   if inspect.isclass(getattr(imported_module, name)) and
                     issubclass(getattr(imported_module, name), Form) and
                     getattr(imported_module, name) != Form]
        # This should be a user visible error message instead of this assertion which will just get buried
        assert len(classes) <= 1, "Only 1 Form class should exist in a module"
        return classes

    def on_historygraph_download_complete(self):
        for form in self.form_stack:
            form.on_historygraph_download_complete()
        self.mount_redraw()
        Router.router.ResetHashChange()

    def stop_project(self, e):
        print('EditorView stop_project called')
        self.program_is_running = False
        for form in self.form_stack:
            form.clear_all_active_timeouts()
            form.clear_all_active_intervals()
        self.form_stack = []
        js.globals.document.print_to_secondary_output = False
        self.cleanup_project()
        self.mount_redraw()
        Router.router.ResetHashChange()

    def cleanup_project(self):
        print('cleanup_project called')
        global project_files
        for f in project_files:
            os.remove(f)
        project_files = []

        global original_modules
        modules_to_remove = [module_name for module_name in sys.modules.keys() if module_name not in original_modules]
        for module_name in modules_to_remove:
            del sys.modules[module_name]
        import gc
        gc.collect()

    def run_project(self, e):
        print('EditorView run_project called')
        if self.get_default_directory_entry() is None:
            js.globals.window.alert('Error: You must select one of the files as the default to run')

        self.save_project(e)
        # Clear the program output area
        js.globals.document.getElementById('secondary-output').innerHTML = ''
        #print('EditorView run_project 0.9')
        try:
            self.program_is_running = True
            js.globals.document.print_to_secondary_output = True
            global project
            historygraphfrontend.initialise_document_collection(project['id'], self.on_historygraph_download_complete)
            #print('EditorView run_project 1')
            #historygraphfrontend.download_document_collection()
            self.write_program_to_virtual_file_system()
            #print('EditorView run_project 2')
            #print('EditorView run_project 3')
            form_classes = self.get_default_module_form_classes()
            print('EditorView run_project form_classes=', form_classes)
            if len(form_classes) > 0:
                print('EditorView run_project Found usable class name=' + form_classes[0].__name__)
                self.form_stack.append(form_classes[0](editorview=self))
                self.mount_redraw()
                Router.router.ResetHashChange()
            else:
                #print('EditorView run_project Found  no usable class')
                js.globals.document.print_to_secondary_output = False
                self.program_is_running = False
                self.cleanup_project()
            #aa.tr()
            #print('EditorView run_project called 4')
        except Exception as e:
            #TODO: There is no unit test for this please make one. This is to solve issue #M21-155 https://binarycrate.atlassian.net/browse/M21-155
            def finish_running():
                js.globals.document.print_to_secondary_output = False
                self.program_is_running = False
                self.cleanup_project()
            # Cleanup in the timeout because we need to be running when the exception is handled to print the output
            timeouts.set_timeout(finish_running, 1)
            raise

    def get_sidebar_nav_items(self):
        def dashboad_click_handler(e):
            if self.save_progress == 0:
                # If there is no running save process save the project
                self.save_project(e)


        if self.program_is_running:
            return []
        else:
            return [
                     navitem('Dashboard', 'fa-dashboard', '#!', onclick=dashboad_click_handler),
                   ]
            #return super(EditorView, self).get_sidebar_nav_items()

    def set_current_file_as_default(self, e):
        #print('set_current_file_as_default called')
        #from binarycrate.controls import Form
        #print('set_current_file_as_default Form=', Form)
        if self.selected_de:
            for de in project['directory_entry']:
                de['is_default'] = False
            self.selected_de['is_default'] = True
        self.mount_redraw()
        Router.router.ResetHashChange()

    def projects_api_ajax_result_handler(self, xmlhttp, response):
        #print('projects_api_ajax_result_handler called')
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            global project
            new_project = json.loads(str(xmlhttp.responseText))
            if project  != new_project:
                self.selected_de = None
                self.selected_file_de = None
                project = new_project
                project['deleted_directory_entries'] = list()
                for de in project['directory_entry']:
                    if de['form_items'] == '':
                        de['form_items'] = []
                    else:
                        de['form_items'] = json.loads(de['form_items'])
                        for fi in de['form_items']:
                            # Some of the form controls in the demo content don't have visibility set
                            if 'visible' not in fi:
                                fi['visible'] = True
                self.mount_redraw()
                Router.router.ResetHashChange()

    def mount(self, element):
        global project
        project = {}
        self.context_menu = None
        self.selected_de = None
        self.selected_file_de = None
        super(EditorView, self).mount(element)

    def get_project(self):
        return project

    def query_project(self):
        global project
        if len(project) == 0:
            # Only load the project if we don't alreayd have it
            def images_api_ajax_result_handler2(xmlhttp, response):
                # Get the images first then the projects
                #TODO: Do this all in one query. Otherwise it get brittle
                #print('images_api_ajax_result_handler2')
                #self.images_api_ajax_result_handler(xmlhttp, response)
                if xmlhttp.status >= 200 and xmlhttp.status <= 299:
                    self.images = json.loads(str(xmlhttp.responseText))
                    #self.mount_redraw()
                    #Router.router.ResetHashChange()
                    ajaxget('/api/projects/' + self.get_root().url_kwargs['project_id'] + '/', self.projects_api_ajax_result_handler)

            ajaxget('/api/projects/image-list/' + self.get_root().url_kwargs['project_id'] + '/', images_api_ajax_result_handler2)

    def was_mounted(self):
        #print('was_mounted called')
        super(EditorView, self).was_mounted()
        self.timeout_val = timeouts.set_timeout(lambda: self.query_project(), 1)

    def get_project_tree(self):
        def get_as_tree(parent_id):
            directory_entries = sorted([de for de in de_source if de['parent_id'] == parent_id], key=itemgetter('name'))
            ret = [BCPFile(de, self.code_mirror, self) if de['is_file'] else BCPFolder(de, get_as_tree(de['id']), self)
                   for de in directory_entries if de['parent_id'] == parent_id]
            return ret

        global project
        if project == {}:
            # If project not loaded yet
            return BCProjectTree([])
        else:
            de_source = project['directory_entry']

            return BCProjectTree(get_as_tree(None))

    def get_new_file_folder_icons(self):
        global project
        #There are no 'new file/folder' icons for html projects
        if project.get('type', None) == 1:
            return []
        else:
            return [
                a({'href': get_current_hash()}, [
                    span({'class': 'fa fa-1x fa-file-code-o', 'onclick': self.display_new_file_modal}),
                ]),
                a({'href': get_current_hash()}, [
                    span({'class': 'fa fa-1x fa-folder-o', 'onclick': self.display_new_folder_modal}),
                ]),
            ]

    def get_central_content(self):
        """
        return    c("div", {'class': "container-fluid code-area", 'style': 'padding-left: 1px; padding-top:1px height:100%;'}, [
                    div({'class': 'row row-wrapper'}, [
                      div({'class': "project-fnf col-ms-2"}, [
                        div({'class': 'top-tree'}, [
                          p({'style': 'display:inline'}, 'Files'),
                        ] + self.get_new_file_folder_icons()),
                        self.get_project_tree(),
                      ]),
                      article({'class': 'col-md-12 row', 'id': 'editor'}, [
                        self.code_mirror,
                        div({'class': 'row col-md-5 output-col'}, [
                          #iframe({'id': 'preview', 'class': 'col-12 code-output'}),
                          div({'id': 'preview', 'class': 'col-12 code-output', 'oncontextmenu': self.contextmenu_preview, 'style': 'padding-left: 0px', 'onmousedown': self.clear_selected_item, 'onmouseup': self.on_mouse_up}, self.get_selected_de_form_controls()),
                          div({'id': 'console', 'class': 'console-editor col-12'}, [
                            pre({'id': 'secondary-output', 'class': 'logMessage'}, [
                              #span('//: '),
                              #t('request sent'),
                            ]),
                          ]),
                        ]),
                      ]),
                    ]),
                  ] +
                  ([style('.CodeMirror { background-color: darkgrey;}')] if self.get_code_mirror_read_only() else []))
"""
        global project
        return c("div",
                 {'class': "container-fluid code-area", 'style': 'padding-left: 1px; padding-top:1px height:100%;'}, [
                     div({'class': 'row row-wrapper'}, [
                         div({'class': "project-fnf col-ms-2"}, [
                             div({'class': 'top-tree'}, [
                                 p({'style': 'display:inline'}, 'Files'),
                             ] + self.get_new_file_folder_icons()),
                             self.get_project_tree(),
                         ]),
                         article({'class': 'col-md-12 row', 'id': 'editor'}, [
                             self.code_mirror,
                             div({'class': 'row col-md-5 output-col'},
                                 (
                                     [
                                        # Generate iframe for webpage projects
                                        iframe({'id': 'preview', 'class': 'col-12 code-output'}),
                                     ]
                                 if (project.get('type', None) == 1) else
                                     [
                                        # Generate preview for python projects
                                        div({'id': 'preview', 'class': 'col-12 code-output',
                                        'oncontextmenu': self.contextmenu_preview, 'style': 'padding-left: 0px',
                                        'onmousedown': self.clear_selected_item, 'onmouseup': self.on_mouse_up},
                                        self.get_selected_de_form_controls()),
                                     ]
                                 ) +
                                 [
                                     div({'id': 'console', 'class': 'console-editor col-12'}, [
                                         pre({'id': 'secondary-output', 'class': 'logMessage'}, [
                                             # span('//: '),
                                             # t('request sent'),
                                         ]),
                                     ]),
                                 ])
                         ]),
                     ]),
                 ])

    def on_body_click(self, e):
        #print("on_body_click called self.context_menu=", self.context_menu)
        if self.program_is_running:
            #print('on_body_click called self.program_is_running')
            if self.form_stack[-1].on_body_click():
                #print('on_body_click redrawing screen')
                self.mount_redraw()
                Router.router.ResetHashChange()
        if self.context_menu is not None:
            self.context_menu = None
            self.mount_redraw()
            Router.router.ResetHashChange()

    def on_body_mousemove(self, e, change_x, change_y):
        change_x = int(change_x)
        change_y = int(change_y)
        if self.program_is_running:
            #print('on_body_mousemove self.program_is_running')
            posx = e.clientX
            posy = e.clientY
            rect = js.globals.document.getElementById('preview').getBoundingClientRect()
            if posx >= rect.left and posy >= rect.top and posx <= rect.right and posy <= rect.bottom:
                posx = posx - rect.left
                posy = posy - rect.top
                if self.form_stack[-1].on_body_mousemove(int(posx), int(posy)):
                    self.mount_redraw()
                    Router.router.ResetHashChange()
        if self.mouse_is_down and self.selected_item != '':
            fi = [fi for fi in self.selected_de['form_items'] if fi['id'] == self.selected_item][0]
            if fi['type'] == 'line':
                if self.selected_handler == HANDLE_NONE:
                    fi['x1'] += change_x
                    fi['y1'] += change_y
                    fi['x2'] += change_x
                    fi['y2'] += change_y
                elif self.selected_handler == HANDLE_TOPLEFT:
                    fi['x1'] += change_x
                    fi['y1'] += change_y
                elif self.selected_handler == HANDLE_TOPRIGHT:
                    fi['x2'] += change_x
                    fi['y1'] += change_y
                elif self.selected_handler == HANDLE_BOTTOMRIGHT:
                    fi['x2'] += change_x
                    fi['y2'] += change_y
                elif self.selected_handler == HANDLE_BOTTOMLEFT:
                    fi['x1'] += change_x
                    fi['y2'] += change_y
            else:
                if self.selected_handler == HANDLE_NONE:
                    fi['x'] += change_x
                    fi['y'] += change_y
                elif self.selected_handler == HANDLE_TOPLEFT:
                    fi['x'] += change_x
                    fi['y'] += change_y
                    fi['width'] -= change_x
                    fi['height'] -= change_y
                elif self.selected_handler == HANDLE_TOPRIGHT:
                    # fi['x'] += change_x
                    fi['y'] += change_y
                    fi['width'] += change_x
                    fi['height'] -= change_y
                elif self.selected_handler == HANDLE_BOTTOMRIGHT:
                    # fi['x'] += change_x
                    # fi['y'] += change_y
                    fi['width'] += change_x
                    fi['height'] += change_y
                elif self.selected_handler == HANDLE_BOTTOMLEFT:
                    fi['x'] += change_x
                    # fi['y'] += change_y
                    fi['width'] -= change_x
                    fi['height'] += change_y
            self.mount_redraw()
            Router.router.ResetHashChange()
            e.stopPropagation()
            e.preventDefault()
            # print('Mouse is down mousemove e=', change_x, ',', change_y)
        # Router.router.ResetHashChange()

    def get_context_menu(self):
        return self.context_menu

    def xy_from_e(self, e):
        #TODO: Shared code put in a library
        if e.pageX or e.pageY:
            posx = e.pageX
            posy = e.pageY
        elif e.clientX or e.clientY:
            posx = e.clientX + js.globals.document.body.scrollLeft + \
                   js.globals.document.documentElement.scrollLeft
            posy = e.clientY + js.globals.document.body.scrollTop + \
                   js.globals.document.documentElement.scrollTop
        return posx, posy

    def contextmenu_preview(self, e):
        posx, posy = self.xy_from_e(e)
        self.context_menu = ContextMenuFormItems(posx, posy, (
                                        ('New Button', self.new_button),
                                        ('New Textbox', self.new_textbox),
                                        ('New Image', self.new_image),
                                        ('New Label', self.new_label),
                                        ('New Frame', self.new_frame),
                                        ('New Checkbox', self.new_checkbox),
                                        #('New Listbox', self.new_listbox),
                                        ('New Rectangle', self.new_rectangle),
                                        ('New Circle', self.new_circle),
                                        ('New Ellipse', self.new_ellipse),
                                        ('New Line', self.new_line),
                                        ('New Hexagon', self.new_hexagon),
                                        ))
        self.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def select_new_item(self, form_item_id, e):
        #print('select_new_item mouse is down')
        self.selected_item = form_item_id
        if e.button == 0:
            self.mouse_is_down = True
            self.selected_handler = HANDLE_NONE
            # print('select_new_item mouse is down')
            self.selected_item = form_item_id
            self.mount_redraw()
            Router.router.ResetHashChange()
            e.stopPropagation()
            e.preventDefault()

    def on_mouse_up(self, e):
        # print('on_mouse_up mouse is up')
        self.mouse_is_down = False
        self.selected_handler = HANDLE_NONE

    def on_handle_mouse_down(self, e, handle):
        if e.button == 0:
            self.mouse_is_down = True
            self.selected_handler = handle
            # print('on_handle_house_down called handle=', handle)

    def delete_selected_form_item(self, form_item_id, e):
        self.selected_de['form_items'] = [form_item for form_item in self.selected_de['form_items'] if
                                          form_item_id != form_item['id']]
        self.selected_item = ''
        self.mount_redraw()
        Router.router.ResetHashChange()

    def display_new_file_modal(self, e):
        jquery = js.globals['$']
        jquery('#newFile').modal('show')
        e.stopPropagation()
        e.preventDefault()

    def display_share_project_modal(self, e):
        print("display_share_project_modal called")
        self.save_project(e)
        jquery = js.globals['$']
        jquery('#shareProj').modal('show')
        e.stopPropagation()
        e.preventDefault()

    def display_rename_file_modal(self, e):
        if self.selected_de is not None and self.selected_de['is_file'] == False:
            js.globals.window.alert('Error: File not selected')
            e.stopPropagation()
            e.preventDefault()
            return
        jquery = js.globals['$']
        jquery('#renameFile').modal('show')
        e.stopPropagation()
        e.preventDefault()

    def display_new_folder_modal(self, e):
        if self.selected_de is not None and self.selected_de['is_file']:
            js.globals.window.alert('Error: You must select a folder to insert this folder in')
            e.stopPropagation()
            e.preventDefault()
            return
        jquery = js.globals['$']
        jquery('#newFolder').modal('show')
        e.stopPropagation()
        e.preventDefault()

    def images_api_ajax_result_handler(self, xmlhttp, response):
        print('images_api_ajax_result_handle status=', xmlhttp.status)
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            self.images = json.loads(str(xmlhttp.responseText))
            self.mount_redraw()
            Router.router.ResetHashChange()

    def display_property_change_modal(self, e, form_item, prop_name):
        #print('display_property_change_modal called form_item[name]=', form_item['name'])
        #print('display_property_change_modal prop_name=', prop_name)
        #print('display_property_change_modal get_form_item_property(form_item[\'type\'])=', get_form_item_property(form_item['type']))
        self.current_prop_name = prop_name
        prop_type = get_form_item_property(form_item['type'])[prop_name]
        #print('display_property_change_modal prop_type=', prop_type)
        self.context_menu = None

        def display_modal():
            jquery = js.globals['$']
            if prop_type == FormItemPropType.BOOLEAN:
                jquery('#changePropertyBoolean').modal('show')
            elif prop_type == FormItemPropType.COLOR:
                jquery('#changePropertyColor').modal('show')
            elif prop_type == FormItemPropType.PRELOADED_IMAGE:
                jquery('#changePropertyPreloadedImage').modal('show')
            else:
                jquery('#changeProperty').modal('show')

        self.mount_redraw()
        Router.router.ResetHashChange()
        #e.stopPropagation()
        #e.preventDefault()
        #print('display_property_change_modal prop_type=', prop_type)

        def images_handler2(xmlhttp, response):
            print('images halndler2')
            #self.images_api_ajax_result_handler(xmlhttp, response)
            if xmlhttp.status >= 200 and xmlhttp.status <= 299:
                self.images = json.loads(str(xmlhttp.responseText))
                self.mount_redraw()
                Router.router.ResetHashChange()
                timeouts.set_timeout(display_modal, 1)

        if prop_type == FormItemPropType.PRELOADED_IMAGE:
            #ajaxget('/api/projects/image-list/' + project['id'] + '/', self.self.images_api_ajax_result_handler)
            ajaxget('/api/projects/image-list/' + project['id'] + '/', images_handler2)
        else:
            timeouts.set_timeout(display_modal, 1)


    def contextmenu_control(self, form_item_id, e):
        posx, posy = self.xy_from_e(e)
        form_item = [form_item for form_item in self.selected_de['form_items'] if form_item_id == form_item['id']][0]
        change_items = tuple(sorted([('Change {}'.format(prop_name),
                                      lambda e, prop_name=prop_name: self.display_property_change_modal(e, form_item,
                                                                                                        prop_name)) for
                                     prop_name in get_form_item_property(form_item['type'])],
                                    key=itemgetter(0)))
        self.context_menu = ContextMenuFormItems(posx, posy, change_items + (
                                        ('Delete', lambda e: self.delete_selected_form_item(form_item_id, e)),
                                        ))
        self.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def get_selected_de_form_controls(self):
        ret = list()
        if self.selected_de and not self.program_is_running:
            for form_item in self.selected_de['form_items']:
                # TODO: Copied code to studentform.py should be refactored

                if form_item['type'] == 'line':
                    style = ''.join(('position: absolute; ',
                                     'z-index: 1; ',
                                     'left: {};'.format(form_item['x1']),
                                     'top: {};'.format(form_item['y1']),
                                     'width: {};'.format(abs(form_item['x2'] - form_item['x1'])),
                                     'height: {};'.format(abs(form_item['y2'] - form_item['y1']))
                                     ))
                else:
                    style = ''.join(('position: absolute; ',
                                     'z-index: 1; ',
                                     'left: {};'.format(form_item['x']),
                                     'top: {};'.format(form_item['y']),
                                     'width: {};'.format(form_item['width']),
                                     'height: {};'.format(form_item['height'])
                                     ))
                # print('get_selected_de_form_controls form_item[id]=',form_item['id'])
                form_item_id = form_item['id']
                attribs = {'style': style, 'onmouseup': self.on_mouse_up,
                           'onmousedown': lambda e, form_item_id=form_item_id: self.select_new_item(form_item_id, e),
                           'oncontextmenu': lambda e, form_item_id=form_item_id: self.contextmenu_control(form_item_id,
                                                                                                          e)
                           }
                attribs_extra = {}
                control_class = None
                if form_item['type'] == 'button':
                    control_class = html_button
                    # control = html_button({'style': style, 'onmouseup': self.on_mouse_up, 'onmousedown': lambda e, form_item_id=form_item_id: self.select_new_item(form_item_id, e)}, form_item['caption'])
                elif form_item['type'] == 'textbox':
                    control_class = html_input
                    attribs_extra = {'type': "text"}
                    #control = html_input({'type': "text", 'style': style, 'onmouseup': self.on_mouse_up, 'onmousedown': lambda e, form_item_id=form_item_id: self.select_new_item(form_item_id, e)}, form_item['caption'])
                elif form_item['type'] == 'image':
                    control_class = img
                    preloaded_image = form_item['preloaded_image']
                    #print('get_selected_de_form_controls preloaded_image=', preloaded_image)
                    if preloaded_image == '':
                        attribs_extra = {'src': form_item['src'], 'preloaded_image': '' }
                    else:
                        image = filter(lambda image: image['id'] == preloaded_image, self.images)[0]
                        i = image['name'].rfind('.')
                        extension = image['name'][i:]
                        attribs_extra = {'src': '/images/images-{0}/{1}{2}'.format(project['id'],
                                         image['id'], extension),
                                         'preloaded_image': preloaded_image }
                elif form_item['type'] == 'label':
                    control_class = p
                    attribs_extra = { }
                elif form_item['type'] == 'frame':
                    control_class = div
                    #attribs_extra = {'s': "text"}
                elif form_item['type'] == 'checkbox':
                    control_class = html_input
                    attribs_extra = merge_dicts({'type': "checkbox", 'form_item': 'True'},
                                                {'checked': 'checked'} if form_item['value'] else {})
                elif form_item['type'] == 'select':
                    control_class = select
                    attribs_extra = { }
                attribs.update(attribs_extra)
                if control_class:
                    control = control_class(attribs, form_item.get('caption', ''))
                    ret.append(control)
            svg_list = list()
            for form_item in self.selected_de['form_items']:
                if form_item['type'] == 'rect':
                    svg_list.append(svg('rect', {'x': form_item['x'],
                                 'y':form_item['y'],
                                 'width': form_item['width'],
                                 'height': form_item['height'],
                                 'fill': form_item['fill'],
                                 'stroke-width':  form_item['stroke_width'],
                                 'stroke': form_item['stroke'],
                                 #'style':"fill:None;stroke-width:5;stroke:rgb(0,255,0)", 'onmouseup': self.on_mouse_up, 'onmousedown': lambda e, form_item_id=form_item['id']: self.select_new_item(form_item_id, e), 'oncontextmenu': lambda e, form_item_id=form_item['id']: self.contextmenu_control(form_item_id, e)}))
                                 'onmouseup': self.on_mouse_up,
                                 'onmousedown': lambda e, form_item_id=form_item['id']: self.select_new_item(form_item_id, e),
                                 'oncontextmenu': lambda e, form_item_id=form_item['id']: self.contextmenu_control(form_item_id, e)}))
                if form_item['type'] == 'circle':
                    svg_list.append(svg('circle', {'cx': form_item['x'] + form_item['width'] / 2,
                                 'cy':form_item['y'] + form_item['height'] / 2,
                                 'r': form_item['width'] / 2,
                                 #'height': form_item['height'],
                                 'fill': form_item['fill'],
                                 'stroke-width':  form_item['stroke_width'],
                                 'stroke': form_item['stroke'],
                                 #'style':"fill:None;stroke-width:5;stroke:rgb(0,255,0)",
                                 'onmouseup': self.on_mouse_up,
                                 'onmousedown': lambda e, form_item_id=form_item['id']: self.select_new_item(form_item_id, e),
                                 'oncontextmenu': lambda e, form_item_id=form_item['id']: self.contextmenu_control(form_item_id, e)}))
                if form_item['type'] == 'ellipse':
                    svg_list.append(svg('ellipse', {'cx': form_item['x'] + form_item['width'] / 2,
                                 'cy':form_item['y'] + form_item['height'] / 2,
                                 'rx': form_item['width'] / 2,
                                 'ry': form_item['height'] / 2,
                                 'fill': form_item['fill'],
                                 'stroke-width':  form_item['stroke_width'],
                                 'stroke': form_item['stroke'],
                                 #'style':"fill:None;stroke-width:5;stroke:rgb(0,255,0)",
                                 'onmouseup': self.on_mouse_up,
                                 'onmousedown': lambda e, form_item_id=form_item['id']: self.select_new_item(form_item_id, e),
                                 'oncontextmenu': lambda e, form_item_id=form_item['id']: self.contextmenu_control(form_item_id, e)}))
                if form_item['type'] == 'line':
                    svg_list.append(svg('line', {'x1': form_item['x1'],
                                 'y1':form_item['y1'],
                                 'x2': form_item['x2'],
                                 'y2': form_item['y2'],
                                 #'fill': form_item['fill'],
                                 'stroke-width':  form_item['stroke_width'],
                                 'stroke': form_item['stroke'],
                                 #'style':"fill:None;stroke-width:5;stroke:rgb(0,255,0)",
                                 'onmouseup': self.on_mouse_up,
                                 'onmousedown': lambda e, form_item_id=form_item['id']: self.select_new_item(form_item_id, e),
                                 'oncontextmenu': lambda e, form_item_id=form_item['id']: self.contextmenu_control(form_item_id, e)}))
                if form_item['type'] == 'hexagon':
                    # Draw a hexagon
                    x1 = form_item['x'] + form_item['width'] / 2
                    y1 = form_item['y']
                    x2 = form_item['x'] + form_item['width']
                    y2 = form_item['y'] + form_item['height'] / 4
                    x3 = form_item['x'] + form_item['width']
                    y3 = form_item['y'] + form_item['height'] * 3 / 4
                    x4 = form_item['x'] + form_item['width'] / 2
                    y4 = form_item['y'] + form_item['height']
                    x5 = form_item['x']
                    y5 = form_item['y'] + form_item['height'] * 3 / 4
                    x6 = form_item['x']
                    y6 = form_item['y'] + form_item['height'] / 4
                    points = '{},{} {},{} {},{} {},{} {},{} {},{}'.format(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6,
                                                                          y6)
                    svg_list.append(svg('polygon', {'points': points,
                                                    'fill': form_item['fill'],
                                                    'stroke-width': form_item['stroke_width'],
                                                    'stroke': form_item['stroke'],
                                                    'onmouseup': self.on_mouse_up,
                                                    'onmousedown': lambda e, form_item_id=form_item[
                                                        'id']: self.select_new_item(form_item_id, e),
                                                    'oncontextmenu': lambda e, form_item_id=form_item[
                                                        'id']: self.contextmenu_control(form_item_id, e)}))
            if self.selected_item != '':
                #print('self.selected_item=', self.selected_item)
                selected_form_item = \
                [form_item for form_item in self.selected_de['form_items'] if self.selected_item == form_item['id']][0]
                if selected_form_item['type'] == 'line':
                    selected_form_item_x = selected_form_item['x1']
                    selected_form_item_y = selected_form_item['y1']
                    selected_form_item_width = abs(selected_form_item['x2'] - selected_form_item['x1'])
                    selected_form_item_height = abs(selected_form_item['y2'] - selected_form_item['y1'])
                else:
                    selected_form_item_x = selected_form_item['x']
                    selected_form_item_y = selected_form_item['y']
                    selected_form_item_width = selected_form_item['width']
                    selected_form_item_height = selected_form_item['height']
                svg_list.extend([
                              svg('rect', {'x': selected_form_item_x,
                                           'y':selected_form_item_y,
                                           'width': selected_form_item_width,
                                           'height': selected_form_item_height,
                                           'style':"fill:None;stroke-width:5;stroke:rgb(255,0,0)",
                                           'onmouseup': self.on_mouse_up,
                                           'oncontextmenu': lambda e, form_item_id=selected_form_item['id']: self.contextmenu_control(form_item_id, e)}),
                              svg('rect', {'id': 'handle-top-left', 'x': selected_form_item_x - 5,
                                           'y':selected_form_item_y - 5,
                                           'width': 10,
                                           'height': 10,
                                           'style':"fill:rgb(255,0,0);stroke-width:5;stroke:rgb(255,0,0)",
                                           'onmousedown': lambda e: self.on_handle_mouse_down(e, HANDLE_TOPLEFT),
                                           'onmouseup': self.on_mouse_up,
                                           #'oncontextmenu': lambda e, form_item_id=selected_form_item['id']: self.contextmenu_control(form_item_id, e)
                                           }),
                              svg('rect', {'id': 'handle-top-right', 'x': selected_form_item_x + selected_form_item_width - 5,
                                           'y':selected_form_item_y - 5,
                                           'width': 10,
                                           'height': 10,
                                           'style':"fill:rgb(255,0,0);stroke-width:5;stroke:rgb(255,0,0)",
                                           'onmousedown': lambda e: self.on_handle_mouse_down(e, HANDLE_TOPRIGHT),
                                           'onmouseup': self.on_mouse_up,
                                           #'oncontextmenu': lambda e, form_item_id=selected_form_item['id']: self.contextmenu_control(form_item_id, e)
                                           }),
                              svg('rect', {'id': 'handle-bottom-right', 'x': selected_form_item_x + selected_form_item_width - 5,
                                           'y':selected_form_item_y + selected_form_item_height - 5,
                                           'width': 10,
                                           'height': 10,
                                           'style':"fill:rgb(255,0,0);stroke-width:5;stroke:rgb(255,0,0)",
                                           'onmousedown': lambda e: self.on_handle_mouse_down(e, HANDLE_BOTTOMRIGHT),
                                           'onmouseup': self.on_mouse_up,
                                           #'oncontextmenu': lambda e, form_item_id=selected_form_item['id']: self.contextmenu_control(form_item_id, e)
                                           }),
                              svg('rect', {'id': 'handle-bottom-left', 'x': selected_form_item_x - 5,
                                           'y':selected_form_item_y + selected_form_item_height - 5,
                                           'width': 10,
                                           'height': 10,
                                           'style':"fill:rgb(255,0,0);stroke-width:5;stroke:rgb(255,0,0)",
                                           'onmousedown': lambda e: self.on_handle_mouse_down(e, HANDLE_BOTTOMLEFT),
                                           'onmouseup': self.on_mouse_up,
                                           #'oncontextmenu': lambda e, form_item_id=selected_form_item['id']: self.contextmenu_control(form_item_id, e)
                                           }),
                            ])
            ret.append(svg('svg', {'id': 'preview-svg', 'height': '100%', 'width': '100%', 'oncontextmenu': self.contextmenu_preview, 'z-index':-5, 'onmousedown': self.clear_selected_item, 'onmouseup': self.on_mouse_up}, svg_list))
        if self.program_is_running and len(self.form_stack) > 0:
            #print('get_selected_de_form_controls getting form controls from from_stack')
            ret = self.form_stack[-1].get_form_control_elements()
            #print('get_selected_de_form_controls ret=', ret)
        return ret

    def clear_selected_item(self, e):
        # self.mouse_is_down = True
        # print('clear_selected_item called')
        if self.selected_item != '':
            self.selected_handler = HANDLE_NONE
            # print('clearing item')
            self.selected_item = ''
            self.mount_redraw()
            Router.router.ResetHashChange()
            e.stopPropagation()
            e.preventDefault()

    def new_control(self, e, control_dict):
        if not self.selected_de:
            return
        posx = e.clientX
        posy = e.clientY
        rect = js.globals.document.getElementById('preview').getBoundingClientRect()
        posx = posx - rect.left
        posy = posy - rect.top
        new_id = str(get_uuid())

        control_dict = copy.copy(control_dict)
        if control_dict['type'] != 'line':
            control_dict.update({'id': new_id,
                                 'x': int(posx),
                                 'y': int(posy),
                                 })
        self.selected_de['form_items'].append(control_dict)
        self.selected_item = new_id

        self.context_menu = None
        self.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def get_next_name(self, prefix):
        s = {fi['name'][len(prefix):] for fi in self.selected_de['form_items'] if fi['name'].startswith(prefix)}
        s = [int(num) for num in s if num.isdigit()]
        s = sorted(s)
        if len(s) == 0:
            return '{}1'.format(prefix)
        else:
            return '{}{}'.format(prefix, str(s[-1] + 1))

    def new_button(self, e):
        self.new_control(e,
            {'type': 'button',
             'width': 100,
             'height': 30,
             'caption': 'Button',
             'visible': True,
             'name': self.get_next_name('button'),
            })

    def new_textbox(self, e):
       self.new_control(e,
            {'type': 'textbox',
             'width': 150,
             'height': 30,
             'visible': True,
             'name': self.get_next_name('textbox'),
            })

    def new_image(self, e):
       self.new_control(e,
            {'type': 'image',
             'width': 200,
             'height': 200,
             'name': self.get_next_name('image'),
             'src': '',
             'preloaded_image': '',
             'visible': True,
            })

    def new_label(self, e):
       self.new_control(e,
            {'type': 'label',
             'width': 150,
             'height': 30,
             'caption': 'Label',
             'name': self.get_next_name('label'),
             'visible': True,
            })

    def new_frame(self, e):
       self.new_control(e,
            {'type': 'frame',
             'width': 300,
             'height': 300,
             'caption': 'Frame',
             'name': self.get_next_name('frame'),
             'visible': True,
            })

    def new_checkbox(self, e):
       self.new_control(e,
            {'type': 'checkbox',
             'width': 150,
             'height': 30,
             'caption': 'Checkbox',
             'name': self.get_next_name('checkbox'),
             'value': False,
             'visible': True,
            })

    def new_listbox(self, e):
       self.new_control(e,
            {'type': 'listbox',
             'width': 150,
             'height': 150,
             'name': self.get_next_name('listbox'),
             'visible': True,
            })

    def new_rectangle(self, e):
       self.new_control(e,
            {'type': 'rect',
             'width': 150,
             'height': 150,
             'name': self.get_next_name('rect'),
             'stroke_width': 5,
             'stroke': 'rgb(0,0,0)',
             'fill': 'none',
             'visible': True,
            })

    def new_circle(self, e):
       self.new_control(e,
            {'type': 'circle',
             'width': 150,
             'height': 150,
             'name': self.get_next_name('circle'),
             'stroke_width': 5,
             'stroke': 'rgb(0,0,0)',
             'fill': 'none',
             'visible': True,
            })

    def new_ellipse(self, e):
       self.new_control(e,
            {'type': 'ellipse',
             'width': 150,
             'height': 150,
             'name': self.get_next_name('ellipse'),
             'stroke_width': 5,
             'stroke': 'rgb(0,0,0)',
             'fill': 'none',
             'visible': True,
            })

    def new_line(self, e):
        if not self.selected_de:
            return
        posx = e.clientX
        posy = e.clientY
        rect = js.globals.document.getElementById('preview').getBoundingClientRect()
        posx = posx - rect.left
        posy = posy - rect.top
        new_id = str(get_uuid())

        control_dict = {'type': 'line',
         'id': new_id,
         'x1': int(posx),
         'y1': int(posy),
         'x2': int(posx) + 50,
         'y2': int(posy) + 50,
         'name': self.get_next_name('line'),
         'stroke_width': 5,
         'stroke': 'rgb(0,0,0)',
         'visible': True,
        }
        self.selected_de['form_items'].append(control_dict)
        self.selected_item = new_id

        self.context_menu = None
        self.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def new_hexagon(self, e):
       self.new_control(e,
            {'type': 'hexagon',
             'width': 150,
             'height': 150,
             'name': self.get_next_name('hexagon'),
             'stroke_width': 5,
             'stroke': 'rgb(0,0,0)',
             'fill': 'none',
             'visible': True,
            })

    def get_selected_de_content(self):
        if self.selected_file_de is None:
            ret = ''
        else:
            ret = self.selected_file_de['content']
        #print('get_selected_de_content ret=', ret)
        return ret

    def get_selected_file_de(self):
        if self.selected_file_de is None:
            return ''
        else:
            return self.selected_file_de['id']

    def get_file_name_content(self, file_name):
        global project
        content = [de['content'] for de in project['directory_entry'] if de['name'] == file_name]
        return content[0]

    def beautiful_soup(self):
        global project
        # Get the content of index.html
        html_content = self.get_file_name_content("index.html")
        html_soup = BeautifulSoup(html_content)  # Creates a html soup out of index.html content
        if html_soup.find('head') is not None:
            # If index.html contains <head> insert <styles> and <scripts> in between
            head = html_soup.head
            if html_soup.find('style') is None:
                style_tag = html_soup.new_tag("style")  # Creates a styles tag
                head.append(style_tag)
            if html_soup.find('script') is None:
                script_tag = html_soup.new_tag("script")  # Creates a script tag
                head.append(script_tag)

            # Insert styles.css into <style> tag
            styles_content = self.get_file_name_content("styles.css")
            if html_soup.find_all('style') != []:   #if a <style> tag exists insert styles.css content inside
                html_soup.style.string = styles_content

            # Insert scripts.js into <script> tag
            scripts_content = self.get_file_name_content("scripts.js")
            if html_soup.find_all('script') != []:  #if a <script> tag exists insert scripts.js content inside
                html_soup.script.string = scripts_content

        return str(html_soup)

    def update_html_preview(self):
        if project.get('type', None) == 1:
            pretty_html = self.beautiful_soup()
            previewFrame = js.globals.document.getElementById('preview');
            preview = previewFrame.contentDocument or previewFrame.contentWindow.document;
            preview.open();
            preview.write(pretty_html);
            preview.close();
            print("update_html_preview called")

    def code_mirror_change(self, content):
        global project
        # print('code_mirror_change called')
        if self.selected_file_de is not None:
            if self.selected_file_de['content'] != str(content):
                self.selected_file_de['content'] = str(content)
                # self.mount_redraw()
                # Router.router.ResetHashChange()

        #Update iframe if html project
        self.update_html_preview()

    def newFile_ok(self, e, form_values):
        root_folder = [de for de in project['directory_entry'] if de['parent_id'] is None][0]
        parent_de = root_folder if self.selected_de is None else self.selected_de
        if parent_de['is_file']:
            parent_de = [de for de in project['directory_entry'] if de['id'] == parent_de['parent_id']][0]
        file_name = str(form_values['txtFileName'])
        if file_name[-3:].lower() != '.py':
            js.globals.window.alert('Error: python files must end with .py')
            return
        class_name = file_name[:file_name.find('.')]
        class_name = class_name[0].upper() + class_name[1:]
        content = 'from __future__ import unicode_literals, absolute_import, print_function\n'
        print("""str(form_values['selFileType'])=""", str(form_values['selFileType']))
        if str(form_values['selFileType']) == 'graphical-py-file':
            content += """from binarycrate.controls import Form
""" + ('from binarycrate.historygraphfrontend.documentcollection import dc\n' if project['type'] == 2 else '' ) + """
class """ + class_name + """(Form):
    file_location = __file__
"""
        new_de = {'id': str(uuid.uuid4()),
                   'name': file_name,
                   'content': content,
                   'is_file': True,
                   'form_items': [],
                   'parent_id': parent_de['id'],
                   'is_default': False,
                  }
        project['directory_entry'].append(new_de)
        self.selected_de = new_de
        self.selected_file_de = new_de
        self.mount_redraw()
        Router.router.ResetHashChange()

    def renameFile_ok(self, e, form_values):
        print('renameFile_ok called')
        file_name = str(form_values['txtFileName'])
        self.selected_de['name'] = file_name
        self.mount_redraw()
        Router.router.ResetHashChange()

    def newFolder_ok(self, e, form_values):
        root_folder = [de for de in project['directory_entry'] if de['parent_id'] is None][0]
        parent_de = root_folder if self.selected_de is None else self.selected_de
        new_de = {'id': str(uuid.uuid4()),
                   'name': str(form_values['txtFolderName']),
                   'content': '',
                   'is_file': False,
                   'form_items': [],
                   'parent_id': parent_de['id'],
                   'is_default': False,
                  }
        project['directory_entry'].append(new_de)
        self.mount_redraw()
        Router.router.ResetHashChange()

    def changeProperty_ok(self, e, form_values):
        # print('changeProperty_ok called')
        fi = [fi for fi in self.selected_de['form_items'] if fi['id'] == self.selected_item][0]
        #print('changeProperty_ok called fi[type]=', fi['type'], ', self.current_prop_name=', self.current_prop_name)
        #print('changeProperty_ok form_values=', form_values)
        #print('changeProperty_ok called self.current_prop_name=', self.current_prop_name)
        #print('changeProperty_ok called FormItemPropType=', get_form_item_property(fi['type'])[self.current_prop_name])
        if self.current_prop_name == 'name':
            matches = [fi for fi in self.selected_de['form_items'] if
                       fi['id'] != self.selected_item and fi['name'] == str(form_values['txtValue'])]
            if len(matches) > 0:
                js.globals.window.alert('Error: Another control with that name already exists')
                self.mount_redraw()
                Router.router.ResetHashChange()
                return
        if get_form_item_property(fi['type'])[self.current_prop_name] == FormItemPropType.INT:
            value = int(form_values['txtValue'])
        elif get_form_item_property(fi['type'])[self.current_prop_name] == FormItemPropType.STRING:
            value = str(form_values['txtValue'])
        elif get_form_item_property(fi['type'])[self.current_prop_name] == FormItemPropType.BOOLEAN:
            value = form_values['chkValue']
        elif get_form_item_property(fi['type'])[self.current_prop_name] == FormItemPropType.COLOR:
            #print('changeProperty_ok form_values=', form_values)
            #print('changeProperty_ok form_values[chkEmpty]=', form_values['chkEmpty'])
            value = 'none' if form_values['chkEmpty'] else 'rgb({},{},{})'.format(form_values['txtRed'], form_values['txtGreen'], form_values['txtBlue'])
        elif get_form_item_property(fi['type'])[self.current_prop_name] == FormItemPropType.PRELOADED_IMAGE:
            #print('changeProperty_ok type is FormItemPropType.PRELOADED_IMAGE')
            value = str(form_values['selChosenImage'])
        else:
            assert False # Unknown property type
        fi[self.current_prop_name] = value
        #print('changeProperty_ok self.current_prop_name=', self.current_prop_name, ', form_values[selChosenImage]', form_values.get('selChosenImage', None))
        #print('changeProperty_ok fi[self.current_prop_name]', fi[self.current_prop_name])
        self.current_prop_name = None
        self.mount_redraw()
        Router.router.ResetHashChange()

    def upload_images(self, e):
        #print('upload images called')
        self.upload_modal = UploadModal(self)
        self.mount_redraw()
        Router.router.ResetHashChange()

    def close_upload_modal(self, e):
        self.upload_modal = False
        self.mount_redraw()
        Router.router.ResetHashChange()

    def get_top_navbar_items(self):
        if self.program_is_running:
            return [
                     #drop_down_item('Stop', 'fa-square', self.stop_project),
                      li({'class': 'nav-item li-create-new dropdown-menu-header'}, [
                        form({'action': '#'}, [
                          a({'class': "btn btn-default navbar-btn crt-btn",
                             'href': get_current_hash(), 'onclick': self.stop_project}, [
                            i({'class': "fa fa-1x fa-square'", 'aria-hidden':"true"}),
                            t('Stop'),
                          ]),
                        ]),
                      ]),

                   ]
        else:
            return [
                      drop_down_menu('File', [
                        #drop_down_item('Run', 'fa-caret-right', self.run_project),
                        drop_down_item('Save Project', '', self.save_project),
                        drop_down_item('Delete File/Folder', '', self.delete_selected_de),
                        drop_down_item('Rename File', '', self.display_rename_file_modal),
                        drop_down_item('Set Default', '', self.set_current_file_as_default),
                        drop_down_item('Upload images...', '', self.upload_images),

                        #drop_down_item('Triangle', 'fa-caret-up', test_click_handler),
                        #drop_down_item('Square', 'fa-square', None),
                        #drop_down_item('Something else here', 'fa-btc', None),
                        #drop_down_submenu('Recent documents', 'fa-caret-right', [
                        #  drop_down_item('Hello.py', '', None),
                        #  drop_down_item('World.py', '', None),
                        #])
                      ]),
                      #drop_down_menu('Edit', [
                      #  drop_down_item('Triangle', 'fa-caret-up', None),
                      #  drop_down_item('Square', 'fa-square', None),
                      #  drop_down_item('Something else here', 'fa-btc', None),
                      #]),
                      drop_down_menu('Debug', [
                        drop_down_item('Run', 'fa-caret-right', self.run_project),
                        #drop_down_item('Square', 'fa-square', None),
                        #drop_down_item('Something else here', 'fa-btc', None),
                      ]),
                      li({'class': 'nav-item li-create-new dropdown-menu-header'}, [
                        form({'action': '#'}, [
                          #ModalTrigger({'class': "btn btn-default navbar-btn crt-btn"}, "Share", "#shareProj"),
                          a({'class': "btn btn-default navbar-btn crt-btn", 'href': get_current_hash(), 'onclick': self.display_share_project_modal}, "Share")
                        ]),
                      ]),
                      span({'style':{'color': 'white', # TODO: This is a really hacky way to display this. Add better styling
                                     'padding-top': '7px',
                                     'margin-left': '5px'}}, [
                        t(lambda: self.get_project().get('name', ''))
                      ])
                    ]

    def get_modals(self):
        # print('EditorView get_modals called')
        def get_current_form_item_prop_val():
            #print('EditorView get_current_form_item_prop_vals called')
            if self.selected_de is None:
                return ''
            #print('1 EditorView get_current_form_item_prop_vals')
            fis = [fi for fi in self.selected_de['form_items'] if fi['id'] == self.selected_item]
            #print('2 EditorView get_current_form_item_prop_vals')
            if len(fis) == 0 or self.current_prop_name == '' or self.current_prop_name is None:
                return ''
            #print('EditorView self.current_prop_name=', self.current_prop_name)
            #print('EditorView fis[0]=', fis[0])
            ret = str(fis[0][self.current_prop_name])
            #print('EditorView get_current_form_item_prop_vals exited ret=', ret)
            return ret
        def get_current_form_item_checked():
            # print ('get_current_form_item_checked 1')
            if self.selected_de is None:
                return {}
            fis = [fi for fi in self.selected_de['form_items'] if fi['id'] == self.selected_item]
            # print ('get_current_form_item_checked 2')
            if len(fis) == 0 or self.current_prop_name == '' or self.current_prop_name is None:
                return {}
            # print ('get_current_form_item_checked self.current_prop_name=', self.current_prop_name)
            # print ('get_current_form_item_checked fis[0][self.current_prop_name]=', fis[0][self.current_prop_name])
            return {'checked': 'checked'} if fis[0][self.current_prop_name] else {}

        def get_current_form_item_color_empty():
            if self.selected_de is None:
                return {}
            fis = [fi for fi in self.selected_de['form_items'] if fi['id'] == self.selected_item]
            # print ('get_current_form_item_checked 2')
            if len(fis) == 0 or self.current_prop_name == '' or self.current_prop_name is None:
                return {}
            # print ('get_current_form_item_checked self.current_prop_name=', self.current_prop_name)
            # print ('get_current_form_item_checked fis[0][self.current_prop_name]=', fis[0][self.current_prop_name])
            return {'checked': 'checked'} if fis[0][self.current_prop_name] == 'none' else {}

        def get_current_form_item_color(color):
            if self.selected_de is None:
                return ''
            fis = [fi for fi in self.selected_de['form_items'] if fi['id'] == self.selected_item]
            if len(fis) == 0 or self.current_prop_name == '' or self.current_prop_name is None:
                return ''
            s = str(fis[0][self.current_prop_name])
            p = re.compile(
                'rgb(\s*)\((\s*)(?P<red>[0-9]+)(\s*),(\s*)(?P<green>[0-9]+)(\s*),(\s*)(?P<blue>[0-9]+)(\s*)\)')
            m = p.search(s)
            if m:
                kwargs = m.groupdict()
                return kwargs.get(color, '')
            return ''

        def get_current_form_item_color_red():
            return get_current_form_item_color('red')

        def get_current_form_item_color_green():
            return get_current_form_item_color('green')

        def get_current_form_item_color_blue():
            return get_current_form_item_color('blue')

        share_url = str(js.globals.window.location.origin) + "/share/" + project.get('id', '') + "/"
        facebook_iframe_src = 'https://www.facebook.com/plugins/share_button.php?' + \
                              urlencode({'href': share_url,
                                         'layout':'button',
                                         'size':'small',
                                         'mobile_iframe':'true',
                                         'width':'59',
                                         'height':'20'})

        return      [
                      Modal("shareProj", "Share Project", [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"formGroupExampleInput"}, 'Web Link'),
                            html_input({'type': "text", 'class':"form-control", 'id':"formGroupExampleInput",
                                         'value':share_url,
                                         'readonly':'readonly'}),
                          ]),
                          div({'class': 'form-group'}, [
                            #label({'for':"exampleFormControlTextarea1"}, 'Share On:'),
                            p('Share On:'),
                            #i({'class': 'fa fa-facebook', 'aria-hidden': 'true'}),
                            #i({'class': 'fa fa-twitter', 'aria-hidden': 'true'}),
                            #i({'class': 'fa fa-envelope-o', 'aria-hidden': 'true'}),
                            iframe({'src':facebook_iframe_src + "&appId",
                                    'width':"59",
                                    'height':"20",
                                    'style':"border:none;overflow:hidden",
                                    'scrolling':"no",
                                    'frameborder':"0",
                                    'allowTransparency':"true",
                                    'allow':"encrypted-media"}),
                          ]),
                        ]),
                      ], None),
                      Modal("newFile", "New File", [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"txtFileName"}, 'File name'),
                            html_input({'type': "text", 'class':"form-control", 'id':"txtFileName", 'placeholder':"New File"}),
                            label({'class':"col-form-label", 'for':"selFileType"}, 'File type'),
                            select({'id': 'selFileType', 'class':"form-control"}, [
                              option({'value': 'plain-py-file', 'class':"form-control"}, 'Plain old Python file'),
                              option({'value': 'graphical-py-file', 'class':"form-control"}, 'Graphical Binary Crate Python file'),
                            ]),
                          ]),
                        ]),
                      ], self.newFile_ok),
                      Modal("newFolder", "New Folder", [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"txtFolderName"}, 'Folder name'),
                            html_input({'type': "text", 'class':"form-control", 'id':"txtFolderName", 'placeholder':"New Folder"}),
                          ]),
                        ]),
                      ], self.newFolder_ok),
                      Modal("changeProperty", "Change Property " + self.current_prop_name if self.current_prop_name else '', [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"txtValue"}, 'Value'),
                            html_input({'type': "text", 'class':"form-control", 'id':"txtValue", 'placeholder':"New Value", 'value': get_current_form_item_prop_val()}),
                          ]),
                        ]),
                      ], self.changeProperty_ok),
                      Modal("changePropertyBoolean", "Change Boolean Property " + self.current_prop_name if self.current_prop_name else '', [
                        form([
                          div({'class': 'form-group'}, [
                              label({'class': "col-form-label", 'for': "chkValue"}, 'Value'),
                              html_input(merge_dicts({'type': "checkbox", 'class': "form-control", 'id': "chkValue"},
                                                     get_current_form_item_checked())),
                          ]),
                      ]),
                  ], self.changeProperty_ok),
            Modal("changePropertyColor",
                  "Change Color Property " + self.current_prop_name if self.current_prop_name else '', [
                      form([
                          div({'class': 'form-group'}, [
                              label({'class': "col-form-label", 'for': "chkEmpty"}, 'Empty'),
                              html_input(merge_dicts({'type': "checkbox", 'class': "form-control", 'id': "chkEmpty"},
                                                     get_current_form_item_color_empty())),
                              label({'class': "col-form-label", 'for': "txtRed"}, 'Red'),
                              html_input(merge_dicts({'type': "text", 'class': "form-control", 'id': "txtRed"},
                                                     get_current_form_item_color_red())),
                              label({'class': "col-form-label", 'for': "txtGreen"}, 'Green'),
                              html_input(merge_dicts({'type': "text", 'class': "form-control", 'id': "txtGreen"},
                                                     get_current_form_item_color_green())),
                              label({'class': "col-form-label", 'for': "txtBlue"}, 'Blue'),
                              html_input(merge_dicts({'type': "text", 'class': "form-control", 'id': "txtBlue"},
                                                     get_current_form_item_color_blue())),
                          ]),
                        ]),
                      ], self.changeProperty_ok),
                      Modal("changePropertyPreloadedImage", "Change Preloaded Image " + self.current_prop_name if self.current_prop_name else '', [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"selChosenImage"}, 'Preloaded Image'),
                            select({'class':"form-control", 'id':"selChosenImage", 'value': get_current_form_item_prop_val()},
                              [option(merge_dicts({'value': ''}, {'selected':'selected'} if get_current_form_item_prop_val() == '' else {}), '(none)')] +
                                [option(merge_dicts({'value': image['id']}, {'selected':'selected'} if get_current_form_item_prop_val() == image['id'] else {}), image['name'])
                                for image in self.images]
                              ),
                          ]),
                        ]),
                      ], self.changeProperty_ok),
                      Modal("renameFile", "Rename File", [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"txtFileName"}, 'File name'),
                            html_input({'type': "text", 'class':"form-control", 'id':"txtFileName", 'value':lambda : self.selected_de['name'] if self.selected_de is not None else ''}),
                          ]),
                        ]),
                      ], self.renameFile_ok),
                    ] + \
                    (self.upload_modal.get_modal_vnodes() if self.upload_modal else [])  + (self.licence_modal.get_modal_vnodes() if self.licence_modal else [])

    def get_code_mirror_read_only(self):
        return self.selected_file_de is None

    def images_api_ajax_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            self.images = json.loads(str(xmlhttp.responseText))
            self.mount_redraw()
            Router.router.ResetHashChange()

    def __init__(self, *args, **kwargs):
        # print('EditorView __init__')
        self.selected_de = None
        self.selected_file_de = None
        self.folder_state = defaultdict(bool)
        self.context_menu = None
        self.selected_item = ''
        self.mouse_is_down = False
        self.current_prop_name = ''
        self.selected_handler = HANDLE_NONE
        self.program_is_running = False
        self.form_stack = list()
        self.code_mirror = CodeMirrorHandlerVNode({'id': 'code', 'name': 'code',
                                                   'class': 'col-md-5 CodeMirror'},
                                                  [t(self.get_selected_de_content)],
                                                  change_handler=self.code_mirror_change,
                                                  read_only=self.get_code_mirror_read_only,
                                                  current_selection_fn=self.get_selected_file_de)
        self.upload_modal = None
        self.images = []
        global original_modules
        if len(original_modules) == 0:
            original_modules = set(sys.modules.keys())
            #print('original_modules=', original_modules)
        #TODO: Option arguments should be kwargs
        self.save_progress = 0 # The number of number processes to save a project.
        super(EditorView, self).__init__(
            None,
            None,
            None, *args, **kwargs)


def editor_view():
    return EditorView()
