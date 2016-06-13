# coding=utf-8

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
import sys
import os.path

module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(module_path)

from er_update import ErUpdate
logging.basicConfig()

sched = BlockingScheduler()


def run():
    try:
        ErUpdate().main()
    except:
        pass
sched.add_job(run, 'interval', max_instances=1, hours=2)
sched.start()
