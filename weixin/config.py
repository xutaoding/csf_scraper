HOST = '192.168.250.208'
PORT = 27017
DB = 'news'
COLLECTION = 'news_conp'

IN_HOST = '192.168.100.20'
IN_PORT = 27017
IN_DB = 'py_crawl'
IN_COLLECTION = 'weixin'

START_PAGE = 1
END_PAGE = 10
BASE_URL = u'http://weixin.sogou.com/weixin?type=2&query=%s&ie=utf8&_sug_=y&_sug_type_='

REFER_FIRST = 'http://weixin.sogou.com/'

HEADERS = {
    'Host': 'weixin.sogou.com',
    'Referer': '',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': '',
    'Connection': 'keep-alive',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

USER_AGENT = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36',

    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0',
    'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0',

    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b11pre) Gecko/20110128 Firefox/4.0b11pre',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b11pre) Gecko/20110131 Firefox/4.0b11pre',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b11pre) Gecko/20110129 Firefox/4.0b11pre',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b11pre) Gecko/20110128 Firefox/4.0b11pre',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0b11pre) Gecko/20110126 Firefox/4.0b11pre',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b10pre) Gecko/20110118 Firefox/4.0b10pre',

]

cookie = {u'ld': u'Kyllllllll2g5uPQlllllVtMzVYlllllnszXukllll9lllllVllll5@@@@@@@@@@', u'SUIR': u'810958CBBEBA8C0B7812F302BF6B77AF', u'SUID': u'9A05ADB45909950A55B05CCC000C0D59', u'LSTMV': u'722%2C68', u'SNUID': u'E96031A2D5D3E1D08F67DFF5D6F4F474', u'ABTEST': u'8|1463636525|v1', u'_ga': u'GA1.2.2103366067.1464573057', u'CXID': u'71FE50C9B43ECF71B0C86AD403F46B30', u'JSESSIONID': u'aaab0hNf2zgqt7XqAvItv', u'SUV': u'007475FAB4AD059A55B061584D803736', u'LCLKINT': u'2588', u'weixinIndexVisited': u'1', u'sct': u'15', u'ssuid': u'8612345832', u'SMYUV': u'1437622920382150', u'IPLOC': u'CN3100', u'pgv_pvi': u'2130437120'}



