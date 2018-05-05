from __future__ import unicode_literals, absolute_import, print_function
from cavorite.HTML import *
from cavorite import c, t, Router
try:
    import js
except ImportError:
    js = None
from cavorite.ajaxget import ajaxpost


class UploadModal(object):
    def __init__(self, ownerview):
        self.ownerview = ownerview

    def on_submit_upload(self, e):
        def dummy_result_handler(xmlhttp, response):
            print('dummy_result_handler called')

        print('on_submit_upload called')
        e.preventDefault()
        file_upload_element = js.globals.document.getElementById('image-upload-form-control')
        print('on_submit_upload files=',file_upload_element.files)
        print('on_submit_upload files[0]=',file_upload_element.files[0])
        f = file_upload_element.files[0]
        form_data = {'name': f.name, 'project': self.ownerview.get_project()['id'], 'file_data': f}
        ajaxpost('/api/projects/image/', form_data, dummy_result_handler)
        self.ownerview.mount_redraw()
        Router.router.ResetHashChange()

    def get_modal_vnodes(self):
        # Return the vnodes to inject into the Virtual DOM to display the modal
        return       [
                      div({'onclick': self.ownerview.close_upload_modal, 'class': 'upload-files-modal-container'}, [
                        div({'class': 'upload-files-modal-content'}, [
                          div({'style': {'width': '100%', 'height': 'calc(100% - 40px - 10px)',
                                         'padding': '20px', 'box-shadow': 'inset 0 0 10px darkgrey'}}, [
                          ]),
                          div({'style': {'width': '100%', 'height': '40px', 'padding-left': '20px',
                                         'padding-right': '20px', 'margin-top': '10px'}}, [
                            div({'style': {'width': 'calc(100% - 120px)', 'height': '40px',
                                           'padding-left': '20px', 'padding-right': '20px',
                                           'display': 'inline-block'}}, [
                              form({'action': '.', 'method': 'post', 'enctype': 'multipart/form-data',
                                    'onsubmit': self.on_submit_upload}, [
                                label({'style': {'margin-right': '15px'}}, 'Upload file'),
                                html_input({'name': 'image', 'type': 'file', 'id': 'image-upload-form-control'}),
                                html_input({'type': 'submit'}, 'Upload'),
                              ]),
                            ]),
                            div({'style': {'width': '120px', 'height': '40px', 'padding-left': '20px',
                                           'padding-right': '20px', 'display': 'inline-block'}}, [
                              html_button({'onclick': self.ownerview.close_upload_modal}, 'Close'),
                            ]),
                          ]),
                        ]),
                      ]),
                     ]


