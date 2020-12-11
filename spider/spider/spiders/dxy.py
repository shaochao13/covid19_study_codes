import json
# import os
import pathlib
import re

import scrapy
from spider.items import SpiderItem


class DxySpider(scrapy.Spider):
    # 表示爬虫的名称，在项目中须唯一
    name = 'dxy'
    # 表示这个爬虫可以从哪些域名下抓取数据
    allowed_domains = ['dxy.cn', 'dxycdn.com']
    # 表示当启动这个爬虫的时候会请求的url
    start_urls = ['http://ncov.dxy.cn/ncovh5/view/pneumonia']

    def parse(self, response):
        print('.......')
        # 1从返回对象中取值
        # 取值方式：
        # 1.1 response.xpath()
        # data_txt = response.xpath('//script[@id="getListByCountryTypeService2true"]/text()').get()
        # print(data_txt)
        # 1.2 response.css()
        data_txt = response.css('#getListByCountryTypeService2true::text').get()
        # print(f'工作目录：{os.getcwd()}')

        # 2 清洗数据
        # 2.1 通过正则匹配出“[]”中的字符串
        data_txt = re.findall('\[.+\]', data_txt)[0]
        # 2.2 通过json模块，将字符串转换化为python对象，在这里为list
        data = json.loads(data_txt)

        item = SpiderItem()
        item['is_last_updated'] = True
        item['data'] = data
        yield item

        # 3 保存数据
        # with  open('datas/last_updated_dxy_datas.json', 'w+') as f:
        #     json.dump(data, f, ensure_ascii=False)

        # 循环 data 得到 每个国家的历史疫情数据 URL
        for country_data in data:
            # 表示 各国家 的历史疫情数据 URL
            url = country_data['statisticsData']
            #国家或地区名称
            country_name = country_data['provinceName']
            countryShortCode = country_data['countryShortCode']
            # 发起请求
            yield scrapy.Request(url, callback=self.country_history_data_parse, meta={'country_name' : country_name, 'countryShortCode': countryShortCode})


    # 响应历史数据请求返回结果
    def country_history_data_parse(self, response):
        # 取出返回结果
        # 通过 response.json()
        data = response.json()
        # 历史疫情数据
        data = data.get('data')

        # 得到 META 中的 country_name的值
        country_name = response.meta['country_name']
        countryShortCode = response.meta['countryShortCode']

        # 循环 历史数据，给每一条数据添加一个country_name 字段，以标注它是属于哪一个国家的数据
        for d in data:
            d['country_name'] = country_name
            d['countryShortCode'] = countryShortCode

        # file_path = f'datas/countries/{country_name}.json'
        # #文件的上一级路径
        # parent_path = pathlib.PosixPath(file_path).parent
        # # 如果文件的上一级不存在，则创建
        # if not parent_path.exists():
        #     #进行㠌套创建目录
        #     parent_path.mkdir(parents=True)
        # # # 保存数据
        # with open(file_path, 'w+') as f:
        #     json.dump(data, f, ensure_ascii=False)

        # 通过 Pipeline 方式进行数据的统一保存
        item = SpiderItem()
        item['is_last_updated'] = False
        item['data'] = data
        yield item




