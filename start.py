#!/usr/bin/env python
# set up for linux

import os
import sys
import web
import munch
import signal
import inspect
import subprocess
import requestlogger
import realtime as rt
import history as hist
import datastructure as ds

from bus_history import update_history
from bus_realtime import update_bus_realtime

#some config
AUTO_RELOAD = True # Will we auto reload when we detect that our gtfs is out of date?
RELOAD_ENABLED = True # is the reloading behavior allowed at all?
COMBINE_WEEKDAYS = False #this doesn't actually do anything right now, and is no longer really needed

# Gracefully exit on a control-c: remove our realtime cron job
def controlc_handler(sig, frame):
    print('\n')
    munch.stop_cron()
    print('EXITING: Gooodbye Everybody!')
    sys.exit(0)

# The call to restart the server - we stop the cron job, and exec ourselves.
# The reason for restart is we load in the new static gtfs again (datastructure.py)
def restart_server():
    if(RELOAD_ENABLED):
        print('\n')
        munch.stop_cron()
        print('RESTARTING: Loading New static GTFS!')
        os.execv(inspect.getfile(lambda: None), sys.argv)

# This method calls a shell script to download the latest static files, and then
# Restarts the server, loading them in.
def download_and_restart():
    print('INVALID GTFS: Automatically restarting... (or reload requested?)')
    try:
        subprocess.call(['./download_new_gtfs.sh'], timeout = 45)
    except subprocess.TimeoutExpired:
        try:
            subprocess.call(['./download_new_gtfs.sh'], timeout = 60)
        except subprocess.TimeoutExpired:
            print('WHAT: timeout expired twice, guess no connection?')
            controlc_handler()
    subprocess.call(['./download_new_routes.sh'], timeout = 15)
    restart_server()
    print('this should never be seen hahaha!')

# This is the function we run when poked by our munching cron job. That job sends
# us a user signal (SIGUSR1), and we install this function as the handler.
def crontask_handler(sig, frame):
    try:
        valid = munch.munch()
        if((not valid) and AUTO_RELOAD):
            download_and_restart()
    except Exception as e:
        # We should not let python exceptions propogate out of here, so we catch them all
        print('MUNCH: (in sighandler) Hit exception...')
        print('MUNCH: Error was: ' + str(e))
    return

# Main routine - start everything up.
if __name__ == "__main__":
    # Hook up signal handlers
    signal.signal(signal.SIGINT, controlc_handler)
    signal.signal(signal.SIGUSR1, crontask_handler)
    # Load in the static gtfs file - this is the core data crunching
    ds.start()
    # Get the latest realtime updates
    rt.download_lastest_files()
    # Check that the realtime is consistant with our data
    valid = rt.load_realtime()
    if(not valid):
        # If its not, set so we don't record anything to history because its wrong.
        # We will automtically download a new gtfs reload upon a future munch here
        print('ERROR: Not valid on startup... now thats a zinger.')
        print('ERROR: Try running the download new gtfs script and try again')
        print('ERROR: Going without logging...')
        rt.data_valid = False
    # Update the (local) history files
    hist.update_last_seen()
    # If we've got this far, we're just about ready to roll. Add the munching cron job
    munch.start_cron()
    # And off we go! To the web file!

    update_bus_realtime()
    update_history()

    web.startup()
