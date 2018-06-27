from __future__ import absolute_import, print_function, unicode_literals
import cavorite
from cavorite.HTML import *
from cavorite import timeouts
import cavorite.bootstrap.modals as modals
try:
    import js
except ImportError:
    js = None
from cavorite.bootstrap.modals import Modal
from cavorite.ajaxget import ajaxpost


class AnonymousView(div):
    def __init__(self, *args, **kwargs):
        super(AnonymousView, self).__init__(*args, **kwargs)

    def get_children(self):
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

    def projects_api_ajax_post_result_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            print('OK received to new project')

    def mount(self, element):
        super(AnonymousView, self).mount(element)
        def display_modal():
            jquery = js.globals['$']
            jquery('#createNew').modal()
        timeouts.set_timeout(display_modal, 1)



def anonymous_project_view():
    return AnonymousView()
