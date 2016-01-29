# -*- coding: UTF-8 -*-

import re
import uuid
import time
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool

from base import BaseDownloadHtml
from tools import ratio, data_by_table_type
import query_string


class MarkReplace(object):
    def __init__(self, code, mark):
        self._code = code
        self._mark = re.compile(r'\s+', re.S).sub('', mark)

    def question_mark(self):
        """ many companies have ? """
        mark = '?'
        code_mark = {
            '002207_SZ_EQ': '.',                # 艾克拜尔?买买提
            '300329_SZ_EQ': '务有限公司',    # 宁波大榭开发区协力模具技术服?  宁波大榭开发区同心企业管理服?
            '300302_SZ_EQ': '企业',           # 天津东方富海股权投资基金合伙?
            '300217_SZ_EQ': '有限合伙）',     # 新疆东方世纪股权投资合伙企业?
            '002722_SZ_EQ': '司',              # 上海攀成德企业管理顾问有限公?
            '002567_SZ_EQ': '司',              # 湖南唐人神控股投资股份有限公?
            '002529_SZ_EQ': '限公司',         # 福州市鼓楼区华达鑫投资咨询有?
            '002498_SZ_EQ': '器有限公司',      # 常州高新技术产业开发区常能电?
            '002492_SZ_EQ': '业（有限合伙）',   # 乌鲁木齐新永鑫股权投资合伙企?
            '002412_SZ_EQ': '企业',             # 新疆汉森股权投资管理有限合伙?
            '002402_SZ_EQ': '企业（有限合伙）',   # 乌鲁木齐和谐安泰股权投资合伙?
            '002297_SZ_EQ': '司',              # 湖南湘投高科技创业投资有限公?
            '002289_SZ_EQ': '限合伙）',       # 南京瑞森投资管理合伙企业（有?
            '002081_SZ_EQ': '司',              # 苏州金螳螂企业（集团）有限公?
            '000755_SZ_EQ': '司',              # 山西省经济建设投资集团有限公?
            '000609_SZ_EQ': '司',              # 北京中北能能源科技有限责任公?
            '000158_SZ_EQ': '司',              # 石家庄常山纺织集团有限责任公?
            '000096_SZ_EQ': '限公司',        # 深圳市广聚投资控股（集团）有?
        }

        if self._code in code_mark and self._mark.endswith(mark):
            self._mark = self._mark.replace(mark, code_mark[self._code])
            return True
        return False

    def plus_mark(self):
        """ 300283_SZ_EQ + """
        mark = '+'
        replace = '伙）'

        if self._mark.endswith(mark):
            self._mark = self._mark.replace(mark, replace)
            return True
        return False

    def excalmatory_mark(self):
        """ 002432_SZ_EQ ! """
        mark = '!'
        replace = '有限合伙）'

        if self._mark.endswith(mark):
            self._mark = self._mark.replace(mark, replace)
            return True
        return False

    def replace_mark(self):
        if self.excalmatory_mark():
            return self._mark
        elif self.plus_mark():
            return self._mark
        elif self.question_mark():
            return self._mark
        return self._mark


