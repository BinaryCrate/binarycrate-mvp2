from __future__ import absolute_import, print_function
import cavorite
from cavorite import c, t, Router, callbacks, timeouts, get_current_hash
from cavorite.HTML import *
try:
    import js
except ImportError:
    js = None
import copy
from .controls import CodeMirrorHandlerVNode
import uuid
from .navigation import BCChrome
import cavorite.bootstrap.modals as modals
from cavorite.bootstrap.modals import ModalTrigger, Modal
from cavorite.ajaxget import ajaxget, ajaxput, ajaxdelete
import json
from operator import itemgetter
from collections import defaultdict
from cavorite.svg import svg


project = { }

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

class BCProjectTree(ol):
    def __init__(self, children):
        super(BCProjectTree, self).__init__( {'class': 'tree'}, children)


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
        input_attribs = {'type': 'checkbox', 'id':self.id, 'onclick': self.on_click}
        label_attribs = {'for': self.id}
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
        self.editor_view.selected_item = ''
        self.editor_view.mount_redraw()
        Router.router.ResetHashChange()

class BCPFile(li):
    def __init__(self, de, code_mirror, editor_view):
        self.de = de
        self.code_mirror = code_mirror
        self.editor_view = editor_view
        super(BCPFile,self).__init__({'class': 'file'})

    def get_children(self):
        a_attribs = {'href': js.globals.window.location.href, 'onclick': self.on_click}
        if self.get_is_active():
            a_attribs.update({'class': 'file-active'})
        return [
          a(a_attribs, self.de['name'])
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
        self.editor_view.mount_redraw()
        Router.router.ResetHashChange()


def sub_menu_handler(e):
    jquery = js.globals['$']
    jquery(e.target).next('div').toggle();
    e.stopPropagation()
    e.preventDefault()

def drop_down_menu(title, members):
    return div({'class':"dropdown nav-item shapes__dropdown dropdown-menu-header"}, [
      html_button({'class':"btn dropdown-toggle crt-btn", 'type':"button", 'id':"dropdownMenuButton", 'data-toggle':"dropdown", 'aria-haspopup':"true", 'aria-expanded':"false"}, title),
      div({'class': "dropdown-menu", 'aria-labelledby':"dropdownMenuButton"}, members)
    ])

def drop_down_item(title, icon_class, click_handler):
    attribs = {'class':"dropdown-item", 'href':get_current_hash()}
    if click_handler is not None:
        attribs['onclick'] = click_handler
    else:
        def dummy_click_handler(e):
            e.stopPropagation()
            e.preventDefault()
        attribs['onclick'] = dummy_click_handler
    return a(attribs, [
      i({'class': "fa fa-1x " + icon_class, 'aria-hidden':"true"}),
      t(title),
    ])

def drop_down_submenu(title, icon_class, members):
    return div({'class': "dropdown-submenu"}, [
      a({'class':"dropdown-item",'href':"#", 'onclick': sub_menu_handler}, [
        i({'class': "fa fa-1x " + icon_class, 'aria-hidden':"true"}),
        t(title),
      ]),
      div({'class': "dropdown-menu"}, members)
    ])

def test_click_handler(e):
    js.globals.window.alert('Hello click handler')
    e.stopPropagation()
    e.preventDefault()
    
def save_project(e):
    def dummy_put_result_handler(xmlhttp, response):
        pass

    def dummy_delete_result_handler(xmlhttp, response):
        pass

    for de in project['directory_entry']:
        if de['name'] != '': # Don't try to save the root folder                
            ajaxput('/api/projects/directoryentry/' + de['id'] + '/', de, dummy_put_result_handler)
    for de_id in project['deleted_directory_entries']:
        ajaxdelete('/api/projects/directoryentry/' + de_id + '/', dummy_delete_result_handler)

class ContextMenu(nav):
    def __init__(self, posx, posy, menu_items, *args, **kwargs):
        self.menu_items = menu_items
        super(ContextMenu, self).__init__({'class': "context-menu", 'style': 'left: {}px; top:{}px'.format(posx, posy)}, *args, **kwargs)

    def get_children(self):
        menu_items = [
                                li({'class': "context-menu__item"}, [
                                  a({'href': get_current_hash(), 'class': "context-menu__link", 'onclick': mi[1]}, [
                                    #i({'class': 'fa fa-eye'}),
                                    t(mi[0]),
                                  ]),
                                ]) for mi in self.menu_items]

        return              [
                              ul({'class': 'context-menu__items'}, menu_items),
                            ]


class EditorView(BCChrome):
    #def add_new_folder_handler(self, e):
    #    pass

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

    def projects_api_ajax_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            global project
            new_project = json.loads(str(xmlhttp.responseText))
            if project != new_project:
                project = new_project
                project['deleted_directory_entries'] = list()
                for de in project['directory_entry']:
                    de['form_items'] = list()
                self.mount_redraw()
                Router.router.ResetHashChange()

    def mount(self, element):
        global project
        project = {}
        self.context_menu = None
        super(EditorView, self).mount(element)

    def query_project(self):
        global project
        if len(project) == 0:
            # Only load the project if we don't alreayd have it
            ajaxget('/api/projects/' + self.get_root().url_kwargs['project_id'], self.projects_api_ajax_result_handler)

    def was_mounted(self):
        super(EditorView, self).was_mounted()
        self.timeout_val = timeouts.set_timeout(lambda : self.query_project(), 1)

    def get_project_tree(self):
        def get_as_tree(parent_id):
            directory_entries = sorted([de for de in de_source if de['parent_id'] == parent_id], key=itemgetter('name'))
            ret = [BCPFile(de, self.code_mirror, self) if de['is_file'] else BCPFolder(de, get_as_tree(de['id']), self)  for de in directory_entries if de['parent_id'] == parent_id]
            return ret
        
        global project
        if project == { }:
            # If project not loaded yet
            return BCProjectTree([])
        else:
            de_source = project['directory_entry']

            return  BCProjectTree(get_as_tree(None))

    def get_central_content(self):
        return    c("div", {'class': "container-fluid code-area", 'style': 'padding-left: 1px; padding-top:1px height:100%;'}, [
                    div({'class': 'row row-wrapper'}, [
                      div({'class': "project-fnf col-ms-2"}, [
                        div({'class': 'top-tree'}, [
                          p({'style': 'display:inline'}, 'Files'),
                          a({'data-toggle': "modal", 'data-target': '#newFile', 'href': get_current_hash(), 'onclick': self.newFile_ok}, [
                            span({'class': 'fa fa-1x fa-file-code-o'}),
                          ]),
                          a({'data-toggle': "modal", 'data-target': '#newFolder', 'href': get_current_hash(), 'onclick': self.newFolder_ok}, [
                            span({'class': 'fa fa-1x fa-folder-o'}),
                          ]),
                        ]),
                        self.get_project_tree(),
                      ]),
                      article({'class': 'col-md-12 row', 'id': 'editor'}, [
                        self.code_mirror,
                        div({'class': 'row col-md-5 output-col'}, [
                          #iframe({'id': 'preview', 'class': 'col-12 code-output'}),
                          div({'id': 'preview', 'class': 'col-12 code-output', 'oncontextmenu': self.contextmenu_preview, 'style': 'padding-left: 0px'}, self.get_selected_de_form_controls()),
                          div({'id': 'console', 'class': 'console-editor col-12'}, [
                            div({'class': 'logMessage'}, [
                              span('//: '),
                              t('request sent'),
                            ]),
                          ]),
                        ]),
                      ]),
                    ]),
                  ])

    def on_body_click(self, e):
        if self.context_menu is not None:
            self.context_menu = None
            self.mount_redraw()
            Router.router.ResetHashChange()


    def get_context_menu(self):
        return self.context_menu

    def xy_from_e(self, e):
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
        self.context_menu = ContextMenu(posx, posy,
                                        (('New Button', self.new_button), )
                                        )
        self.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def select_new_item(self, form_item_id, e):
        #print('select_new_item form_item_id=', form_item_id)
        self.selected_item = form_item_id
        self.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def get_selected_de_form_controls(self):
        ret = list()
        if self.selected_de:
            for form_item in self.selected_de['form_items']:
                style = ''.join(('position: absolute; ',
                                'z-index: 1; ',
                                'left: {};'.format(form_item['x']),
                                'top: {};'.format(form_item['y']),
                                'width: {};'.format(form_item['width']),
                                'height: {};'.format(form_item['height'])
                                ))
                #print('get_selected_de_form_controls form_item[id]=',form_item['id'])
                form_item_id = form_item['id']
                ret.append(html_button({'style': style, 'onclick': lambda e, form_item_id=form_item_id: self.select_new_item(form_item_id, e)}, form_item['caption']))
            if self.selected_item != '':
                selected_form_item = [form_item for form_item in self.selected_de['form_items'] if self.selected_item == form_item['id']][0]
                ret.extend([svg('svg', {'id': 'preview-svg', 'height': '100%', 'width': '100%', 'oncontextmenu': self.contextmenu_preview, 'z-index':-5, 'onclick': self.clear_selected_item}, [
                              svg('rect', {'x': selected_form_item['x'], 
                                           'y':selected_form_item['y'],
                                           'width': selected_form_item['width'],
                                           'height': selected_form_item['height'],
                                           'style':"fill:None;stroke-width:5;stroke:rgb(255,0,0)"}),
                              svg('rect', {'x': selected_form_item['x'] - 5, 
                                           'y':selected_form_item['y'] - 5,
                                           'width': 10,
                                           'height': 10,
                                           'style':"fill:rgb(255,0,0);stroke-width:5;stroke:rgb(255,0,0)"}),
                              svg('rect', {'x': selected_form_item['x'] + selected_form_item['width'] - 5, 
                                           'y':selected_form_item['y'] - 5,
                                           'width': 10,
                                           'height': 10,
                                           'style':"fill:rgb(255,0,0);stroke-width:5;stroke:rgb(255,0,0)"}),
                              svg('rect', {'x': selected_form_item['x'] + selected_form_item['width'] - 5, 
                                           'y':selected_form_item['y'] + selected_form_item['height'] - 5,
                                           'width': 10,
                                           'height': 10,
                                           'style':"fill:rgb(255,0,0);stroke-width:5;stroke:rgb(255,0,0)"}),
                              svg('rect', {'x': selected_form_item['x'] - 5, 
                                           'y':selected_form_item['y'] + selected_form_item['height'] - 5,
                                           'width': 10,
                                           'height': 10,
                                           'style':"fill:rgb(255,0,0);stroke-width:5;stroke:rgb(255,0,0)"}),
                            ])])
        return ret

    def clear_selected_item(self, e):
        self.selected_item = ''
        self.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def new_button(self, e):
        if not self.selected_de:
            return
        posx = e.clientX
        posy = e.clientY
        rect = js.globals.document.getElementById('preview').getBoundingClientRect()
        posx = posx - rect.left
        posy = posy - rect.top
        new_id = str(uuid.uuid4())

        self.selected_de['form_items'].append(
            {'type': 'button',
             'x': posx,
             'y': posy,
             'width': 100,
             'height': 30,
             'caption': 'Button',
             'name': 'button1',
             'id': new_id,
            })
        self.selected_item = new_id

        self.context_menu = None
        self.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def get_selected_de_content(self):
        if self.selected_file_de is None:
            return ''
        else:
            return self.selected_file_de['content']

    def code_mirror_change(self, content):
        if self.selected_file_de is not None:
            self.selected_file_de['content'] = content

    def newFile_ok(self, e, form_values):
        root_folder = [de for de in project['directory_entry'] if de['parent_id'] is None][0]
        parent_de = root_folder if self.selected_de is None else self.selected_de
        new_de = {'id': str(uuid.uuid4()), 
                   'name': str(form_values['txtFileName']),
                   'content': '',
                   'is_file': True, 
                   'parent_id': parent_de['id'],
                  }
        project['directory_entry'].append(new_de)
        self.mount_redraw()
        Router.router.ResetHashChange()

    def newFolder_ok(self, e, form_values):
        root_folder = [de for de in project['directory_entry'] if de['parent_id'] is None][0]
        parent_de = root_folder if self.selected_de is None else self.selected_de
        new_de = {'id': str(uuid.uuid4()), 
                   'name': str(form_values['txtFolderName']),
                   'content': '',
                   'is_file': False, 
                   'parent_id': parent_de['id'],
                  }
        project['directory_entry'].append(new_de)
        self.mount_redraw()
        Router.router.ResetHashChange()

    def get_top_navbar_items(self):
        return [
                      drop_down_menu('File', [
                        drop_down_item('Save Project', '', save_project),
                        drop_down_item('Delete File/Folder', '', self.delete_selected_de),
                        drop_down_item('Triangle', 'fa-caret-up', test_click_handler),
                        drop_down_item('Square', 'fa-square', None),
                        drop_down_item('Something else here', 'fa-btc', None),
                        drop_down_submenu('Recent documents', 'fa-caret-right', [
                          drop_down_item('Hello.py', '', None),
                          drop_down_item('World.py', '', None),
                        ])
                      ]),
                      drop_down_menu('Edit', [
                        drop_down_item('Triangle', 'fa-caret-up', None),
                        drop_down_item('Square', 'fa-square', None),
                        drop_down_item('Something else here', 'fa-btc', None),
                      ]),
                      drop_down_menu('Options', [
                        drop_down_item('Triangle', 'fa-caret-up', None),
                        drop_down_item('Square', 'fa-square', None),
                        drop_down_item('Something else here', 'fa-btc', None),
                      ]),
                      li({'class': 'nav-item li-create-new dropdown-menu-header'}, [
                        form({'action': '#'}, [
                          ModalTrigger({'class': "btn btn-default navbar-btn crt-btn"}, "Share", "#shareProj"),
                        ]),
                      ]),
                    ]

    def __init__(self, *args, **kwargs):
        self.selected_de = None
        self.selected_file_de = None
        self.folder_state = defaultdict(bool)
        self.context_menu = None
        self.selected_item = ''
        self.code_mirror = CodeMirrorHandlerVNode({'id': 'code', 'name': 'code', 'class': 'col-md-5 CodeMirror'}, [t(self.get_selected_de_content)], change_handler=self.code_mirror_change)
        super(EditorView, self).__init__(
                    None,
                    None,
                    [
                      Modal("shareProj", "Share Project", [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"formGroupExampleInput"}, 'Title'),
                            html_input({'type': "text", 'class':"form-control", 'id':"formGroupExampleInput", 'placeholder':"http://bc.com/o82Ssdms/"}),
                          ]),
                          div({'class': 'form-group'}, [
                            label({'for':"exampleFormControlTextarea1"}, 'Share On:'),
                            i({'class': 'fa fa-facebook', 'aria-hidden': 'true'}),
                            i({'class': 'fa fa-twitter', 'aria-hidden': 'true'}),
                            i({'class': 'fa fa-envelope-o', 'aria-hidden': 'true'}),
                          ]),
                        ]),
                      ], None),
                      Modal("newFile", "New File", [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"txtFileName"}, 'File name'),
                            html_input({'type': "text", 'class':"form-control", 'id':"txtFileName", 'placeholder':"New File"}),
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
                    ], *args, **kwargs)

def editor_view():
    return EditorView()

