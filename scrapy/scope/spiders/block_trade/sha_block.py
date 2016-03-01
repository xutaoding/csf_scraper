# -*- coding: utf-8 -*-
import scrapy
import simplejson
from scrapy.loader import ItemLoader
from scrapy.items import BlockStockFundItem


class ShaBlockSpider(scrapy.Spider):
    name = "sha_block"

    start_url="http://query.sse.com.cn/commonQuery.do?&" \
              "isPagination=true&" \
              "sqlId=COMMON_SSE_XXPL_JYXXPL_DZJYXX_LATEST_L_1&" \
              "stockId=&" \
              "startDate=%s&" \
              "endDate=%s&" \
              "pageHelp.pageSize=15&" \
              "pageHelp.pageNo=%d&" \
              "pageHelp.beginPage=1&" \
              "pageHelp.endPage=5&" \
              "pageHelp.cacheSize=1"
    
    keys = ["tradedate", "stockid", "tradeprice", "tradeamount", "tradeqty", "branchbuy", "branchsell", "ifZc"]

    def start_requests(self):
        yield scrapy.Request(self.start_url%("2016-02-25","2016-02-25",1),
                             headers={"referer": "http://www.sse.com.cn/disclosure/diclosure/block/deal/"})

    def parse(self, response):
        page_help = simplejson.loads(response.body)["pageHelp"]
        page_count = int(page_help["pageCount"])
        page_no = int(page_help["pageNo"])

        for data in page_help["data"]:
            item=BlockStockFundItem()
            for key in self.keys:
                item[key]=data[key]
            yield item

        if page_no < page_count:
            yield scrapy.Request(self.start_url % ("2016-02-25","2016-02-25",page_no+1))


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    cp = CrawlerProcess()
    cp.crawl(ShaBlockSpider)
    cp.start()
