#coding:utf-8
import sys
import os
import traceback
import logging
logger = logging.getLogger(__name__)

from time import sleep

import time

# from selenium.webdriver import Firefox
from seleniumrequests import Firefox
from selenium.webdriver import FirefoxOptions
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class SeleConf(object):
    executable_path_linux = 'framework/components/fetchers/fetchlib/bin/geckodriver'
    executable_path_win = r'framework\components\fetchers\fetchlib\bin\geckodriver.exe'


def get_cookies(browser, url):
    browser.implicitly_wait(15)

    logger.info('Getting first time')
    browser.get(url)
    logger.info('Get done')
    # ret = browser.page_source
    # time.sleep(0.1)

    logger.info('Getting second time')
    # browser.get(url)
    # ret = browser.page_source

    # resp = browser.request('GET', url)
    browser.get(url)

    logger.info('Getting done')

    cookies = browser.get_cookies()

    s = []
    for cookie in cookies:
        s.append(cookie['name'] + '=' + cookie['value'])

    cookies = ';'.join(s)

    logger.info(cookies)

    return cookies


class SeleLib(object):

    def __init__(self):
        self.is_win = self.is_windows()
        logger.info('is windows:' + str(self.is_win))

        self.display = None

    def is_windows(self):
        if sys.platform == 'win32':
            return True
        else:
            return False

    def v_display(self):
        from pyvirtualdisplay import Display
        window_size = (800, 600)
        display = Display(visible=0, size=window_size)
        self.display = display

        logger.info('Starting virtual display')
        display.start()

    def browser_in_linux(self, url, callback):
        # log_file = open('/home/las/spider/firefox.log', 'w+')
        # binary = FirefoxBinary("/usr/bin/firefox", log_file=log_file)
        self.v_display()

        firefox_capabilities = DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = False

        fireFoxOptions = FirefoxOptions()
        fireFoxOptions.set_headless()

        executable_path = SeleConf.executable_path_linux

        assert os.path.exists(executable_path)

        try:
            browser = Firefox(
                # firefox_binary=binary,
                executable_path=executable_path,
                firefox_options=fireFoxOptions,
                capabilities=firefox_capabilities,

                # firefox_profile=profile
            )
        except Exception, e:
            logger.error(traceback.format_exc())
            return

        res = callback(browser, url)

        browser.close()
        try:
            browser.quit()
        except:
            logger.error(traceback.format_exc())

        try:
            logger.info('Closing virtual display')

            display = self.display
            os.system('kill -15 ' + str(display.pid))
            display.sendstop()
            display.popen.kill()
            display.popen.terminate()
            display.stop()
        except:
            logger.error(traceback.format_exc())

        return res

    def browser_in_win(self, url, callback):
        fireFoxOptions = FirefoxOptions()
        fireFoxOptions.set_headless()

        executable_path = SeleConf.executable_path_win

        assert os.path.exists(executable_path)
        try:
            browser = Firefox(
                executable_path=executable_path,
                firefox_options=fireFoxOptions,
            )
        except Exception, e:
            logger.error(traceback.format_exc())
            return

        res = callback(browser, url)

        browser.close()
        try:
            browser.quit()
        except:
            logger.error(traceback.format_exc())

        return res

    def browser(self, url, callback):
        if self.is_win:
            return self.browser_in_win(url, callback)
        else:
            return self.browser_in_linux(url, callback)

    def get_cookies(self, url):
        cookies = self.browser(url, get_cookies)
        return cookies




