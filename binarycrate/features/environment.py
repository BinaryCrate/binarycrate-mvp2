# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver

def before_all(context):
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'browser': 'ALL'}
    context.browser = WebDriver('http://chrome:4444/wd/hub', d)


def after_all(context):
	context.browser.quit()
