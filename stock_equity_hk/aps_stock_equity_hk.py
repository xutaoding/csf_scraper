# coding=utf-8

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from stock_equity import StockEquity

logging.basicConfig()

sched = BlockingScheduler()


def run():
    steq = StockEquity()
    steq.main()
    steq.check_omission()

sched.add_job(run, 'interval', max_instances=5, hours=2)
sched.start()
