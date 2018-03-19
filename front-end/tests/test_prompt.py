# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
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

