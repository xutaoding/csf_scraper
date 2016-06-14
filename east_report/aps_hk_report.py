# coding=utf-8

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from hk_report import HKReport

logging.basicConfig()

sched = BlockingScheduler()


def run():
    hk = HKReport()
    hk.spider()

sched.add_job(run, 'interval', max_instances=1, hours=2)
sched.start()
