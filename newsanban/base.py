# -*- coding: utf-8 -*-

import os
import time
import urllib2
from multiprocessing import Lock

base_path = 'D:/temp/'
lock = Lock()


def get_html(url, data=None):
    for i in range(1, 13):
        req = urllib2.Request(url) if not data else urllib2.Request(url, data)
        req.add_header('Host', 'v2.neeq.com.cn')
        req.add_header('Referer', 'http://v2.neeq.com.cn/nq/quotation.html?tabId=X')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/44.0.2403.157 Safari/537.36')

        try:
            response = urllib2.urlopen(req, timeout=30)
            feed_data = response.read()
            response.close()
            return feed_data
        except Exception as e:
            print 'Web open error', i, 'times:', e
            time.sleep(5.0)
    return '([{}])'


def write(file_path, lines, repl=';'):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with lock:
        if not isinstance(lines, (tuple, list)):
            raise TypeError('data format error!')

        with open(file_path, 'a') as fd:
            fd.write(repl.join(lines) + '\n')
