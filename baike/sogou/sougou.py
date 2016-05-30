# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
import chardet
import requests
from pyquery import PyQuery
from pymongo import MongoClient
from requests.exceptions import ConnectionError, Timeout, InvalidURL, HTTPError

from config import base_url, suffix, header
from config import host, port, db, collection
from config import in_host, in_port, in_db, in_collection


class BaseDownloadHtml(object):
    @staticmethod
    def get_html(url, data=None, headers=None, encoding=False):
        headers = headers or header

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


class SogouBaike(BaseDownloadHtml):
    def __init__(self):
        self.__base_url = base_url
        self._partial_url = base_url % suffix

        self.client = MongoClient(in_host, in_port)
        self.collection = self.client[in_db][in_collection]

    @staticmethod
    def get_required_name():
        name = []
        client = MongoClient(host, port)
        coll = client[db][collection]

        for docs in coll.find({}, {'name': 1}):
            name.append(docs['name'].strip()[:-3])

        client.close()
        return name

    def get_url(self, name):
        html = self.get_html(self._partial_url.format(name=name))
        return self.__base_url.encode('u8') % html.strip()

    @staticmethod
    def remove_nodes(document, css):
        css_list = css if isinstance(css, (tuple, list)) else [css]

        for _selector in css_list:
            document(_selector).remove()

    def no_result(self, document):
        css = '.no_result_wrapper'
        return bool(document(css).length)

    def extract(self, html, name):
        document = PyQuery(html)
        remove_css = '.btn_edit'
        kw_css = '.ed_inner_link'
        css = '.lemma_content_wrap .section_wrap section'
        self.remove_nodes(document, remove_css)
        log_id_list = self.get_log_id(document)

        if self.no_result(document):
            return {'w': name, 'info': [], 'cat': 'sogou', 'ct': datetime.now()}

        w = document('#title').text().strip()
        abstract = document('.abstract').text().strip()
        kw = [t.text().strip() for t in document('.abstract %s' % kw_css).items() if t.text().strip()]
        data = [{'k': w, 'con': abstract, 'kw': kw}]

        temp = []
        cut_section = []
        ks = [document(css_id).text().strip() for css_id in log_id_list]
        log_id_list.pop(0)

        for section in document(css).items():
            for _id in log_id_list:
                if not section(_id).length:
                    temp.append(section)
                else:
                    cut_section.append(temp)
                    temp = []
                    self.remove_nodes(section, _id)
                    log_id_list.remove(_id)
                    temp.append(section)

            if not log_id_list:
                temp.append(section)
        else:
            cut_section.append(temp)

        cons = [''.join([t.text().strip() for t in seg]) for seg in cut_section]
        kws = self.get_kws(cut_section, kw_css)
        data.extend([{'k': _k, 'kw': kws[_ind], 'con': cons[_ind]} for _ind, _k in enumerate(ks)])
        return {'w': name, 'info': data, 'cat': 'sogou', 'ct': datetime.now()}

    @staticmethod
    def get_kws(sections, kw_css):
        all_kw = []

        for seg in sections:
            temp = []

            for t in seg:
                kw = t(kw_css).text().strip().split()
                temp.extend([k.strip() for k in kw if k.strip()])
            all_kw.append(list(set(temp)))
        return all_kw

    @staticmethod
    def get_log_id(document):
        css = '#sideNavListWrap .headline1'
        return [tag.attr('href') for tag in document(css).items()]

    def insert2mongo(self, data):
        try:
            self.collection.insert(data)
        except Exception as e:
            print 'Insert mongo error: type <{}>, msg <{}>'.format(e.__class__, e)

    def crawl(self, start=None):
        all_name = self.get_required_name()

        for index, name in enumerate(all_name if start is None else all_name[start:]):
            html = self.get_html(self.get_url(name))
            self.insert2mongo(self.extract(html, name))
            print 'name: %s crawl Done!' % name
        self.client.close()


if __name__ == '__main__':
    sg = SogouBaike()
    sg.crawl()


