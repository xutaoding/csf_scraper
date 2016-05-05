import sys
from os.path import abspath, dirname

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

sys.path.append(dirname(dirname(abspath(__file__))))

from events.envents import EventsWords


jobstores = {
    'default': MemoryJobStore()
}

executors = {
    'default': ThreadPoolExecutor(3),
    # 'processpool': ProcessPoolExecutor(1)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 1
}

app = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
app.add_job(EventsWords().get_events_info, trigger='cron', hour='9', minute='30', second='0', misfire_grace_time=10)
app.start()

