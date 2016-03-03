# -*- coding: utf-8 -*-
from base import BaseNewsSpider

class IfengSpider(BaseNewsSpider):
    name = "ifeng"
    title = "#artical_topic"
    date = ".ss01"
    auth = ".ss03"
    content = "#main_content"
    block = ["h2", "h3", ".list03"]
    page_urls = [{"url": "http://finance.ifeng.com/cmppdyn/756/665/%s/dynlist.html", "pages": 1, "cate": "宏观新闻"}]


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    cp = CrawlerProcess()
    cp.crawl(IfengSpider)
    cp.start()
