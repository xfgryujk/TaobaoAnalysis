# -*- coding: utf-8 -*-

from selenium import webdriver

__driver = webdriver.PhantomJS()
__driver.get('about:blank')


def execute(*js):
    return __driver.execute_script(';'.join(js))
