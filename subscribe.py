import sys
from pytz import utc
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import MySpamMethods



sched = BlockingScheduler()
sched.timezone = utc
logging.basicConfig()


#@sched.scheduled_job('interval', minutes=3)
#def timed_job():
  #print('This job is run every 3 minutes.')
  #MySpamMethods.spamsample()
  #sys.stdout.flush()

@sched.scheduled_job('cron', hour='*', )
def scheduled_job():
   print('This job is run every hour')
   #MySpamMethods.spamsample()
   sys.stdout.flush()

if __name__ == '__main__':
   sched.start()


