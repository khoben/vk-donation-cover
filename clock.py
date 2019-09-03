import requests
from apscheduler.schedulers.blocking import BlockingScheduler

from config import DONATION_UPDATE_INTERVAL
from donations import checkDonations
from lxml.html import fromstring

sched = BlockingScheduler()

@sched.scheduled_job("interval", seconds=DONATION_UPDATE_INTERVAL)
def timed_job():
    checkDonations()


sched.start()
