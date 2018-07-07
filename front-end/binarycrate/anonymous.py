from __future__ import absolute_import, print_function, unicode_literals
import cavorite
from cavorite.HTML import *
from cavorite import timeouts, Router
import cavorite.bootstrap.modals as modals
try:
    import js
except ImportError:
    js = None
from cavorite.bootstrap.modals import Modal
from cavorite.ajaxget import ajaxpost, ajaxget
from .editor import EditorView


class AnonymousEditorView(EditorView):
    def __init__(self, project_id, *args, **kwargs):
        self.project_id = project_id
        super(AnonymousEditorView, self).__init__(*args, **kwargs)

    def get_project_id(self):
        return self.project_id

class AnonymousView(div):
    def __init__(self, *args, **kwargs):
        super(AnonymousView, self).__init__(*args, **kwargs)
        self.project_view = None
        self.project_id = None

    def was_mounted(self):
        super(AnonymousView, self).was_mounted()
        if self.project_view is None:
            self.project_id = str(js.globals.document.body.getAttribute('data-anonymous-project-id'))
            if self.project_id != '' and not (self.project_id is None):
                self.project_view = AnonymousEditorView(self.project_id)
                self.project_view.parent = self
                self.mount_redraw()
                Router.router.ResetHashChange()

    def get_children(self):
        print('get_children self.project_view=', self.project_view)
        if self.project_view is not None:
            return [self.project_view]
        else:
            return [
                  #TODO: This modal is used in more than one place so it should be in a library
                  Modal("createNew", "Create New", [
                    div({'class': 'form-group'}, [
                      label({'class': 'col-form-label', 'for': 'txtProjectName'}, 'Title'),
                      html_input({'type': 'text', 'class': 'form-control', 'id': 'txtProjectName', 'placeholder': "Name of project"}),
                    ]),
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
    def createNew_ok(self, e, form_values):
        data = {'name': form_values['txtProjectName'],
                'type': form_values['selectProjectType'],
                'public': True}
        ajaxpost('/api/projects/', data, self.projects_api_ajax_post_result_handler)

    def project_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            pass

    def projects_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            print('OK received to list projects')
            self.project_view = AnonymousEditorView(response[0]['id'])
            self.mount_redraw()
            Router.router.ResetHashChange()
            #ajaxget('/api/projects/' + response[0]['id'] + '/', self.project_result_handler)

    def projects_api_ajax_post_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            print('OK received to new project')

            ajaxget('/api/projects/', self.projects_result_handler)

    def mount(self, element):
        super(AnonymousView, self).mount(element)
        def display_modal():
            jquery = js.globals['$']
            jquery('#createNew').modal()
        timeouts.set_timeout(display_modal, 1)



def anonymous_project_view():
    return AnonymousView()
