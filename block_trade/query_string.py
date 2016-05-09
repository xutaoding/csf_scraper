# -*- coding: utf-8 -*-

from eggs.db.mongodb import Mongodb
from eggs.db.mysql_client import MySQLClient

base_url = 'http://www.szse.cn/szseWeb/FrontController.szse?randnum=&'
query_string = 'ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1265_xyjy&TABKEY=tab1&tab1PAGECOUNT={0}&' \
               'tab1RECORDCOUNT={1}&REPORT_ACTION=navigate&tab1PAGENUM={2}'
bond_string = 'ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=dzjy_xyjy&TABKEY=tab1&tab1PAGECOUNT={0}&' \
              'tab1RECORDCOUNT={1}&REPORT_ACTION=navigate&tab1PAGENUM={2}'


user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
referer = 'http://www.sse.com.cn/disclosure/diclosure/block/deal/'

stock_fund_url = 'http://query.sse.com.cn/commonQuery.do?&jsonCallBack=&isPagination=true&' \
                          'sqlId=COMMON_SSE_XXPL_JYXXPL_DZJYXX_L_1&stockId=&startDate=%s&endDate=%s&' \
                          'pageHelp.pageSize=15&pageHelp.pageNo=1&pageHelp.beginPage=%s&pageHelp.endPage=5&' \
                          'pageHelp.cacheSize=1'

bond_url = 'http://query.sse.com.cn/commonQuery.do?&jsonCallBack=&isPagination=true&' \
                    'sqlId=COMMON_SSE_XXPL_JYXXPL_DZJYXX_L_2&stockId=&startDate=%s&endDate=%s&' \
                    'pageHelp.pageSize=15&pageHelp.pageNo=1&pageHelp.beginPage=%s&pageHelp.endPage=5&' \
                    'pageHelp.cacheSize=1'

coll_in = Mongodb('192.168.251.95', 27017, 'ada', 'base_block_trade')
coll_stock = Mongodb('192.168.251.95', 27017, 'ada', 'base_stock')
coll_fund = Mongodb('192.168.251.95', 27017, 'fund', 'base_fund')
coll_bond = Mongodb('192.168.251.95', 27017, 'ada', 'base_bond')
coll_vary = Mongodb('192.168.251.95', 27017, 'ada', 'base_share_vary')
mysql = MySQLClient("192.168.251.95", "python_team", "python_team", "ada-fd")

sha_command_history = r'casperjs D:\project\autumn\crawler\block_trade\block_trade_with_date.js ' \
                      r'--st_date={0} --ed_date={1} --outfile={0}'
sha_command_update = r'casperjs block_trade.js'
