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
