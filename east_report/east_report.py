#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import re
import socket
import urllib2
import cookielib
import time
import chardet
import xlrd
from datetime import datetime
from multiprocessing import Process
from pymongo import Connection
from eggs.utils.utils import write


class EastReport(object):
    def __init__(self):
        self.__date = re.compile(r'<li class="date">(.*?)</li>', re.S)  # 26 per page, 25 need
        self.__origin = re.compile(r'<li class="name"><a href=".*?">(.*?)</a></li>', re.S)  # 25 per page
        self.__url = re.compile(r'<li class="titleL title"><a href="(.*?)">', re.S)  # 25 per page
        self.__title = re.compile(r'<div class="report-title"><h1>(.*?)</h1></div>', re.S)  # at url page
        self.__content = re.compile(r'<div class="report-body Body" id="ContentBody">(.*?)</div>', re.S)  # at url page

    def get_html(self, url, data=None, encoding=False):
        for i in range(1, 13):
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
                time.sleep(30.0)
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

    @staticmethod
    def get_date(str_date):
        if not str_date:
            raise ValueError(' date value error!')
        return datetime.strptime(str_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')

    def next_page(self, html):
        pat_next_url = re.compile(r'<a target="_self" href="(.*?)" >下一页</a>')
        try:
            next_url = pat_next_url.findall(html)[0]
            return 'http://data.eastmoney.com' + next_url
        except Exception as e:
            print 'next_url error:', e

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

    def main(self, p_name, stocks):
        conn = Connection('192.168.0.212', 27017)
        coll = conn.crawler.east_report
        start = time.time()
        for k, stock_code in enumerate(stocks):
            next_url, flag, page, nums = 'http://data.eastmoney.com/report/%s.html#pageAnchor' % stock_code, 0, 1, 0
            while 1:
                print next_url
                html = self.get_html(next_url, encoding=True)
                next_url, date_all = self.next_page(html), self.__date.findall(html)
                origin, urls = self.__origin.findall(html), self.__url.findall(html)

                try:
                    date_all.remove(date_all[0])
                except Exception as e:
                    print 'date_all error:', e

                for i, url in enumerate(urls):
                    url = 'http://data.eastmoney.com' + url
                    if coll.find_one({'url': url}) is None:
                        now_html = self.get_html(url, encoding=True)
                        try:
                            pub_date = self.get_date(date_all[i])
                            title = self.remove_tag(self.__title.findall(now_html)[0])
                            content = self.remove_tag(self.__content.findall(now_html)[0])
                            # write(r'D:\project\autumn\crawler\east_report\east_report', [title, str(pub_date), origin[i]])
                            # write(r'D:\project\autumn\crawler\east_report\east_report', content)
                            data = {'url': url, 'title': title, 'date': pub_date, 'origin': origin[i], 'content': content, 'stock-code': stock_code}
                            coll.insert(data)
                            nums += 1
                            print p_name, '|code:', stock_code, 'page:', page, 'nums:', k + 1,   '|(', nums, ')',  title, pub_date, origin[i]
                        except Exception as e:
                            print 'main error:', e
                            write(r'D:\project\autumn\crawler\east_report\log', [stock_code, str(next_url)])
                page += 1
                time.sleep(5.0)
                if not next_url:
                    break
            time.sleep(30)
        print time.time() - start

    def get_stock_codes(self):
        open_book = xlrd.open_workbook('stock_code.xlsx')
        sheet = open_book.sheet_by_index(0)
        stock_codes = sheet.col_values(0)
        stock_codes.remove(stock_codes[0])
        codes, all_codes = [], []
        for i, code in enumerate(stock_codes):
            codes.append(code)
            if (i + 1) % 30 == 0:
                all_codes.append(codes)
                codes = []
        all_codes.append(codes)
        return all_codes

    def multi_process(self, all_codes):
        jobs = []
        for p_name, stock_codes in enumerate(all_codes):
            p = Process(target=self.main, args=(p_name, stock_codes))
            jobs.append(p)
            p.start()

        for j in jobs:
            j.join()

if __name__ == '__main__':
    er = EastReport()
    total_codes = er.get_stock_codes()
    ##############################################
    parts_codes = total_codes[82:87]  # 每次执行5个进程，每个进程30个上市公司code
    er.multi_process(parts_codes)
    ##############################################
    # print len(total_codes)
    # for _codes in total_codes:
    #     print len(_codes)
