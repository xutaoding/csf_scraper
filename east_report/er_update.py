#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import socket
import urllib2
import cookielib
import time
import chardet
import json
import datetime

import sys
sys.path.append('/home/xutaoding/autumn/')

from eggs.db.mongodb import Mongodb


class ErUpdate(object):
    def __init__(self):
        self.__title = re.compile(r'<div class="report-title">.*?<h1>(.*?)</h1>', re.S)
        self.__content = re.compile(r'<div class="report-body Body" id="ContentBody">(.*?)</div>', re.S)

    def get_html(self, url, data=None, encoding=False):
        for i in range(1, 4):
            socket.setdefaulttimeout(20)
            req = urllib2.Request(url) if not data else urllib2.Request(url, data)
            req.add_header('User-Agent', '	Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')
            cj = cookielib.CookieJar()
            cj.clear()  # clear cookie
            try:
                response = urllib2.urlopen(req)
                feed_data = response.read()
                response.close()
                if not encoding:
                    time.sleep(0.35)
                    return feed_data
                return eval(self.__class__.__name__).to_utf8(feed_data)
            except Exception, e:
                print 'Web open error', i, 'times:', e
                time.sleep(40.0)
        return 'None'

    @staticmethod
    def to_utf8(string):
        charset = chardet.detect(string)['encoding']  # return value is a dictionary(have a key is 'encoding')
        if charset is None:
            return string
        if charset != 'utf-8' and charset == 'GB2312':
            charset = 'gb18030'
        try:
            return string.decode(charset).encode('utf-8')
        except Exception, e:
            print 'chardet error:', e

    def remove_tag(self, string):
        try:
            value = re.sub(r'<p>', '\n', string)
            value = re.sub(r'<.*?>', '', value)
            for char in ['&nbsp;', '&ensp;', '&ldquo;', '&rdquo;', '&gt;']:
                value = value.replace(char, '')
            return value.strip()
        except Exception as e:
            print 'remove tag error:', e
        return 'None'

    def rr_research_org_code(self, origin):
        coll = Mongodb('192.168.251.95', 27017, 'ada', 'rr_research_org')
        try:
            for doc in coll.query({'abbr.szh': {'$regex': origin}}):
                if doc['abbr']['szh'] == origin or origin in doc['rs']:
                    return doc['code']
        except Exception as e:
            print 'no get code by origin. Error:', e

    def base_stock_code(self, stock_code):
        coll = Mongodb('192.168.251.95', 27017, 'ada', 'base_stock')
        try:
            for d in coll.query({'tick': stock_code}).sort([('crt', 1)]):
                return d.get('code')
        except Exception as e:
            print 'no get code by base_stock. Error:', e

    def main(self, query=None):
        if query is None:
            query_date = [str(datetime.date.today())]
        else:
            query_date = query

        flag = False
        min_date = min(query_date)
        coll = Mongodb('192.168.251.95', 27017, 'news', 'research_report_def')
        url = 'http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?'
        query_string = 'type=SR&sty=GGSR&ps=50&p=%s&mkt=0&stat=0&cmd=2&code=&rt='
        for page in range(1, 20):
            py_data = json.loads(self.get_html(url + query_string % str(page), encoding=True)[1:-1])
            for data in py_data:
                code, agency = data['secuFullCode'][:6], data['insName']
                date_time, url_info_code = data['datetime'][:10], data['infoCode']
                report_url = 'http://data.eastmoney.com/report/%s/%s.html' % (date_time.replace('-', ''), url_info_code)

                if date_time in query_date:
                    src = self.rr_research_org_code(agency) or ''  # get src
                    secu = self.base_stock_code(code) or ''  # get secu
                    if coll.get({'url': report_url}, {'titl': 1}) is None:
                        try:
                            now_html = self.get_html(report_url, encoding=True)
                            title = self.remove_tag(self.__title.findall(now_html)[0])
                            content = self.remove_tag(self.__content.findall(now_html)[0])

                            to_data = {
                                'url': report_url, 'titl': {'szh': title, 'en': ''}, 'bio': {'en': '', 'szh': content},
                                'rdt': date_time, 'upu': '', 'typ': '30001', 'stat': 1, 'upt': datetime.datetime.now(),
                                'crt': datetime.datetime.now(),
                            }

                            to_data.update({'src': src, 'secu': secu})
                            if not src or not secu:
                                vn_src = '' if src else agency
                                vn_secu = '' if secu else code
                                to_data['vn'] = '^'.join([vn_src, vn_secu])
                            else:
                                to_data['vn'] = None
                            coll.insert(to_data)
                            print '[%s  %s FROM %s] -->>> Now insert mongodb!' % (code, date_time, agency)
                        except Exception as e:
                            print 'title: %s, url: %s' % (data['title'], report_url), 'Error:', e
                    else:
                        print '[%s  %s FROM %s] -->>> mongodb table is existed' % (code, date_time, agency)
                elif date_time < min_date:
                    flag = True
                    break
            if flag:
                break
        coll.disconnect()

    def get_history(self):
        coll = Mongodb('192.168.251.95', 27017, 'news', 'research_report_def')
        url = 'http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?'
        query_string = 'type=SR&sty=GGSR&ps=50&p=%s&mkt=0&stat=0&cmd=2&code=&rt='

        for page in range(1, 943):
            if page <= 941:
                continue

            py_data = json.loads(self.get_html(url + query_string % str(page), encoding=True)[1:-1])
            for data in py_data:
                code, agency = data['secuFullCode'][:6], data['insName']
                date_time, url_info_code = data['datetime'][:10], data['infoCode']
                report_url = 'http://data.eastmoney.com/report/%s/%s.html' % (date_time.replace('-', ''), url_info_code)

                src = self.rr_research_org_code(agency) or ''  # get src
                secu = self.base_stock_code(code) or ''  # get secu
                if coll.get({'url': report_url}) is None:
                    try:
                        now_html = self.get_html(report_url, encoding=True)
                        title = self.remove_tag(self.__title.findall(now_html)[0])
                        content = self.remove_tag(self.__content.findall(now_html)[0])

                        to_data = {
                            'url': report_url, 'titl': {'szh': title, 'en': ''}, 'bio': {'en': '', 'szh': content},
                            'rdt': date_time, 'upu': '', 'typ': '30001', 'stat': 1, 'upt': datetime.datetime.now()
                        }

                        to_data.update({'src': src, 'secu': secu})
                        if not src or not secu:
                            vn_src = '' if src else agency
                            vn_secu = '' if secu else code
                            to_data['vn'] = '^'.join([vn_src, vn_secu])
                        else:
                            to_data['vn'] = None
                        coll.insert(to_data)
                        print 'page: %s, [%s  %s FROM %s] -->>> Now insert mongodb!' % (page, code, date_time, agency)
                    except Exception as e:
                        print 'title: %s, url: %s' % (data['title'], report_url), 'Error:', e
                else:
                    print 'page: %s,[%s  %s FROM %s] -->>> mongodb table is existed' % (page, code, date_time, agency)
            time.sleep(3.5)
        coll.disconnect()


if __name__ == '__main__':
    # old_query = ['2014-08-19']
    ErUpdate().main()
    # ErUpdate().get_history()
