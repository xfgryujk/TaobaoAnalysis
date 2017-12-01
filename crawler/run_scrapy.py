# -*- coding: utf-8 -*-

"""
方便启动和调试Scrapy爬虫的脚本
用法：run_scrapy.py spider_name
"""

from sys import argv

from scrapy.cmdline import execute

if __name__ == '__main__':
    if len(argv) != 2:
        print('用法：run_scrapy.py spider_name')
    else:
        execute(['scrapy', 'crawl', argv[1]])
