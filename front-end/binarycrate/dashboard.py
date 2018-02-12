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


#dv = None


projects = []

class Project(div):
    def __init__(self, dv, proj, redraw_function):
        self.proj = proj
        self.redraw_function = redraw_function
        self.dv = dv
        super(Project, self).__init__(cssClass="col-md-3 col-sm-4")

    def projectdropdownitem(self, title, data_target, projectname):
        source = None
        def modaltrigger(e):
            self.dv.project_name = projectname
            self.redraw_function()
            jquery = js.globals['$']
            jquery(data_target).modal()
        source = li([a({'data-toggle': "modal", 'data-target': data_target, 'href': get_current_hash(), 'onclick': modaltrigger}, [t(title), ]), ])
        return source

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
                  self.projectdropdownitem('Rename', "#renameProj", self.proj['name']),
                  self.projectdropdownitem('Share', "#shareProj", self.proj['name']),
                  self.projectdropdownitem('Delete', "#deleteProj", self.proj['name']),
                ]),
              ]),
              p(self.proj['name']),
            ]),
          ]),
        ]
        ret[0].parent = self
        return ret

class DashboardView(BCChrome):
    def __init__(self, *args, **kwargs):
        self.project_name = 'No Project'
        super(DashboardView, self).__init__(*args, **kwargs)

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

    def get_modals(self):
        return      [
                      Modal("deleteProj", "Delete Project", [
                        p({'class': 'text-center'}, [
                          t("Are you sure you want to delete "),
                          strong([t(lambda: self.project_name)]),
                          t(", this will also delete all projects and data."),
                        ]),
                      ], None),
                      Modal("renameProj", "Rename Project", [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"formGroupExampleInput"}, 'Title'),
                            html_input({'type': "text", 'class':"form-control", 'id':"formGroupExampleInput", 'value':lambda: self.project_name}),
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
                      ], self.createNew_ok),
                    ]

    def projects_api_ajax_post_result_handler(self, xmlhttp, response):
        print("projects_api_ajax_post_result_handler called")
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            #dv.mount_redraw()
            self.query_projects()

    def createNew_ok(self, e, form_values):
        data = {'name': form_values['txtProjectName'],
                'type': form_values['selectProjectType'],
                'public': True}
        ajaxpost('/api/projects/', data, self.projects_api_ajax_post_result_handler)

    def get_central_content(self):
        return [Project(self, proj, self.mount_redraw) for proj in projects]


def dashboard_view():
    #global dv
    #dv = None

   # def projectsfn():
   #     return [Project(proj, dv.mount_redraw) for proj in projects]

    dv = DashboardView([
                      li({'class': 'nav-item li-create-new'}, [
                        form({'action': '#'}, [
                          ModalTrigger({'class': "btn btn-default navbar-btn crt-btn"}, "Create New", "#createNew"),
                        ]),
                      ]),
                    ],
                    None,
                    None)

    #def projects_api_ajax_post_result_handler(xmlhttp, response):
    #    print("projects_api_ajax_post_result_handler called")
    #    if xmlhttp.status >= 200 and xmlhttp.status <= 299:
    #        #dv.mount_redraw()
    #        dv.query_projects()

    #dv.projects_api_ajax_post_result_handler = projects_api_ajax_post_result_handler

    return dv

