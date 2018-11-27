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

from __future__ import absolute_import, print_function, unicode_literals
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
from cavorite.ajaxget import ajaxget, ajaxpost, ajaxput, ajaxdelete
from cavorite import timeouts
import json
from . import editor
import traceback
import sys
from .urllib import urlencode


projects = []

class Project(div):
    def __init__(self, dv, proj, redraw_function):
        self.proj = proj
        self.redraw_function = redraw_function
        self.dv = dv
        super(Project, self).__init__(cssClass="col-md-3 col-sm-4")

    def projectdropdownitem(self, title, data_target, project):
        source = None
        def modaltrigger(e):
            try:
                print('projectdropdownitem modaltrigger called')
                self.dv.selected_project = project
                self.redraw_function()
                jquery = js.globals['$']
                jquery(data_target).modal()
                Router.router.ResetHashChange()
            except Exception as err:
                try:
                    exc_info = sys.exc_info()

                    # do you usefull stuff here
                    # (potentially raising an exception)
                    try:
                        raise TypeError("Again !?!")
                    except:
                        pass
                    # end of useful stuff


                finally:
                    # Display the *original* exception
                    #traceback.print_exception(*exc_info)
                    (exc_type, exc_value, exc_traceback) = exc_info
                    print('Inner exception exc_type=',exc_type)
                    print('Inner exception exc_value=',exc_value)
                    print('Inner exception exc_traceback=',exc_traceback)
                    print('Inner exception extract_tb=',traceback.extract_tb(exc_traceback))
                    del exc_info


        try:
            source = li([a({'data-toggle': "modal", 'data-target': data_target, 'href': get_current_hash(), 'onclick': modaltrigger}, [t(title), ]), ])
        except Exception as err:
            try:
                exc_info = sys.exc_info()

                # do you usefull stuff here
                # (potentially raising an exception)
                try:
                    raise TypeError("Again !?!")
                except:
                    pass
                # end of useful stuff


            finally:
                # Display the *original* exception
                traceback.print_exception(*exc_info)
                del exc_info

                print('Outer exception')

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
                  self.projectdropdownitem('Rename', "#renameProj", self.proj),
                  self.projectdropdownitem('Share', "#shareProj", self.proj),
                  self.projectdropdownitem('Delete', "#deleteProj", self.proj),
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
        self.selected_project = None
        self.projects_loaded = False
        super(DashboardView, self).__init__(*args, **kwargs)

    def get_project_name(self):
        return self.selected_project['name'] if self.selected_project is not None else 'No project'

    def get_share_url(self):
        return str(js.globals.window.location.origin) + "/share/" + \
            self.selected_project.get('id', '') + "/" \
            if self.selected_project is not None else 'No project'

    def get_facebook_iframe_src(self):
        return  'https://www.facebook.com/plugins/share_button.php?' + \
                              urlencode({'href': self.get_share_url(),
                                         'layout':'button',
                                         'size':'small',
                                         'mobile_iframe':'true',
                                         'width':'59',
                                         'height':'20'})  + "&appId"

    def projects_api_ajax_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            self.projects_loaded = True
            global projects
            new_projects = json.loads(str(xmlhttp.responseText))
            if projects != new_projects:
                projects = new_projects
                self.mount_redraw()
                Router.router.ResetHashChange()

    def query_projects(self):
        if self.projects_loaded == False:
            ajaxget('/api/projects/', self.projects_api_ajax_result_handler)
            self.mount_redraw()
            Router.router.ResetHashChange()

    def was_mounted(self):
        super(DashboardView, self).was_mounted()
        self.timeout_val = timeouts.set_timeout(lambda : self.query_projects(), 1)

    def get_modals(self):
        return      [
                      Modal("deleteProj", "Delete Project", [
                        p({'class': 'text-center'}, [
                          t("Are you sure you want to delete "),
                          strong([t(lambda: self.get_project_name())]),
                          t(", this will also delete all projects and data."),
                        ]),
                      ], self.deleteProj_ok),
                      Modal("renameProj", "Rename Project", [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"txtProjectName"}, 'Title'),
                            html_input({'type': "text", 'class':"form-control", 'id':"txtProjectName", 'value':lambda: self.get_project_name()}),
                          ]),
                          #div({'class': 'form-group'}, [
                          #  label({'for':"exampleFormControlTextarea1"}, 'Description'),
                          #  textarea({'class': "form-control", 'id': "exampleFormControlTextarea1", 'rows':"3"}),
                          #]),
                        ]),
                      ], self.renameProj_ok),
                      Modal("shareProj", "Share Project", [
                        form([
                          div({'class': 'form-group'}, [
                            label({'class':"col-form-label", 'for':"formGroupExampleInput"}, 'Title'),
                            html_input({'type': "text", 'class':"form-control", 'id':"formGroupExampleInput", 'placeholder':self.get_share_url}),
                          ]),
                          div({'class': 'form-group'}, [
                            p('Share On:'),
                            iframe({'src':self.get_facebook_iframe_src,
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
                            option({'value': 0}, 'Python'), #TODO: The values in these selects should somehow be made portable between the frond and back ends
                            option({'value': 1}, 'Webpage'),
                            option({'value': 2}, 'Python with Storage (HistoryGraph)'),
                          ]),
                        ]),
                      ], self.createNew_ok),
                    ]

    def projects_api_ajax_post_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            new_project = json.loads(str(xmlhttp.responseText))
            js.globals.document.location = '/#!editor/' + new_project['id']

    def projects_api_ajax_put_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            self.query_projects()

    def projects_api_ajax_delete_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            self.query_projects()

    def createNew_ok(self, e, form_values):
        self.projects_loaded = False
        data = {'name': form_values['txtProjectName'],
                'type': form_values['selectProjectType'],
                'public': True}
        ajaxpost('/api/projects/', data, self.projects_api_ajax_post_result_handler)

    def renameProj_ok(self, e, form_values):
        self.projects_loaded = False
        data = {'id': self.selected_project['id'],
                'name': form_values['txtProjectName'],
                'type': self.selected_project['type'],
                'public': True}
        ajaxput('/api/projects/' + self.selected_project['id'] + '/', data, self.projects_api_ajax_put_result_handler)

    def deleteProj_ok(self, e, form_values):
        self.projects_loaded = False
        ajaxdelete('/api/projects/' + self.selected_project['id'] + '/',self.projects_api_ajax_delete_result_handler)

    def get_central_content(self):
        return c("div", {'class': "container-fluid", 'style': {'padding-left': '1px'}}, [
                 div({'class': 'row first-row'}, [Project(self, proj, self.mount_redraw) for proj in projects])
                ])


def dashboard_view():
    dv = DashboardView([
                      li({'class': 'nav-item li-create-new'}, [
                        form({'action': '#'}, [
                          ModalTrigger({'class': "btn btn-default navbar-btn crt-btn"}, "Create New", "#createNew"),
                        ]),
                      ]),
                    ],
                    None,
                    None)

    return dv
