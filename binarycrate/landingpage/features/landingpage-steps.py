from lettuce import step
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver
import time

browser = None

@step(u'Given I browse to "([^"]*)"')
def b_given_i_browse_to_url(step, url):
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'browser': 'ALL'}
    global browser
    browser = WebDriver('http://chrome:4444/wd/hub', d)
    browser.get('http://webserver:8000')

@step(u'When I wait for the browser to render the page')
def b_when_i_wait_for_the_browser_to_render_the_page(step):
    time.sleep(0.1)

@step(u'Then I the browsers URL is "([^"]*)"')
def b_then_i_the_browsers_url_is_url(step, url):
    global browser
    assert browser.current_url == url, 'Browser url = {0}, test url = {1}'.format(browser.current_url, url)

