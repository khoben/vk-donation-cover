from apscheduler.schedulers.blocking import BlockingScheduler
from donations import checkDonations
from config import INTERVAL
sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=INTERVAL)
def timed_job():
    checkDonations()


sched.start()
