import logging

from scrapy import signals

logger = logging.getLogger(__name__)


class DelayDownloaderMiddleware(object):
    def __init__(self, crawler):
        self.crawler = crawler
        crawler.signals.connect(self.response, signal=signals.response_downloaded)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def response(self, response, request, spider):
        slot = self.crawler.engine.downloader.slots.get(request.meta.get('download_slot'))
        slot.delay = 0
