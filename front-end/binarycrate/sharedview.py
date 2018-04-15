from __future__ import unicode_literals, absolute_import, print_function
from .editor import EditorView, project
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

    def query_project(self):
        #global project
        #print('query_project project=', project)
        if len(project) == 0:
            body = js.globals.document.body
            project_id = str(body.getAttribute('data-project-id'))

            # Only load the project if we don't alreayd have it
            ajaxget('/api/projects/' + project_id + '/', self.projects_api_ajax_result_handler)

    def projects_api_ajax_result_handler(self, xmlhttp, response):
        super(SharedView, self).projects_api_ajax_result_handler(xmlhttp, response)
        if self.project_has_run is False:
            self.project_has_run = True
            self.run_project(None)

    def __init__(self, *args, **kwargs):
        super(SharedView, self).__init__(*args, **kwargs)
        self.project_has_run = False


def shared_view():
    return SharedView()


