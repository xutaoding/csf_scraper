from __future__ import unicode_literals

base_url = 'http://baike.sogou.com%s'
suffix = '/enterBarLemma.v?searchText={name}'

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/44.0.2403.157 Safari/537.36',
}


host = '192.168.100.20'
port = 27017
db = 'py_crawl'
collection = 'jrj'

in_host = '192.168.100.20'
in_port = 27017
in_db = 'py_crawl'
in_collection = 'baike'
