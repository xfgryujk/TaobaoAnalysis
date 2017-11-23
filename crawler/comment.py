# -*- coding: utf-8 -*-

import codecs
import json
import math
import re

from selenium import webdriver
from selenium.common.exceptions import *

from utils.path import DATA_DIR, COMMENTS_DIR


def gen_start_urls():
    with codecs.open(DATA_DIR + '/ItemId.txt', 'r', 'utf-8') as file:
        for line in file:
            yield 'https://item.taobao.com/item.htm?id=' + line.strip()


class CommentSpider:
    """
    评论爬虫，仿Scrapy风格
    """

    name = 'Comment'
    start_urls = gen_start_urls()
    
    def start_requests(self):
        driver = webdriver.PhantomJS(executable_path=r'F:\WebDriver\phantomjs-2.1.1-windows\bin\phantomjs.exe')
        driver.implicitly_wait(10)
        try:
            for url in self.start_urls:
                print('Crawling "{}"'.format(url))
                driver.get(url)
                self.parse_item(driver)
            
            return []
            
        finally:
            driver.close()

    def parse_item(self, driver):
        try:
            if '//item.taobao.com/item.htm' not in driver.current_url:
                print('Unknown page')
                return
            
            comment_count = int(driver.find_element_by_class_name('J_ReviewsCount').text)
            if comment_count == 0:
                print('No comment')
                return
            print('Estimated max pages', math.ceil(comment_count / 20))
        
        except Exception as e:
            print(e)
            
        try:
            # hook JSONP回调
            driver.execute_script('jsonp_tbcrate_reviews_list = '
                                  'function(data){ comment_data = data }')
            # 查看评论
            driver.find_element_by_css_selector('a.tb-tab-anchor[data-index="1"]').click()
            revbd_elem = driver.find_element_by_class_name('tb-revbd')
        
        except Exception as e:
            print(e)
            return
        
        with codecs.open(self.get_filename(driver), 'w', 'utf-8') as file:
            page = 0
            while True:
                page += 1
                print('Page', page)
                
                if not self.parse_comments(driver, revbd_elem, file):
                    break
                if not self.go_to_next_page(revbd_elem):
                    break

    @staticmethod
    def get_filename(driver):
        replace = {
            '\\': '＼',
            '/': '／',
            ':': '：',
            '*': '＊',
            '?': '？',
            '"': "'",
            '<': '＜',
            '>': '＞',
            '|': '｜'
        }
        title = driver.title
        for k, v in replace.items():
            title = title.replace(k, v)
            
        return '{}/{} {}.txt'.format(
                COMMENTS_DIR,
                re.findall(r'[\?&]id=(\d+)', driver.current_url)[0],
                title
            )

    @staticmethod
    def parse_comments(driver, revbd_elem, file):
        try:
            # 等待请求结束
            comment_elems = revbd_elem.find_elements_by_class_name('J_KgRate_ReviewItem')
            if not comment_elems:
                print('Anti spider!')
                return False
                
            # 取JSONP响应
            comment_data = driver.execute_script('return comment_data')
            json.dump(comment_data, file)
            file.write('\n')
            
        except Exception as e:
            print(e)
        
        return True

    @staticmethod
    def go_to_next_page(revbd_elem):
        try:
            next_elem = revbd_elem.find_element_by_class_name('pg-next')
            if 'pg-disabled' in next_elem.get_attribute('class'):
                return False
            next_elem.click()
            
        except NoSuchElementException:  # 只有1页
            return False
        except Exception as e:
            print(e)
            return False
            
        return True


if __name__ == '__main__':
    spider = CommentSpider()
    spider.start_requests()
