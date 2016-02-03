# -*- coding: utf-8 -*-

import time
import simplejson
from multiprocessing.dummy import Pool as ThreadPool

import configs
from base import get_html, write


class AgreementWay(object):
    def __init__(self):
        self.__path = configs.aw_path
        self.__fn_hq = self.__path + configs.filename_hq
        self.__fn_deal = self.__path + configs.filename_deal
        self.__fn_declare = self.__path + configs.filename_declare

        self.__hq_url = configs.aw_hq_url
        self.__deal_url = configs.aw_deal_url
        self.__declare_buy_url = configs.aw_declare_buy_url
        self.__declare_sale_url = configs.aw_declare_sale_url

        self.__base_headers = configs.aw_headers
        self.__deal_headers = configs.aw_deal_headers
        self.__declare_headers = configs.aw_declare_headers

        self.init()

    @staticmethod
    def unpickle(back_url, *args_keys):
        max_recursion = 1000

        for _ in range(max_recursion):
            response = get_html(back_url)
            try:
                data = simplejson.loads(response[1:-1])[0]
                return data[args_keys[0]] if len(args_keys) == 1 else [data[key] for key in args_keys]
            except (simplejson.JSONDecodeError, IndexError, KeyError):
                pass
        return {}

    @staticmethod
    def format(data):
        _data = []

        for _each in data:
            if isinstance(_each, basestring):
                _data.append(_each.encode('u8'))
            elif isinstance(_each, (int, float, long)):
                _data.append(str(_each))
        return _data

    def init(self):
        write(self.__fn_hq, self.__base_headers)
        write(self.__fn_deal, self.__deal_headers)
        write(self.__fn_declare, self.__declare_headers)

    def total_pages(self):
        return self.unpickle(self.__hq_url, 'totalPages')

    def agreement(self, current_page):
        keys = ['hqzqdm', 'hqzqjc', 'hqzrsp', 'hqjrkp', 'hqzjcj', 'hqcjsl', 'hqcjje', 'hqbjw1', 'hqsjw1', 'hqzdf']

        url = self.__hq_url % current_page
        hq_data = self.unpickle(url, 'content')

        for _item in hq_data:
            code = _item['hqzqdm']
            items_list = self.format([_item[k] for k in keys])
            write(self.__fn_hq, items_list)

            self.agreement_deal(code)
            self.agreement_declare(code)

    def agreement_declare(self, code):
        buy_start_page, buy_total_pages = 0, 1
        sale_start_page, sale_total_pages = 0, 1
        info_keys = ['XYWTJG', 'XYWTSL', 'XYYWLB', 'XYJYDY', 'XYYDH', 'XYWTSJ']

        while buy_start_page < buy_total_pages:
            buy_url = self.__declare_buy_url % (buy_start_page, code)

            if buy_start_page == 0:
                buy_data, buy_total_pages = self.unpickle(buy_url, 'content', 'totalPages')
            else:
                buy_data = self.unpickle(buy_url, 'content')

            for _item in buy_data:
                items_list = [code]

                for _key in info_keys:
                    if 'XYYWLB' == _key:
                        items_list.append(u'定价买入')
                    else:
                        items_list.append(_item[_key])
                write(self.__fn_declare, self.format(items_list))

            buy_start_page += 1

        while sale_start_page < sale_total_pages:
            sale_url = self.__declare_sale_url % (sale_start_page, code)

            if sale_start_page == 0:
                sale_data, sale_total_pages = self.unpickle(sale_url, 'content', 'totalPages')
            else:
                sale_data = self.unpickle(sale_url, 'content')

            for _sale_item in sale_data:
                items_list = [code]

                for _key in info_keys:
                    if 'XYYWLB' == _key:
                        items_list.append(u'定价卖出')
                    else:
                        items_list.append(_sale_item[_key])
                write(self.__fn_declare, self.format(items_list))

            sale_start_page += 1

    def agreement_deal(self, code):
        start_page, total_pages = 0, 1
        keys = ['HQCJJG', 'HQCJSL', 'HQCJJE', 'HQBJYDY', 'HQSJYDY', 'HQCJSJ']

        while start_page < total_pages:
            if start_page == 0:
                data, total_pages = self.unpickle(self.__deal_url % (start_page, code), 'content', 'totalPages')
            else:
                data = self.unpickle(self.__deal_url % (start_page, code), 'content')

            for _item in data:
                items_list = [code]
                items_list.extend([_item[_k] for _k in keys])
                write(self.__fn_deal, self.format(items_list))

            start_page += 1

    def spider(self):
        pages = self.total_pages()
        print 'Total pages:', pages

        pool = ThreadPool(16)
        pool.map(self.agreement, [_ for _ in range(pages)])
        pool.close()
        pool.join()


if __name__ == '__main__':
    start_time = time.time()
    AgreementWay().spider()
    print 'Need time:', time.time() - start_time
