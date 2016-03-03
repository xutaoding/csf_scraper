# -*- coding: utf-8 -*-

import re
import uuid
import datetime
import query_string
from secu_bond import BaseDownloadHtml
from tools import secu_currency, close_price, total_equity


class SzxSecurity(BaseDownloadHtml):
    def __init__(self):
        # securities block trade(Trade agreement), to history data with excel on web page
        self._crawl_pages = 4
        self._coll_in = query_string.coll_in
        self._base_url = query_string.base_url
        self._latest_date = self._get_latest_date()
        self._date = re.compile(r"<td  class='cls-data-td'  width='70'  align='center' >(.*?)</td>", re.S)
        self._code_price_volu_amou = re.compile(r"<td  class='cls-data-td' style='mso-number-format.*?>(.*?)</td>",
                                                re.S)
        self._buy_sale = re.compile(r"<td  class='cls-data-td'  align='left' >(.*?)</td>", re.S)
        self._query_string = query_string.query_string.format(*self._get_pages_count() + ('{0}',))

    def _get_latest_date(self):
        try:
            find_one = self._coll_in.get({'typ': 'szx_secu'}, spec_sort=('y', -1))
            return find_one['y']
        except (IndexError, TypeError, KeyError, AttributeError):
            return '0000-00-00'

    def _get_pages_count(self):
        pages_text = lambda s: re.compile(r'<td align="left" width="128px">(.*?)</td>', re.S).search(s)
        html = self.get_html('http://www.szse.cn/main/disclosure/news/xyjy/')
        m = pages_text(html).group(1)

        if m is None:
            raise ValueError('Get page and count error!')

        try:
            pages = re.compile(r'(\d+)').findall(m)
            return str(pages[-1]), str(int(pages[-1].strip()) * 20)
        except(IndexError, AttributeError) as e:
            raise e.__class__(e.message)

    def parse_web(self, url):
        html = self.get_html(url, encoding=True)
        dt_all = self._date.findall(html)  # trade date
        code_price_volu_amou_all = self._code_price_volu_amou.findall(html)  # code, price, volu, amou
        buy_sale_all = self._buy_sale.findall(html)  # buy side, sale side
        assert_flag = len(dt_all) == len(code_price_volu_amou_all) / 4 and len(dt_all) == len(buy_sale_all) / 2

        assert assert_flag, ' regex parse element is not equal'
        length1, length2 = len(code_price_volu_amou_all) / 4, len(buy_sale_all) / 2
        return (dt_all,
                [code_price_volu_amou_all[k * 4: (k + 1) * 4] for k in range(length1)],
                [buy_sale_all[t * 2: (t + 1) * 2] for t in range(length2)]
                )

    def main(self):
        pages = self._crawl_pages
        precision = lambda d: '{0:.2f}'.format(float(d.strip()) * 10000)

        for page in range(1, pages + 1):
            url = self._base_url + self._query_string.format(page)
            dt, code_price_volu_amou, buy_sale = self.parse_web(url)
            for i in range(len(dt)):
                # Note that this program to securities (stock and fund , fond is None)
                # True insert all data at dt[i] date, otherwise insert omission data
                rp_flag = self._latest_date < dt[i]
                secu, curr = secu_currency(code_price_volu_amou[i][0], 'stock', 'fund')
                clo_price = close_price(secu, dt[i], 'mysql')
                disc = '' if clo_price is None else ('%.4f' % (float(code_price_volu_amou[i][1]) -
                                                               float(clo_price) - 1))
                total = total_equity(secu, dt[i], 'vary', 'stock')
                volu = float(precision(code_price_volu_amou[i][2]))
                ratio = '' if total is None else ('%.4f' % ((volu / total) * 100))

                name = ''.join([dt[i]] + code_price_volu_amou[i] + buy_sale[i])
                uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
                data = {
                    'secu': secu, 'y': dt[i], 'buy': buy_sale[i][0], 'sale': buy_sale[i][1],
                    'price': code_price_volu_amou[i][1],  'disc': disc, 'ratio':  ratio, 'stat': 2,
                    'volu': volu, 'amou': precision(code_price_volu_amou[i][3]),
                    'c': {'cd': curr, 'szh': '人民币' if curr == 'CNY' else '港币', 'en': curr},
                    'uuid': uid, 'crt': datetime.datetime.now(), 'typ': 'szx_secu','upt': datetime.datetime.now()
                }

                if not rp_flag and not self._coll_in.get({'uuid': uid}):
                    self._coll_in.insert(data)
                elif rp_flag:
                    self._coll_in.insert(data)
            print u'权益类证券大宗交易 page: %d done!' % page
        self._coll_in.disconnect()


if __name__ == '__main__':
    SzxSecurity().main()
