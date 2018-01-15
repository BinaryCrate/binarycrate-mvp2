from __future__ import absolute_import, print_function
from cavorite import c, t, Router, callbacks, timeouts
from cavorite.HTML import *
import js
import copy
from .controls import CodeMirrorHandlerVNode
import uuid


def navitem(title, icon_class, href):
    return li({'class':"nav-item", 'data-toggle':"tooltip", 'data-placement':"right", 'title':title}, [
             a({'class':"nav-link", 'href': href, 'style': {'min-height': '56px'}}, children=[
               i(cssClass=["fa", "fa-fw"] + [icon_class]),
               span({'class':"nav-link-text"}, title),
             ]),
           ])


def navsubmenu(title, parent_id, sublist_id, subitems):
    return \
    li({'class': 'nav-item', 'data-toggle': 'tooltip', 'data-placement': 'right', 'title': title}, [
      a({'class': 'nav-link nav-link-collapse collapsed', 'data-toggle': 'collapse', 'href': '#' + sublist_id, 'data-parent':'#' + parent_id}, [
        i({'class': "fa fa-fw fa-wrench"}),
        span({'class': "nav-link-text"}, title),
      ]),
      ul({'class': "sidenav-second-level collapse", 'id':sublist_id}, subitems),
    ])

def navsubmenuitem(title, url):
    return li([a({'href': url}, title)])


body = js.globals.document.body

menu_collapsed = False

def collapse_menu(e):
    global menu_collapsed
    menu_collapsed = not menu_collapsed
    if menu_collapsed:
        body.classList.add("sidenav-toggled")
    else:
        body.classList.remove("sidenav-toggled")
    jquery = js.globals['$']
    jquery(".navbar-sidenav .nav-link-collapse").addClass("collapsed");
    jquery(".navbar-sidenav .sidenav-second-level, .navbar-sidenav .sidenav-third-level").removeClass("show");
    e.preventDefault()    
    return False

def get_current_hash():
    return str(js.globals.window.location.hash)


class ModalTrigger(a):
    def __init__(self, attribs, children, target):
        attribs = copy.copy(attribs)
        attribs.update({'data-toggle': "modal", 'data-target': target, 'href': get_current_hash()})
        super(ModalTrigger, self).__init__(attribs, children)


class Modal(div):
    def __init__(self, id, title, body):
        self.id = id
        self.title = title
        self.body = body
        super(Modal, self).__init__({'class': "modal fade", "id":id, "tabindex": "-1", "role": "dialog", "aria-labeledby": "{}Label".format(id), "aria-hidden": "true"})

    def get_children(self):
        return  [
                  div({'class': "modal-dialog", "role": "document"}, [
                    div({'class': 'modal-content'}, [
                      div({'class': 'modal-header'}, [
                        h5({'class': 'modal-title', 'id':  "{}Label".format(self.id)}, self.title),
                        html_button({'type': 'button', 'class': 'close', 'data-dismiss': 'modal', 'aria-label': 'Close'}, [
                          span({'aria-hidden': 'true'}, 'X'),
                        ]),
                      ]),
                      div({'class': 'modal-body'}, [
                        form(self.body)
                      ]),
                      div({'class': 'modal-footer'}, [
                        html_button({'type': "button", 'class':"btn btn-secondary", 'data-dismiss':"modal"}, 'Cancel'),
                        html_button({'type': "button", 'class':"btn btn-primary"}, 'OK'),
                      ]),
                    ]),
                  ]),
                ]

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
    def __init__(self, title):
        super(BCPFile,self).__init__({'class': 'file'}, [a({'href': ''}, title)])

    

