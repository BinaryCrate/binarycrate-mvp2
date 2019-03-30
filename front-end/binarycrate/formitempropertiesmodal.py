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


class FormItemPropertiesModal(PropertiesModal):
    def __init__(self, ownerview, form_item_id):
        self.form_item_id = form_item_id
        super(FormItemPropertiesModal, self).__init__(ownerview)

    def get_initial_properties(self):
        fis = [fi for fi in self.ownerview.selected_de['form_items'] if fi['id'] == self.form_item_id]
        assert len(fis) == 1
        return {k: v for k,v in six.iteritems(fis[0]) if k != 'id'}
        #return merge_dicts({'height': '0', 'width': '0'},
        #    self.ownerview.selected_de['form_properties'])

    def save_value(self, key, value):
        pass
        #self.ownerview.selected_de['form_properties'][key] = str(value)
