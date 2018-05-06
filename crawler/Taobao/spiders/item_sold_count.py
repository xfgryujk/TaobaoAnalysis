# -*- coding: utf-8 -*-

import json

import re
from scrapy import Spider, Request

from utils.database import session, Item


class SoldCountSpider(Spider):
    """
    补充之前未爬的销量
    """

    name = 'SoldCount'
    allowed_domains = ('taobao.com',)

    def start_requests(self):
        for item in session.query(Item).filter(Item.sold_count.is_(None)):
            url = ('https://detailskip.taobao.com/service/getData/1/p1'
                   '/item/detail/sib.htm?itemId={}&sellerId={}&modules'
                   '=soldQuantity&callback=onSibRequestSuccess'
                   ).format(item.id, item.shop.seller_id)
            headers = {
                'referer': 'https://item.taobao.com/item.htm?id=' + str(item.id)
            }
            yield Request(url, dont_filter=True, headers=headers)

    def parse(self, response):
        data = response.text[response.text.find('{'):
                             response.text.rfind('}') + 1]
        data = json.loads(data)
        sold_quantity = data['data']['soldQuantity']

        match = re.search(r'itemId=(\d+)', response.url)
        if not match:
            return
        item = session.query(Item).filter_by(id=match[1]).first()

        item.sold_count = sold_quantity['soldTotalCount']
        item.confirm_count = sold_quantity['confirmGoodsCount']
        session.commit()
