# -*- coding: utf-8 -*-

import re
import requests
from pyquery import PyQuery
from config import CONFIG
from multiprocessing.dummy import Pool as TheadPool
from apscheduler.schedulers.blocking import BlockingScheduler

from eggs.utils.bridge import Bridge
from eggs.db.mysql_client import MySQLClient


def remove_js_style(func):
    def html_parse_wrapper(*args, **kwargs):
        _html = func(*args, **kwargs)
        remove_tags_dict = dict(_comments_=re.compile(r'<!.*?>', re.S | re.I),
                                _script_=re.compile(r'<script.*?>.*?</script>', re.S | re.I),
                                _style_=re.compile(r'<style.*?>.*?</style>', re.S | re.I))
        for re_value in remove_tags_dict.itervalues():
            _html = re_value.sub('', _html)
        return _html
    return html_parse_wrapper


@remove_js_style
def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:36.0) Gecko/20100101 Firefox/36.0'}
    try:
        r = requests.get(url, timeout=30, headers=headers)
        return r.content
    except Exception as e:
        print e
    return ''


def static_app_count(url_conf_dct):
    # spider download count of zhitou app from baidu, apk, 360, wandoujia, huawei, qq platform.
    url, kwargs = url_conf_dct['url'], url_conf_dct['conf']
    index, selector = kwargs.get('eq'), kwargs['selector']
    document = PyQuery(unicode(get_html(url), 'utf-8'))
    app_count = lambda t: re.compile(r'(\d+\.)?(\d+)').findall(t)
    try:
        text = document(selector).text() if index is None else document(selector).eq(index).text()
        if kwargs.get('platform') == 'hiapk':
            return kwargs['type'], text

        download_count = ''.join(app_count(text)[0])
        if u'万' in text:
            download_count = int(float(download_count) * 10000)
        return kwargs['type'], download_count
    except (IndexError, AttributeError):
        return kwargs['type'], 0


def login_app_count(cmd_typ):
    # to fetch download count of app from appchina, qpp_mi, jifeng platform.
    cmd, typ = cmd_typ
    app_count = Bridge(cmd).value
    if app_count.strip().isdigit():
        return typ, app_count.strip()
    return typ, 0


def get_data():
    sorted_type = [('appchina', 5), ('app_mi', 6), ('jifeng', 8)]
    command_type = [('casperjs login_app.js {0}'.format(app_typ[0]), app_typ[1]) for app_typ in sorted_type]

    pool = TheadPool(8)
    rets = pool.map(static_app_count, [CONFIG[k] for k in CONFIG])
    rets.extend(pool.map(login_app_count, command_type))
    pool.close()

    db = MySQLClient('122.144.134.3', 'ada_user', 'ada_user', 'invest')
    sql = "INSERT INTO mobile_app_count(typ, platform, total_count, day_count, upt) values(%s, %s, %s, %s, NOW())"
    platform = {1: u'百度手机助手', 2: u'安卓市场', 3: u'91手机助手', 4: u'应用宝', 5: u'掌上应用汇',
                6: u'小米', 7: u'360手机助手', 8: u'机锋市场', 9: u'豌豆荚', 10: u'华为应用'}
    for ty, num in rets:
        day_count, total_count = num if isinstance(num, tuple) else ('', num or '')
        print ty, platform.get(ty), day_count, total_count
        db.execute(sql, *(ty, platform.get(ty), total_count, day_count))
    db.disconnect()


if __name__ == '__main__':
    job_defaults = {
        'coalesce': False,
        'max_instances': 1
    }

    scheduler = BlockingScheduler(job_defaults=job_defaults)
    scheduler.add_job(get_data, 'cron', args=(), minite=15, hour='9, 17', day_of_week='mon-fri')
    scheduler.start()

    # get_data()
