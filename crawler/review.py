# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime
from math import ceil

from selenium import webdriver
from selenium.common.exceptions import *

from crawler.Taobao.spiders.item_id import ItemIdFromHomePageSpider
from utils.database import session, Seller, Shop, Item, Review

logger = logging.getLogger('ReviewSpider')


class ReviewSpider:
    """
    评论爬虫
    需要已有商品ID
    由于取评论用的参数中UserAction算法未知，使用了PhantomJS爬取评论
    需要PhantomJS在环境变量path里
    """

    def __init__(self):
        self.logger = logger
        self.driver = webdriver.PhantomJS()
        self.driver.implicitly_wait(10)

        self.item_id = 0
        self.revbd_elem = None

    @staticmethod
    def gen_start_urls():
        with open(ItemIdFromHomePageSpider.get_file_path()) as file:
            for line in file:
                item_id = int(line.strip())
                query = session.query(Item).filter_by(id=item_id)
                if not session.query(query.exists()).scalar():
                    yield 'https://item.taobao.com/item.htm?id=' + str(item_id)
    
    def start_requests(self):
        for url in self.gen_start_urls():
            self.logger.info('正在爬 "%s"', url)

            self.driver.get(url)
            self.parse()

            try:
                session.commit()
            except:
                self.logger.exception('提交数据库时出错：')
                return

    def parse(self):
        try:
            if '//item.taobao.com/item.htm' not in self.driver.current_url:
                self.logger.warning('未知的页面 "%s"', self.driver.current_url)
                return

            # 解析商店
            if not self.parse_shop():
                return

            # 估计评论页数
            review_count = int(self.driver.find_element_by_class_name('J_ReviewsCount').text)
            if review_count == 0:
                self.logger.info('无评论')
                return
            self.logger.info('估计最大页数：%d', ceil(review_count / 20))

        except:
            self.logger.exception('获取评论数时出错：')
            return
            
        try:
            # hook JSONP回调
            self.driver.execute_script('jsonp_tbcrate_reviews_list = '
                                       'function(data){ review_data = data }')
            # 查看评论
            self.driver.find_element_by_css_selector('a.tb-tab-anchor[data-index="1"]').click()
            self.revbd_elem = self.driver.find_element_by_class_name('tb-revbd')
        
        except:
            self.logger.exception('查看评论时出错：')
            return

        # 解析评论
        page = 0
        while True:
            page += 1
            self.logger.info('%d', page)

            if not self.parse_reviews():
                break
            if not self.go_to_next_page():
                break

    def parse_shop(self):
        try:
            # 卖家
            data = self.driver.execute_script('return g_config.idata')
            seller_id = int(data['seller']['id'])
            query = session.query(Seller).filter_by(id=seller_id)
            if not session.query(query.exists()).scalar():
                session.add(Seller(id=seller_id,
                                   age=data['seller']['shopAge']
                                   ))

            # 商店
            shop_id = int(data['shop']['id'])
            query = session.query(Shop).filter_by(id=shop_id)
            if not session.query(query.exists()).scalar():
                session.add(Shop(id=shop_id,
                                 url=data['shop']['url'],
                                 seller_id=seller_id
                                 ))

            # 商品
            self.item_id = int(data['item']['id'])
            session.add(Item(id=self.item_id,
                             title=data['item']['title'],
                             shop_id=shop_id
                             ))

        except:
            self.logger.exception('解析商店时出错：')
            return False

        return True

    def parse_reviews(self):
        try:
            # 等待请求结束
            review_elems = self.revbd_elem.find_elements_by_class_name('J_KgRate_ReviewItem')
            if not review_elems:
                self.logger.warning('被反爬虫了！')
                return False
                
            # 取JSONP响应
            review_data = self.driver.execute_script('return review_data')
            for review in review_data['comments']:
                date = (datetime.strptime(review['date'], '%Y年%m月%d日 %H:%M')
                        if review['date'] else None)
                appends = [i['content'] for i in review['appendList']]
                appends = '\n'.join(appends)
                session.add(Review(  # id=review['rateId'],  # 有冲突，暂时不用淘宝的ID
                                   raw=json.dumps(review),
                                   item_id=self.item_id,
                                   rate=review['rate'],
                                   content=review['content'],
                                   date=date,
                                   appends=appends,
                                   user_rank=review['user']['rank'] if review['user'] else None
                                   ))

        except:
            self.logger.exception('解析评论时出错：')

        return True

    def go_to_next_page(self):
        try:
            next_elem = self.revbd_elem.find_element_by_class_name('pg-next')
            if 'pg-disabled' in next_elem.get_attribute('class'):
                return False
            next_elem.click()
            
        except NoSuchElementException:  # 只有1页
            return False

        except:
            self.logger.exception('转到下一页时出错：')
            return False
            
        return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)-15s [%(name)s] %(levelname)s: %(message)s')
    spider = ReviewSpider()
    spider.start_requests()
