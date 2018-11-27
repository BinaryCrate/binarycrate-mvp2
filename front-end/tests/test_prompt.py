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
from mock import Mock
import cavorite_tests.fakejs as js
import binarycrate.controls.windowprompt
from binarycrate.controls import window_prompt as input


class TestPrompt(object):
    def test_input_opens_a_browser_prompt(self, monkeypatch):
        monkeypatch.setattr(binarycrate.controls.windowprompt, 'js', js)
        js.globals.window.prompt = Mock(return_value='John Smith')
        ret = input('Please enter your name')
        js.globals.window.prompt.assert_called_with('Please enter your name')
        assert ret == 'John Smith'
