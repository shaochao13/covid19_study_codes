import json
import re

import scrapy


class DxySpider(scrapy.Spider):
    # 表示爬虫的名称，在项目中须唯一
    name = 'dxy'
    # 表示这个爬虫可以从哪些域名下抓取数据
    allowed_domains = ['dxy.cn', 'dxycdn.com']
    # 表示当启动这个爬虫的时候会请求的url
    start_urls = ['http://ncov.dxy.cn/ncovh5/view/pneumonia']

    def parse(self, response):
        # 1从返回对象中取值
        # 取值方式：
        # 1.1 response.xpath()
        # data_txt = response.xpath('//script[@id="getListByCountryTypeService2true"]/text()').get()
        # print(data_txt)
        # 1.2 response.css()
        data_txt = response.css('#getListByCountryTypeService2true::text').get()


        # 2 清洗数据
        # 2.1 通过正则匹配出“[]”中的字符串
        data_txt = re.findall('\[.+\]', data_txt)[0]
        # 2.2 通过json模块，将字符串转换化为python对象，在这里为list
        data = json.loads(data_txt)

        # 3 保存数据
        with  open('datas/last_updated_dxy_datas.json', 'w+') as f:
            json.dump(data, f, ensure_ascii=False)

        for d in data:
            url = d['statisticsData']
            yield scrapy.Request(url, callback=self.country_history_data_parse, meta=d)

    def country_history_data_parse(self, response):
        meta = response.meta['provinceName']
        data = response.json()
        with open(f'datas/countries/{meta}.json', 'w+') as f:
            json.dump(data, f, ensure_ascii=False)
