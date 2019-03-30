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
from cavorite import merge_dicts


class PropertiesModal(object):
    def __init__(self, ownerview):
        #print('PropertiesModal __init__ called')
        self.ownerview = ownerview
        self.images = []
        self.popup = None
        self.properties = self.get_initial_properties()
        #print('self.form_properties=', self.form_properties)
        #print('type(self.form_properties)=', type(self.form_properties))

    def handle_ok(self, e):
        #print('handle_ok called')
        keys = sorted(self.properties.keys())
        for k in keys:
            control = js.globals.document.getElementById("prop" + k)
            if control == js.null:
                #print(k + " control not found")
                pass
            else:
                #print(k + "=" + str(control.value))
                self.save_value(k, str(control.value))
        self.ownerview.close_form_properties_modal(e)

    def get_modal_vnodes(self):
        keys = sorted(self.properties.keys())
        #print('UploadModal get_modal_vnodes called')
        # Return the vnodes to inject into the Virtual DOM to display the modal
        return       [
                      div({'onclick': self.ownerview.close_form_properties_modal, 'class': 'upload-files-modal-container'}, [
                        div({'class': 'upload-files-modal-content'}, [
                          div({'style': {'width': '100%', 'height': 'calc(100% - 40px - 10px)',
                                         'padding': '20px', 'box-shadow': 'inset 0 0 10px darkgrey'}}, [
                            #p('Dummy content'),
                            table({'cellpadding':"2", 'cellspacing':"2", 'style':"width: 100%; xwhite-space: nowrap; xtable-layout: fixed; border: 1px solid black;"}, [
                              tr({'style': 'border: 1px solid black;'}, [
                                td({'style':"width: 50%; border: 1px solid black;"}, [
                                  p({'style': 'padding:5px'}, k)
                                ]),
                                td({'style':"width: 50%; border: 1px solid black;"}, [
                                  #p({'style': 'padding:5px'}, "Prop Value")
                                  self.get_cell(k)
                                ])
                              ]) for k in keys
                            ]),
                          ]),
                          div({'style': {'width': '100%', 'height': '40px', 'padding-left': '20px',
                                         'padding-right': '20px', 'margin-top': '10px'}}, [
                            div({'style': {'width': 'calc(100% - 200px)', 'height': '40px',
                                           'padding-left': '20px', 'padding-right': '20px',
                                           'display': 'inline-block'}}, [
                            ]),
                            div({'style': {'width': '200px', 'height': '40px', 'padding-left': '20px',
                                           'padding-right': '20px', 'display': 'inline-block'}}, [
                              html_button({'style': 'margin-right:10px', 'onclick': self.handle_ok}, 'OK'),
                              html_button({'onclick': self.ownerview.close_form_properties_modal}, 'Cancel'),
                            ]),
                          ]),
                        ]),
                      ]),
                     ] + (self.popup.get_content() if self.popup else [])
