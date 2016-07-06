import time
import urllib2
import urllib
import requests
from random import choice

from log import logger as _logger


class HtmlLoader(object):
    logger = _logger

    @classmethod
    def get_html(cls, url, headers=None, cookies=None, **kwargs):
        required_cookie = cookies
        required_headers = headers or {'User-Agent': choice(USER_AGENT)}

        for _ in range(3):
            try:
                response = requests.get(url, headers=required_headers, cookies=required_cookie, timeout=40, **kwargs)
                return response.content
            except Exception as e:
                cls.logger.info("Get html error: type <{}>, msg <{}>".format(e.__class__, e))
        return '<html></html>'

    @classmethod
    def get_raw_html(cls, url, data=None, **kwargs):
        for i in range(1, 4):
            req = urllib2.Request(url) if not data else urllib2.Request(url, urllib.urlencode(data))
            req.add_header('User-Agent', choice(USER_AGENT))

            for head_value in kwargs.itervalues():
                for key, value in head_value.iteritems():
                    req.add_header(key, value)

            try:
                response = urllib2.urlopen(req, timeout=30)
                feed_data = response.read()
                response.close()
                return feed_data
            except Exception as e:
                cls.logger.info('Web open error: type <{}>, msg <{}>, time <{}>'.format(e.__class__, e, i))
                time.sleep(3)
        return '<html></html>'

USER_AGENT = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36',

    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0',
    'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0',

    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b11pre) Gecko/20110128 Firefox/4.0b11pre',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b11pre) Gecko/20110131 Firefox/4.0b11pre',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b11pre) Gecko/20110129 Firefox/4.0b11pre',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b11pre) Gecko/20110128 Firefox/4.0b11pre',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0b11pre) Gecko/20110126 Firefox/4.0b11pre',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b10pre) Gecko/20110118 Firefox/4.0b10pre',
]
