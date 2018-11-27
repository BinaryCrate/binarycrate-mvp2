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
from cavorite.HTML import *
from cavorite import c, t, Router, timeouts, get_current_hash
try:
    import js
except ImportError:
    js = None
from cavorite.ajaxget import ajaxpost, ajaxget, ajaxdelete, ajaxput
import json
import traceback
import sys
import uuid
from binarycrate.controls import ContextMenu

#TODO: There appear to be no unit tests for anything in this file. Please make them


class ConfirmRenamePopup(div):
    # This pops up a deletion confirmation dialog over this popup to confirm this
    def __init__(self, upload_modal, image, *args, **kwargs):
        self.upload_modal = upload_modal
        self.image = image
        self.text_id = str(uuid.uuid4())
        super(ConfirmRenamePopup, self).__init__({'style': {'position': 'fixed',
                                                     'left': '0',
                                                     'top': '0',
                                                     'height': '100%',
                                                     'width': '100%',
                                                     'background-color': 'rgba(0, 0, 0, 0)',
                                                     'padding': '40px',
                                                     'z-index':'10002'}}, *args, **kwargs)

    def on_cancel_click(self, e):
        self.upload_modal.popup = None
        self.upload_modal.ownerview.mount_redraw()
        Router.router.ResetHashChange()

    def on_ok_click(self, e):
        def put_image_handler(xmlhttp, response):
            print('put_image_handler called')
            if xmlhttp.status >= 200 and xmlhttp.status <= 299:
                print('put_image_handler requery images')
                self.upload_modal.popup = None
                self.upload_modal.query_images()

        new_name = str(js.globals.document.getElementById(self.text_id).value)
        print('on_ok_click value=', new_name)
        ajaxput('/api/projects/image/' + self.image['id'] + '/', {'name': str(new_name)}, put_image_handler)
        """
        def delete_image_handler(xmlhttp, response):
            if xmlhttp.status >= 200 and xmlhttp.status <= 299:
                self.upload_modal.popup = None
                self.upload_modal.query_images()
        ajaxdelete('/api/projects/image/' + self.image['id'] + '/', delete_image_handler)
        """

    def get_content(self):
        return \
          [
            div({'class': 'popup-modal-container'}, [
              div({'class': 'popup-modal-content'}, [
                div([
                  p('Enter a new name for image ' + self.image['name'] + '?'),
                  div({'style': {'margin-bottom': '10px'}}, [
                    html_input({'value': self.image['name'], 'id': self.text_id}),
                  ]),
                  div({'style': {'display': 'inline-block', 'float': 'right'}}, [
                    html_button({'style': {'margin-right': '10px'}, 'onclick': self.on_cancel_click}, 'Cancel'),
                    html_button({'onclick': self.on_ok_click}, 'OK'),
                  ]),
                ]),
              ]),
            ]),
          ]



class ConfirmDeletePopup(div):
    # This pops up a deletion confirmation dialog over this popup to confirm this
    def __init__(self, upload_modal, image, *args, **kwargs):
        self.upload_modal = upload_modal
        self.image = image
        super(ConfirmDeletePopup, self).__init__({'style': {'position': 'fixed',
                                                     'left': '0',
                                                     'top': '0',
                                                     'height': '100%',
                                                     'width': '100%',
                                                     'background-color': 'rgba(0, 0, 0, 0)',
                                                     'padding': '40px',
                                                     'z-index':'10002'}}, *args, **kwargs)

    def on_cancel_click(self, e):
        self.upload_modal.popup = None
        self.upload_modal.ownerview.mount_redraw()
        Router.router.ResetHashChange()

    def on_ok_click(self, e):
        def delete_image_handler(xmlhttp, response):
            if xmlhttp.status >= 200 and xmlhttp.status <= 299:
                self.upload_modal.popup = None
                self.upload_modal.query_images()
        ajaxdelete('/api/projects/image/' + self.image['id'] + '/', delete_image_handler)

    def get_content(self):
        return \
          [
            div({'class': 'popup-modal-container'}, [
              div({'class': 'popup-modal-content'}, [
                div([
                  p('Are you sure you want to delete this image?'),
                  div({'style': {'display': 'inline-block', 'float': 'right'}}, [
                    html_button({'style': {'margin-right': '10px'}, 'onclick': self.on_cancel_click}, 'Cancel'),
                    html_button({'onclick': self.on_ok_click}, 'OK'),
                  ]),
                ]),
              ]),
            ]),
          ]



class UploadedImage(div):
    def __init__(self, owner, image):
        self.image = image
        self.context_menu = None
        self.owner = owner
        super(UploadedImage, self).__init__({'oncontextmenu': self.popup_contextmenu,
                                             'style': {'width':'165px',
                                                       'height': '150px',
                                                       #'border': '1px solid red'
                                                       'overflow': 'hidden',
                                                       'display': 'inline-block',
                                                       }})

    def rename_image(self, e):
        self.owner.popup = ConfirmRenamePopup(self.owner, self.image)
        """
        def put_image_handler(xmlhttp, response):
            print('put_image_handler called')
            if xmlhttp.status >= 200 and xmlhttp.status <= 299:
                print('put_image_handler requery images')
                self.owner.query_images()

        new_name = js.globals.window.prompt('Enter a new name for image ' + self.image['name'] + '?', self.image['name'])
        print('rename_image new_name=', new_name)
        #TODO: Remove this and replace with a more standard example of our popups. The confirm function ends up being called twice for some reason
        if new_name:
            print('Sending new name to server')
            ajaxput('/api/projects/image/' + self.image['id'] + '/', {'name': str(new_name)}, put_image_handler)
        """

    def delete_image(self, e):
        self.owner.popup = ConfirmDeletePopup(self.owner, self.image)

    def popup_contextmenu(self, e):
        posx, posy = ContextMenu.xy_from_e(e)
        self.owner.ownerview.context_menu = ContextMenu(self, posx, posy, (
                                        ('Rename Image', self.rename_image),
                                        ('Delete Image', self.delete_image),
                                        ))
        self.owner.ownerview.mount_redraw()
        Router.router.ResetHashChange()
        e.stopPropagation()
        e.preventDefault()

    def close_context_menu(self, e):
        self.owner.ownerview.context_menu = None
        self.owner.ownerview.mount_redraw()
        Router.router.ResetHashChange()

    def get_children(self):
        return [
                 img({'src': self.image['image_url'],
                      'oncontextmenu': self.popup_contextmenu,
                      'style': {'width': '145px',
                                'height': '95px',
                                'margin': '10px',
                                }
                      }),
                 p({'oncontextmenu': self.popup_contextmenu,
                    'style': {'font-size': '12px',
                              'margin': '4px'
                             }
                   }, self.image['name'])
               ]


class UploadModal(object):
    def __init__(self, ownerview):
        print('UploadModal __init__ called')
        self.ownerview = ownerview
        timeouts.set_timeout(lambda : self.query_images(), 1)
        self.images = []
        self.popup = None

    def image_list_callback_handler(self, xmlhttp, response):
        if xmlhttp.status >= 200 and xmlhttp.status <= 299:
            self.images = json.loads(str(xmlhttp.responseText))
            self.ownerview.mount_redraw()
            Router.router.ResetHashChange()

    def get_images_for_display(self):
        return [UploadedImage(self, image) for image in self.images]

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
        #print('UploadModal get_modal_vnodes called')
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
                     ] + (self.popup.get_content() if self.popup else [])

    def close_context_menu(self, e):
        self.context_menu = None
        self.ownerview.mount_redraw()
        Router.router.ResetHashChange()
