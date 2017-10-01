from lettuce import *
#from lxml import html
#from django.test.client import Client
#from nose.tools import assert_equals

#ASDASD

#@before.all
#def set_browser():
#    pass
#    #world.browser = Client()

#@step(r'I access the url "(.*)"')
#def access_url(step, url):
#    response = world.browser.get(url)
#    world.dom = html.fromstring(response.content)

#@step(r'I see the header "(.*)"')
#def see_header(step, text):
#    header = world.dom.cssselect('h1')[0]
#    assert header.text == text

from lettuce import step

@step(u'Given I browse to "([^"]*)"')
def b_given_i_browse_to_group1(step, url):
    assert False, 'This step must be implemented'

@step(u'When I wait for the browser to render the page')
def b_when_i_wait_for_the_browser_to_render_the_page(step):
    assert False, 'This step must be implemented'

@step(u'Then I the browsers URL is "([^"]*)"')
def b_then_i_the_browsers_url_is_group1(step, url):
    assert False, 'This step must be implemented'

