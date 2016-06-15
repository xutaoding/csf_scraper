# -*-  coding:utf-8 -*-

from pymongo import MongoClient


class Duplicate(object):

    @classmethod
    def find_id(cls, table):
        cj_id = []
        client = MongoClient('192.168.100.20', 27017)
        collection = client['py_crawl'][table]
        cursor = collection.find()
        for cur in cursor:
            cj_id.append(cur['_id'])
        return cj_id

    @classmethod
    def filter(cls, id):
        comp_id = Duplicate.find_id('comp_info')
        jobs_id = Duplicate.find_id('jobs')
        if id in comp_id or id in jobs_id:
            return True
        else:
            return False
