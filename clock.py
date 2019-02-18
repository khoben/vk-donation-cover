import requests
from apscheduler.schedulers.blocking import BlockingScheduler

from config import DONATION_UPDATE_INTERVAL
from donations import checkDonations
from lxml.html import fromstring

sched = BlockingScheduler()

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


@sched.scheduled_job("interval", seconds=DONATION_UPDATE_INTERVAL)
def timed_job():
    proxies = get_proxies()
    checkDonations(proxies=proxies)


sched.start()
