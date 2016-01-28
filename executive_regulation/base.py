# -*- coding: utf-8 -*-

import requests
import chardet
from requests.exceptions import ConnectionError, Timeout, InvalidURL, HTTPError


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
