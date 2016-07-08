# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import hashlib
from datetime import date
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

        if query_date is not None:
            dt = query_date.replace('-')
        else:
            dt = date.today().strftime('%Y%m%d')
        self.query_date = query_date
        self.aws_path = SETTINGS['AWS_PATH'].format(dt=dt)

        if not exists(dirname(self.aws_path)):
            os.makedirs(dirname(self.aws_path))

        # Base Mongo Config
        self.client = MongoClient(SETTINGS['MONGO_HOST'], SETTINGS['MONGO_PORT'])
        self.collection = self.client[SETTINGS['MONGO_DB']][SETTINGS['MONGO_COLLECTION']]

        # Filtering Config
        self.filtering = set()
        filter_path = join(dirname(abspath(__file__)), 'filter')

        if not exists(filter_path):
            os.makedirs(filter_path)
        self.filter_filename = join(filter_path, 'filter.txt')
        self._get_unique_from_file()

    def _get_unique_from_file(self):
        """ 从过滤文件取得 Mongo 中的 `_id` 来作为过滤字段 """
        if not exists(self.filter_filename):
            raise ValueError('Have not `filter.txt` file')

        with open(self.filter_filename) as fp:
            self.filtering.union({line.strip() for line in fp})

    def _get_unique_from_mongo(self):
        """ 可以从上海环境122.144.95取得关于当日的公告信息 """
        required_pdf = []
        api_url = 'http://122.144.134.3:8010/api/cron/mongo_info/95/'
        to_python_data = simplejson.loads(requests.get(api_url, timeout=120).content)

        for docs in to_python_data:
            _id = str(docs.pop('_id'))

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
    def __init__(self):
        self.loader_count = 0
        super(SyncFilesLoaders, self).__init__()
        self.required_files = self._get_unique_from_mongo()
        self.logger.info('Download S3 files Start: Expect Download Count <{c}>'.format(c=len(self.required_files)))

    @staticmethod
    def valid_filename(path, fn, ext):
        fn_path = path + fn + '.' + ext

        if fn_path.startswith('/'):
            return fn_path[1:]
        return fn_path

    def get_files(self):
        """ 将文件(PDF, TXT, HTML或其他类型)从AWS S3下载下来 """
        for docs in self.required_files:
            s3_name = self.valid_filename(docs['url'], docs['fn'], docs['ext'])
            local_name = self.valid_filename(self.aws_path, docs['title'], docs['ext'])
            # local_name = self.valid_filename(self.aws_path, docs['fn'], docs['ext'])

            self.bucket.get(s3_name, local_name)
            self.loader_count += 1

    def __del__(self):
        with open(self.filter_filename, 'wb') as fp:
            fp.writelines('\n'.join(list(self.filtering)).encode('u8'))

        self.client.close()
        self.logger.info('Download S3 files Finished: Download Count <{c}>'.format(c=self.loader_count))


if __name__ == '__main__':
    SyncFilesLoaders().get_files()