editor_view = \
              div([ 
                nav({'class': "navbar navbar-expand-lg navbar-dark bg-dark fixed-top", 'id': 'mainNav'}, [
                  a({'class': "nav-link", 'id':"sidenavToggler", 'style':"padding: 0px 10px 0px 0px; color:white;"}, [
                    i({'class': "fa fa-fw fa-bars", "onclick": collapse_menu})
                  ]),
                  a({'class': "navbar-brand", 'href':"#!"}, "Binary Crate"),
                  html_button({'class':"navbar-toggler navbar-toggler-right",
                               'type':"button", 'data-toggle':"collapse",
                               'data-target':"#navbarResponsive", 'aria-controls':"navbarResponsive",
                               'aria-expanded':"false", 'aria-label':"Toggle navigation"}, [
                    span({'class': "navbar-toggler-icon"}),
                  ]),
                  div({'class':"collapse navbar-collapse", 'id':"navbarResponsive"}, [
                    ul({'class':"navbar-nav navbar-sidenav", 'id':"exampleAccordion"}, [
                      navitem('Dashboard', 'fa-dashboard', '#!'),
                      navitem('Editor', 'fa-code', '#!editor'),
                      navitem('Classroom', 'fa-laptop', '#!classroom'),
                      navsubmenu('Settings', 'exampleAccordion', 'collapseComponents', [
                        navsubmenuitem('Navbar', '#!navbar'),
                        navsubmenuitem('Cards', '#!cards'),
                      ])
                    ]),
                    ul({'class': 'navbar-nav mr-auto'}, [
                      div({'class':"dropdown nav-item shapes__dropdown dropdown-menu-header"}, [
                        html_button({'class':"btn dropdown-toggle crt-btn", 'type':"button", 'id':"dropdownMenuButton", 'data-toggle':"dropdown", 'aria-haspopup':"true", 'aria-expanded':"false"}, 'File'),
                        div({'class': "dropdown-menu", 'aria-labelledby':"dropdownMenuButton"}, [
                          a({'class':"dropdown-item",'href':"#"}, [
                            i({'class': "fa fa-1x fa-caret-up", 'aria-hidden':"true"}),
                            t('Triangle'),
                          ]),
                          a({'class':"dropdown-item",'href':"#"}, [
                            i({'class': "fa fa-1x fa-square", 'aria-hidden':"true"}),
                            t('Square'),
                          ]),
                          a({'class':"dropdown-item",'href':"#"}, [
                            i({'class': "fa fa-1x fa-btc", 'aria-hidden':"true"}),
                            t('Something else here'),
                          ]),
                        ]),
                      ]),
                      div({'class':"dropdown nav-item shapes__dropdown dropdown-menu-header"}, [
                        html_button({'class':"btn dropdown-toggle crt-btn", 'type':"button", 'id':"dropdownMenuButton", 'data-toggle':"dropdown", 'aria-haspopup':"true", 'aria-expanded':"false"}, 'Edit'),
                        div({'class': "dropdown-menu", 'aria-labelledby':"dropdownMenuButton"}, [
                          a({'class':"dropdown-item",'href':"#"}, [
                            i({'class': "fa fa-1x fa-caret-up", 'aria-hidden':"true"}),
                            t('Triangle'),
                          ]),
                          a({'class':"dropdown-item",'href':"#"}, [
                            i({'class': "fa fa-1x fa-square", 'aria-hidden':"true"}),
                            t('Square'),
                          ]),
                          a({'class':"dropdown-item",'href':"#"}, [
                            i({'class': "fa fa-1x fa-btc", 'aria-hidden':"true"}),
                            t('Something else here'),
                          ]),
                        ]),
                      ]),
                      div({'class':"dropdown nav-item shapes__dropdown dropdown-menu-header"}, [
                        html_button({'class':"btn dropdown-toggle crt-btn", 'type':"button", 'id':"dropdownMenuButton", 'data-toggle':"dropdown", 'aria-haspopup':"true", 'aria-expanded':"false"}, 'Options'),
                        div({'class': "dropdown-menu", 'aria-labelledby':"dropdownMenuButton"}, [
                          a({'class':"dropdown-item",'href':"#"}, [
                            i({'class': "fa fa-1x fa-caret-up", 'aria-hidden':"true"}),
                            t('Triangle'),
                          ]),
                          a({'class':"dropdown-item",'href':"#"}, [
                            i({'class': "fa fa-1x fa-square", 'aria-hidden':"true"}),
                            t('Square'),
                          ]),
                          a({'class':"dropdown-item",'href':"#"}, [
                            i({'class': "fa fa-1x fa-btc", 'aria-hidden':"true"}),
                            t('Something else here'),
                          ]),
                        ]),
                      ]),
                      li({'class': 'nav-item li-create-new dropdown-menu-header'}, [
                        form({'action': '#'}, [
                          ModalTrigger({'class': "btn btn-default navbar-btn crt-btn"}, "Share", "#shareProj"),
                        ]),
                      ]),
                    ]),
                    ul({'class': 'navbar-nav ml-auto'}, [
                      li({'class': 'nav-item'}, [
                        ModalTrigger({'class':"nav-link"}, [
                          i({'class': "fa fa-fw fa-sign-out"}),
                          t("Logout"),
                        ], "#logoutModal"),
                      ]),
                    ]),
                  ]),
                ]),
                div({'class': "content-wrapper", 'style': {'padding-top': '1px'}}, [c("div", {'class': "container-fluid", 'style': {'padding-left': '1px'}}, [
                  div({'class': 'row'}, [
                    div({'class': "project-fnf"}, [
                      div({'class': 'top-tree'}, [
                        span({'class': 'fa fa-1x fa-file-code-o'}),
                        span({'class': 'fa fa-1x fa-folder-o'}),
                      ]),
                      BCProjectTree([
                        BCPFolder('Animals', True, [
                          BCPFile('Birds'),
                          BCPFolder('Mammals', True, [
                            BCPFile('Elephants'),
                            BCPFile('Mouse'),
                          ]),
                          BCPFile('Reptiles'),
                        ]),
                        BCPFolder('Plants', True, [
                          BCPFolder('Flowers', False, [
                            BCPFile('Rose'),
                            BCPFile('Tulip'),
                          ]),
                          BCPFile('Trees'),
                        ]),
                      ]),
                    ]),
                    article([
                      CodeMirrorHandlerVNode({'id': 'code', 'name': 'code'}, example_html),
                      iframe({'id': 'preview'}),
                    ]),
                  ]),
                ])]),
                footer({'class': "sticky-footer"}, [
                  div({'class':"container"}, [
                    div({'class':"text-center"}, [
                      small("Copyright (C) Binary Crate 2018"),
                    ]),
                  ]),
                ]),
                Modal("logoutModal", "Logout", [
                  div("Select \"Logout\" below if you are ready to end your current session."),
                ]),
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
                ]),
              ])


