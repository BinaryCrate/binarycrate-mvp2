# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from accounts.models import User
from project.models import Project, DirectoryEntry
import uuid
from bddutils import (find_element_by_id, find_element_by_css_selector,
                      find_element_by_xpath, set_element_text)
import time


@given(u'I set up default projects')
def step_impl(context):
    mark = User.objects.get(email='mark@hackerpals.com')
    hasib = User.objects.get(email='hasib@hackerpals.com')

    de = DirectoryEntry.objects.create(name='', is_file=False)
    Project.objects.create(id=uuid.uuid4(), name='marksproject', type=0, public=True,
                           root_folder=de, owner=mark)


    de = DirectoryEntry.objects.create(name='', is_file=False)
    Project.objects.create(id=uuid.uuid4(), name='hasibsproject', type=0, public=True,
                           root_folder=de, owner=hasib)


@then(u'the browser window contains a project named "{projname}"')
def step_impl(context, projname):
    time.sleep(10)
    context.browser.save_screenshot('screenshot.png')
    data = context.browser.get_log('browser')
    element = find_element_by_xpath(context, '//p[text()="' + projname + '"]')
    assert element is not None

@then(u'the browser window does not contain a project named "{projname}"')
def step_impl(context, projname):
    assert len(context.browser.find_elements_by_xpath('//p[text()="' + projname + '"]')) == 0

@given(u'I click on "{tagname}" with content "{content}"')
def step_impl(context, tagname, content):
    button = find_element_by_xpath(context, '//' + tagname + '[text()="' + content + '"]')
    button.click()

@then(u'"{tagname}" with id "{content}" is visible')
def step_impl(context, tagname, content):
    div = find_element_by_xpath(context, '//' + tagname + '[@id="' + content + '"]')

@when(u'I click the "{inner_tagname}" labelled "{inner_label}" inside the "{outer_tagname}" with id "{outer_id}"')
def step_impl(context, inner_tagname, inner_label, outer_tagname, outer_id):
    button = find_element_by_xpath(context, '//' + outer_tagname + '[@id="' + outer_id + '"]//' + inner_tagname + '[text()="' + inner_label + '"]')
    button.click()

@given(u'I enter "{some_text}" in to the element with id "{element_id}"')
def step_impl(context, some_text, element_id):
    element = find_element_by_id(context, element_id)
    element.send_keys(some_text)

