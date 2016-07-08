from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from loaders import SyncFilesLoaders

jobstores = {
    'default': MemoryJobStore()
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
app = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
app.add_job(lambda: SyncFilesLoaders().get_files(), trigger='interval', seconds=3)
app.start()

