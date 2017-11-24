# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime
from math import ceil

from selenium import webdriver
from selenium.common.exceptions import *

from utils.database import session, Seller, Shop, Item, Review
from utils.path import DATA_DIR, PHANTOM_JS_PATH

logger = logging.getLogger(__name__)


class CommentSpider:
    """
    评论爬虫
    """

    def __init__(self):
        self.logger = logger
        self.driver = webdriver.PhantomJS(executable_path=PHANTOM_JS_PATH)
        self.driver.implicitly_wait(10)

        self.item_id = 0
        self.revbd_elem = None

    @staticmethod
    def gen_start_urls():
        with open(DATA_DIR + '/ItemId.txt') as file:
            for line in file:
                item_id = int(line.strip())
                query = session.query(Item).filter_by(id=item_id)
                if not session.query(query.exists()).scalar():
                    yield 'https://item.taobao.com/item.htm?id=' + str(item_id)
    
    def start_requests(self):
        for url in self.gen_start_urls():
            self.logger.info('Crawling "%s"', url)

            self.driver.get(url)
            self.parse()

            try:
                session.commit()
            except:
                logger.exception('提交数据库时出错：')
                return

    def parse(self):
        try:
            if '//item.taobao.com/item.htm' not in self.driver.current_url:
                self.logger.warning('Unknown page: %s', self.driver.current_url)
                return

            # 解析商店
            if not self.parse_shop():
                return

            # 估计评论页数
            comment_count = int(self.driver.find_element_by_class_name('J_ReviewsCount').text)
            if comment_count == 0:
                self.logger.info('No comment')
                return
            self.logger.info('Estimated max pages %d', ceil(comment_count / 20))

        except:
            logger.exception('获取评论数时出错：')
            return
            
        try:
            # hook JSONP回调
            self.driver.execute_script('jsonp_tbcrate_reviews_list = '
                                       'function(data){ comment_data = data }')
            # 查看评论
            self.driver.find_element_by_css_selector('a.tb-tab-anchor[data-index="1"]').click()
            self.revbd_elem = self.driver.find_element_by_class_name('tb-revbd')
        
        except:
            logger.exception('查看评论时出错：')
            return

        # 解析评论
        page = 0
        while True:
            page += 1
            self.logger.info('Page %d', page)

            if not self.parse_comments():
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
            logger.exception('解析商店时出错：')
            return False

        return True

    def parse_comments(self):
        try:
            # 等待请求结束
            comment_elems = self.revbd_elem.find_elements_by_class_name('J_KgRate_ReviewItem')
            if not comment_elems:
                self.logger.warning('Anti spider!')
                return False
                
            # 取JSONP响应
            comment_data = self.driver.execute_script('return comment_data')
            for comment in comment_data['comments']:
                date = (datetime.strptime(comment['date'], '%Y年%m月%d日 %H:%M')
                        if comment['date'] else None)
                appends = [i['content'] for i in comment['appendList']]
                appends = '\n'.join(appends)
                session.add(Review(  # id=comment['rateId'],  # 有冲突，暂时不用淘宝的ID
                                   raw=json.dumps(comment),
                                   item_id=self.item_id,
                                   rate=comment['rate'],
                                   content=comment['content'],
                                   date=date,
                                   appends=appends,
                                   user_rank=comment['user']['rank'] if comment['user'] else None
                                   ))

        except:
            logger.exception('解析评论时出错：')

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
            logger.exception('转到下一页时出错：')
            return False
            
        return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)-15s [%(name)s] %(levelname)s: %(message)s')
    spider = CommentSpider()
    spider.start_requests()
