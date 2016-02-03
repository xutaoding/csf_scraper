# -*- coding: utf-8 -*-
import time
from multiprocessing.dummy import Pool as ThreadPool

import configs
from agreement import AgreementWay
from base import get_html, write


class MarketMakingWay(object):
    def __init__(self):
        self.__market_making_fn = configs.mm_fn
        self.__market_making_url = configs.mm_url
        self.__market_making_headers = configs.mm_headers

        write(self.__market_making_fn, self.__market_making_headers)

    def __total_pages(self):
        return AgreementWay.unpickle(self.__market_making_url % 0, 'totalPages')

    def make_market_data(self, current_page):
        keys = ['hqzqdm', 'hqzqjc', 'hqzrsp', 'hqjrkp', 'hqzjcj', 'hqcjsl', 'hqcjje', 'hqbjw1', 'hqsjw1', 'hqzdf']

        url = self.__market_making_url % current_page
        data = AgreementWay.unpickle(url, 'content')

        for _item in data:
            item_list = AgreementWay.format([_item[k] for k in keys])
            write(self.__market_making_fn, item_list)

    def spider(self):
        pages = self.__total_pages()

        pool = ThreadPool(16)
        pool.map(self.make_market_data, range(pages))
        pool.close()
        pool.join()


if __name__ == '__main__':
    start = time.time()
    MarketMakingWay().spider()
    print 'Need time:', time.time() - start
