from apscheduler.schedulers.blocking import BlockingScheduler
from donations import checkDonations
from config import INTERVAL
sched = BlockingScheduler()

# store last donation
lastDonation = {}

@sched.scheduled_job('interval', seconds=INTERVAL)
def timed_job():
    global lastDonation
    checkDonations(lastDonation)

sched.start()