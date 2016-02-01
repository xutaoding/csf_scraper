# -*- coding: utf-8 -*-

import os
import time
import socket
import urllib2
from multiprocessing import Lock

base_path = 'D:/temp/'
lock = Lock()


def get_html(url, data=None):
    for i in range(1, 9):
        socket.setdefaulttimeout(20)
        req = urllib2.Request(url) if not data else urllib2.Request(url, data)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')
        try:
            response = urllib2.urlopen(req)
            feed_data = response.read()
            response.close()
            return feed_data
        except Exception, e:
            print 'Web open error', i, 'times:', e
            time.sleep(5.0)
    return '{}'


def write(file_path, lines, repl=';'):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with lock:
        if not isinstance(lines, (tuple, list)):
            raise TypeError('data format error!')

        with open(file_path, 'a') as fd:
            fd.write(repl.join(lines) + '\n')
