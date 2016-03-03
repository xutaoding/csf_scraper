# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import hashlib

class NewsPipeline(object):
    def process_item(self, item, spider):
        news="\n".join([
            item["url"],
            item["date"],
            item["src"],
            item["cate"],
            item["title"],
            "#&#".join(item["content"]).strip(),
            "0",
            item["ctime"]
        ])

        md5=hashlib.md5()
        md5.update(item["url"])

        txt_path="%s%s%s_%s.txt"%(spider.txt_path,os.sep,item["date"],md5.hexdigest())

        with open(txt_path,"w") as txt:
            txt.write(news.encode("utf8"))


class ShaBlockPipeline(object):
    def process_item(self,item,spider):
        pass
