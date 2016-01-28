# -*- coding: utf-8 -*-

import sys
import os.path
import re
import types
import urllib2
import time
import chardet
import json
import datetime
from time import strftime, sleep

module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(module_path)

from eggs.db.mongodb import Mongodb


class HKReport(object):
    def __init__(self):
        self._regex_json_data = re.compile(r'(\{.*\})', re.S)
        self._rp_url = 'http://data.eastmoney.com{0}'
        self._title = re.compile(r'<h4>(.*?)<span', re.S)
        self._content = re.compile(r'<pre>(.*?)</pre>', re.S)
        self._collection = Mongodb('192.168.250.208', 27017, 'news', 'research_report_def')
        self._url = 'http://data.eastmoney.com/notice_n/reportHK.aspx?ajax=ajax&type=gs&page={0}&code=&jsname=&rt='

    def get_html(self, url, data=None, encoding=False):
        for i in range(1, 4):
            req = urllib2.Request(url) if not data else urllib2.Request(url, data)
            req.add_header('User-Agent', '	Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')
            try:
                response = urllib2.urlopen(req, timeout=30.0)
                feed_data = response.read()
                response.close()
                if not encoding:
                    time.sleep(0.35)
                    return feed_data
                return self.to_utf8(feed_data)
            except Exception as e:
                print 'Web open error', i, 'times:', e
                time.sleep(40.0)
        return 'None'

    @staticmethod
    def to_utf8(string):
        charset = chardet.detect(string)['encoding']
        if charset is None:
            return string
        if charset != 'utf-8' and charset == 'GB2312':
            charset = 'gb18030'
        try:
            return string.decode(charset).encode('utf-8')
        except Exception, e:
            print 'chardet error:', e

    @staticmethod
    def remove_tag(string):
        try:
            value = re.sub(r'<p>', '\n', string)
            value = re.sub(r'<.*?>', '', value)
            for char in ['&nbsp;', '&sbquo;', '&ensp;', '&ldquo;', '&rdquo;', '&gt;']:
                value = value.replace(char, '')
            return value.strip()
        except Exception as e:
            print 'remove tag error:', e
        return 'None'

    @staticmethod
    def get_rr_research_org_code(origin):
        coll = Mongodb('192.168.250.200', 27017, 'ada', 'rr_research_org')
        try:
            for doc in coll.query({'abbr.szh': {'$regex': origin}}):
                if doc['abbr']['szh'] == origin or origin in doc['rs']:
                    return doc['code']
        except Exception as e:
            print 'no get code by origin. Error:', e

    @staticmethod
    def get_base_stock_code(stock_code):
        coll = Mongodb('192.168.250.200', 27017, 'ada', 'base_stock')
        try:
            for d in coll.query({'tick': stock_code}).sort([('crt', 1)]):
                return d.get('code')
        except Exception as e:
            print 'no get code by base_stock. Error:', e

    def extract_data(self, rp_date, rp_url, rp_code, agency):
        # line_data_list is list of split comma with "date, report title, url, agent, type, code, company name"
        url = self._rp_url.format(rp_url)

        if self._collection.get({'url': url}, {'titl': 1}) is None:
            html = self.get_html(url, encoding=True)
            try:
                title = self.remove_tag(self._title.findall(html)[0])
                content = self.remove_tag(self._content.findall(html)[0])

                src = self.get_rr_research_org_code(agency) or ''  # get src
                secu = self.get_base_stock_code(rp_code) or ''  # get secu

                data = {
                    'url': url, 'titl': {'szh': title, 'en': ''}, 'bio': {'en': '', 'szh': content},
                    'rdt': rp_date, 'upu': '', 'typ': '30001', 'stat': 1, 'upt': datetime.datetime.now(),
                }

                data.update({'src': src, 'secu': secu})
                if not src or not secu:
                    vn_src = '' if src else agency
                    vn_secu = '' if secu else rp_code
                    data['vn'] = '^'.join([vn_src, vn_secu])
                else:
                    data['vn'] = None

                self._collection.insert(data)
            except (IndexError, TypeError):
                print('index error in extrat_data func.')
            return True
        return False

    def _split_info(self, rp_infos):
        truncate_start_index = 1
        items = rp_infos.split(',')
        rp_tit, rp_typ, rp_url = '', '', ''
        temp_info = items[truncate_start_index: -3]
        rp_date, rp_code, rp_name = items[0], items[-2], items[-1]

        # start with '/notice_n/', then get it
        for k, item in enumerate(temp_info):
            if item.startswith('/notice_n/'):
                rp_url = item
                truncate_start_index += k
                break
        rp_agency = self.remove_tag(''.join(temp_info[truncate_start_index:]))
        return rp_date, rp_tit, rp_url, rp_agency, rp_typ, rp_code, rp_name

    def spider(self, updating=None):
        # updating is None, spider latest hk reports
        # updating is [0000-00-00, ], spider all hk reports in this list date.
        # updating is 'all', spider all history  hk reports.
        query_dates = []
        pages_switch = False
        next_page_flag = True
        now_day = str(datetime.date.today())
        start_page, total_pages = 1, 200

        if isinstance(updating, types.NoneType):
            query_dates.append(now_day)

        # date must sequential, or spider error.
        if isinstance(updating, (tuple, list)):
            query_dates.append(now_day)
            query_dates.extend(list(updating))

        while start_page <= total_pages:
            json_data_with_var = self.get_html(self._url.format(start_page), encoding=True)
            json_data = self._regex_json_data.findall(json_data_with_var)[0]

            if not json_data:
                print('Current page is {0}, total pages : {1}'.format(start_page, total_pages))
                continue

            py_objects = json.loads(json_data)
            if not pages_switch:
                pages_switch = True
                total_pages = py_objects['pages']
                print 'fff:', total_pages

            for items in py_objects['data']:
                # each items is string, like "date, report title, url, agent, type, code, company name"
                rp_date, rp_tit, rp_url, rp_agency, rp_typ, rp_code, rp_name = self._split_info(items)

                if isinstance(updating, (types.NoneType, list, tuple)) and rp_date not in query_dates:
                    next_page_flag = False
                    break

                if self.extract_data(rp_date, rp_url, rp_code, rp_agency):
                    print '[%s  %s FROM %s] -->>> Now insert mongodb!' % (rp_code, rp_date, rp_agency)
                else:
                    print '[%s  %s FROM %s] -->>> mongodb table is existed' % (rp_code, rp_date, rp_agency)

            if not next_page_flag:
                break

            start_page += 1
            if start_page % 3 == 0:
                sleep(30)


if __name__ == '__main__':
    update_time = ['0130', '0430', '0800', '1100', '1130']
    while 1:
        if strftime('%H%M') not in update_time:
            print strftime('%Y-%m-%d %H:%M:%S %A')
            sleep(20.0)
        else:
            try:
                HKReport().spider()
            except:
                pass

    # query = ['2015-09-24', '2015-09-23', '2015-09-22', '2015-09-21', '2015-09-19', '2015-09-18', '2015-09-17', '2015-09-16', '2015-09-15']
    # HKReport().spider()
