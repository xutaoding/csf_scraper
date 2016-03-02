# -*- coding: utf-8 -*-
import scrapy

from scrapy.loader import ItemLoader
from scrapy.items import NewsItem


class BaseNewsSpider(scrapy.Spider):
    name = "base_news"
    page_urls = []
    title = ""
    date = ""
    auth = ""
    content = ""
    block = None
    next_page = None

    def start_requests(self):
        for page_url in self.page_urls:
            pages = int(page_url["pages"])
            for page in xrange(1, pages + 1):
                request = scrapy.Request(page_url["url"] % page)
                request.meta["cate"] = page_url["cate"]
                yield request

    def parse(self, response):
        sel = scrapy.Selector(response)
        for block in [sel.css(b) for b in self.block]:
            for url in block.css("a::attr(href)").extract():
                request = scrapy.Request(url, self.parse_detail)
                request.meta["cate"] = response.meta["cate"]
                yield request

        if not self.next_page:
            return

        next_page = sel.css("%s::attr(href)"%self.next_page).extract_first()
        yield scrapy.Request(next_page, callback=self.parse)

    def parse_detail(self, response):
        il = ItemLoader(NewsItem(), response=response)

        il.add_css("title", "%s::text" % self.title)
        il.add_css("date", "%s::text" % self.date)
        il.add_css("auth", "%s::text" % self.auth)
        il.add_css("content", "%s > p::text" % self.content)
        il.add_value("cate", response.meta["cate"])
        return il.load_item()


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    cp = CrawlerProcess()
    cp.crawl(BaseNewsSpider)
    cp.start()
