# -*- coding: utf-8 -*-

import json
import scrapy
from time import time


class CnkiSpider(scrapy.Spider):
    name = 'cnki'
    allowed_domains = ['cnki.net']
    base_url = 'http://kns.cnki.net/kns/brief/default_result.aspx'
    cookie_url = 'http://kns.cnki.net/KRS/scripts/Recommend.js'
    page_url = 'http://kns.cnki.net/kns/brief/brief.aspx?curpage=2&RecordsPerPage=20&QueryID=7&ID=&turnpage=1&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=listmode&PageName=ASP.brief_default_result_aspx'


    # start_urls = ['http://kns.cnki.net/kns/brief/default_result.aspx']
    t = int(time())
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'kns.cnki.net',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    }
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': headers
    }

    def start_requests(self):

        url = self.base_url
        yield scrapy.Request(url, meta={'cookiejar': 1})

    def parse(self, response):
        url = self.cookie_url
        yield scrapy.Request(url, meta={'cookiejar': response.meta['cookiejar']},
                             callback=self.parse_cookie)

    def parse_cookie(self, response):
        url = self.page_url
        yield scrapy.Request(url, meta={'cookiejar': response.meta['cookiejar']},
                             callback=self.parse_url)

    def parse_url(self, response):
        pass
    #     data = json.loads(response.text)['Rows']
    #     for i in data:
    #         id = i.get('Id', '')
    #         url = self.id_url.format(id)
    #         yield scrapy.Request(url, callback=self.detail)
    #
    # def detail(self, response):
    #     data = dict()
    #     data['url'] = response.url
    #     data['title'] = ''.join(response.xpath('//*[@id="mainArea"]/div[3]/div[1]/h2/text()').extract())
    #     data['author'] = ''.join(response.xpath('//*[@id="mainArea"]/div[3]/div[1]/div[1]/span/a/text()').extract())
    #
    #     yield data

