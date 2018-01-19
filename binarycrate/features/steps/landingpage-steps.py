# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver
import time
from accounts.models import User
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def find_element_by_id(context, id):
    WebDriverWait(context.browser, 20).until(
        EC.presence_of_element_located((By.ID, id)))
    return WebDriverWait(context.browser, 20).until(
        EC.visibility_of_element_located((By.ID, id)))

def find_element_by_css_selector(context, selector):
    WebDriverWait(context.browser, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    return WebDriverWait(context.browser, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))

def find_element_by_xpath(context, xpath):
    WebDriverWait(context.browser, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    return WebDriverWait(context.browser, 20).until(
        EC.visibility_of_element_located((By.XPATH, xpath)))

def set_element_text(element, text):
    element.clear()
    element.send_keys(text)

@given(u'I browse to "{url}"')
def step_impl(context, url):
    context.browser.get(url)

@when(u'I wait for the browser to render the page')
def b_when_i_wait_for_the_browser_to_render_the_page(context):
    time.sleep(0.1)

@then(u'I the browsers URL is "{url}"')
def b_then_i_the_browsers_url_is_url(context, url):
    assert context.browser.current_url == url, 'Browser url = {0}, test url = {1}'.format(context.browser.current_url, url)

@given(u'I set up default credentials')
def given_i_setup_default_credentials(context):
    #print('dir(context)=', dir(context))
    #print('context.base_url=', context.base_url)
    #print('context._runner=', context._runner)
    #assert False
    u = User.objects.create(username='mark@hackerpals.com', email='mark@hackerpals.com')
    u.set_password('temp1234')
    u.save()
    assert User.objects.count() == 1

@when(u'I login in with the default credentials')
def when_i_login_with_the_default_credentials(context):
    login_input = find_element_by_id(context, 'id_login')
    set_element_text(login_input, 'mark@hackerpals.com')
    password_input = find_element_by_id(context, 'id_password')
    set_element_text(password_input, 'temp1234')
    password_input.send_keys(Keys.ENTER)

