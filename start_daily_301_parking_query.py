#!/usr/bin/env python

from apscheduler.scheduler import Scheduler
import parking_301
import time

"""
Script starts a cron-like process that will query the 301 API for parking status in NYC.
"""

# initialize
scheduler = Scheduler()
scheduler.start()

# schedule the job
scheduler.add_cron_job(parking_301.write_parking_status_json, minute='0')
print 'starting cron job..'

while True: # silly work around to avoid thread termination
	time.sleep(60)

