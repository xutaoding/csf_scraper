# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    url = scrapy.Field()
    date = scrapy.Field()
    src = scrapy.Field()
    cate = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    ctime = scrapy.Field()

    auth = scrapy.Field()


class BlockStockFundItem(scrapy.Item):
    tradedate = scrapy.Field()
    stockid = scrapy.Field()
    tradeprice = scrapy.Field()
    tradeamount = scrapy.Field()
    tradeqty = scrapy.Field()
    branchbuy = scrapy.Field()
    branchsell = scrapy.Field()
    ifZc = scrapy.Field()
