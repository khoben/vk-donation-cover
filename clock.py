from apscheduler.schedulers.blocking import BlockingScheduler
from main import main
from config import INTERVAL
sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=INTERVAL)
def timed_job():
    main()


sched.start()