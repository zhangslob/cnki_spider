# -*- coding: utf-8 -*-

import json
import scrapy
from time import time


class CnkiSpider(scrapy.Spider):
    name = 'cnki'
    allowed_domains = ['cnki.net']
    base_url = 'http://kns.cnki.net'
    id_url = 'http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CJFQ&dbname=CJFDTEMP&filename={}'
    # start_urls = ['http://kns.cnki.net/kns/brief/default_result.aspx']
    t = int(time())
    headers = {
    'ip': "127.0.0.1",
    'sign': "4f07c0eb90f194803aeee9783abe781b5e3da611",
    'location': "0,0",
    'app_id': "cnki_cajcloud",
    'did': "{123456}",
    'timestamp': t,
    'host': "api2.cnki.net",
    'connection': "Keep-Alive",
    'accept-encoding': "gzip",
    'user-agent': "okhttp/2.7.5",
    'cache-control': "no-cache",
    }
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': headers
    }

    def start_requests(self):

        url = 'http://api2.cnki.net/v20/api/db/Literature%7BCJFD%2CCDFD%2CCMFD%2CCPFD%7D?fields=Source,Contributor,Creator,Title,UpdateDate,SubjectCode,SubjectSubColumnCode,CitedTimes,DownloadedTimes,Date,Summary,IsPublishAhead,Year,Issue,CoreJournal,SourceCode,FILETYPE&query=Subject+like+XLS%28%27%E6%B5%99%E6%B1%9F+%E5%88%9B%E6%96%B0+%E5%8C%BA%E5%9F%9F%27%29+or+Title+eq+XLS%28%27%E6%B5%99%E6%B1%9F+%E5%88%9B%E6%96%B0+%E5%8C%BA%E5%9F%9F%27%29+and+Date+Ge+%272013-04-09%27+&group=&order=Date+desc&start=30&length=15'
        yield scrapy.Request(url, meta={'cookiejar': 1})

    def parse(self, response):
        data = json.loads(response.text)['Rows']
        for i in data:
            id = i.get('Id', '')
            url = self.id_url.format(id)
            yield scrapy.Request(url, callback=self.detail)

    def detail(self, response):
        data = dict()
        data['url'] = response.url
        data['title'] = ''.join(response.xpath('//*[@id="mainArea"]/div[3]/div[1]/h2/text()').extract())
        data['author'] = ''.join(response.xpath('//*[@id="mainArea"]/div[3]/div[1]/div[1]/span/a/text()').extract())

        yield data

