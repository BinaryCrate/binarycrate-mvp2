# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver

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

def find_element_by_xpath(context, xpath, timeout=20):
    return WebDriverWait(context.browser, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    #return WebDriverWait(context.browser, timeout).until(
    #    EC.visibility_of_element_located((By.XPATH, xpath)))

def set_element_text(element, text):
    element.clear()
    element.send_keys(text)


