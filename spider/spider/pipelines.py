# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import json

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SpiderPipeline:

    # 表示当项目启动时，会执行一次，中间不再执行
    def open_spider(self, spider):
        # 用来保存所有国家的疫情历史数据
        self.datas = []

    # 表示每次收到 item 返回时，都会执行
    def process_item(self, item, spider):
        # 只需要将 item['data'] 的数据 添加到 self.datas 中即可
        self.datas.extend(item['data'])
        return item


    # 表示当项目执行结束时，会调用
    def close_spider(self, spider):
        # 将所有的数据，self.datas 保存到文件中即可
        with open('datas/all_countris_datas.json', 'w+') as f:
            json.dump(self.datas, f, ensure_ascii=False)
