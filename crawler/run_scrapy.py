# -*- coding: utf-8 -*-

from sys import argv

from scrapy.cmdline import execute

if __name__ == '__main__':
    if len(argv) != 2:
        print('用法：run_scrapy.py spider_name')
    else:
        execute(['scrapy', 'crawl', argv[1]])
