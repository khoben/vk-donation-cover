from apscheduler.schedulers.blocking import BlockingScheduler
from donations import checkDonations
from config import DONATION_UPDATE_INTERVAL

sched = BlockingScheduler()


@sched.scheduled_job("interval", seconds=DONATION_UPDATE_INTERVAL)
def timed_job():
    checkDonations()


sched.start()
