# -*- coding: utf-8 -*-

import re
import sys
import uuid
import simplejson
from datetime import date, datetime, timedelta

import query_string
from base import BaseDownloadHtml
from eggs.db.mongodb import Mongodb
from eggs.db.mysql_client import MySQLClient
from tools import secu_code, sha_seba


class BaseMt(BaseDownloadHtml):
    def __init__(self):
        self.default_pages = True
        self.details_date = self._parse_date(sys.argv[1:])

    @staticmethod
    def _parse_date(details_date):
        if not details_date:
            query_date = str(date.today() - timedelta(days=1)).replace('-', '')
        else:
            query_date = details_date[0].replace('-', '')

        pat = re.compile('\d{8}')
        if pat.match(query_date) is None:
            raise ValueError('Date format error, expected:0000-00-00')

        return query_date

    def unpickle(self, json_data):
        try:
            data = simplejson.loads(json_data)['pageHelp']
            if self.default_pages is True:
                self.default_pages = data['pageCount']
            return data['data']
        except (simplejson.JSONDecodeError, KeyError) as e:
            self.default_pages = 1
            print 'decode json data error:', e


class ShaMarginTrading(BaseMt):
    def __init__(self):
        super(ShaMarginTrading, self).__init__()

        self.url = query_string.sha_query_string
        self.__headers = {'Referer': query_string.referer, 'User-Agent': query_string.user_agent}
        self.keys = ['opDate', 'stockCode', 'securityAbbr', 'rzye', 'rzmre', 'rzche', 'rqyl', 'rqmcl', 'rqchl']

    @staticmethod
    def _valid(_data_list):
        _data = []

        for _item in _data_list:
            if isinstance(_item, basestring):
                _data.append(_item)
            else:
                _data.append(str(_item))
        return _data

    def insert_db(self, total_data):
        coll_in = Mongodb('192.168.251.95', 27017, 'ada', 'base_margin_trading')
        coll_stock = Mongodb('192.168.251.95', 27017, 'ada', 'base_stock')
        coll_fund = Mongodb('192.168.251.95', 27017, 'fund', 'base_fund')
        sql_db = MySQLClient("192.168.251.95", "python_team", "python_team", "ada-fd")

        print '\tnow start to insert mongodb, waiting......'
        d = (lambda v: '%.4f' % float(v))
        for pdt in total_data:
            # 信用交易日期	标的证券代码	标的证券简称	本日融资余额(元)	本日融资买入额(元)
            # 本日融资偿还额(元) 本日融券余量	本日融券卖出量	本日融券偿还量
            secu_cd = secu_code(pdt[1], coll_stock, coll_fund)
            trade_date = '-'.join([pdt[0][:4], pdt[0][4:6], pdt[0][6:]])
            uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, ''.join(self._valid(pdt)).encode('u8')))

            data = {
                'secu': secu_cd or pdt[1], 'date': trade_date, 'total': d(int(pdt[3])), 'stat': 2,
                'typ': 'sha', 'crt': datetime.now(), 'uuid': uid,
                'fi': {
                    'ba': d(pdt[3]),
                    'bu': d(pdt[4]),
                    're': d(pdt[5])
                },
                'se': {
                    'ba': '0.0000',
                    'ma': d(pdt[6]),
                    'so': d(pdt[7]),
                    're': d(pdt[8])
                },
                'upt': datetime.now()
            }

            if coll_in.get({'uuid': uid,  'typ': 'sha'}, {'secu': 1}):
                continue
            elif secu_cd is None:
                coll_in.insert(data)
            else:
                seba = sha_seba(secu_cd, pdt[6], trade_date, sql_db)
                if seba is not None:
                    data['total'] = d(int(pdt[3]) + seba)
                    data['se']['ba'] = d(seba)
                    coll_in.insert(data)

        coll_in.disconnect()
        coll_stock.disconnect()
        sql_db.disconnect()
        print '\tinsert all done!'

    def main(self):
        data = []
        start_page = 1

        while start_page <= self.default_pages:

            url = self.url % (self.details_date, start_page, start_page, start_page)
            response = self.get_html(url, headers=self.__headers)
            pickle_data = self.unpickle(response)

            for item in pickle_data:
                data.append([item[k] for k in self.keys])

            print 'page: %s done!' % start_page
            start_page += 1

        print 'data length:', len(data)
        self.insert_db(data)

if __name__ == '__main__':
    ShaMarginTrading().main()
