from __future__ import unicode_literals, absolute_import, print_function
from cavorite.HTML import *
from cavorite import c, t, Router, timeouts
try:
    import js
except ImportError:
    js = None
from cavorite.ajaxget import ajaxpost, ajaxget
import json


class UploadedImage(div):
    def __init__(self, image):
        self.image = image
        super(UploadedImage, self).__init__({'style': {'width':'165px', 
                                                       'height': '150px',
                                                       #'border': '1px solid red'
                                                       'overflow': 'hidden',
                                                       'display': 'inline-block',
                                                       }})

    def get_children(self):
        return [
                 img({'src': self.image['image_url'],
                      'style': {'width': '145px',
                                'height': '95px',
                                'margin': '10px',
                                }
                      }), 
                 p({'style': {'font-size': '12px',
                              'margin': '4px'
                             }
                   }, self.image['name'])
               ]


class UploadModal(object):
    def __init__(self, ownerview):
        self.ownerview = ownerview
        timeouts.set_timeout(lambda : self.query_images(), 1)
        self.images = []

    def image_list_callback_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            self.images = json.loads(str(xmlhttp.responseText))
            self.ownerview.mount_redraw()
            Router.router.ResetHashChange()

    def get_images_for_display(self):
        return [UploadedImage(image) for image in self.images]      

    def query_images(self):
        ajaxget('/api/projects/image-list/' + self.ownerview.get_project()['id'],
                self.image_list_callback_handler)

    def on_submit_upload(self, e):
        def ajaxpost_result_handler(xmlhttp, response):
            self.query_images()

        e.preventDefault()
        file_upload_element = js.globals.document.getElementById('image-upload-form-control')
        f = file_upload_element.files[0]
        form_data = {'name': f.name, 'project': self.ownerview.get_project()['id'], 'file_data': f}
        ajaxpost('/api/projects/image/', form_data, ajaxpost_result_handler)
        self.ownerview.mount_redraw()
        Router.router.ResetHashChange()

    def get_modal_vnodes(self):
        # Return the vnodes to inject into the Virtual DOM to display the modal
        return       [
                      div({'onclick': self.ownerview.close_upload_modal, 'class': 'upload-files-modal-container'}, [
                        div({'class': 'upload-files-modal-content'}, [
                          div({'style': {'width': '100%', 'height': 'calc(100% - 40px - 10px)',
                                         'padding': '20px', 'box-shadow': 'inset 0 0 10px darkgrey'}}, self.get_images_for_display),
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


