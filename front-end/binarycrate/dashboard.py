from __future__ import absolute_import, print_function
import cavorite
from cavorite import c, t, Router, get_current_hash
from cavorite.HTML import *
try:
    import js
except ImportError:
    js = None
import copy
from .navigation import BCChrome
import cavorite.bootstrap.modals as modals
from cavorite.bootstrap.modals import ModalTrigger, Modal
from cavorite.ajaxget import ajaxget, ajaxpost
from cavorite import timeouts
import json


dv = None

def projectdropdownitem(title, data_target, projectname, redraw_function):
    source = None
    def modaltrigger(e):
        global project_name
        project_name = projectname
        #source.get_root().mount_redraw()
        #dv.mount_redraw()
        redraw_function()
        jquery = js.globals['$']
        jquery(data_target).modal()
    source = li([a({'data-toggle': "modal", 'data-target': data_target, 'href': get_current_hash(), 'onclick': modaltrigger}, [t(title), ]), ])
    return source


projects = []

class Project(div):
    def __init__(self, proj, redraw_function):
        self.proj = proj
        self.redraw_function = redraw_function
        super(Project, self).__init__(cssClass="col-md-3 col-sm-4")

    def get_children(self):
        ret = [
          div(cssClass="wrimagecard wrimagecard-topimage", children=[
            div(cssClass="wrimagecard-topimage_header", style="background-color: rgba(51, 105, 232, 0.1)", children=[
              a({'href': '#!editor/' + self.proj['id']}, [
                center([i(cssClass="fa fa-code fa-5x", style="color:#3369e8")]),
              ]),
            ]),
            div(cssClass="wrimagecard-topimage_title", children=[
              div(cssClass='dropdown', children=[
              li({'class': "fa fa-pencil fa-lg edit", 'id': "menu1", 'data-toggle': "dropdown"}),
                ul({'class': "dropdown-menu", 'role': "menu", 'aria-labelledby':"menu1"}, [
                  projectdropdownitem('Rename', "#renameProj", self.proj['name'], self.redraw_function),
                  projectdropdownitem('Share', "#shareProj", self.proj['name'], self.redraw_function),
                  projectdropdownitem('Delete', "#deleteProj", self.proj['name'], self.redraw_function),
                ]),
              ]),
              p(self.proj['name']),
            ]),
          ]),
        ]
        ret[0].parent = self
        return ret

project_name = 'No Project'

def get_project_name():
    return project_name

class DashboardView(BCChrome):
    def projects_api_ajax_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            global projects
            new_projects = json.loads(str(xmlhttp.responseText))
            if projects != new_projects:
                projects = new_projects
                self.mount_redraw()
                Router.router.ResetHashChange()

    def query_projects(self):
        ajaxget('/api/projects/', self.projects_api_ajax_result_handler)

    def was_mounted(self):
        super(DashboardView, self).was_mounted()
        self.timeout_val = timeouts.set_timeout(lambda : self.query_projects(), 1)


def dashboard_view():
    global dv
    dv = None

    def projects_api_ajax_post_result_handler(xmlhttp, response):
        print("projects_api_ajax_post_result_handler called")
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            #dv.mount_redraw()
            dv.query_projects()

    def createNew_ok(e, form_values):
        data = {'name': form_values['txtProjectName'],
                'type': form_values['selectProjectType'],
                'public': True}
        ajaxpost('/api/projects/', data, projects_api_ajax_post_result_handler)
        pass

    def projectsfn():
        return [Project(proj, dv.mount_redraw) for proj in projects]

    dv = DashboardView([
                      li({'class': 'nav-item li-create-new'}, [
                        form({'action': '#'}, [
                          ModalTrigger({'class': "btn btn-default navbar-btn crt-btn"}, "Create New", "#createNew"),
                        ]),
                      ]),
                    ],
                    projectsfn,
                    [
                      Modal("deleteProj", "Delete Project", [
                        p({'class': 'text-center'}, [
                          t("Are you sure you want to delete "),
                          strong([t(get_project_name)]),
                          t(", this will also delete all projects and data."),
                        ]),
                      ], None),
                      Modal("renameProj", "Rename Project", [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"formGroupExampleInput"}, 'Title'),
                            html_input({'type': "text", 'class':"form-control", 'id':"formGroupExampleInput", 'value':get_project_name}),
                          ]),
                          #div({'class': 'form-group'}, [
                          #  label({'for':"exampleFormControlTextarea1"}, 'Description'),
                          #  textarea({'class': "form-control", 'id': "exampleFormControlTextarea1", 'rows':"3"}),
                          #]),
                        ]),
                      ], None),
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
                      Modal("createNew", "Create New", [
                        div({'class': 'form-group'}, [
                          label({'class': 'col-form-label', 'for': 'txtProjectName'}, 'Title'),
                          html_input({'type': 'text', 'class': 'form-control', 'id': 'txtProjectName', 'placeholder': "Name of project"}),
                        ]),
                        #div({'class': 'form-group'}, [
                        #  label({'for': 'exampleFormControlTextarea1'}, 'Description'),
                        #  textarea({'class': 'form-control', 'id':"exampleFormControlTextarea1", 'placeholder':"Description of project", 'rows':"3"}),
                        #]),
                        div({'class': 'form-group'}, [
                          label({'for': 'selectProjectType'}, 'Project Type'),
                          select({'class': 'form-control', 'id': 'selectProjectType'}, [
                            option({'value': 0}, 'Python'),
                          ]),
                        ]),
                      ], createNew_ok),
                    ])

    dv.projects_api_ajax_post_result_handler = projects_api_ajax_post_result_handler

    return dv

