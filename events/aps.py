import os
import sys
from os.path import abspath, dirname

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

sys.path.append(dirname(dirname(abspath(__file__))))

from events.envents import EventsWords

sqlite_path = dirname(abspath(__file__))
for sql_path in os.listdir(sqlite_path):
    if sql_path.endswith('.db'):
        os.remove(os.path.join(sqlite_path, sql_path))

jobstores = {
    # 'default': MemoryJobStore()  # `cron` fail
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
}

executors = {
    'default': ThreadPoolExecutor(3),
    # 'processpool': ProcessPoolExecutor(1)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 1
}


def get_events_info():
    EventsWords().get_events_info()


app = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
app.add_job(
    func=get_events_info,
    trigger='cron',
    hour='10',
    minute='0',
    second='0',
    misfire_grace_time=5
)

app.start()


