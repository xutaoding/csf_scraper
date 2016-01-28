# -*- coding: utf-8 -*-

import sys
import os.path
from apscheduler.schedulers.blocking import BlockingScheduler

module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(module_path)

from sha_block import BlockBond, BlockStockFund
from secu_bond import SzxBond
from szse_security import SzxSecurity




def job():
    BlockStockFund().get_data()
    BlockBond().get_data()

    SzxBond().main()
    SzxSecurity().main()


if __name__ == '__main__':
    job_defaults = {
        'coalesce': False,
        'max_instances': 1
    }

    scheduler = BlockingScheduler(job_defaults=job_defaults)
    scheduler.add_job(job, 'cron', args=(), minute=15, hour='9,13,17', day_of_week='mon-fri')
    scheduler.start()
