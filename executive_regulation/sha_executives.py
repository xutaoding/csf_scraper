# -*- coding: utf-8 -*-

import re
import sys
import uuid
import simplejson
from datetime import datetime

import query_string
from base import BaseDownloadHtml
from tools import ratio, data_by_table_type


class BaseExecutives(BaseDownloadHtml):
    def __init__(self):
        self.default_pages = 5
        self.start, self.end = self._parse_date(sys.argv[1:])

    @staticmethod
    def _parse_date(details_date):
        if not details_date:
            start = end = None
            return start, end
        else:
            start, end = details_date[0], details_date[1]

        pat = re.compile('\d{4}-\d\d-\d\d')
        if pat.match(start) is None or pat.match(end) is None:
            raise ValueError('Date format error, expected:0000-00-00')

        return start, end

    def unpickle(self, json_data):
        try:
            data = simplejson.loads(json_data)['pageHelp']
            setattr(self, 'page_count', data['pageCount'])
            return data['data']
        except (simplejson.JSONDecodeError, KeyError) as e:
            setattr(self, 'page_count', 1)
            print 'decode json data error:', e


class ShaExecutives(BaseExecutives):
    def __init__(self):
        """
        This class deal with to base data from the Shanghai stock exchange.
        The default base latest data, hint update is True, otherwise base all history data.
        url: http://www.sse.com.cn/disclosure/credibility/change/
        """
        super(ShaExecutives, self).__init__()

        self._coll_in = query_string.coll_in

        if self.start is None and self.end is None:
            self.url = query_string.sha_updating_of_day
        elif self.start and self.end:
            self.url = query_string.sha_query_string
        else:
            raise

        self.__headers = {'Referer': query_string.referer, 'User-Agent': query_string.user_agent}
        self.keys = ['COMPANY_CODE', 'COMPANY_ABBR', 'NAME', 'DUTY', 'STOCK_TYPE', 'CURRENCY_TYPE', 'CURRENT_NUM',
                     'CHANGE_NUM', 'CURRENT_AVG_PRICE', 'HOLDSTOCK_NUM', 'CHANGE_REASON', 'CHANGE_DATE', 'FORM_DATE']

    def insert(self, total_data):
        # data order:
        # 公司代码 公司简称 董监高姓名 职务 股票种类 货币种类 本次变动前持股数
        # 变动数 本次变动平均价格 变动后持股数 变动原因 变动日期 填报日期
        number = (lambda num: num.replace(',', ''))

        for item in total_data:
            currency = data_by_table_type({'zhsname': item[5]}, [('code',)], 'curr')
            secu_code, orgid = data_by_table_type({'tick': item[0]}, [('code', ), ('org', 'id')], 'stock')

            query_name_en = {'name.szh': item[2], 'orgid': orgid}
            name_en, pid = data_by_table_type(query_name_en, [('name', 'en'), ('pid',)], 'exec')
            to_ratio, cir_ratio = ratio(number(item[7]), secu_code, 'stock', 'vary')
            uid_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, ''.join(item).encode('u8')))

            data = {
                'secu': secu_code or item[0], 'org': orgid, 'scp': {'szh': '', 'en': ''}, 'uuid': uid_uuid,
                'name': {'szh': item[2], 'en': name_en}, 'relation': '', 'pid': pid,
                'change': item[7], 'after': item[9], 'cur': currency, 'cause': item[10], 'cd': item[11],
                'rd': item[12], 'stat': 1, 'price': item[8], 'upt': datetime.now(), 'upu': 'system',
                'torat': to_ratio, 'cirrat': cir_ratio, 'typ': 'sha'
            }

            if not self._coll_in.get({'uuid': uid_uuid}, {'secu': 1}):
                self._coll_in.insert(data)
            else:
                print 'uuid existed:', uid_uuid
        self._coll_in.disconnect()

    def main(self):
        data = []

        for page in range(1, self.default_pages + 1):
            if self.start is None and self.end is None:
                url = self.url % (page, page, page)
            else:
                url = self.url % (self.start, self.end, page)

            response = self.get_html(url, headers=self.__headers)
            pickle_data = self.unpickle(response)

            for item in pickle_data:
                data.append([item[k] for k in self.keys])

            if self.page_count == page:
                break

        print 'data length:', len(data)
        self.insert(data)


if __name__ == '__main__':
    ShaExecutives().main()
