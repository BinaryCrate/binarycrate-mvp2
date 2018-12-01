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

class LicenceModal(object):
    def __init__(self, ownerview):
        #print('UploadModal __init__ called')
        self.ownerview = ownerview

    def get_modal_vnodes(self):
        #print('LicenceModal get_modal_vnodes called')
        # Return the vnodes to inject into the Virtual DOM to display the modal
        return       [
                      div({'onclick': self.ownerview.close_licence_modal, 'class': 'upload-files-modal-container'}, [
                        div({'class': 'upload-files-modal-content'}, [
                          div({'style': {'width': '100%', 'height': 'calc(100% - 40px - 10px)',
                                         'padding': '20px', 'box-shadow': 'inset 0 0 10px darkgrey'}}, [
                            p('Licenced under the Affero GNU Public Licence (AGPL)'),
                            a({'href':'https://github.com/BinaryCrate/binarycrate-mvp2', 'target':'_blank'}, 'Source code')
                          ]),
                          div({'style': {'width': '100%', 'height': '40px', 'padding-left': '20px',
                                         'padding-right': '20px', 'margin-top': '10px'}}, [
                            div({'style': {'width': 'calc(100% - 120px)', 'height': '40px',
                                           'padding-left': '20px', 'padding-right': '20px',
                                           'display': 'inline-block'}}, [
                            ]),
                            div({'style': {'width': '120px', 'height': '40px', 'padding-left': '20px',
                                           'padding-right': '20px', 'display': 'inline-block'}}, [
                              html_button({'onclick': self.ownerview.close_licence_modal}, 'Close'),
                            ]),
                          ]),
                        ]),
                      ]),
                     ]
