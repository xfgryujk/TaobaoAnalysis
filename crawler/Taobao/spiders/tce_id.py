# -*- coding: utf-8 -*-

from .base import BaseSpider
import json


class TceIdSpider(BaseSpider):
    """
    小分类ID爬虫
    """

    name = 'TceId'
    start_urls = (
        'https://www.taobao.com/markets/nvzhuang/taobaonvzhuang',
        'https://www.taobao.com/markets/nanzhuang/2017new',
        'https://neiyi.taobao.com',
        'https://www.taobao.com/markets/xie/nvxie/index',
        'https://www.taobao.com/markets/bao/xiangbao',
        'https://pei.taobao.com',
        'https://www.taobao.com/markets/qbb/index?spm=a21bo.50862.201879-item-1008.5.YrbXb6&pvid=b9f2df4c-6d60-4af4-b500-c5168009831f&scm=1007.12802.34660.100200300000000',
        'https://www.taobao.com/markets/qbb/index?spm=a21bo.50862.201867-main.8.mL7cax&pvid=b9f2df4c-6d60-4af4-b500-c5168009831f&scm=1007.12802.34660.100200300000000',
        'https://www.taobao.com/markets/qbb/index?spm=a21bo.50862.201867-main.8&pvid=b9f2df4c-6d60-4af4-b500-c5168009831f&scm=1007.12802.34660.100200300000000',
        'https://www.taobao.com/markets/jiadian/index',
        'https://www.taobao.com/markets/3c/shuma',
        'https://www.taobao.com/markets/3c/sj',
        'https://mei.taobao.com/',
        'https://www.taobao.com/market/baihuo/xihuyongpin.php?spm=a217u.7383845.a214d5z-static.49.e8DQmz',
        'https://g.taobao.com/brand_detail.htm?navigator=all&_input_charset=utf-8&q=%E8%90%A5%E5%85%BB%E5%93%81&spm=a21bo.50862.201867-links-4.54.oMw9IU',
        'https://www.taobao.com/market/peishi/zhubao.php',
        'https://www.taobao.com/market/peishi/yanjing.php?spm=a219r.lm5630.a214d69.14.CkLAJ7',
        'https://www.taobao.com/market/peishi/shoubiao.php',
        'https://www.taobao.com/markets/coolcity/coolcityHome',
        'https://www.taobao.com/markets/coolcity/coolcityHome',
        'https://www.taobao.com/markets/amusement/home',
        'https://game.taobao.com',
        'https://www.taobao.com/markets/acg/dongman',
        'https://www.taobao.com/markets/acg/yingshi',
        'https://chi.taobao.com',
        'https://chi.taobao.com',
        'https://chi.taobao.com',
        'https://s.taobao.com/search?q=%E5%9B%AD%E8%89%BA&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.50862.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170419',
        'https://s.taobao.com/search?ie=utf8&initiative_id=staobaoz_20170419&stats_click=search_radio_all%3A1&js=1&imgfile=&q=%E8%BF%9B%E5%8F%A3%E7%8B%97%E7%B2%AE&suggest=history_3&_input_charset=utf-8&wq=&suggest_query=&source=suggest',
        'https://s.taobao.com/search?q=%E5%86%9C%E8%B5%84&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.50862.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170221',
        'https://fang.taobao.com/',
        'https://s.taobao.com/list?spm=a21bo.50862.201867-links-10.27.iQWRJS&source=youjia&cat=50097129',
        'https://www.jiyoujia.com/markets/youjia/zhuangxiucailiao',
        'https://s.taobao.com/list?spm=a21bo.7932212.202572.1.rtUtMQ&source=youjia&q=%E5%AE%B6%E5%85%B7',
        'https://s.taobao.com/list?source=youjia&cat=50065206%2C50065205',
        'https://s.taobao.com/list?spm=a21bo.50862.201867-links-11.80.K6jN68&source=youjia&cat=50008163&bcoffset=0&s=240',
        'https://car.tmall.com/wow/car/act/carfp',
        'https://2car.taobao.com/',
        'https://car.tmall.com/wow/car/act/carfp',
        'https://www.taobao.com/markets/bangong/pchome',
        'https://www.taobao.com/markets/dingzhi/home',
        'https://wujin.taobao.com/',
        'https://s.taobao.com/list?source=youjia&q=%E7%99%BE%E8%B4%A7',
        'https://s.taobao.com/list?source=youjia&cat=50035867&bcoffset=0&s=240',
        'https://www.taobao.com/market/jiadian/baojian.php?spm=a21bo.50862.201867-main.46.K6jN68',
        'https://xue.taobao.com',
        'https://ka.taobao.com/',
        'https://s.taobao.com/list?q=%E4%B8%8A%E9%97%A8%E6%9C%8D%E5%8A%A1&cat=50097750'
    )

    def parse(self, response):
        data = response.xpath('//div[@tms-data]/@tms-data').extract()
        data = [json.loads(cur_data) for cur_data in data]
        
        tce_ids = []
        for cur_data in data:
            for key in cur_data:
                if not key.startswith('items'):
                    continue
                for item in cur_data[key]:
                    if not ('tms_type' in item 
                            and item['tms_type'] == 'jsonp'):
                        continue
                    tce_ids.append([
                        str(item['data_para']['tce_sid']),
                        item['data_para']['tce_vid']
                    ])
                        
        if not tce_ids:
            self.logger.warning('No tce_id on "%s"', response.url)
        else:
            for tce_id in tce_ids:
                json.dump(tce_id, self.file)
                self.file.write('\n')
