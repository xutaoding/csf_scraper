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
    def unpickle(dumps, comment=None):
        try:
            data = simplejson.loads(dumps[1:-1])
            return data[0]
        except (simplejson.JSONDecodeError, IndexError) as e:
            print 'Error:', e.__class__, e, dumps[:15]
            print 'Comment:', comment
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

    def total_pages(self, typ=0):
        """
        :param typ: int, 0 is hangqing, 1 is deal, 2, is shenbao buy info, 3 is shenbao sale info
        """
        map_url = {
            0: self.__hq_url,
            1: self.__deal_url,
            2: self.__declare_buy_url,
            3: self.__declare_sale_url
        }
        response = get_html(map_url[typ])
        return self.unpickle(response, map_url[typ]).get('totalPages', 1)

    def agreement(self, current_page):
        keys = ['hqzqdm', 'hqzqjc', 'hqzrsp', 'hqjrkp', 'hqzjcj', 'hqcjsl', 'hqcjje', 'hqbjw1', 'hqsjw1', 'hqzdf']

        url = self.__hq_url % current_page
        response = get_html(url)
        hq_data = self.unpickle(response, url)['content']

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
            url = self.__declare_buy_url % (buy_start_page, code)
            buy_response = get_html(url)
            but_data = self.unpickle(buy_response, url)

            for _item in but_data['content']:
                items_list = [code]

                for _key in info_keys:
                    if 'XYYWLB' == _key:
                        items_list.append(u'定价买入')
                    else:
                        items_list.append(_item[_key])
                write(self.__fn_declare, self.format(items_list))

            if buy_start_page == 0:
                buy_total_pages = but_data.get('totalPages', 1)

            buy_start_page += 1

        while sale_start_page < sale_total_pages:
            sale_url = self.__declare_sale_url % (sale_start_page, code)
            sale_response = get_html(sale_url)
            sale_data = self.unpickle(sale_response, sale_url)

            for _sale_item in sale_data['content']:
                items_list = [code]

                for _key in info_keys:
                    if 'XYYWLB' == _key:
                        items_list.append(u'定价卖出')
                    else:
                        items_list.append(_sale_item[_key])
                write(self.__fn_declare, self.format(items_list))

            if sale_start_page == 0:
                sale_total_pages = sale_data.get('totalPages', 1)

            sale_start_page += 1

    def agreement_deal(self, code):
        start_page, total_pages = 0, 1
        keys = ['HQCJJG', 'HQCJSL', 'HQCJJE', 'HQBJYDY', 'HQSJYDY', 'HQCJSJ']

        while start_page < total_pages:
            url = self.__deal_url % (start_page, code)
            sale_response = get_html(url)
            data = self.unpickle(sale_response, url)

            for _item in data['content']:
                items_list = [code]
                items_list.extend([_item[_k] for _k in keys])
                write(self.__fn_deal, self.format(items_list))

            if start_page == 0:
                total_pages = data.get('totalPages', 1)

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
