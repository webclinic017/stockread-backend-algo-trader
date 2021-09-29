from datetime import datetime
import time
import atexit
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

def print_sleep(job_id: str):
    print(job_id)
    time.sleep(1)


def my_job(wait: int, job_id: str):
    for _ in range(wait):
        print_sleep(job_id)

    print('Job ID - {}, {}'.format(job_id, time.ctime()))


def shutdownjob(sch: BlockingScheduler):
    sch.shutdown(wait=False)


if __name__ == "__main__":

    executors = {
        'default': ThreadPoolExecutor(20)
    }
    scheduler = BlockingScheduler(max_instances=10, executors=executors)

    # The interval is set to 1 second, and you can also use minutes, hours, days, weeks, etc.
    intervalTrigger = IntervalTrigger(seconds=15)

    # # Execute the job in the first second
    # intervalTrigger = CronTrigger(second=1)

    # Set an id for the job to facilitate the subsequent operations of the job, pause, cancel, etc.
    # scheduler.add_job(my_job, 'interval', seconds=15, args=[5, 'job1'], id='my_job_id1',
    #                   next_run_time=datetime.now().replace(hour=13, minute=43, second=00))
    scheduler.add_job(my_job, intervalTrigger, args=[5, 'job1'], id='my_job_id1', next_run_time=datetime.now())
    scheduler.add_job(my_job, intervalTrigger, args=[10, 'job2'], id='my_job_id2', next_run_time=datetime.now())
    # scheduler.add_job(shutdownjob, trigger='cron', hour='16', minute='52', args=[scheduler])
    # next_run_time=datetime.utcnow().replace(hour=17, minute=37, second=00))
    scheduler.start()

    print('=== end. ===')
    # Shut down the scheduler when exiting the app
    # atexit.register(lambda: scheduler.shutdown())
