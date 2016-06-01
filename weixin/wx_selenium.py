from __future__ import unicode_literals
import re
import sys
import time
import hashlib
import urllib2
from random import randint
from random import choice
from datetime import datetime

import requests
from pyquery import PyQuery
from pymongo import MongoClient
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from config import START_PAGE, END_PAGE
from config import HOST, PORT, DB, COLLECTION
from config import IN_HOST, IN_PORT, IN_DB, IN_COLLECTION
from config import USER_AGENT, REFER_FIRST

in_client = MongoClient(IN_HOST, IN_PORT)
in_collection = in_client[IN_DB][IN_COLLECTION]


class Base(object):
    @staticmethod
    def get_html(url, headers=None, cookies=None, **kwargs):
        required_cookie = cookies
        required_headers = headers or {'User-Agent': choice(USER_AGENT)}
        for _ in range(3):
            try:
                response = requests.get(url, headers=required_headers, cookies=required_cookie, **kwargs).content
                return response
            except Exception as e:
                print "Get html error:", e.__class__, e
        return ''

    @staticmethod
    def get_raw_html(url, data=None):
        for i in range(1, 4):
            req = urllib2.Request(url) if not data else urllib2.Request(url, data)
            req.add_header('User-Agent', choice(USER_AGENT))

            try:
                response = urllib2.urlopen(req, timeout=30)
                feed_data = response.read()
                response.close()
                return feed_data
            except Exception as e:
                print 'Web open error', i, 'times:', e
                time.sleep(3)
        return '<html></html>'

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
            html = self.get_raw_html(url)
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


class WeixinSelenium(Base):
    def __init__(self):
        self.start_page = START_PAGE
        self.end_page = END_PAGE
        self.weixin_url = REFER_FIRST

        self.driver = Firefox()

        self.client = MongoClient(HOST, PORT)
        self.collection = self.client[DB][COLLECTION]
        self.all_uids = self.uids

    def open_weixin_browser(self, word):
        self.driver.get(self.weixin_url)
        self.driver.set_page_load_timeout(3)

        self.driver.find_element_by_id('upquery').send_keys(word)
        self.driver.find_element_by_class_name('swz').click()
        self.driver.implicitly_wait(3)

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

    @property
    def uids(self):
        return {docs['uid'] for docs in in_collection.find({}, {'uid': 1}) if 'uid' in docs}

    def extract_urls_uids(self, word):
        urls_uids = []
        timestamp = [_t.get_attribute('t') for _t in self.driver.find_elements_by_css_selector('div.s-p')]
        urls_tits = [(t.get_attribute('href'), self.trim(t.text))
                     for t in self.driver.find_elements_by_css_selector('h4 a')]

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
            return index
        except ValueError:
            pass
        return 0

    @property
    def is_forbidden(self):
        css_id = 'seccodeForm'

        try:
            if self.driver.find_element_by_id(css_id):
                return True
        except NoSuchElementException:
            pass
        return False

    def appear_element(self, by):
        try:
            WebDriverWait(self.driver, 20).until(lambda driver: driver.find_element_by_id(by))
            return True
        except TimeoutException:
            pass
        return False

    def crawl(self, word=None, go=0):
        cut_word = word
        is_go = True
        is_break = False
        go_page = int(go)
        next_page_css = 'sogou_page_%s'
        query_words = self.get_query_words()
        ind = self.query_index(query_words, cut_word)

        for index, word in enumerate(query_words[ind:], 1):
            self.open_weixin_browser(word)

            for page in range(self.start_page + 1, self.end_page + 2):
                if is_go and page < go_page:
                    continue
                else:
                    is_go = False

                if self.is_forbidden:
                    is_break = True
                    print('\tCrawl was forbidden, break spider, input identifying code!')
                    break

                if page != go_page:
                    urls_uids = self.extract_urls_uids(word=word)
                    Article(urls_uids=urls_uids, word=word).extract()

                if page <= self.end_page:
                    if not self.appear_element(by=next_page_css % page):
                        break

                    self.driver.find_element_by_id(next_page_css % page).click()
                wait_time = randint(8, 30) if page % 5 == 0 else randint(3, 15)

                if page != go_page:
                    print('[{}]: {} Word <{}>, Page <{}> Done, sleeping {}s!'.format(
                        datetime.now(), ind + index, word, page - 1, wait_time))
                self.driver.implicitly_wait(wait_time)

            if is_break:
                break

        in_client.close()
        self.driver.close()


if __name__ == '__main__':
    wx_sel = WeixinSelenium()

    if sys.argv[1:]:
        params = [unicode(p, 'gb18030').split('=') for p in sys.argv[1:]]
        wx_sel.crawl(**dict(params))
