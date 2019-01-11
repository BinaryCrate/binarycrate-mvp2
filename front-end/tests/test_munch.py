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
from binarycrate.bcmunch import BCMunch
import pytest
from binarycrate.controls.bcform import Button, Line


class TestBCMunch(object):
    def test_can_create_bc_munch_and_assign_values(self):
        class TestMunch1(BCMunch):
            _members = ['foo']

        m = TestMunch1({'foo': 'bar'})
        assert m.foo == 'bar'
        assert m['foo'] == 'bar'

    @pytest.mark.xfail
    def test_must_supply_necessary_values_to_bc_munch(self):
        class TestMunch1(BCMunch):
            _members = ['foo']

        with pytest.raises(AssertionError):
            m = TestMunch1()

    @pytest.mark.xfail
    def test_must_not_supply_unnecessary_values_to_bc_munch(self):
        class TestMunch1(BCMunch):
            _members = ['foo']

        with pytest.raises(AssertionError):
            m = TestMunch1({'foo': 'bar', 'foo2': 'bar2'})


class TestBCFormItemMunches(object):
    def test_can_create_form_item_and_assign_values(self):
        b = Button({'x': 1, 'y': 2, 'width': 100, 'height': 20,
                    'name': 'button1', 'caption': 'Hello', 'visible': True})
        assert b.caption == 'Hello'
        assert b['caption'] == 'Hello'
        assert b['type'] == 'button'
        assert 'id' in b

    def test_can_create_form_item_and_assign_values_with_optional_event_handler(self):
        def dummy_handler(e):
            pass
        b = Button({'x': 1, 'y': 2, 'width': 100, 'height': 20,
                    'name': 'button1', 'caption': 'Hello',
                    'onclick': dummy_handler, 'visible': True})
        assert b.caption == 'Hello'
        assert b['caption'] == 'Hello'
        assert b['type'] == 'button'
        assert 'id' in b

    @pytest.mark.xfail
    def test_must_supply_necessary_values_to_form_item(self):
        with pytest.raises(AssertionError):
            m = Button()

    @pytest.mark.xfail
    def test_must_not_supply_unnecessary_values_to_form_item(self):
        with pytest.raises(AssertionError):
            m = Button({'x': 1, 'y': 2, 'width': 100, 'height': 20,
                        'name': 'button1', 'caption': 'Hello', 'visible': True,
                        'foo2': 'bar2'})

    def test_lines(self):
        b = Line({'x1': 1, 'y1': 1, 'x2': 10, 'y2':10,
                  'name': 'line1', 'stroke_width':1, 'stroke': 'solid',
                  'visible': True})
        assert b.x2 == 10
        assert b['x2'] == 10
        assert b['type'] == 'line'
        assert 'id' in b
