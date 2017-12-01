# -*- coding: utf-8 -*-

import codecs

from scrapy import Spider

from utils.path import CRAWLER_DATA_DIR


class BaseSpider(Spider):
    """
    所有淘宝Scrapy爬虫基类，定义通用属性和储存文件路径
    """

    allowed_domains = ('taobao.com',)
    file_title = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.file = codecs.open(self.get_file_path(), 'w', 'utf-8')

    @classmethod
    def get_file_path(cls):
        return '{}/{}.txt'.format(CRAWLER_DATA_DIR, cls.file_title or cls.name)
