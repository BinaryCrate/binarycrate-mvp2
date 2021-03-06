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

from __future__ import absolute_import, unicode_literals, print_function

from accounts.models import User
from project.models import Project, DirectoryEntry
import uuid
from bddutils import (find_element_by_id, find_element_by_css_selector,
                      find_element_by_xpath, set_element_text)
import time
from selenium.webdriver.common.action_chains import ActionChains


@given(u'I set up default projects')
def step_impl(context):
    mark = User.objects.get(email='mark@hackerpals.com')
    hasib = User.objects.get(email='hasib@hackerpals.com')

    de_rootfolder = DirectoryEntry.objects.create(name='', is_file=False)
    Project.objects.create(id=uuid.uuid4(), name='marksproject', type=0, public=True,
                           root_folder=de_rootfolder, owner=mark)
    de_hello_world = DirectoryEntry.objects.create(parent=de_rootfolder, name='hello_world.py', is_file=True)
    de_hello_world.content = "print('Hello world')"
    de_hello_world.save()
    de_folder = DirectoryEntry.objects.create(parent=de_rootfolder, name='folder', is_file=False)
    de_hello_folder = DirectoryEntry.objects.create(parent=de_folder, name='hello_folder.py', is_file=True)
    de_hello_folder.content = \
"""for i in range(3):
    print('Hello folder i={}'.format(i))
"""
    de_hello_folder.save()


    de = DirectoryEntry.objects.create(name='', is_file=False)
    Project.objects.create(id=uuid.uuid4(), name='hasibsproject', type=0, public=True,
                           root_folder=de, owner=hasib)


@then(u'the browser window contains a project named "{projname}"')
def step_impl(context, projname):
    time.sleep(10)
    #context.browser.save_screenshot('screenshot.png')
    #data = context.browser.get_log('browser')
    element = find_element_by_xpath(context, '//p[text()="' + projname + '"]')
    assert element is not None

@then(u'the browser window does not contain a project named "{projname}"')
def step_impl(context, projname):
    assert len(context.browser.find_elements_by_xpath('//p[text()="' + projname + '"]')) == 0

@given(u'I click on "{tagname}" with content "{content}"')
def step_impl(context, tagname, content):
    time.sleep(10)
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
    time.sleep(15)
    context.browser.save_screenshot('screenshot.png')
    element = context.browser.find_element_by_id(element_id)
    element.send_keys(some_text)

@given(u'I browse to the default projects editor page')
def step_impl(context):
    mark = User.objects.get(email='mark@hackerpals.com')
    #print(' Project.objects.filter(owner=mark).count()=',  Project.objects.filter(owner=mark).count())
    assert Project.objects.filter(owner=mark).count() == 1
    project = Project.objects.first()
    context.browser.get(context.base_url + '#!editor/' + str(project.id))

@then(u'the browser window contains a BCPFile named "{file_name}" in the root folder')
def step_impl(context, file_name):
    time.sleep(25)
    #context.browser.save_screenshot('screenshot.png')
    #element = find_element_by_xpath(context, '//ol[@class="tree"]/li[@class="file"]/a[text()="' + file_name + '"]')
    elements = context.browser.find_elements_by_xpath('//ol[@class="tree"]//li[contains(@class,"file")]/a[text()="' + file_name + '"]')
    print('file elements = ', elements)
    #print('log data = ', context.browser.get_log('browser'))
    assert len(elements) == 1
    #assert False

@then(u'the browser window contains a BCPFolder named "{folder_name}" in the root folder')
def step_impl(context, folder_name):
    context.browser.save_screenshot('screenshot.png')
    #element = find_element_by_xpath(context, '//ol[@class="tree"]/li[@class="file"]/a[text()="' + file_name + '"]')
    elements = context.browser.find_elements_by_xpath('//ol[@class="tree"]/li//label[text()="' + folder_name + '"]')
    print('folder elements = ', elements)
    #print('log data = ', context.browser.get_log('browser'))
    assert len(elements) == 1
    elements[0].click()
    time.sleep(1)

@then(u'the browser window contains a BCPFile named "{file_name}" in the BCPFolder named "{folder_name}"')
def step_impl(context, file_name, folder_name):
    context.browser.save_screenshot('screenshot.png')
    #element = find_element_by_xpath(context, '//ol[@class="tree"]/li[@class="file"]/a[text()="' + file_name + '"]')
    elements = context.browser.find_elements_by_xpath('//ol[@class="tree"]/li//ol/li[@class="file"]/a[text()="' + file_name + '"]')
    print('folder - file elements = ', elements)
    #print('log data = ', context.browser.get_log('browser'))
    assert len(elements) == 1

