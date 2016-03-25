# -*- coding: utf-8 -*-
import os
import re
import time
import os.path
import requests
import pymongo
from optparse import OptionParser
from datetime import datetime, date
from multiprocessing.dummy import Pool as ThreadPool

client = pymongo.MongoClient('192.168.250.200', 27017)
path = os.path.dirname(os.path.abspath(__file__)) + '/config_stock_equity.txt'
log_path = os.path.dirname(os.path.abspath(__file__)) + '/' + str(date.today())
db = client.ada
coll_stock = db.base_stock
coll_share_vary = db.base_share_vary


def get_html(url, data=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0'}
    for _ in range(0, 3):
        try:
            if data is None:
                r = requests.get(url, params={}, timeout=30.0, headers=headers)
            else:
                r = requests.post(url, data=data, timeout=30.0, headers=headers)
            return r.content
        except Exception as e:
            pass
    return 'None'


def write(file_abs_path, sequ, replace='\n'):
    dir_path = os.path.dirname(file_abs_path)
    file_name = os.path.basename(file_abs_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    os.chdir(dir_path)

    with open(file_name + '.txt', 'a') as fd:
        sequence = replace.join(sequ) if isinstance(sequ, (list, tuple)) else sequ + replace
        fd.writelines(sequence)


def remove_comment(source_html):
    remove_tags_lists = [re.compile(r'<!--.*?-->', re.S), re.compile(r'<!.*?>', re.S), ]
    for re_value in remove_tags_lists:
        source_html = re_value.sub('', source_html)
    return source_html


class StockEquity(object):
    def __init__(self):
        self.omission_codes = []
        self._pattern = re.compile(r'Issued Shares.*?<font.*?>(.*?)&nbsp;.*?<br>\(as at(.*?)\)', re.S)

    def get_all_codes(self, by_step):
        all_codes = []
        with open(path) as fd:
            for each_line in fd:
                item = each_line.strip()
                all_codes.append(''.join(['0' * (5 - len(item)), item]))
        all_codes.sort()
        div, mod = divmod(len(all_codes), by_step)
        length = div if mod == 0 else div + 1
        return [all_codes[k * by_step:(k + 1) * by_step] for k in range(length)]

    def id_from_stock(self, code):
        try:
            org_id = coll_stock.find_one({'code': code + '_HK_EQ'}, {'org.id': 1})
            return org_id['org']['id']
        except Exception as e:
            print 'id_from_stock error:', e

    def latest_share_dict(self, s_id):
        try:
            for d in coll_share_vary.find({'org.id': s_id}).sort([('vdt', -1)]).limit(1):
                d.pop('_id')
                return d
        except Exception as e:
            print 'latest_total_share error:', e

    def update_equity(self, code):
        url = 'http://www.hkex.com.hk/eng/invest/company/profile_page_e.asp?WidCoID=%s&WidCoAbbName=' \
              '&Month=&langcode=e' % code

        id_from = self.id_from_stock(code)
        date_list = (lambda s: re.compile(r'\d+').findall(s))
        recent_share_dict = self.latest_share_dict(id_from) if id_from is not None else None
        if recent_share_dict is None:
            self.log_omission(code, id_from, 'last issue share is None from mongodb', 'error')
            return

        try:
            share_text, date_text = self._pattern.findall(remove_comment(get_html(url)))[0]
            issued_share = ''.join(re.compile(r'\d+', re.S).findall(share_text.strip()))
            print_text = 'latest share: [%s], web share: [%s] | ' % (recent_share_dict['total'], issued_share)
            if recent_share_dict['total'] != issued_share:
                recent_share_dict['src'] = url
                recent_share_dict['total'] = recent_share_dict['share'][0]['amt'] = issued_share
                recent_share_dict['vdt'] = datetime.strptime('-'.join(date_list(date_text)), '%d-%m-%Y')
                recent_share_dict['crt'] = recent_share_dict['upt'] = datetime.now()
                recent_share_dict['stat'] = 2
                coll_share_vary.insert(recent_share_dict)
                print print_text, code + '_HK_EQ | id:', id_from, ' |date text: ', date_text, ' | Updating the latest...'
            else:
                print print_text, code + '_HK_EQ | id:', id_from,  ' |date text: ', date_text, ' | Already the latest...'
        except Exception as e:
            self.omission_codes.append(code)
            print 'update_equity error:', e
            self.log_omission(code, id_from, e, 'update_equity error')

    def log_omission(self, code, idf, e_type, error):
        message = ' | '.join([str(datetime.now()),  'code:' + code,  'id:' + str(idf), '%s: [%s]' % (error, str(e_type))])
        write(log_path, message)

    def check_omission(self, miss=None):
        if miss is None:
            miss_codes = self.omission_codes
            del self.omission_codes[:]
        else:
            miss_codes = miss

        for code in miss_codes:
            code = ''.join(['0' * (5 - len(code)), code])
            print 'omission code:', code + '_HK_EQ'
            steq.update_equity(code)

    def main(self):
        all_items = 0
        pool = ThreadPool(16)
        for k, code_list in enumerate(self.get_all_codes(30)):
            all_items += len(code_list)
            pool.map(self.update_equity, [arg for arg in code_list])
            print 'indx: [%s], all items: [%s]' % (k + 1, all_items), 'sleeping 15s ......'
            time.sleep(15)
            if all_items % 90 == 0:
                print 'now program will sleep 60 * 2 seconds....'
                time.sleep(60 * 2)
        pool.close()
        pool.join()
        client.close()


if __name__ == '__main__':
    while 1:
        steq = StockEquity()
        parser = OptionParser()
        option, args = parser.parse_args()

        strf = time.strftime('%H%M')
        if strf in ['2330', '1300']:
            steq.main()
            steq.check_omission()

        if args:
            steq.check_omission(args)
            break

        if int(strf[2:]) % 3 == 0:
            print time.strftime('%Y-%m-%d %H:%M:%S %A')
        time.sleep(20)
