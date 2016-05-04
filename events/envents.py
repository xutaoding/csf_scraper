# -*- coding: utf-8 -*-

import re
import urllib
from urlparse import urlparse
from datetime import date, datetime

import chardet
import requests
from pyquery import PyQuery
from pymongo import MongoClient
from requests.exceptions import ConnectionError, Timeout, InvalidURL, HTTPError

from config import base_url
from config import header
from config import host_port, db, table


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
        return ''

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


class EventsWords(BaseDownloadHtml):
    def __init__(self, query_list=None, is_history=False):
        if query_list is None:
            self.query_list = [str(date.today()).replace('-', '')]
        else:
            self.query_list = list(query_list)

        self.is_history = is_history
        self.client = MongoClient(*host_port)
        self.mongo = self.client[db][table]
        self.cache = self.property_cache

    @property
    def property_cache(self):
        _cached = set()
        fields = {'topic', 'date', 'cat'}

        for docs in self.mongo.find({}, fields):
            key = docs['topic'] + docs['date'] + docs['cat']
            _cached.add(key)
        return _cached

    def insert2mongo(self, event_date, other_list):
        try:
            for _oth in other_list:
                docs = self.formatter(event_date, _oth)
                uuid = docs['topic'] + docs['date'] + docs['cat']
                if uuid not in self.cache:
                    self.mongo.insert(self.formatter(event_date, _oth))
                    pass
        except Exception as e:
            print('Insert mongo Error: <{}>, <{}>'.format(e.__class__, e))

    @staticmethod
    def get_kw(href):
        query = urlparse(href).query
        string = query.split('=')[-1]
        return urllib.unquote(string).split('+')

    @staticmethod
    def get_event_date(element):
        selector = 'div.blockTitle3 h3'
        document = PyQuery(element)
        event_date = (lambda s: ''.join(re.compile(r'\d').findall(s)))
        return event_date(document(selector).text())

    def get_event_words(self, element):
        data = []
        keys = ['topic', 'kw']
        selector = 'ul.windVaneList li'
        document = PyQuery(element)

        for _element in document(selector):
            doc_word = PyQuery(_element)('a')
            topic = doc_word.text().strip()
            kw = self.get_kw(doc_word.attr('href'))
            data.append(dict(zip(keys, [topic, kw])))
        return data

    @staticmethod
    def formatter(_date, other):
        formatter = other.copy()
        formatter.update(
            date=_date,
            cat='21so',
            hr=re.compile(r'[:-]|\s+').sub('', str(datetime.now()))[:12]
        )
        return formatter

    def extract(self, html):
        document = PyQuery(html)
        sections = document('div.windVane')

        for _section in sections:
            event_date = self.get_event_date(_section)
            words_dict = self.get_event_words(_section)

            if self.is_history:
                self.insert2mongo(event_date, words_dict)
            else:
                if event_date in self.query_list:
                    self.insert2mongo(event_date, words_dict)
        self.client.close()

        return True if sections else False

    def get_events_info(self):
        start = 1
        end = 87

        while start <= end:
            html = self.get_html(base_url % start, header, encoding=True)
            if not self.extract(html=html):
                break
            print('Finished %s page' % start)
            start += 1


if __name__ == '__main__':
    EventsWords(is_history=True).get_events_info()

