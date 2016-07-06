import pandas as pd
from os.path import dirname, abspath, join
from datetime import datetime

from pyquery import PyQuery
from pymongo import MongoClient

from html_loader import HtmlLoader
from conf import BASE_URL as _BU
from conf import INDEX_URL as _IU
from conf import HOST_PORT, DB, TABLE


class ReaderExcel(object):
    @property
    def excel_path(self):
        return join(dirname(abspath(__file__)), 'data', 'etf.xlsx')

    @property
    def etf_codes(self):
        df = pd.read_excel(self.excel_path, header=0)
        return [code.split()[0] for code in df['CODE'].values.tolist()]


class ETFCrawler(HtmlLoader):
    def __init__(self):
        self.base_url = _BU
        self.etf_codes = ReaderExcel().etf_codes
        self.client = MongoClient(*HOST_PORT)
        self.collection = self.client[DB][TABLE]
        self.key_func = (lambda k: '_'.join(k.replace(':', '').split()))

    def create_unique_index(self):
        pass

    def get_vitals_detail(self, vitals_document):
        index_key = 'index_url'
        vitals_data = {index_key: None}

        for li_tag in vitals_document('li').items():
            span_tag = li_tag('span')

            value = span_tag.eq(1).text()
            key = self.key_func(span_tag.eq(0).text()).lower()

            if value.lower() == 'home page':
                vitals_data[key] = (span_tag.eq(1))('a').attr('href')
            else:
                vitals_data[key] = value

            if key == 'tracks_this_index':
                vitals_data[index_key] = _IU + (span_tag.eq(1))('a').attr('href')
        return vitals_data

    def get_index_intro(self, index_url):
        intro_key = 'intro'

        if index_url is None:
            return {intro_key: None}

        html = self.get_html(index_url)
        document = PyQuery(html)('.article__textile-block ').eq(0)
        return {intro_key: document.text()}

    def get_etf_summary(self, home_url):
        summary = {'summary': {}}
        css = '.instr_summary'
        'http://www.ipathetn.com/US/16/en/details.app?partial=true&instrumentId=31021&_d=1467340430121'

        if not home_url:
            document = PyQuery('<html></html>')
        else:
            document = PyQuery(self.get_html(home_url))

        summary_doc = document(css)
        if not summary_doc.size():
            return summary

        for tag in summary_doc('.summary_doc').items():
            key = self.key_func(tag.eq(0).text())
            value = tag.eq(0).text().strip()
            summary['summary'][key] = value
        print summary
        return summary

    def insert(self, docs, **kwargs):
        docs.update(
            crt=datetime.now(),
            upt=datetime.now(),
            **kwargs
        )

        try:
            self.collection.insert_one(docs)
        except Exception as e:
            self.logger.info('Insert Mongo <{} {} {}> error: type <{}>, msg <{}>'.format(
                HOST_PORT, DB, TABLE, e.__class__, e))

    def crawl(self):
        # for code in ['JO']:
        for code in self.etf_codes:
            url = self.base_url.format(code=code)
            print url
            html = self.get_html(url=url)
            document = PyQuery(html)
            vitals = document('ul.list-unstyled').eq(0)
            data = self.get_vitals_detail(vitals)
            data.update(**self.get_index_intro(data.get('index_url')))
            data.update(**self.get_etf_summary(data.get('etf_home_page')))
            # print data
            self.insert(data, code=code)
            # break
        self.client.close()


if __name__ == '__main__':
    # print ReaderExcel().excel_path
    # print ReaderExcel().etf_codes
    ETFCrawler().crawl()
    # ETFCrawler().create_unique_index()

