# -*- coding: utf-8 -*-

"""
主要用来解析JSON不支持的JS对象
需要PhantomJS在环境变量path里
"""

from selenium import webdriver

__driver = webdriver.PhantomJS()
__driver.get('about:blank')


def execute(*js):
    """
    执行JS代码
    尽量一次传入多条代码
    如果要取返回值，代码中必须有return
    """

    return __driver.execute_script(';'.join(js))
