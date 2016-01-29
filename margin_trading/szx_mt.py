# -*- coding: utf-8 -*-

import re
from datetime import datetime, date, timedelta

from base import BaseDownloadHtml
from eggs.db.mongodb import Mongodb
from tools import secu_code, szx_fiba_bre, szx_sema_bre


class SzxMarginTrading(BaseDownloadHtml):
    def __init__(self, query_date=None):
        """
        query_date parameter must '0000-00-00'
        """
        if query_date is None:
            weekday = date.today().weekday()
            self._query_date = self._get_query_date()
            print self._query_date
            self._validity = False if weekday == 6 else True
            self._query_string = 'ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1837_xxpl&TABKEY=tab1&tab2PAGECOUNT=30' \
                                 '&tab2RECORDCOUNT=800&REPORT_ACTION=navigate&tab2PAGENUM={1}'
        else:
            self._query_date = query_date
            self._validity = True
            self._query_string = 'ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1837_xxpl&txtDate={0}&TABKEY=tab1&' \
                                 'tab2PAGECOUNT=21&tab2RECORDCOUNT=404&REPORT_ACTION=navigate&tab2PAGENUM={1}'

        self.__code = re.compile(r"<td  class='cls-data-td' style='mso-number-format:\\@' align='center' >(\d+?)</td>", re.S)
        self.__others = re.compile(r"<td  class='cls-data-td'  align='right' >(.*?)</td>", re.S)
        self.__pages_c = re.compile(r'<td align="left" width="128px">(.*?)</td>', re.S)

    def _get_query_date(self):
        html = self.get_html('http://www.szse.cn/main/disclosure/rzrqxx/rzrqjy/')
        m_date = lambda s: re.compile(r"<span class='cls-subtitle'>(.*?)</span>").search(s)

        s_query_date = m_date(html)
        if s_query_date is None:
            raise ValueError('Query date error!')

        return s_query_date.group(1).strip()

    def extract(self, html):
        codes = self.__code.findall(html)
        others_infos = self.__others.findall(html)[6:]
        if len(codes) != len(others_infos) // 6:
            raise ValueError('len(codes) not equalto len(others_infos), check...')

        # code, 融资买入额(fi.bu), 融资余额(fi.ba), 融券卖出量(se.so),
        # 融券余量(se.ma), 融券余额(se.ba), 融资融券余额(total)
        l = lambda v: v.replace(',', '').strip()
        ots = [others_infos[i * 6: (i + 1) * 6] for i in range(len(codes))]
        return ((l(codes[k]), l(v[0]), l(v[1]), l(v[2]), l(v[3]), l(v[4]), l(v[5])) for k, v in enumerate(ots))

    def main(self):
        if not self._validity:
            print 'SZX this is Saturday or Monday!'
            return 0

        coll_in = Mongodb('192.168.250.200', 27017, 'ada', 'base_margin_trading')
        coll_stock = Mongodb('192.168.250.200', 27017, 'ada', 'base_stock')
        coll_fund = Mongodb('192.168.250.200', 27017, 'fund', 'base_fund')

        url = 'http://www.szse.cn/szseWeb/FrontController.szse?randnum=&'
        t = lambda v: '%.4f' % float(v)
        for page in range(1, 30):
            break_point = False
            html = self.get_html(url + self._query_string.format(self._query_date, page), encoding=True)
            for it in self.extract(html):
                # print it[0], it[1], it[2], it[3], it[4], it[5], it[6]
                break_point = True
                secu_cd = secu_code(it[0], coll_stock, coll_fund)
                fiba_bre = szx_fiba_bre(secu_cd, coll_in, self._query_date)
                sema_bre = szx_sema_bre(secu_cd, coll_in, self._query_date)

                # 本日融资偿还额 = 前日融资余额 ＋ 本日融资买入- 本日融资余额(元) (fi.re = fi.ba(上期) + fi.bu - fi.ba)
                # 融券偿还量 = 融券卖出量 + 融券余量(上期) - 融券余量 (se.re = se.so + se.ma(上期) - se.ma)
                szx_fs_data = {
                    'secu': secu_cd or it[0], 'date': self._query_date, 'total': t(it[6]), 'stat': 2,
                    'typ': 'szx', 'crt': datetime.now(),
                    'fi': {
                        'ba': t(it[2]),
                        'bu': t(it[1]),
                        're': t(float(it[1]) + fiba_bre - float(it[2]))
                    },
                    'se': {
                        'ba': t(it[5]),
                        'ma': t(it[4]),
                        'so': t(it[3]),
                        're': t(float(it[3]) + sema_bre - float(it[4]))
                    }
                }
                if not coll_in.get({'secu': secu_cd or it[0], 'date': self._query_date, 'typ': 'szx'}):
                    coll_in.insert(szx_fs_data)

            if not break_point:
                break
            print u'szx [%s] 融资融券交易明细 day update: %d page done!' % (self._query_date, page)
            # break

        coll_in.disconnect()
        coll_stock.disconnect()
        coll_fund.disconnect()


if __name__ == '__main__':
    # SzxFs().main()
    SzxMarginTrading('2015-12-03').main()

