from datetime import datetime
import time
import atexit
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger


def my_job(wait: int, job_id: str):
    for _ in range(wait):
        print(job_id)
        time.sleep(1)

    print('Job ID - {}, {}'.format(job_id, time.ctime()))


if __name__ == "__main__":
    scheduler = BlockingScheduler(max_instances=10)

    # The interval is set to 1 second, and you can also use minutes, hours, days, weeks, etc.
    intervalTrigger = IntervalTrigger(seconds=15,
                                      start_date=datetime.now().replace(hour=13, minute=55, second=00).isoformat(),
                                      end_date=datetime.now().replace(hour=13, minute=56, second=00).isoformat())

    # Set an id for the job to facilitate the subsequent operations of the job, pause, cancel, etc.
    # scheduler.add_job(my_job, 'interval', seconds=15, args=[5, 'job1'], id='my_job_id1',
    #                   next_run_time=datetime.now().replace(hour=13, minute=43, second=00))
    scheduler.add_job(my_job, intervalTrigger, args=[5, 'job1'], id='my_job_id1')
    scheduler.add_job(my_job, intervalTrigger, args=[10, 'job2'], id='my_job_id2')
    # next_run_time=datetime.utcnow().replace(hour=17, minute=37, second=00))
    scheduler.start()

    print('=== end. ===')
