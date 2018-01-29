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
    data = context.browser.get_log('browser')
    element = find_element_by_xpath(context, '//p[text()="' + projname + '"]')
    assert element is not None

@then(u'the browser window does not contain a project named "{projname}"')
def step_impl(context, projname):
    assert len(context.browser.find_elements_by_xpath('//p[text()="' + projname + '"]')) == 0

