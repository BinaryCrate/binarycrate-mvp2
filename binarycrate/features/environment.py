from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver

def before_all(context):
    """
	desired_capabilities = webdriver.DesiredCapabilities.FIREFOX
	desired_capabilities['version'] = 'latest'
	desired_capabilities['platform'] = 'WINDOWS'
	desired_capabilities['name'] = 'Testing Selenium with Behave'
	desired_capabilities['client_key'] = 'key'
	desired_capabilities['client_secret'] = 'secret'

	context.browser = webdriver.Remote(
		desired_capabilities=desired_capabilities,
		command_executor="https://hub.testingbot.com/wd/hub"
	)
    """
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'browser': 'ALL'}
    #global browser
    context.browser = WebDriver('http://chrome:4444/wd/hub', d)


def after_all(context):
	context.browser.quit()
