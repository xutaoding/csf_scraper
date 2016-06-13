# coding=utf-8

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
logging.basicConfig()

sched = BlockingScheduler()
import sys
import os.path
from time import sleep, strftime

module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(module_path)

from sha_mt import ShaMarginTrading
from szx_mt import SzxMarginTrading


def block_fs():
    ShaMarginTrading().main()
    SzxMarginTrading().main()

sched.add_job(block_fs, 'interval', max_instances=1, hours=2)
sched.start()
