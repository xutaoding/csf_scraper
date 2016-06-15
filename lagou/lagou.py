# -*-  coding:utf-8  -*-

import lxml.html
import requests
import json
import logging
from Queue import Queue
from threading import Thread
import sys
from random import randint
from functools import partial
import re
import os.path
import pymongo
import time
from ConfigParser import ConfigParser
import codecs

logger = logging.getLogger("LaGou")
logger.addHandler(logging.NullHandler())
logging.basicConfig(level=logging.DEBUG)


class LaGou(object):
    def __init__(self, **kwargs):
        """
        LaGou web site crawling:include company information and position details
        kwargs : Http post data requests(url,data = **kwargs)
            kwargs accepted data model:
            gj : work experience
            xl : degree(such as bachelor)
            jd : staged(A staged or B staged .etc)
            hy : company field(O2O .etc)
            px :the latest job requirement
            gx: internship or full-time
            yx : salary
            city : city name
            district : district name
            bizArea : company location general information
            first : default value true
        Note : not all params fill up necessary
        """
        self.queue = Queue()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) \
                        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"}
        self.kv = kwargs
        self.page_url = r"http://www.lagou.com/jobs/list_%s"
        self.find_url = r"http://www.lagou.com/jobs/positionAjax.json"
        self.job_info_url = r"http://www.lagou.com/jobs/%s.html"
        self.com_info_url = r"http://www.lagou.com/gongsi/%s.html"
        self.company_id = set()
        self.position_id = []
        self.content_dict = []
        self.white = re.compile('\s+', re.S)

    def check_input(self):
        """
        Return bool
        Check args
        """
        standard = ['gj', 'xl', 'jd', 'hy', 'px', 'yx', 'city', 'district', 'gx', 'bizArea', 'first', 'kd']
        keys = self.kv.keys()
        for key in keys:
            if key in standard:
                continue
            else:
                logger.error("Error input:%s ,The args input string must in standard list" % key)
                return False
        logger.info("All args in standard list,Right ")
        return True

    def get_pages(self, skill):
        """
        Return total pages ,Which job search
        @:arg skill : job skill requirement
        """
        params = self.kv
        try:
            resp = requests.get(url=self.page_url % skill, params=params, timeout=20)
        except requests.ConnectTimeout, e:
            raise e.message
        tree = lxml.html.fromstring(resp.content)
        counts = tree.xpath('//div[@class="page-number"]/span[@class="span totalNum"]/text()')
        if counts:
            logger.info(counts[0])
            return int(counts[0])
        else:
            raise Exception("None: got null counts")

    def job_spider(self, skill, page_number=None, first="true"):
        """
        TODO:
        crawling all jobs by skill,Which we need search.Such as python ,java, c++ .etc
        fetch companyId ,postionId and job detail info
        @:arg skill : job skill requirement
        @:arg page_number : current page number
        @:arg first : default true
        """
        if not skill and not page_number:
            raise ValueError('Please input skill and page_numbers values')
        if not isinstance(self.kv, dict):
            raise ValueError("Please input right data format")
        self.kv['kd'] = skill
        self.kv['pn'] = page_number
        self.kv['first'] = first
        resp = requests.post(self.find_url, data=self.kv, headers=self.headers)
        if resp.status_code != 200:
            raise RuntimeError("Request http error")
        resp_dict = json.loads(resp.content)
        if resp_dict:
            self.content_dict.append(resp_dict)
            result = resp_dict['content']['positionResult']['result']
            for i in range(len(result)):
                self.position_id.append(result[i]['positionId'])
                self.company_id.add(result[i]['companyId'])

    def search_loop(self, skill):
        """
        TODO: loop insert data into job_all ,companyId, positionId
        """
        page_counts = self.get_pages(skill)
        for page in range(1, page_counts + 1):
            self.job_spider(skill, page_number=page)

    def fetch(self, threads, ids, urls, parse_name):
        """
        TODO: put job url into Queue
        :arg: threads : define how many thread should run
        """
        logger.info("loading the list of job detail info that will be crawler...")
        for id in ids:
            url = urls % id
            self.queue.put(url)
            logger.info(url)
        logger.info("%d daemon threads will be created." % threads)
        for _ in range(threads):
            t = Thread(target=self.crawl, args=(parse_name,), name="LaGouCrawler")
            t.setDaemon(True)
            t.start()
        self.queue.join()

    def crawl(self, func):
        """
        TODO: fetch job urls
        """
        while not self.queue.empty():
            try:
                url = self.queue.get_nowait()
                try:
                    resp = requests.get(url, timeout=20, headers=self.headers)
                    time.sleep(randint(3, 8))
                except requests.ConnectTimeout, e:
                    raise e.message
                out_put = partial(func, resp)
                out_put()
            except Exception, e:
                _, _, tb = sys.exc_info()
                logger.exception(tb)
            self.queue.task_done()

    def parse_job(self, resp):
        """
        @:arg : Http request response
        :return: Update resp_dict dict and return
        """
        job_requirement = ""
        tree = lxml.html.fromstring(resp.content)
        url = resp.url
        if url:
            id = int(os.path.split(url)[1].split('.')[0])
        else:
            id = ''
        requirement = tree.xpath('//dd[@class="job_bt"]')
        if requirement:
            for node in range(len(requirement)):
                job_requirement += re.sub(self.white, '', requirement[node].text_content().strip())
        else:
            job_requirement = ''
        update_dict = dict(position_info=job_requirement)
        for m in range(len(self.content_dict)):
            result = self.content_dict[m]['content']['positionResult']['result']
            for i in range(len(result)):
                if result[i]['positionId'] == id:
                    result[i].update(update_dict)

    def clear(self, tree):
        xpath = '//div[@class="mlist_total_desc"]'
        for e in tree.xpath(xpath):
            e.clear()

    def parse_company(self, resp):
        """
        :arg resp: Http request response
        :return: Company basic information, management team, company label and company detail info
        """
        basic_info = []
        manage_team = []
        label = []
        data_names = []
        detail_info = []
        infos = []
        detail_list = []
        product_info = []
        history_info = []
        new = dict()
        new_2 = dict()

        tree = lxml.html.fromstring(resp.content)
        self.clear(tree)
        url = resp.url
        if url:
            id = int(os.path.split(url)[1].split('.')[0])
        else:
            id = ''
        company_node = tree.xpath('//div[@class="company_main"]/h1/a[@class="hovertips"]')
        company_name = company_node[0].get('title') if company_node else None

        elems = tree.xpath('//div[@id="basic_container"]/text()|//div[@id="basic_container"]//span/text()')
        if elems:
            for e in range(len(elems)):
                if elems[e].strip(u'\n    ') == '':
                    continue
                basic_info.append(elems[e])

        members = tree.xpath('//ul[@class="manager_list"]/li[@class="item_has rotate_item  rotate_active "] \
                            | ////ul[@class="manager_list"]/li[@class="item_has rotate_item "]')
        if members:
            for m in members:
                if re.sub(self.white, '', m.text_content().strip()) == '':
                    continue
                manage_team.append(re.sub(self.white, '', m.text_content()).replace('\n', ''))

        labs = tree.xpath('//div[@class="tags_container item_container"]//text()')
        if labs:
            for lab in labs:
                if re.sub(self.white, '', lab.strip()) == '':
                    continue
                label.append(lab.strip(u'\n').replace('\n', ''))

        nodes = tree.xpath('//div[@class="nav_item"]|//div[@class="nav_item nav_selected"]|'
                           '//div[@class="nav_item nav_item_last"]')
        if nodes:
            for node in nodes:
                data_names.append(node.get("data-name").strip('#'))
        if 'interview_container' in data_names:
            data_names.remove('interview_container')

        for data_name in data_names:
            try:
                if data_name == "company_products":
                    title = tree.get_element_by_id(str(data_name)).find_class("item_ltitle")
                    if title:
                        product = title[0].text_content()
                    elems = tree.get_element_by_id(str(data_name)).find_class("product_details")
                    if elems:
                        for e in elems:
                            product_info.append(re.sub(self.white, '', e.text_content()))
                        new = {product: product_info}
                elif data_name == "history_container":
                    title = tree.get_element_by_id(str(data_name)).find_class("item_ltitle")
                    if title:
                        container = title[0].text_content()
                    elems = tree.get_element_by_id(str(data_name)).find_class('history_li clearfix')
                    elems_2 = tree.get_element_by_id(str(data_name)).find_class('history_li clearfix history_li_last')
                    if elems:
                        for e in elems:
                            history_info.append(re.sub(self.white, '', e.text_content()))
                    if elems_2:
                        for e in elems_2:
                            history_info.append(re.sub(self.white, '', e.text_content()))
                    new_2 = {container: history_info}
                else:
                    infos.append(tree.get_element_by_id(str(data_name)))
            except KeyError, e:
                logger.debug("%s" % e.message)

        for info in infos:
            remove_info = re.split(self.white, info.text_content())
            detail_list.append(remove_info[1])
            detail_info.append(re.sub(self.white, '', info.text_content().replace(remove_info[1], '')))
        information = dict(zip(detail_list, detail_info))
        information.update(new)
        information.update(new_2)
        self.insert(id, company_name, basic_info, manage_team, label, information)

    def load_data(self, database, table='jobs'):
        try:
            client = pymongo.MongoClient('192.168.100.20', 27017)
            collection = client[database][table]
            for m in range(len(self.content_dict)):
                result = self.content_dict[m]['content']['positionResult']['result']

                for id in range(len(result)):
                    collection.insert({
                        '_id': result[id]['positionId'],
                        'query': self.kv,
                        'job_info': result[id],
                        'ct': time.strftime("%Y%m%d%H%M%S")
                    })
        except Exception, e:
            logger.error(e.message)
        finally:
            client.close()

    def insert(self, id, company_name, basic_info, manage_team, label, detail_info):
        try:
            client = pymongo.MongoClient('192.168.100.20', 27017)
            collection = client['py_crawl']['comp_info']
            collection.insert({
                '_id': id,
                'company_name': company_name,
                'basic_info': basic_info,
                'manage_team': manage_team,
                'label': label,
                'detail_info': detail_info,
                'ct': time.strftime("%Y%m%d%H%M%S")
            })
        except Exception, e:
            logger.error(e.message)
        finally:
            client.close()

    def main(self, skill):
        """
        TODO: check_input() -> search_loop():{ job_spider():{self.get_pages()}} ->
            fetch():{
                        threads: thread
                        ids: self.position_id, self.company_id
                        urls: self.job_info_url, self.com_info_url
                        runner() -> crawl(func):{func=self.parse_job, func=self.parse_company}
                    }
        @:arg string skill such as java, python, c++ .etc.
        """
        if self.check_input():
            self.search_loop(skill=skill)
            self.fetch(1, self.position_id, self.job_info_url, self.parse_job)
            self.load_data(database='py_crawl')
            self.fetch(1, self.company_id, self.com_info_url, self.parse_company)
        else:
            raise KeyError("Error keys input,Please input once again")

    def parse_conf(self):
        """
        Return string for instance args
        """
        args = []
        config = ConfigParser()
        config.readfp(codecs.open(r'config.cfg', 'r', 'utf8'))
        options = config.items('Options')
        for j in range(len(options)):
            opt_dict = dict([it.strip() for it in item.split('=')] for item in options[j][1][1: -1].split(','))
            args.append(opt_dict)
        return args


if __name__ == '__main__':
    arg = LaGou().parse_conf()
    for i in range(len(arg)):
        try:
            lg = LaGou(city=arg[i]['city'],
                       district=arg[i]['district'],
                       bizArea=arg[i]['bizArea'],
                       gj=arg[i]['gj'],
                       xl=arg[i]['xl'],
                       jd=arg[i]['jd'],
                       hy=arg[i]['hy'],
                       px=arg[i]['px'],
                       gx=arg[i]['gx'],
                       yx=arg[i]['yx'])
            lg.main(skill=arg[i]['skill'])
        except KeyError, e:
            logger.info(e.args)
        time.sleep(randint(30, 200))


