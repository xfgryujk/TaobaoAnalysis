# -*- coding: utf-8 -*-

from selenium import webdriver

from .path import PHANTOM_JS_PATH

__driver = webdriver.PhantomJS(executable_path=PHANTOM_JS_PATH)
__driver.get('about:blank')


def execute(*js):
    return __driver.execute_script(';'.join(js))
