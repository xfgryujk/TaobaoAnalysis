# -*- coding: utf-8 -*-

import codecs

import scrapy

from utils.path import DATA_DIR


class BaseSpider(scrapy.Spider):

    allowed_domains = ('taobao.com',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.file = codecs.open('{}/{}.txt'.format(DATA_DIR, self.name),
                                'w', 'utf-8')
