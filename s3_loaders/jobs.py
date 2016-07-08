import os
from os.path import dirname, abspath

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from loaders import SyncFilesLoaders


def create_sqlite():
    sqlite_path = dirname(abspath(__file__))
    for sql_path in os.listdir(sqlite_path):
        if sql_path.endswith('.db'):
            os.remove(os.path.join(sqlite_path, sql_path))

create_sqlite()

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
}

# using ThreadPoolExecutor as default other than ProcessPoolExecutor(not work) to executors
executors = {
    'default': ThreadPoolExecutor(2),
    # 'processpool': ProcessPoolExecutor(50)
    # 'default': ProcessPoolExecutor(20)  # not work
}

job_defaults = {
    'coalesce': False,
    'max_instances': 1
}


def jobs():
    SyncFilesLoaders().get_files()

app = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
app.add_job(jobs, trigger='cron', minute='*/10')
app.start()

