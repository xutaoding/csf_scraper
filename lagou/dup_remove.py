# -*-  coding:utf-8 -*-

from pymongo import MongoClient


def find_id():
    cj_id = set()
    client = MongoClient('192.168.100.20', 27017)
    collection = client['py_crawl']['comp_info']
    cursor = collection.find()
    for cur in cursor:
        cj_id.add(cur['_id'])
    coll = client['py_crawl']['jobs']
    cur_sor = coll.find()
    for cur in cur_sor:
        cj_id.add(cur['_id'])
    client.close()
    return cj_id
cj_ids = find_id()

