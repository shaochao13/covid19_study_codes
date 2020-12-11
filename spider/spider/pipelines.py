# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import json
import pymysql

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SpiderPipeline:

    def __init__(self):
        self.connect = pymysql.connect(
            host="192.168.0.88",
            port=3307,
            db="coronavirus",
            user="test",
            passwd="123456@abcABC",
            charset='utf8',
            use_unicode=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        # 通过cursor执行增删查改
        self.cursor = self.connect.cursor()

    # # 表示当项目启动时，会执行一次，中间不再执行
    # def open_spider(self, spider):
    #     # 用来保存所有国家的疫情历史数据
    #     self.datas = []

    # 表示每次收到 item 返回时，都会执行
    def process_item(self, item, spider):

        is_last_updated = item['is_last_updated']
        if is_last_updated:
            for d in item['data']:
                self.cursor.execute(
                    '''INSERT INTO tb_virus_last_updated_data(
                                    provinceName,
                                    countryShortCode,
                                    confirmedCount,
                                    currentConfirmedCount,
                                    curedCount,
                                    deadCount)
                                    VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE  confirmedCount = %s,
                                    currentConfirmedCount = %s,
                                    curedCount = %s,
                                    deadCount = %s;'''
                                    ,
                                    (
                                        d['provinceName'],
                                        d['countryShortCode'],
                                        d['confirmedCount'],
                                        d['currentConfirmedCount'],
                                        d['curedCount'],
                                        d['deadCount'],

                                        d['confirmedCount'],
                                        d['currentConfirmedCount'],
                                        d['curedCount'],
                                        d['deadCount']
                                    )
                )
        else:
            # 只需要将 item['data'] 的数据 添加到 self.datas 中即可
            # self.datas.extend(item['data'])

            # 添加数据保存到数据库的逻辑代码
            for d in item['data']:
                self.cursor.execute(
                    '''INSERT INTO tb_virus_history_data(
                                    countryShortCode_dateId,
                                    dateId,
                                    country_name,
                                    countryShortCode,
                                    confirmedCount,
                                    currentConfirmedCount,
                                    curedCount,
                                    deadCount)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE  confirmedCount = %s,
                                    currentConfirmedCount = %s,
                                    curedCount = %s,
                                    deadCount = %s;'''
                                    ,
                                    (
                                        d['countryShortCode'] + str(d['dateId']),
                                        d['dateId'],
                                        d['country_name'],
                                        d['countryShortCode'],
                                        d['confirmedCount'],
                                        d['currentConfirmedCount'],
                                        d['curedCount'],
                                        d['deadCount'],

                                        d['confirmedCount'],
                                        d['currentConfirmedCount'],
                                        d['curedCount'],
                                        d['deadCount']
                                    )
                )

        self.connect.commit()

        return item


    # 表示当项目执行结束时，会调用
    def close_spider(self, spider):
        # 将所有的数据，self.datas 保存到文件中即可
        # with open('datas/all_countris_datas.json', 'w+') as f:
        #     json.dump(self.datas, f, ensure_ascii=False)

        self.connect.close()
        self.cursor.close()