def get_BCPFile_by_name(context, file_name):
    return context.browser.find_element_by_xpath('//ol[@class="tree"]//li[contains(@class,"file")]/a[text()="' + file_name + '"]')

@given(u'I click on the BCPFile named "{file_name}"')
def step_impl(context, file_name):
    element = get_BCPFile_by_name(context, file_name)
    element.click()
    time.sleep(5)

@then(u'the element id "{element_id}" contains "{element_content}"')
def step_impl(context, element_id, element_content):
    element = context.browser.find_element_by_id(element_id)
    #print('element.text=', element.text)
    #print('element_content=', element_content)
    assert element.text == element_content

@then(u'the BCPFile named "{file_name}" is highlighted')
def step_impl(context, file_name):
    #context.browser.save_screenshot('screenshot.png')
    element = get_BCPFile_by_name(context, file_name)
    assert 'file-active' in element.get_attribute('class')

@then(u'the BCPFolder named "{folder_name}" is not highlighted')
def step_impl(context, folder_name):
    label_element = context.browser.find_element_by_xpath('//ol[@class="tree"]/li//label[text()="' + folder_name + '"]')
    assert 'file-active' not in label_element.get_attribute('class')

@then(u'the BCPFolder named "{folder_name}" is not checked')
def step_impl(context, folder_name):
    label_element = context.browser.find_element_by_xpath('//ol[@class="tree"]/li//label[text()="' + folder_name + '"]')
    input_element = label_element.find_element_by_xpath('following-sibling::*')
    #print('input_element.get_attribute(\'checked\')=', input_element.get_attribute('checked'))
    context.browser.save_screenshot('screenshot.png')
    print('input_element.is_selected()=', input_element.is_selected())
    assert input_element.is_selected() == False

@then(u'the BCPFile named "{file_name}" is not highlighted')
def step_impl(context, file_name):
    #context.browser.save_screenshot('screenshot.png')
    element = get_BCPFile_by_name(context, file_name)
    assert 'file-active' not in element.get_attribute('class')

@given(u'I click on the BCPFolder named "{folder_name}"')
def step_impl(context, folder_name):
    #context.browser.save_screenshot('screenshot.png')
    label_element = context.browser.find_element_by_xpath('//ol[@class="tree"]/li//label[text()="' + folder_name + '"]')
    input_element = label_element.find_element_by_xpath('following-sibling::*')
    # Hack needed to click element from https://github.com/seleniumhq/selenium-google-code-issue-archive/issues/2766#issuecomment-191962655
    #input_element.click()
    ActionChains(context.browser).move_to_element_with_offset(input_element, 20, 0).click().perform()

@then(u'the BCPFolder named "{folder_name}" is highlighted')
def step_impl(context, folder_name):
    label_element = context.browser.find_element_by_xpath('//ol[@class="tree"]/li//label[text()="' + folder_name + '"]')
    assert 'file-active' in label_element.get_attribute('class')

@then(u'the BCPFolder named "{folder_name}" is checked')
def step_impl(context, folder_name):
    label_element = context.browser.find_element_by_xpath('//ol[@class="tree"]/li//label[text()="' + folder_name + '"]')
    input_element = label_element.find_element_by_xpath('following-sibling::*')
    print('input_element.get_attribute(\'checked\')=', input_element.get_attribute('checked'))
    print('input_element.is_selected()=', input_element.is_selected())
    assert input_element.is_selected()
    #assert False

@then(u'I send keys "{keys}" to element with text "{content}"')
def step_impl(context, keys, content):
    #element = context.browser.find_element_by_xpath('//*[contains(text(), "print") and contains(text(), "Hello world")]')
    element = context.browser.find_element_by_xpath('//pre[contains(class, "CodeMirror-Line")]/span')
    print('CodeMirror-Line element.text=', element.text)
    element.send_keys(keys)
    print('CodeMirror-Line element.text=', element.text)

@given(u'I click on the Drop Down Toggle named "{name}"')
def step_impl(context, name):
    element = context.browser.find_element_by_xpath('//button[contains(class, \'dropdown-toggle\') and text()="' + folder_name + '"]')
    element.click()

@given(u'I click on the Drop Down Item named "{name}"')
def step_impl(context, name):
    element = context.browser.find_element_by_xpath('//a[@class=\'dropdown-item\') and text()="' + name + '"]')
    element.click()

@then(u'the DirectoryEntry with name "{name}" has content "{content}"')
def step_impl(context, name, content):
    assert DirectoryEntry.objects.get(name=name).content == content
