#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import requests

from scrapy.selector import Selector


default_headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) '
                      'Version/11.0 Mobile/15A372 Safari/604.1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }


class CnkiSpier(object):

    def __init__(self, *args):
        self.session = requests.session()
        self.session.headers.update(default_headers)
        # self.session.proxies = {''}
        self.kw = list(args)
        self.payload = 'searchtype=0&pageindex={}&pagesize=10&keyword={}&fieldtype=101&sorttype=0&articletype=-1&screentype=0'
        self.search_url = 'http://wap.cnki.net/touch/web/Article/Search'

    def _get_index(self):
        self.session.get('http://wap.cnki.net/touch/web', timeout=15)

    def _get_page_count(self, kw):
        url = 'http://wap.cnki.net/touch/web/Article/Search/?kw={}&field=5'.format(kw)
        response = self.session.request('GET', url, timeout=15)
        total_count = re.findall('<span id=\"totalcount\">(\d+)<\/span>', response.text)[0]
        return total_count

    def _get_detail_info(self, url):
        pass

    def run(self):
        self._get_index()

        for kw in self.kw:
            count = self._get_page_count(kw)
            all_page = int(count) // 10 + 2
            for page in range(1, all_page):
                data = self.payload.format(page, kw)
                response = self.session.request('POST', self.search_url, data=data)
                s = Selector(text=response)
                detail_url = s.xpath('//div[@class="c-company__body-item"]/')
        pass


if __name__ == '__main__':
    c = CnkiSpier('p', 'a')

