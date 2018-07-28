from __future__ import unicode_literals, absolute_import, print_function
from .editor import EditorView
try:
    import js
except ImportError:
    js = None
from cavorite.ajaxget import ajaxget
import json


class SharedView(EditorView):
    def get_top_navbar_items(self):
        return []

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

            # Only load the project if we don't alreayd have it
            ajaxget('/api/projects/' + project_id + '/', self.projects_api_ajax_result_handler)

    def projects_api_ajax_result_handler(self, xmlhttp, response):
        super(SharedView, self).projects_api_ajax_result_handler(xmlhttp, response) #unpacks self object and calls super class version of it (inhertied from)
        project = self.get_project()
        print('projects_api_ajax_result_handler project.get(type)=', project.get('type'))
        if project.get('type', None) == 1:
            self.update_html_preview()
        elif project.get('type', None) == 0:
            self.run_project(None)

    def get_code_mirror_read_only(self):
        return True



def shared_view():
    return SharedView()


