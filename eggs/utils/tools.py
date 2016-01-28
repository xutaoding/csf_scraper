#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf8")
# sys.path.append('/opt/news_analyse/full_news/autumn/')

import hashlib
import difflib
from datetime import date
from eggs.db.mongodb import Mongodb
from eggs.db.pybsddb import FileBsd
from eggs.utils.conf import titles_config


def md5(md5_str):
    if not isinstance(md5_str, basestring):
        raise ValueError('md5 must string!')
    m = hashlib.md5()
    m.update(md5_str)
    return m.hexdigest()


def string_diff(a, b):
    diff = difflib.SequenceMatcher(None, a, b)
    if diff.ratio() * 100.0 >= 99.0:
        return 1
    return 0


def secondary_filter(origin):
    """
        return :
            0 title isn't need filter
            1 title need filter
    """
    for key, values in titles_config.iteritems():
        for tit in values:
            if "start" == key and string_diff(md5(tit), md5(origin.strip()[:len(tit)])):
                return 1
            elif "end" == key and string_diff(md5(tit), md5(origin.strip()[len(origin) - len(tit):])):
                return 1
            elif "in" == key and tit in origin:
                return 1
            elif "start_regex" == key and tit.match(origin.strip()):
                return 1
    return 0


def match_ratio(file_db_path, title, lock):
    val = 1  # 表示正常的
    with lock:
        filedb = FileBsd('hash', file_db_path)
        if secondary_filter(title.strip()):
            val = 2  # 表示过滤的
        
        tit_comp = md5(title.strip())
        if filedb.has_key(tit_comp):
            val = 0  # 表示上一次抓过的
        else:
            filedb.put(tit_comp)
        filedb.close()
    return val


def filter_titles(db_path):
    month = str(date.today()).split('-')[1]
    year_mon = ''.join(str(date.today()).split('-')[:-1])
    days = {'01': '31', '02': '28', '03': '31', '04': '30', '05': '31', '06': '30', '07': '31', '08': '31',
            '09': '30', '10': '31', '11': '30', '12': '31'}
    coll = Mongodb('192.168.0.212', 27017, 'arvin', 'finance_news_all')
    condition = {'date': {'$gte': long(year_mon + '01000000'), '$lte': long(year_mon + days.get(month) + '232359')}}

    ########################################################
    print 'db `title` is loading now, waiting .......'
    ########################################################

    filedb = FileBsd('hash', db_path)
    for k, doc in enumerate(coll.query(condition)):
        try:
            filedb.put(md5(doc['title']))
        except Exception as e:
            print 'filter_titles error:', e
    coll.disconnect()
    filedb.close()

    #####################################################
    print 'title filter loading finished'
    #####################################################


if __name__ == '__main__':
    title = '12月18日四大证券报头版头条内容精华摘要'
    print secondary_filter(title)
