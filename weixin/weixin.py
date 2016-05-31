from __future__ import unicode_literals
import re
import sys
import time
import hashlib
from random import randint
from copy import deepcopy
from random import choice
from datetime import datetime

import requests.packages.urllib3
from pyquery import PyQuery
from pymongo import MongoClient

from config import cookie
from config import START_PAGE, END_PAGE
from config import HOST, PORT, DB, COLLECTION
from config import IN_HOST, IN_PORT, IN_DB, IN_COLLECTION
from config import BASE_URL, HEADERS, USER_AGENT, REFER_FIRST

in_client = MongoClient(IN_HOST, IN_PORT)
in_collection = in_client[IN_DB][IN_COLLECTION]


class Base(object):
    session = requests.Session()

    def get_html(self, url, headers=None, cookies=None, **kwargs):
        required_cookie = cookies or choice(cookie)
        for _ in range(3):
            try:
                response = self.session.get(url, headers=headers, cookies=required_cookie, **kwargs).content
                return response
            except Exception as e:
                print "Get html error:", e.__class__, e
        return ''

    @staticmethod
    def md5(value):
        if not isinstance(value, basestring):
            raise ValueError('md5 must string!')
        m = hashlib.md5()
        try:
            m.update(value)
        except UnicodeEncodeError:
            m.update(value.encode('u8'))
        return m.hexdigest()

    @staticmethod
    def trim(text):
        return re.compile(r'\s+', re.S).sub(' ', text)


class Article(Base):
    def __init__(self, urls_uids, word):
        self.__urls_uids = urls_uids
        self.__word = word
        self.__url = re.compile(r'var msg_link = "(.*?)"', re.S)
        self.__timestamp = re.compile(r'var ct = "(.*?)"', re.S)

    def pub_dt(self, html, document):
        timestamp = self.__timestamp.findall(html)

        try:
            if timestamp:
                return datetime.fromtimestamp(int(timestamp[0]))
            else:
                dt_str = self.trim(document('#post-date').text())
                return datetime.strptime(dt_str, "%Y-%m-%d")
        except (ValueError, TypeError, AttributeError):
            pass

    def extract(self):
        for index, url_uid in enumerate(self.__urls_uids):
            url, uid = url_uid['url'], url_uid['uid']
            html = self.get_html(url)
            document = PyQuery(html)

            try:
                link = self.__url.findall(html)[0]
                title = self.trim(document('#activity-name').text())
                auth = self.trim(document('.profile_nickname').text())
                wx_account = self.trim(document('.profile_meta_value').eq(0).text())
                pub_dt = self.pub_dt(html, document)
                content = self.trim(document('#js_content').text())
            except Exception as e:
                print ('Crawl error: type <{}>, msg <{}>, url <{}>'.format(e.__class__, e, url))
            else:
                data = {
                    'url': url, 'link': link, 'uid': uid, 't': title, 'auth': auth, 'upu': 'xu',
                    'wx_account': wx_account, 'dt': pub_dt, 'con': content, 'w': self.__word, 'ct': datetime.now()
                }

                try:
                    in_collection.insert(data)
                except Exception as e:
                    print ('Insert Mongo error: type <{}>, msg <{}>'.format(e.__class__, e))


class WeiXin(Base):
    def __init__(self):
        self.__base_url = BASE_URL
        self.__headers = HEADERS
        self.__user_agent = USER_AGENT
        self.__refer_first = REFER_FIRST
        self.start_page = START_PAGE
        self.end_page = END_PAGE

        self.client = MongoClient(HOST, PORT)
        self.collection = self.client[DB][COLLECTION]
        self.all_uids = self.uids

    def get_query_words(self):
        query_words = []

        for docs in self.collection.find({}, {'rel': 1, 'conp': 1}).sort([('_id', 1)]):
            w = docs['conp']

            if w not in query_words:
                query_words.append(w)

            for item in docs['rel']:
                if item not in query_words:
                    query_words.append(item)

        self.client.close()
        return query_words

    def get_headers(self, next_refer=None):
        user_agent = choice(self.__user_agent)
        next_refer = next_refer or self.__refer_first
        headers_copy = deepcopy(self.__headers)
        headers_copy['Referer'] = next_refer
        headers_copy['User-Agent'] = user_agent

        return headers_copy

    def get_cookie(self):
        pass

    @property
    def uids(self):
        return {docs['uid'] for docs in in_collection.find({}, {'uid': 1}) if 'uid' in docs}

    def extract_urls_uids(self, document, word):
        urls_uids = []
        timestamp = [_t.attr('t') for _t in document('div.s-p').items()]
        urls_tits = [(tag.attr('href'), self.trim(tag.text())) for tag in document('h4').items('a')]

        if len(urls_tits) != len(timestamp):
            return urls_uids

        for index, url_tit in enumerate(urls_tits):
            uid = self.md5(timestamp[index] + url_tit[1] + word)

            if uid not in self.all_uids:
                self.all_uids.add(uid)
                urls_uids.append({'url': url_tit[0], 'uid': uid})
        return urls_uids

    @staticmethod
    def query_index(words, cut_word):
        try:
            index = words.index(cut_word)
            return index + 1
        except ValueError:
            pass
        return 0

    @staticmethod
    def is_forbidden(document):
        css_id = '#seccodeForm'

        if document(css_id).length:
            return True
        return False

    def crawl(self, word=None, proxy=None):
        cut_word = word
        is_break = False
        proxies = {'http': 'http://%s' % proxy} if proxy else {}
        query_words = self.get_query_words()

        for word in query_words[self.query_index(query_words, cut_word):]:
            for page in range(self.start_page, self.end_page + 1):
                if page == 1:
                    url = (self.__base_url % word).encode('u8')
                    headers = self.get_headers()
                else:
                    url = (self.__base_url % word + u'&page=%s' % page).encode('u8')
                    headers = self.get_headers(url)

                html = self.get_html(url=url, headers=headers, proxies=proxies)
                document = PyQuery(html)
                # print html

                while True:
                    if self.is_forbidden(document):
                        # is_break = True
                        print('\tCrawl was forbidden, break spider, input identifying code!')
                        # break
                        time.sleep(10)
                    else:
                        break

                urls_uids = self.extract_urls_uids(document, word)
                Article(urls_uids=urls_uids, word=word).extract()

                sleep_time = randint(60, 160) if page % 4 == 0 else randint(3, 20)
                print ('[{}]: Word <{}>, Page <{}> Done, sleeping {}s!'.format(datetime.now(), word, page, sleep_time))
                time.sleep(sleep_time)

            if is_break:
                break

        in_client.close()


if __name__ == '__main__':
    if sys.argv[1:]:
        params = [unicode(p, 'gb18030').split('=') for p in sys.argv[1:]]
        WeiXin().crawl(**dict(params))

