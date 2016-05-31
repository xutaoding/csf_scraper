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

cookie = [
    # {u'SUIR': u'1464250820', u'SUID': u'9AA7F63A60C80D0A00000000573D5BF9', u'SNUID': u'D158099AEFEBDAF4A7E77A73EF5E08F4', u'ABTEST': u'0|1464250820|v1', u'LCLKINT': u'1281', u'JSESSIONID': u'aaaV0nsoS0Wzp44wktItv', u'SUV': u'1463639046589595', u'PHPSESSID': u'ofhumri4ijr24rabeh0o0rc3e2', u'IPLOC': u'CN3100', u'LSTMV': u'92%2C295', u'sct': u'2', u'weixinIndexVisited': u'1'}
    # , {u'ld': u'Kyllllllll2g5uPQlllllVtMzVYlllllnszXukllll9lllllVllll5@@@@@@@@@@', u'seccodeRight': u'success', u'SUIR': u'810958CBBEBA8C0B7812F302BF6B77AF', u'SUID': u'9A05ADB45909950A55B05CCC000C0D59', u'LSTMV': u'707%2C65', u'SNUID': u'E96031A2D5D3E1D08F67DFF5D6F4F474', u'ABTEST': u'8|1463636525|v1', u'_ga': u'GA1.2.2103366067.1464573057', u'CXID': u'71FE50C9B43ECF71B0C86AD403F46B30', u'JSESSIONID': u'aaab0hNf2zgqt7XqAvItv', u'SUV': u'007475FAB4AD059A55B061584D803736', u'LCLKINT': u'8426', u'PHPSESSID': u'37qgq640nf57a1uldhvvvh8da7', u'weixinIndexVisited': u'1', u'sct': u'17', u'successCount': u'1|Tue, 31 May 2016 04:28:18 GMT', u'ssuid': u'8612345832', u'refresh': u'1', u'SMYUV': u'1437622920382150', u'IPLOC': u'CN3100', u'pgv_pvi': u'2130437120'}
    # , {u'ld': u'Kyllllllll2g5uPQlllllVtMzVYlllllnszXukllll9lllllVllll5@@@@@@@@@@', u'seccodeRight': u'success', u'SUIR': u'810958CBBEBA8C0B7812F302BF6B77AF', u'SUID': u'9A05ADB45909950A55B05CCC000C0D59', u'LSTMV': u'715%2C63', u'SNUID': u'E96031A2D5D3E1D08F67DFF5D6F4F474', u'ABTEST': u'8|1463636525|v1', u'_ga': u'GA1.2.2103366067.1464573057', u'CXID': u'71FE50C9B43ECF71B0C86AD403F46B30', u'JSESSIONID': u'aaab0hNf2zgqt7XqAvItv', u'SUV': u'007475FAB4AD059A55B061584D803736', u'LCLKINT': u'6436', u'PHPSESSID': u'37qgq640nf57a1uldhvvvh8da7', u'weixinIndexVisited': u'1', u'sct': u'17', u'successCount': u'1|Tue, 31 May 2016 05:24:18 GMT', u'ssuid': u'8612345832', u'refresh': u'1', u'SMYUV': u'1437622920382150', u'IPLOC': u'CN3100', u'pgv_pvi': u'2130437120'}

    {u'ld': u'nyllllllll2g5UIdlllllVtdvX1lllllNnWL5Zllll9lllll9Zlll5@@@@@@@@@@', u'wuid': u'AAFAOd5+EQAAAAqSMyUKxAEA1wA=', u'fromwww': u'1', u'SUID': u'6D06E2741508990A0000000056F893C9', u'IPLOC': u'CN3100', u'ABTEST': u'0|1463640359|v1', u'JSESSIONID': u'aaawdq0-h8g3faQcH3euv', u'SNUID': u'149CCD5F2A2E1E2202A84F112B4594BE', u'SUV': u'1459131337378471', u'weixinIndexVisited': u'1', u'sct': u'25', u'ssuid': u'9999492928', u'usid': u'EP6CHrWhMCF150Na', u'pgv_pvi': u'976066560'}
    , {u'SUIR': u'9CA1F13D060334A0F84D80B207D0329E', u'SUID': u'3FB6E7742E08990A0000000057456A75', u'SNUID': u'3CB5E3770306301EE339AEB904D72281', u'ABTEST': u'0|1464167029|v1', u'LCLKINT': u'1668', u'JSESSIONID': u'aaaegpIh7CGmddEbH3euv', u'SUV': u'00451BC574E7B63F57456A7569A80260', u'IPLOC': u'CN3100', u'LSTMV': u'168%2C168', u'sct': u'6', u'weixinIndexVisited': u'1'}

]

