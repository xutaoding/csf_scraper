# -*- coding: utf-8 -*-

from datetime import date

# agreement way
filename_hq = 'hangqing.txt'
filename_deal = 'hangqing_deal.txt'
filename_declare = 'hangqing_shenbao.txt'

aw_path = 'D:/temp/' + str(date.today()).replace('-', '') + '/'

aw_hq_url = 'http://www.neeq.com.cn/nqhqController/nqhq.do?callback=&page=%s&type=X&zqdm=&sortfield=&sorttype='
aw_deal_url = 'http://www.neeq.com.cn/nqxyxxController/nqxygkxxPage.do?callback=&page=%s&zqzm=%s'
aw_declare_buy_url = 'http://www.neeq.com.cn/nqxyxxController/nqxyxxPage.do?callback=&page=%s&zqzm=%s&xyywlb=6B'
aw_declare_sale_url = 'http://www.neeq.com.cn/nqxyxxController/nqxyxxPage.do?callback=&page=%s&zqzm=%s&xyywlb=6S'

aw_headers = ['公司代码', '简称', '前收', '开盘', '成交价', '成交量(万股)', '成交额(万元)', '最高', '最低', '涨跌幅']
aw_declare_headers = ['公司代码', '报价价格(元/股)', '股份数量(股)', '委托类别', '报价单元', '自动约定号', '报价时间']
aw_deal_headers = ['公司代码', '成交价格(元/股)', '股份数量(股)', '成交金额', '买方券商', '卖方券商', '成交时间']

# market making way
mm_url = 'http://www.neeq.com.cn/nqhqController/nqhq.do?callback=&page=%s&type=Z&zqdm=&sortfield=&sorttype='
mm_headers = ['公司代码', '简称', '前收', '开盘', '成交价', '成交量(万股)', '成交额(万元)', '最高', '最低', '涨跌幅']
mm_fn = aw_path + 'market.txt'

