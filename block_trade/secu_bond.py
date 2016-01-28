# -*- coding: utf-8 -*-

import re
import uuid
import datetime
import chardet
import requests
from requests.exceptions import ConnectionError, Timeout, InvalidURL, HTTPError

import query_string
from tools import secu_currency, close_price, total_equity


class BaseDownloadHtml(object):
    @staticmethod
    def get_html(url, data=None, headers=None, encoding=False):
        headers = headers or {}

        for _ in range(3):
            try:
                if data is not None:
                    response = requests.post(url, data=data, headers=headers).content
                else:
                    response = requests.get(url, headers=headers).content

                if not encoding:
                    return response
                else:
                    return BaseDownloadHtml.to_utf8(response)
            except (ConnectionError, Timeout, InvalidURL, HTTPError) as e:
                print "Get html error:", e.__class__, e

    @staticmethod
    def to_utf8(string):
        """
        Auto convert encodings to utf8, because For the encoding of different site content is different,
        must be turned into UTF-8 code
        return: return value is a dictionary(have a key is 'encoding')
        note:
            1、`decode('GB2312')` is messy code, due to `GB2312` character set less than `gb18030`
            2、`Big5` is Traditional Chinese
        """
        charset = chardet.detect(string)['encoding']
        if charset is None:
            return string
        elif charset != 'utf-8' and charset == 'GB2312':
            charset = 'gb18030'
        elif charset.lower()[:4] == 'big5' or charset.lower() == 'windows-1252':
            charset = 'big5hkscs'
        try:
            return string.decode(charset).encode('utf-8')
        except Exception as e:
            print 'chardet error:', e


class SzxBond(BaseDownloadHtml):
    def __init__(self):
        # bond block trade(Trade agreement), to history data with excel on web page
        self._crawl_pages = 4
        self._coll_in = query_string.coll_in
        self._base_url = query_string.base_url
        self._latest_date = self._get_latest_date()
        self._query_string = query_string.bond_string.format(*self._get_pages_count() + ('{0}',))
        self.__dts_short = re.compile(r"<td  class='cls-data-td'  width='8%'  align='center' >(.*?)</td>", re.S)
        self.__codes = re.compile(r"""<td  class='cls-data-td' style='mso-number-format:\\@' width='8%'  align='center' >(.*?)</td>""", re.S)
        self.__price = re.compile(r"""<td  class='cls-data-td' style='mso-number-format:\\@' width='10%'  align='right' >(.*?)</td>""", re.S)
        self.__volu = re.compile(r"<td  class='cls-data-td' style='mso-number-format:\\@' width='8%'  align='right' >(.*?)</td>")
        self.__buy = re.compile(r"""<td  class='cls-data-td'  width='280px'  align='left' >(.*?)</td>""", re.S)
        self.__sale = re.compile(r"<td  class='cls-data-td'  align='left' >(.*?)</td>", re.S)

    def _get_latest_date(self):
        try:
            find_one = self._coll_in.get({'typ': 'szx_bond'}, spec_sort=('y', -1))
            return find_one['y']
        except (IndexError, TypeError, KeyError, AttributeError):
            return '0000-00-00'

    def _get_pages_count(self):
        all_pages = lambda t: re.compile(r'\d+').findall(t)
        regex_pages = re.compile(r'<td align="left" width="128px">(.*?)</td>', re.S)
        html = self.get_html('http://www.szse.cn/main/disclosure/news/zqxyjy/')
        try:
            pages_text = regex_pages.findall(html)[0]
            pages = all_pages(pages_text)
            return pages[-1], str(int(pages[-1].strip()) * 20)
        except Exception as e:
            raise ValueError(e.message)

    def parse_web(self, url):
        html = self.get_html(url, encoding=True)
        dts, codes = self.__dts_short.findall(html), self.__codes.findall(html)  # dts_short, codes
        prices, volus = self.__price.findall(html), self.__volu.findall(html)  # price, volu
        buys, sales = self.__buy.findall(html), self.__sale.findall(html)  # buy, sale

        flag_one, flag_two = len(dts) / 2 == len(prices), len(prices) == len(volus)
        flag_thr, flag_fou = len(volus) == len(buys), len(buys) == len(sales)

        if not (flag_one and flag_two and flag_thr and len(codes) == len(prices)):
            raise ValueError('parse element not equent.')

        l, t = lambda v, lt: lt[v * 2].strip(), lambda v: v.strip()
        # return date, code, price, volu, buy, sale
        return ((l(k, dts), t(codes[k]), t(price), t(volus[k]), t(buys[k]), t(sales[k]))
                for k, price in enumerate(prices))

    def main(self):
        pages = self._crawl_pages
        for page in range(1, pages + 1):
            url = self._base_url + self._query_string.format(page)
            for item in self.parse_web(url):
                # Note that this program to securities (stock and fund , fond is None)
                # True insert all data at item[0] date, otherwise insert omission data
                rp_flag = self._latest_date < item[0]
                secu, curr = secu_currency(item[1], typ_bond='bond')
                clo_price = close_price(secu, item[0], 'mysql')
                disc = '' if clo_price is None else ('%.4f' % (float(item[2]) - float(clo_price) - 1))
                total = total_equity(secu, item[0], 'vary', 'stock')
                ratio = '' if total is None else ('%.4f' % ((float(item[3]) / total) * 100))

                uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, ''.join(item)))
                data = {
                    'secu': secu, 'y': item[0], 'buy': item[4], 'sale': item[5],
                    'price': item[2],  'disc': disc, 'ratio':  ratio, 'stat': 2,
                    'volu': '{0:.2f}'.format(float(item[3])),
                    'amou': '{0:.2f}'.format(float(item[3]) * float(item[2])),
                    'c': {'cd': curr, 'szh': '人民币' if curr == 'CNY' else '港币', 'en': curr},
                    'uuid': uid, 'crt': datetime.datetime.now(), 'typ': 'szx_bond'
                }

                if not rp_flag and not self._coll_in.get({'uuid': uid}):
                    self._coll_in.insert(data)
                elif rp_flag:
                    self._coll_in.insert(data)
            print u'债券大宗交易 page: %d done!' % page

if __name__ == '__main__':
    SzxBond().main()