class SzxExecutives(BaseDownloadHtml):
    def __init__(self, query_start_dt=None, query_end_dt=None):
        self._base_url = query_string.base_url
        self._query_start_date = query_start_dt
        self._query_end_date = query_end_dt
        self._coll_in = query_string.coll_in
        self._latest_cd_data = self._coll_in.get({"typ": "szx"}, spec_sort=('cd', -1))['cd']

        if self._query_start_date is None and self._query_end_date is None:
            self.crawl_pages = 10
            self._pages, self._count = self.get_pages_count(query_string.URL)
            self._query_string = query_string.query_string_update.format(self._pages, self._count, '{0}')
        elif self._query_start_date is not None and self._query_end_date is not None:
            url_part = query_string.query_string_by_date.format(self._query_start_date, self._query_end_date)
            self._pages, self._count = self.get_pages_count(self._base_url + url_part)
            self.crawl_pages = int(self._pages)
            self._query_string = query_string.query_string_history.format(self._query_start_date, self._query_end_date,
                                                                          self._pages, self._count, '{0}')
        else:
            raise ValueError('query start date or end date is nor excepted!')
        print 'Query count: [{0}], pages: [{1}]'.format(self._count, self._pages)

        # expression what we want ot base date
        self.__secu = re.compile(r"<td  class='cls-data-td' style='mso-number-format.*?align='center' >(.*?)</td>", re.S)
        self.__change = re.compile(r"<td  class='cls-data-td'  width='80'  align='right' >(.*?)</td>", re.S)
        self.__after = re.compile(r"<td  class='cls-data-td'  width='80'  align='center' >(.*?)</td>", re.S)
        self.__org = re.compile(r"<td  class='cls-data-td'  width='60'  align='center' >(.*?)</td>", re.S)
        self.__price = re.compile(r"<td  class='cls-data-td'  width='55'  align='right' >(.*?)</td>", re.S)
        self.__scp = re.compile(r"<td  class='cls-data-td'  width='90'  align='center' >(.*?)</td>", re.S)
        self.__n_c_d_r = re.compile(r"<td  class='cls-data-td'  width='70'  align='center' >(.*?)</td>", re.S)

    def get_pages_count(self, url):
        pat_pages_count = re.compile(r'<td align="left" width="222px">(.*?)</td>', re.S)
        html = self.get_html(url)
        try:
            pages_count = re.findall(r'(\d+)', pat_pages_count.findall(html)[0])
            return pages_count[2], pages_count[0]
        except (IndexError, ):
            return 0, 0

    def parse_data(self, url):
        html = self.get_html(url, encoding=True)

        # all regex expression show target of crawling what above regex, as follow:
        # 证券代码(secus) 变动股份数量(changes) 变动比例-当日结存股数(__afters) 证券简称(org)
        # 成交均价(price) 股份变动人姓名(scps) 董监高姓名-变动日期-变动原因-变动人与董监高的关系(ncdrs)
        try:
            secus = self.__secu.findall(html)
            # orgs = self.__org.findall(html)
            changes = self.__change.findall(html)
            afters = [after for i, after in enumerate(self.__after.findall(html)) if i % 2]  # 当日结存股数
            prices = self.__price.findall(html)
            scps = self.__scp.findall(html)
            _ncdr = self.__n_c_d_r.findall(html)  # name, cd, case, relation
            ncdrs = [_ncdr[k - 3:k + 1] for k, nd in enumerate(_ncdr) if (k + 1) % 4 == 0]
            return secus, changes, afters, prices, scps, ncdrs
        except (IndexError, AttributeError) as e:
            raise e.__class__('parse data error:' + e.message)

    def main(self, multi_pool_page=None):
        assert multi_pool_page is None or isinstance(multi_pool_page, int), '`multi_pool_page` must None or int.'

        if multi_pool_page is None:
            start_page, end_page = 1, self.crawl_pages
        else:
            start_page, end_page = multi_pool_page, multi_pool_page

        for page in range(start_page, end_page + 1):
            url = self._base_url + self._query_string.format(page)
            secus, changes, afters, prices, scps, ncdrs = self.parse_data(url)
            for i in range(len(secus)):
                # Getting secu_code, orgid with `tick` from coll_stock table
                # Getting name_en, pid with `董监高姓名` from coll_exec table
                # Getting to_ratio, cir_ratio with `变动股份数量` and `secu_code` from coll_stock and coll_vary table

                # update data change_date greater than self._latest_cd_data
                cp_flag = self._latest_cd_data < ncdrs[i][1]

                secu_code, orgid = data_by_table_type({'tick': secus[i]}, [('code',), ('org', 'id')], 'stock')
                query_name_en__pid = {'name.szh': ncdrs[i][0], 'orgid': orgid}
                name_en, pid = data_by_table_type(query_name_en__pid, [('name', 'en'), ('pid',)], 'exec')
                to_ratio, cir_ratio = ratio(changes[i], secu_code, 'stock', 'vary')

                # uuid is unique identifier
                name = ''.join([secus[i], ncdrs[i][0], ncdrs[i][1], changes[i], prices[i], ncdrs[i][2],
                                afters[i], scps[i].replace('\\', ''), ncdrs[i][3]])
                uid_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
                data = {
                    'secu': secu_code or secus[i], 'org': orgid, 'change': changes[i], 'after': afters[i],
                    'price': prices[i], 'cd': ncdrs[i][1], 'cause': ncdrs[i][2], 'relation': ncdrs[i][3],
                    'stat': 1, 'name': {'szh': ncdrs[i][0], 'en': name_en},
                    'scp': {
                        'szh': MarkReplace(secu_code, scps[i].replace('\\', '')).replace_mark(),
                        'en': data_by_table_type({'name.szh': scps[i]}, [('name', 'en')], 'exec')
                    },
                    'cur': 'CNY', 'rd': '', 'pid': pid, 'uuid': uid_uuid, 'typ': 'szx',
                    'upu': 'system', 'upt': datetime.now(), 'torat': to_ratio, 'cirrat': cir_ratio
                }

                if not cp_flag and not self._coll_in.get({'uuid': uid_uuid}, {'secu': 1}):
                    self._coll_in.insert(data)
                elif cp_flag:
                    self._coll_in.insert(data)
            print 'page: [{0}] done!'.format(page)
        self._coll_in.disconnect()

    def multi_thread_crawl(self):
        interval = 48
        pages_list = range(1, self.crawl_pages + 1)
        div, mod = divmod(len(pages_list), interval)
        arguments = [pages_list[interval * i: interval * (i + 1)] for i in range(div + (mod and 1))]

        pool = ThreadPool(16)
        for pages_args in arguments:
            pool.map(self.main, pages_args)
            time.sleep(30)
        pool.close()
        pool.join()


if __name__ == '__main__':
    # SzxExecutives().main()
    SzxExecutives('2015-01-29', '2015-01-29').main()


