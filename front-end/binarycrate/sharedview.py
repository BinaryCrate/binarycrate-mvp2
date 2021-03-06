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
from .editor import EditorView
try:
    import js
except ImportError:
    js = None
from cavorite.ajaxget import ajaxget
import json
from cavorite.HTML import *
from cavorite import t, get_current_hash, Router
from .licencemodal import LicenceModal


class SharedView(EditorView):
    def get_top_navbar_items(self):
        return [
          span({'style':{'color': 'white', # TODO: This is a really hacky way to display this. Add better styling
                         'padding-top': '7px',
                         'margin-left': '5px'}}, [
            t(lambda: self.get_project().get('name', ''))
          ]),
          li({'class': 'nav-item li-create-new',
              'style': 'margin-left: 8px'}, [
            form({'action': '#'}, [
              a({'class': "btn btn-default navbar-btn crt-btn",
                 'href': get_current_hash(),
                 'onclick': self.on_about_click}, "About"),
            ]),
          ]),
          li({'class': 'nav-item li-create-new',
              'style': 'margin-left: 8px'}, [
            form({'action': '#'}, [
              a({'class': "btn btn-default navbar-btn crt-btn",
                 'href': '/accounts/signup/', 'target':'_blank'}, "Sign Up"),
            ]),
          ]),
          li({'class': 'nav-item li-create-new',
              'style': 'margin-left: 8px'}, [
            form({'action': '#'}, [
              #ModalTrigger({'class': "btn btn-default navbar-btn crt-btn"}, "Share", "#shareProj"),
              a({'class': "btn btn-default navbar-btn crt-btn",
                 'href': get_current_hash(),
                  'onclick': self.display_share_project_modal},
                 "Share")
            ]),
          ])
        ]

    def on_about_click(self, e):
        #print('on_about_click called')
        self.licence_modal = LicenceModal(self)
        self.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def get_sidebar_nav_items(self):
        return []

    def get_logout_link(self):
        return []

    def get_new_file_folder_icons(self):
        return []

    def query_project(self):
        project = self.get_project()
        if len(project) == 0:
            body = js.globals.document.body
            project_id = str(body.getAttribute('data-project-id'))
            # Only load the project if we don't already have it
            def images_api_ajax_result_handler2(xmlhttp, response):
                # Get the images first then the projects
                #TODO: Do this all in one query. Otherwise it get brittle
                #print('images_api_ajax_result_handler2')
                #self.images_api_ajax_result_handler(xmlhttp, response)
                if xmlhttp.status >= 200 and xmlhttp.status <= 299:
                    self.images = json.loads(str(xmlhttp.responseText))
                    #self.mount_redraw()
                    #Router.router.ResetHashChange()
                    ajaxget('/api/projects/' + project_id + '/', self.projects_api_ajax_result_handler)

            ajaxget('/api/projects/image-list/' + project_id + '/', images_api_ajax_result_handler2)

            # Only load the project if we don't alreayd have it
            #ajaxget('/api/projects/' + project_id + '/', self.projects_api_ajax_result_handler)

    def projects_api_ajax_result_handler(self, xmlhttp, response):
        super(SharedView, self).projects_api_ajax_result_handler(xmlhttp, response) #unpacks self object and calls super class version of it (inhertied from)
        project = self.get_project()
        if project.get('type', None) == 1:
            self.update_html_preview()
        #Run program for python projects
        elif project.get('type', None) == 0:
            if not self.program_is_running:
                self.run_project(None)

    def get_code_mirror_read_only(self):
        return True

    def save_project(self, e):
        pass

def shared_view():
    return SharedView()
