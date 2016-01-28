# -*- coding: utf-8 -*-

from eggs.db.mongodb import Mongodb

URL = 'http://www.szse.cn/main/disclosure/jgxxgk/djggfbd/'

base_url = 'http://www.szse.cn/szseWeb/FrontController.szse?randnum=&'

query_string_by_date = 'ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1801_cxda&TABKEY=tab1&selectGsbk=&txtDMorJC=&' \
                       'txtGgxm=&txtStart={0}&txtEnd={1}&REPORT_ACTION=search'

query_string_update = 'ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1801_cxda&TABKEY=tab1&tab1PAGECOUNT={0}&' \
                      'tab1RECORDCOUNT={1}&REPORT_ACTION=navigate&tab1PAGENUM={2}'

query_string_history = 'ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1801_cxda&txtStart={0}&txtEnd={1}&TABKEY=tab1&' \
                       'tab1PAGECOUNT={2}&tab1RECORDCOUNT={3}&REPORT_ACTION=navigate&tab1PAGENUM={4}'


referer = 'http://www.sse.com.cn/disclosure/credibility/change/'
user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'

sha_query_string = 'http://query.sse.com.cn/commonQuery.do?&jsonCallBack=&isPagination=true&' \
                   'sqlId=COMMON_SSE_XXPL_CXJL_SSGSGFBDQK_S&COMPANY_CODE=&NAME=&BEGIN_DATE=%s&END_DATE=%s&' \
                   'pageHelp.pageSize=15&pageHelp.pageNo=1&pageHelp.beginPage=%s&pageHelp.cacheSize=1&' \
                   'pageHelp.endPage=5'


coll_in = Mongodb('192.168.250.200', 27017, 'ada', 'base_executive_regulation')
coll_stock = Mongodb('192.168.250.200', 27017, 'ada', 'base_stock')
coll_exec = Mongodb('192.168.250.200', 27017, 'ada', 'base_executive')
coll_vary = Mongodb('192.168.250.200', 27017, 'ada', 'base_share_vary')
coll_curr = Mongodb('192.168.250.200', 27017, 'ada', 'dict_currency')
