# -*- coding: utf-8 -*-
import scrapy


class CnkiSpider(scrapy.Spider):
    name = 'cnki'
    allowed_domains = ['cnki.net']
    base_url = 'http://kns.cnki.net{}'
    start_urls = ['http://nvsm.cnki.net/kns/brief/brief.aspx?curpage={}&RecordsPerPage=20&QueryID=14&ID=&turnpage=1' \
                  '&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=listmode&PageName=ASP.' \
                  'brief_default_result_aspx&isinEn=1'.format(i)
                  for i in range(1, 3)]
    Cookie = {
        'RsPerPage': '20',
        'cnkiUserKey': '742cdeeb-0019-4ac7-bd6e-5e86559a7c97',
        '_pk_ref': '%5B%22%22%2C%22%22%2C1522721459%2C%22http%3A%2F%2Fwww.cnki.net%2F%22%5D',
        '_pk_id': '2de4e639-84b6-4a7c-89cb-dc9cedcb11dc.1522721459.1.1522721603.1522721459.',
        'ASP.NET_SessionId': 'ua1iawyev3hdwnfwcmg1mf1e',
        'Ecp_IpLoginFail': '18040447.74.181.237',
        'SID_kns': '011102',
        'KNS_SortType': '',
        'DisplaySave': '3',
    }

    def start_requests(self):
        for i in range(1, 3):  # max 300
            headers = {'referer': 'http://nvsm.cnki.net/kns/brief/default_result.aspx'}
            url = 'http://nvsm.cnki.net/kns/brief/brief.aspx?curpage={}&RecordsPerPage=20&' \
                  'QueryID=14&ID=&turnpage=1&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=' \
                  'listmode&PageName=ASP.brief_default_result_aspx&isinEn=1'
            yield scrapy.Request(url.format(i), headers=headers, cookies=self.Cookie)

    def parse(self, response):
        for i in response.xpath('//table[@class="GridTableContent"]/tr')[1:]:
            url = ''.join(i.xpath('td[2]/a/@href').extract()).replace('kns', 'KCMS')
            yield scrapy.Request(self.base_url.format(url), callback=self.get_detail)

    def get_detail(self, response):
        data = dict()
        data['url'] = response.url
        data['title'] = ''.join(response.xpath('//*[@id="mainArea"]/div[3]/div[1]/h2/text()').extract())
        data['author'] = ''.join(response.xpath('//*[@id="mainArea"]/div[3]/div[1]/div[1]/span/a/text()').extract())
        pass

