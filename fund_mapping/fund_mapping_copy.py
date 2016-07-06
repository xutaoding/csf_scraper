# -*- coding: utf-8 -*-

import re
import requests
from pyquery import PyQuery
from pymongo import MongoClient


class FundMapping(object):
    def __init__(self):
        self._collection = self.db('122.144.134.95', 27017, 'fund', 'base_fund')
        self._url = 'http://fund.csrc.gov.cn/web/classification_show.organization'

    def db(self, host, port, database, collection):
        self.__conn = MongoClient(host, port)
        _db = self.__conn[database]
        collection = _db[collection]
        return collection

    def close_db(self):
        self.__conn.close()

    def get_fund_mapping(self):
        # sub_code, sub_name, main_code, main_name
        sub_to_main_mapping = []
        html = requests.get(self._url, timeout=30.0).content
        document = PyQuery(unicode(html, 'utf-8'))

        fund_blocks = [document.items('.aa'), document.items('.dd')]
        for each_block in fund_blocks:
            for class_tag in each_block:
                items_list = [item.text() for item in class_tag.items('td')]
                sub_to_main_mapping.append((items_list[1], items_list[3]))
        return dict(sub_to_main_mapping)

    def update_to_mongo(self):
        fund_mapping = self.get_fund_mapping()

        for item in self._collection.find({}, {'code': 1}).sort([('_id', 1)]):
            key = item['code'][:6]
            main_fund_code = fund_mapping.get(key)
            if main_fund_code is not None:
                regex = re.compile(r'{0}'.format(main_fund_code))
                main_fund_sid = self._collection.find_one({'code': regex}, {'sid': 1})
                print 'main:', main_fund_sid
                main = (main_fund_sid or {}).get('sid', '')
                self._collection.update({'_id': item['_id']}, {"$set": {'main': main}})
        self.close_db()


if __name__ == '__main__':
    FundMapping().update_to_mongo()
    # schedule.every().friday.at('15:30').do(FundMapping().update_to_mongo)
    #
    # while True:
    #     schedule.run_pending()
    #     if int(time.strftime('%M')) % 5 == 0:
    #         print(time.strftime('%Y-%m-%d %H:%M:%S %A'))
    #     time.sleep(15)
