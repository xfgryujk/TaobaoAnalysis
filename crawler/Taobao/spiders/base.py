# -*- coding: utf-8 -*-

import codecs

import scrapy

from utils.path import CRAWLER_DATA_DIR


class BaseSpider(scrapy.Spider):

    allowed_domains = ('taobao.com',)
    file_title = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.file = codecs.open(self.get_file_path(), 'w', 'utf-8')

    @classmethod
    def get_file_path(cls):
        return '{}/{}.txt'.format(CRAWLER_DATA_DIR, cls.file_title or cls.name)
