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

from __future__ import unicode_literals, absolute_import, print_function
from .propertiesmodal import PropertiesModal
from cavorite import merge_dicts
from cavorite.HTML import *


class FormPropertiesModal(PropertiesModal):
    def get_initial_properties(self):
        return merge_dicts({'height': '0', 'width': '0'},
            self.ownerview.selected_de['form_properties'])

    def save_value(self, key, value):
        self.ownerview.selected_de['form_properties'][key] = str(value)

    def get_cell(self, k):
        return html_input({'type': "text", 'id': "prop" + k,
                     'style': 'width:calc(100% - 10px); margin:5px;',
                     'value':self.properties[k]})
