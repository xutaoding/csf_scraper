# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import hashlib
from datetime import date, timedelta
from os.path import exists, dirname, join, abspath

import requests
import simplejson
from pymongo import MongoClient

from bucket import Bucket
from log import logger
from settings import SETTINGS


class UtilsBase(object):
    logger = logger

    def __init__(self, query_date=None):
        """
        基本的工具，
        :param query_date:
        """
        self.bucket = Bucket()

        self.query_date = date.today().strftime('%Y-%m-%d') if query_date is None else query_date
        self.aws_path = SETTINGS['AWS_PATH'].format(dt=self.query_date.replace('-', ''))

        if not exists(dirname(self.aws_path)):
            os.makedirs(dirname(self.aws_path))

        # Base Mongo Config
        self.client = MongoClient(SETTINGS['MONGO_HOST'], SETTINGS['MONGO_PORT'])
        self.collection = self.client[SETTINGS['MONGO_DB']][SETTINGS['MONGO_COLLECTION']]

        # Filtering Config
        filter_path = join(dirname(abspath(__file__)), 'filter')

        if not exists(filter_path):
            os.makedirs(filter_path)
        self.filter_filename = join(filter_path, 'filter.txt')
        self._get_unique_from_file()

    def _get_unique_from_file(self):
        """ 从过滤文件取得 Mongo 中的 `_id` 来作为过滤字段 """
        if not exists(self.filter_filename):
            self.logger.info('Warning, not have `filter.txt` file')

        with open(self.filter_filename) as fp:
            self.filtering = {line.strip() for line in fp}

    def _get_unique_from_mongo(self):
        """ 可以从上海环境122.144.95取得关于当日的公告信息 """
        required_pdf = []
        api_url = 'http://122.144.134.3:8010/api/cron/mongo_info/95/?date=%s' % self.query_date
        to_python_data = simplejson.loads(requests.get(api_url, timeout=120).content)

        self.logger.info('<filter.txt> existed <{c}> record!'.format(c=len(self.filtering)))

        for docs in to_python_data:
            _id = docs.pop('_id')

            if _id not in self.filtering:
                self.filtering.add(_id)
                required_pdf.append(docs)
        return required_pdf

    @staticmethod
    def get_md5(string):
        if not isinstance(string, basestring):
            raise ValueError('md5 must string!')
        m = hashlib.md5()
        try:
            m.update(string)
        except UnicodeEncodeError:
            m.update(string.encode('u8'))
        return m.hexdigest()


class SyncFilesLoaders(UtilsBase):
    """ 将A股公告下载到AWS 84 服务器上 """
    def __init__(self, query_date=None):
        self.loader_count = 0
        super(SyncFilesLoaders, self).__init__(query_date)
        self.required_files = self._get_unique_from_mongo()
        self.logger.info('Download S3 files Start: Expect Download Count <{c}>, at <{dt}>'.format(
            c=len(self.required_files), dt=self.query_date))

    @staticmethod
    def valid_filename(path, fn, ext, prefix=True):
        fn_path = path + fn + '.' + ext

        if prefix and fn_path.startswith('/'):
            return fn_path[1:]
        return fn_path

    def get_files(self):
        """ 将文件(PDF, TXT, HTML或其他类型)从AWS S3下载下来 """
        for docs in self.required_files:
            s3_name = self.valid_filename(docs['url'], docs['fn'], docs['ext'])
            local_name = self.valid_filename(self.aws_path, docs['title'], docs['ext'], prefix=False)
            # local_name = self.valid_filename(self.aws_path, docs['fn'], docs['ext'])

            if self.bucket.get(s3_name, local_name):
                self.loader_count += 1

    def __del__(self):
        with open(self.filter_filename, 'wb') as fp:
            fp.writelines('\n'.join(list(self.filtering)).encode('u8'))

        self.client.close()
        self.logger.info('Download S3 files Finished: Download Count <{c}>, at <{dt}>\n'.format(
            c=self.loader_count, dt=self.query_date))


def get_date_range(start, end=None):
    """
    calculate date range
    :param start: string, yyyymmdd, start date
    :param end: string, yyyymmdd, end date
    :return: list, date string range list
    """
    date_range = []
    split_ymd = (lambda _d: (int(_d[:4]), int(_d[4:6]), int(_d[6:8])))
    date_start = date(*split_ymd(start))
    date_end = date(*split_ymd(end or start))

    while date_start <= date_end:
        date_range.append(str(date_start))
        date_start = timedelta(days=1) + date_start
    return date_range


if __name__ == '__main__':
    import sys
    arguments = [arg.strip() for arg in sys.argv[1:]]

    if not arguments:
        SyncFilesLoaders().get_files()
        pass
    else:
        # 满足0000-00-00, 0000-00-00格式
        dt_range = get_date_range(*arguments)

        for _query_date in dt_range:
            SyncFilesLoaders(_query_date).get_files()

