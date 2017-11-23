# -*- coding: utf-8 -*-

import codecs
import json

from utils.path import DATA_DIR
from .base import BaseSpider


def gen_start_urls():
    tce_sids = []
    tce_vids = []
    with codecs.open(DATA_DIR + '/TceId.txt', 'r', 'utf-8') as file:
        for line in file:
            data = json.loads(line)
            tce_sids.append(data[0])
            tce_vids.append(data[1])
    size = len(tce_sids)

    for start in range(0, size, 20):  # 每次最多20个
        end = min(start + 20, size)
        url = ('https://tce.taobao.com/api/mget.htm?'
               'callback=jsonp123&tce_sid={0}&tce_vi'
               'd={1}&tid={2}&tab={2}&topic={2}&coun'
               't={2}'
               ).format(','.join(tce_sids[start:end]),
                        ','.join(tce_vids[start:end]),
                        ',' * (end - start)
                        )
        yield url


class ItemIdSpider(BaseSpider):
    """
    商品ID爬虫
    """

    name = 'ItemId'
    start_urls = gen_start_urls()

    def parse(self, response):
        data = response.text[response.text.find('{'):
                             response.text.rfind('}') + 1]
        data = json.loads(data)
        
        # if 'result' not in data:
        #     return
        for tce in data['result'].values():
            for item in tce['result']:
                if ('auction_id' not in item
                   or item['auction_id'] == '0'):
                    continue
                self.file.write(item['auction_id'])
                self.file.write('\n')
