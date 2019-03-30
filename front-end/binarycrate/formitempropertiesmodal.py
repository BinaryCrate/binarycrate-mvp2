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
import six
from cavorite.HTML import *
from binarycrate.controls.bcform import get_form_item_property, FormItemPropType
import re


class FormItemPropertiesModal(PropertiesModal):
    def __init__(self, ownerview, form_item_id):
        self.form_item_id = form_item_id
        fis = [fi for fi in ownerview.selected_de['form_items'] if
               fi['id'] == self.form_item_id]
        assert len(fis) == 1
        self.form_item = fis[0]
        super(FormItemPropertiesModal, self).__init__(ownerview)

    def get_initial_properties(self):
        return {k: v for k,v in six.iteritems(self.form_item) if k != 'id' and
                k != 'type'}
        #return merge_dicts({'height': '0', 'width': '0'},
        #    self.ownerview.selected_de['form_properties'])

    def save_value(self, key, value):
        pass
        #self.ownerview.selected_de['form_properties'][key] = str(value)

    def get_cell(self, k):
        prop_type = get_form_item_property(self.form_item['type'])[k]
        value = self.properties[k]
        if prop_type == FormItemPropType.BOOLEAN:
            return html_input(merge_dicts({'type': "checkbox",
                                           'id': "prop" + k,
                                           'style': 'width:calc(100% - 10px); margin:5px;'},
                                            {'checked': 'checked'} if value else {}))
        elif prop_type == FormItemPropType.PRELOADED_IMAGE:
            return select({'id': "prop" + k, 'style': 'width:calc(100% - 10px); margin:5px;', 'value': value},
                              [option(merge_dicts({'value': ''}, {'selected':'selected'} if value == '' else {}), '(none)')] +
                                [option(merge_dicts({'value': image['id']}, {'selected':'selected'} if value == image['id'] else {}), image['name'])
                                for image in self.ownerview.images]
                              )
        elif prop_type == FormItemPropType.COLOR:
            def get_color_portion(color, value):
                s = str(value)
                p = re.compile(
                    'rgb(\s*)\((\s*)(?P<red>[0-9]+)(\s*),(\s*)(?P<green>[0-9]+)(\s*),(\s*)(?P<blue>[0-9]+)(\s*)\)')
                m = p.search(s)
                if m:
                    kwargs = m.groupdict()
                    return {'value': kwargs.get(color, '')}
                return {'value': ''}


            color_empty = {'checked': 'checked'} if value == 'none' else {}
            color_red = get_color_portion('red', value)
            color_green = get_color_portion('green', value)
            color_blue = get_color_portion('blue', value)
            return div({'style': {'display': 'inline-block', 'style': 'padding:5px'}}, [
                label({'for': "chkEmpty" + k}, 'Empty'),
                html_input(merge_dicts({'type': "checkbox", 'id': "chkEmpty" + k,
                                        'style': 'margin-left: 5px; margin-right:5px'},
                                       color_empty)),
                label({'for': "txtRed" + k}, 'Red'),
                html_input(merge_dicts({'type': "text", 'id': "txtRed" + k,
                                        'style': 'margin-left: 5px; margin-right:5px;max-width:70px'},
                                       color_red)),
                label({'for': "txtGreen" + k}, 'Green'),
                html_input(merge_dicts({'type': "text", 'id': "txtGreen" + k,
                                        'style': 'margin-left: 5px; margin-right:5px;max-width:70px'},
                                       color_green)),
                label({'for': "txtBlue" + k}, 'Blue'),
                html_input(merge_dicts({'type': "text", 'id': "txtBlue" + k,
                                        'style': 'margin-left: 5px; margin-right:5px;max-width:70px'},
                                       color_blue))
            ])
        else:
            return html_input({'type': "text", 'id': "prop" + k,
                         'style': 'width:calc(100% - 10px); margin:5px;',
                         'value':value})
