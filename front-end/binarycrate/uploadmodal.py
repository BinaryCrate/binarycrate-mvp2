from __future__ import unicode_literals, absolute_import, print_function
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


class ContextMenu2(div):
    # An improved context menu which can hopefully take care of collapsing itself
    def __init__(self, owner, posx, posy, menu_items, *args, **kwargs):
        self.owner = owner
        self.menu_items = menu_items
        self.posx = posx
        self.posy = posy
        super(ContextMenu2, self).__init__({'onclick': self.owner.close_context_menu,
                                           'style': {'position': 'fixed',
                                                     'left': '0',
                                                     'top': '0',
                                                     'height': '100%',
                                                     'width': '100%',
                                                     'background-color': 'rgba(0, 0, 0, 0)',
                                                     'padding': '40px',
                                                     'z-index':'10001'}}, *args, **kwargs)

    def get_children(self):
        menu_items = [
                                li({'class': "context-menu__item"}, [
                                  a({'href': get_current_hash(), 'class': "context-menu__link", 'onclick': mi[1]}, [
                                    #i({'class': 'fa fa-eye'}),
                                    t(mi[0]),
                                  ]),
                                ]) for mi in self.menu_items]

        return [
                 nav({'class': "context-menu", 'style': 'left: {}px; top:{}px'.format(self.posx, self.posy)}, [
                   ul({'class': 'context-menu__items'}, menu_items),
                 ])
               ]


is_delete_confirm_open = False # TODO: Very hacky but for some reason the delete_image method is called twice

class UploadedImage(div):
    def __init__(self, owner, image):
        self.image = image
        self.context_menu = None
        self.owner = owner
        #global is_delete_confirm_open
        #is_delete_confirm_open = False
        super(UploadedImage, self).__init__({'oncontextmenu': self.popup_contextmenu,
                                             'style': {'width':'165px', 
                                                       'height': '150px',
                                                       #'border': '1px solid red'
                                                       'overflow': 'hidden',
                                                       'display': 'inline-block',
                                                       }})

    def xy_from_e(self, e):
        #TODO: Shared code put in a library
        if e.pageX or e.pageY:
            posx = e.pageX
            posy = e.pageY
        elif e.clientX or e.clientY:
            posx = e.clientX + js.globals.document.body.scrollLeft + \
                               js.globals.document.documentElement.scrollLeft
            posy = e.clientY + js.globals.document.body.scrollTop + \
                               js.globals.document.documentElement.scrollTop
        return posx, posy

    def rename_image(self, e):
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

    def delete_image(self, e):
        global is_delete_confirm_open
        if is_delete_confirm_open:
            return
        is_delete_confirm_open = True
        def delete_image_handler(xmlhttp, response):
            if xmlhttp.status >= 200 and xmlhttp.status <= 299:
                self.owner.query_images()

        if js.globals.window.confirm('Are you sure you want to delete image ' + self.image['name'] + '?'):
            #TODO: Remove this and replace with a more standard example of our popups. The confirm function ends up being called twice for some reason
            ajaxdelete('/api/projects/image/' + self.image['id'] + '/', delete_image_handler)
        is_delete_confirm_open = False

    def popup_contextmenu(self, e):
        posx, posy = self.xy_from_e(e)
        self.owner.ownerview.context_menu = ContextMenu2(self, posx, posy, (
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
        self.ownerview = ownerview
        timeouts.set_timeout(lambda : self.query_images(), 1)
        self.images = []

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

    def close_context_menu(self, e):
        self.context_menu = None
        self.ownerview.mount_redraw()
        Router.router.ResetHashChange()


