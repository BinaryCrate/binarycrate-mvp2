from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver
import time

@given(u'I browse to "{url}"')
def step_impl(context, url):
    context.browser.get(url)

@when(u'I wait for the browser to render the page')
def b_when_i_wait_for_the_browser_to_render_the_page(context):
    time.sleep(0.1)

@then(u'I the browsers URL is "{url}"')
def b_then_i_the_browsers_url_is_url(context, url):
    assert context.browser.current_url == url, 'Browser url = {0}, test url = {1}'.format(context.browser.current_url, url)

