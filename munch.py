#this script performs a munch - it should get called by schedule_relationship
from crontab import CronTab
import os
import realtime as rt
import scrape_fleetnums as scrape
import start
import history as hist

from bus_history import update_history
from bus_realtime import update_bus_realtime

CRON_ID_STR = 'vgtfs-muncher'
cron_interval_mins = 5
munch_count = 1

# add the realtime munching cron job - its a simple command to send us a signal
def start_cron():
    with CronTab(user=True) as cron:
        cron.remove_all(comment=CRON_ID_STR)
        job = cron.new(command='kill -s USR1 {0}'.format(os.getpid()), comment=CRON_ID_STR)
        job.minute.every(cron_interval_mins)
    print('MUNCHER: cron job to munch realtime was just setup')

# very important: remove the realtime munching cron job
# This gets run every time the app is stopped gracefully (and by control-c) to
# avoid leaving useless cron jobs in the cron table
def stop_cron():
    with CronTab(user=True) as cron:
        cron.remove_all(comment=CRON_ID_STR)
    print('MUNCHER:  cron job to munch realtime was just removed')

# code to run under cron: cron uses kill to send us a SIGUSR1 signal which we handle
# called from the assigned signal handler in start.py
# this should get triggered every cron_interval_mins mins
def munch():
    global munch_count
    print('MUNCHER: Munching!')
    munch_count += 1
    rt.download_lastest_files()
    scrape.scrape()
    rt.setup_fleetnums()
    valid = rt.load_realtime()

    update_bus_realtime(True)

    if(valid):
        hist.update_last_seen()
        update_history()
    if((not rt.data_valid) and (munch_count % 2 == 0)):
        print('INVALID DATA: downloading new gtfs and trying again!')
        start.download_and_restart()
    return valid
