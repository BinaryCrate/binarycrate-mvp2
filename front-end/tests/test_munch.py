# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from binarycrate.bcmunch import BCMunch
import pytest
from binarycrate.controls.bcform import Button


class TestBCMunch(object):
    def test_can_create_bc_munch_and_assign_values(self):
        class TestMunch1(BCMunch):
            _members = ['foo']

        m = TestMunch1({'foo': 'bar'})
        assert m.foo == 'bar'
        assert m['foo'] == 'bar'

    def test_must_supply_necessary_values_to_bc_munch(self):
        class TestMunch1(BCMunch):
            _members = ['foo']

        with pytest.raises(AssertionError):
            m = TestMunch1()

    def test_must_not_supply_unnecessary_values_to_bc_munch(self):
        class TestMunch1(BCMunch):
            _members = ['foo']

        with pytest.raises(AssertionError):
            m = TestMunch1({'foo': 'bar', 'foo2': 'bar2'})


class TestBCFormItemMunches(object):
    def test_can_create_form_item_and_assign_values(self):
        b = Button({'x': 1, 'y': 2, 'width': 100, 'height': 20,
                    'name': 'button1', 'caption': 'Hello'})
        assert b.caption == 'Hello'
        assert b['caption'] == 'Hello'
        assert b['type'] == 'button'
        assert 'id' in b

    def test_must_supply_necessary_values_to_form_item(self):
        with pytest.raises(AssertionError):
            m = Button()

    def test_must_not_supply_unnecessary_values_to_form_item(self):
        with pytest.raises(AssertionError):
            m = Button({'x': 1, 'y': 2, 'width': 100, 'height': 20,
                        'name': 'button1', 'caption': 'Hello', 'foo2': 'bar2'})
