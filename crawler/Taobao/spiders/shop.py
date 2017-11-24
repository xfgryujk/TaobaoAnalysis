# -*- coding: utf-8 -*-

from scrapy import Spider

from utils.database import session, Seller, Shop, Item
from utils.js_parser import execute


def gen_start_urls():
    for result, in session.query(Item.id).filter(Item.shop_id == None):
        yield 'https://item.taobao.com/item.htm?id=' + str(result)


class ShopSpider(Spider):
    """
    补充Item的商店信息
    """

    name = 'Shop'
    start_urls = gen_start_urls()

    def parse(self, response):
        js = response.xpath('/html/head/script[1]/text()').extract_first()
        data = execute(js, 'return g_config.idata')
        if not data:
            self.logger.warning('No idata on "%s"', response.url)
            return

        seller_id = int(data['seller']['id'])
        query = session.query(Seller).filter_by(id=seller_id)
        if not session.query(query.exists()).scalar():
            session.add(Seller(id=seller_id,
                               age=data['seller']['shopAge']
                               ))

        shop_id = int(data['shop']['id'])
        query = session.query(Shop).filter_by(id=shop_id)
        if not session.query(query.exists()).scalar():
            session.add(Shop(id=shop_id,
                             url=data['shop']['url'],
                             seller_id=seller_id
                             ))

        item = session.query(Item).filter_by(id=int(data['item']['id'])).one()
        item.shop_id = shop_id

        session.commit()
