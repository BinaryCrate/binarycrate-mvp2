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
from cavorite.bootstrap.modals import ModalTrigger, Modal
from cavorite.ajaxget import ajaxget
import json
from operator import itemgetter

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
    def __init__(self, title, checked, folder_children):
        self.title = title
        self.folder_children = folder_children
        self.checked = checked
        self.id = str(uuid.uuid4())
        super(BCPFolder, self).__init__()

    def get_children(self):
        input_styles = {'type': 'checkbox', 'id':self.id}
        if self.checked:
            input_styles.update({'checked': 'checked'})
        return [label({'for': self.id}, self.title),
                html_input(input_styles),
                ol(self.folder_children)]

class BCPFile(li):
    def __init__(self, de, code_mirror):
        self.de = de
        self.code_mirror = code_mirror
        super(BCPFile,self).__init__({'class': 'file'}, [a({'href': js.globals.window.location.href, 'onclick': lambda e: self.update_content(e)}, de['name'])])

    def update_content(self, e):
        self.code_mirror.editor.setValue(self.de['content'])


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
    attribs = {'class':"dropdown-item",'href':"#"}
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
    

class EditorView(BCChrome):
    def projects_api_ajax_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            global project
            new_project = json.loads(str(xmlhttp.responseText))
            if project != new_project:
                project = new_project
                self.mount_redraw()

    def query_project(self):
        ajaxget('/api/projects/' + self.get_root().url_kwargs['project_id'], self.projects_api_ajax_result_handler)

    def was_mounted(self):
        super(EditorView, self).was_mounted()
        self.timeout_val = timeouts.set_timeout(lambda : self.query_project(), 1)

    def get_project_tree(self):
        def get_as_tree(parent_id):
            directory_entries = sorted([de for de in de_source if de['parent_id'] == parent_id], key=itemgetter('name'))
            ret = [BCPFile(de, self.code_mirror) if de['is_file'] else BCPFolder(de['name'], False, get_as_tree(de['id']))  for de in directory_entries if de['parent_id'] == parent_id]
            return ret
        
        global project
        if project == { }:
            # If project not loaded yet
            return BCProjectTree([])
        else:
            de_source = project['directory_entry']
            root_element = [de for de in de_source if de['parent_id'] is None]
            assert len(root_element) == 1
            root_element = root_element[0]       

            return  BCProjectTree(get_as_tree(root_element['id']))

    def get_central_content(self):
        return      [
                      div({'class': "project-fnf"}, [
                        div({'class': 'top-tree'}, [
                          span({'class': 'fa fa-1x fa-file-code-o'}),
                          span({'class': 'fa fa-1x fa-folder-o'}),
                        ]),
                        self.get_project_tree(),
                      ]),
                      article([
                        self.code_mirror,
                        iframe({'id': 'preview'}),
                      ]),
                    ]

    def __init__(self, *args, **kwargs):
        self.code_mirror = CodeMirrorHandlerVNode({'id': 'code', 'name': 'code'}, '')
        super(EditorView, self).__init__(
                    [
                      drop_down_menu('File', [
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
                    ],
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
                    ], *args, **kwargs)

def editor_view():
    return EditorView()
