# -*- coding: utf-8 -*-

import re
import sys
import uuid
import requests
import simplejson
from datetime import date, datetime, timedelta
from requests.exceptions import ConnectionError, Timeout, InvalidURL, HTTPError

import query_string
from tools import secu_currency, close_price, total_equity


class BaseBlock(object):
    def __init__(self):
        self.default_pages = 10
        self.details_date = self._parse_date(sys.argv[1:])

    @staticmethod
    def get_html(url, data=None, headers=None):
        headers = headers or {}

        for _ in range(3):
            try:
                if data is not None:
                    return requests.post(url, data=data, headers=headers).content
                else:
                    return requests.get(url, headers=headers).content
            except (ConnectionError, Timeout, InvalidURL, HTTPError) as e:
                print "Get html error:", e.__class__, e

    @staticmethod
    def _parse_date(details_date):
        if not details_date:
            details_date = str(date.today() - timedelta(days=1))
        else:
            details_date = details_date[0]

        m = re.compile('\d{4}-\d\d-\d\d').search(details_date)
        if details_date and m is None:
            raise ValueError('Date format error, expected:0000-00-00')

        return m.group()

    def unpickle(self, json_data):
        try:
            data = simplejson.loads(json_data)['pageHelp']
            setattr(self, 'page_count', data['pageCount'])
            return data['data']
        except (simplejson.JSONDecodeError, KeyError) as e:
            setattr(self, 'page_count', 1)
            print 'decode json data error:', e

    @staticmethod
    def insert(typ_key, secu_bond_datas):
        assert typ_key == 'sf_data' or typ_key == 'bond_data'

        coll_in = query_string.coll_in
        data_list = secu_bond_datas[typ_key]
        if typ_key == 'sf_data':
            typ = 'sha_secu'
            keys = ['y', 'secu', 'price', 'amou', 'volu', 'buy', 'sale', 'ot']
        else:
            typ = 'sha_bond'
            keys = ['y', 'secu', 'price', 'volu', 'ot']

        print('Now will insert [{0}] data to mongo'.format(typ))
        for data in data_list:
            to_data = dict(zip(keys, data))
            to_data.pop('ot')

            if typ_key == 'sf_data':
                to_data['amou'] = '{0:.2f}'.format(float(to_data['amou']) * 10000)
                to_data['volu'] = '{0:.2f}'.format(float(to_data['volu']) * 10000)
                secu, curr = secu_currency(to_data['secu'], 'stock', 'fund')
            else:
                to_data['buy'], to_data['sale'] = '', ''
                to_data['volu'] = '{0:.2f}'.format(float(to_data['volu']) * 10000 * 10)
                to_data['amou'] = '{0:.2f}'.format(float(to_data['price']) * float(to_data['volu']))
                secu, curr = secu_currency(to_data['secu'], typ_bond='bond')

            clo_price = close_price(secu, to_data['y'], 'mysql')
            disc = '' if clo_price is None else ('%.4f' % (float(to_data['price']) - float(clo_price) - 1))
            total = total_equity(secu, to_data['y'], 'vary', 'stock')
            ratio = '' if total is None else ('%.4f' % ((float(to_data['volu']) / total) * 100))

            uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, ''.join(data).encode('u8')))
            new_dict = {'typ': typ, 'disc': disc, 'ratio':  ratio, 'stat': 2,
                        'c': {'cd': curr, 'szh': '人民币' if curr == 'CNY' else '港币', 'en': curr},
                        'uuid': uid, 'crt': datetime.now(), 'secu': secu}
            to_data.update(new_dict)

            if not coll_in.get({'uuid': uid}):
                coll_in.insert(to_data)
        print('[{0}] data insert ok.'.format(typ))
        coll_in.disconnect()


class BlockStockFund(BaseBlock):
    def __init__(self):
        super(BlockStockFund, self).__init__()

        self.__headers = {'Referer': query_string.referer, 'User-Agent': query_string.user_agent}
        self.url = query_string.stock_fund_url % (self.details_date, self.details_date, '%s')
        self.keys = ['tradedate', 'stockid', 'tradeprice', 'tradeamount', 'tradeqty', 'branchbuy', 'branchsell', 'ifZc']

    def get_data(self):
        data = []

        for page in range(1, self.default_pages + 1):
            response = self.get_html(self.url % page, headers=self.__headers)
            pickle_data = self.unpickle(response)

            for item in pickle_data:
                data.append([item[k] for k in self.keys])

            if self.page_count == page:
                break

        self.insert('sf_data', {'sf_data': data})


class BlockBond(BaseBlock):
    def __init__(self):
        super(BlockBond, self).__init__()

        self.__headers = {'Referer': query_string.referer, 'User-Agent': query_string.user_agent}
        self.url = query_string.bond_url % (self.details_date, self.details_date, '%s')
        self.keys = ['tradedate', 'stockid', 'tradeprice', 'tradeqty', 'ifZc']

    def get_data(self):
        data = []

        for page in range(1, self.default_pages + 1):
            response = self.get_html(self.url % page, headers=self.__headers)
            pickle_data = self.unpickle(response)

            for item in pickle_data:
                data.append([item[k] for k in self.keys])

            if self.page_count == page:
                break

        self.insert('bond_data', {'bond_data': data})


if __name__ == '__main__':
    BlockStockFund().get_data()
    BlockBond().get_data()
