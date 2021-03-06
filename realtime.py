import wget
import time
from datetime import datetime
from datetime import date
import os.path
from os import path
import datastructure as ds
import start
import json
import businfotable as businfo

#realtime bus status
STATUS_UNKNOWNFLEETNUM = 0 #this is not a BC transit bus we know about
STATUS_INACTIVE = 1 #this bus is not active right now
STATUS_TRACKING = 2 #this bus is tracking but is not assigned to any block
STATUS_LOGGEDIN = 3 #this bus is assigned to a block but is not "onroute"
STATUS_ONROUTE = 4 #this bus is fully on route (all systems go)
STATUS_UNKNOWN_TRANSLATION = 5 #we recognize this fleet number but we don't have a translation for it (same as 0 really)

#flag to log data or not
data_valid = False

# from protoc
import protobuf.data.gtfs_realtime_pb2 as rt

class RTVehiclePosition:
    def __init__(self, fleetid, tripid, blockid, scheduled, onroute, stopid, lat, lon):
        self.fleetid = fleetid
        self.tripid = tripid
        self.scheduled = scheduled
        self.onroute = onroute
        self.stopid = stopid
        self.blockid = blockid
        self.lat = lat
        self.lon = lon
        self.fleetnum = 'Unknown'
        self.unknown_fleetnum_flag = True

def make_realtime_filename():
    return 'gtfsrt_vehiclepos' + str(int(time.time())) + '.bin'

default_positions_file = 'data/realtime_downloads/default_gtfrealtime_VehiclePositions.bin'
vehicle_positions_path = default_positions_file
override_rt_flag = False  # for debug

# global dicts exported that other modules make use of
rtvehicle_dict = {}
id2fleetnum_dict = {}
fleetnum2id_dict = {}

victoria_gtfs_rt_url = 'http://victoria.mapstrat.com/current/gtfrealtime_VehiclePositions.bin'
last_rt_download_time = time.time()
# dynamically download the latest realtime files, save them somewhere with a logical path, update path variables here

# download the latest realtime updates from bc transit api
def download_lastest_files():
    global vehicle_positions_path
    global last_rt_download_time
    print('Downloading latest gtfs-realtime files...')
    last_rt_download_time = time.time()
    fname = make_realtime_filename()
    fpath = 'data/realtime_downloads/' + fname
    try:
        wget.download(victoria_gtfs_rt_url, fpath)
        if path.exists(fpath):
            vehicle_positions_path = fpath  # update path to new download
    except:
        print('victoria GTFS download failed!')
    # now, test the date to see if we are out of date
    if(int(ds.get_today_str()) > int(ds.this_sheet_enddate)):
        print('THIS SHEET IS OUT OF DATE! Please reload the server lol')
    if override_rt_flag:  # for debug
        vehicle_positions_path = default_positions_file

# update the fleet number lookup dictionaries based on the latest entries
# in the id2fleetnum json file that the scraping module maintains
# allows the rest of the site to map fleetnumbers to internal realtime ids and vice versa
def setup_fleetnums():
    global id2fleetnum_dict
    global fleetnum2id_dict
    fleetnum2id_dict = {}
    print('Realtime: Imported latest fleet numbers!')
    with open('data/nextride/id2fleetnum.json', 'r') as f:
        id2fleetnum_dict = json.load(f)
    for pair in id2fleetnum_dict.items(): #flip the dict
        fleetnum2id_dict[pair[1]] = pair[0]

def get_data_refreshed_time_str():
    return time.strftime("%B %-d, %Y at %H:%M", time.localtime(last_rt_download_time))

def get_gmaps_url(lat, lon):
    return 'https://www.google.com/maps/search/?api=1&query={0},{1}'.format(lat, lon)

# returns status, and rt object if any
def get_current_status(fleetnum):
    if(not businfo.is_known_bus(fleetnum)):
        return STATUS_UNKNOWNFLEETNUM, False
    try:
        fleetid = fleetnum2id_dict[fleetnum]
    except KeyError:
        return STATUS_UNKNOWN_TRANSLATION, False
    try:
        vehicle_rt = rtvehicle_dict[fleetid]
        if(vehicle_rt.scheduled and vehicle_rt.onroute):
            return STATUS_ONROUTE, vehicle_rt
        if(vehicle_rt.scheduled):
            return STATUS_LOGGEDIN, vehicle_rt
        if(vehicle_rt.onroute and not vehicle_rt.scheduled): #should be impossible?
            print('REALTIME: Whaaat? apparently a vehicle is onroute but not scheduled')
            return STATUS_TRACKING, vehicle_rt
        return STATUS_TRACKING, vehicle_rt
    except KeyError:
        return STATUS_INACTIVE, False

'''
The Detect Outdated GTFS Algorithm...

When a new gtfs is uploaded, this apparently breaks the site because generally
the blockids are scrambled around. The site has the old gtfs while the realtime
data comes with blockids for the new gtfs, leading to the site reporting busses
being on the wrong blocks - especially bad for the new history features.

There is a script to download a new static gtfs, and archive the old one. Loading
a new gtfs static data dump in, however, presently requires restarting the server -
hopefully that can change in a later version. I have recently included code to do
the restart for now. However, when to run this download and restart?

What this algorithm is doing is checking to see if any of realtime bus
entries include a blockid that points to a block in the static gtfs
that makes no sense: for example, the bus is apparently on a tuesday block
but its currently saturday or the block listed does not contain the route
the bus is apparently on.

It is possible by chance that a given block happens to also be on the right day.
For that reason, a number of blocks are to be tried. For at least 7 service ids
and normally more, its a 1/7 chance that we miss an error on days alone
for each comparison, and 10 comparisons means there is a 99.9999996% chance of
missing the error for any given realtime update, and 10 checks should still be fast.

When there are fewer logged in busses than 10, we just check all of them.
'''

#number of comparisons to do here on loading a new gtfs realtime
CONFIDENCE_COUNT = 10
def check_for_broken_gtfs():
    tries = 0
    if len(rtvehicle_dict) == 0:
        return False
    for vehicle in rtvehicle_dict.values():
        if(tries >= 10):
            return False #we've hit the limit, all is apparently good
        if(not vehicle.scheduled): #we dont care about unscheduled vehicles they tell us nothing
            continue #doesnt count as a try
        try:
            serviceid1 = ds.blockdict[vehicle.blockid].serviceid
            serviceid2 = ds.tripdict[vehicle.tripid].serviceid
            if(serviceid1 != serviceid2):
                print('CHECKGTFS: service ids of block and trip dont match: {0} vs {1}'.format(serviceid1, serviceid2))
                return True
            dayofweek = ds.days_of_week_dict[serviceid1]
            this_hour = datetime.now().hour
            try: #inner try because we can get special day strings which we'll ignore
                dnum = ds.dow_number_dict[dayofweek]
                if(this_hour < 5):
                    if(( dnum + 1 ) != datetime.today().weekday()):
                        print('CHECKGTFS: realtime id {0} not running on service day (its past 12): {1} vs {2}'.format(vehicle.fleetid, dnum, datetime.today().weekday()))
                        return True
                else:
                    if(dnum != datetime.today().weekday()):
                        print('CHECKGTFS: realtime id {0} not running on today: {1} vs {2}'.format(vehicle.fleetid, dnum, datetime.today().weekday()))
                        return True
            except KeyError: #case for weekdays with consolidated mon - thurs gtfs
                if(dayofweek == 'Mon-Thurs' and this_hour >= 5):
                    if(datetime.today().weekday() > 3):
                        print('CHECKGTFS: realtime id {0} not running on today: {1} vs {2}'.format(vehicle.fleetid, dnum, datetime.today().weekday()))
                        return True
                continue #doesnt count as a try
        except KeyError:
            print('CHECKGTFS: realtime block has invalid blockid')
            return True
        #if we got down here, things look ok for this one - increment and try again
        tries +=1
    return False #we got out of the loop, so I guess that means its fine

def handle_key_error():
    print('Hit a key error (But the heuristic says the static gtfs is fine?)')
    if(start.RELOAD_ENABLED):    
        start.download_and_restart()

# just for interest
busidlist = []
count_scheduled = 0
count_unsched = 0

pos_data = None

# main function for realtime - parses the latest realtime files that have been
# downloaded and saved into the realtime datastructures for the rest of the site to use
def load_realtime():
    print('Loading the realtime data now...')
    global rtvehicle_dict
    global count_scheduled
    global count_unsched
    global busidlist
    global pos_data
    global data_valid
    count_offroute = 0
    count_scheduled = 0
    count_unsched = 0
    busidlist = []
    rtvehicle_dict = {}
    with open(vehicle_positions_path, 'rb') as vpp_f:
        feed_message = rt.FeedMessage()
        feed_message.ParseFromString(vpp_f.read())

    pos_data = feed_message.entity
    for vehicle_struct in pos_data:
        try:
            bus = vehicle_struct.vehicle
            fleetid = bus.vehicle.id
        except AttributeError:
            print('What??? No vehicle and or id in this bus?')
            continue
        try:
            trip = bus.trip
            if(bus.stop_id != ''):
                stopid = bus.stop_id
                onroute = True
            else:
                onroute = False
                stopid = 'EMPTY'
                count_offroute += 1

            tripid = trip.trip_id
            if(trip.schedule_relationship == 0 and tripid != ''):
                scheduled = True
                try:
                    blockid = ds.tripdict[tripid].blockid
                except KeyError:
                    blockid = '0' #uh oh - something is wrong....
                count_scheduled += 1
            else:
                scheduled = False
                count_unsched += 1
                blockid = 'NONE'
        except AttributeError:
            stopid = 'None: Not signed in'
            tripid = 'NONE'
            blockid = 'NONE'
            scheduled = False
            count_unsched += 1
            onroute = False
        try:
            pos = bus.position
            lat = pos.latitude
            lon = pos.longitude
        except AttributeError:
            print('No Lat Lon!')
            lat = 0
            lon = 0
        rtvehicle_dict[fleetid] = RTVehiclePosition(
            fleetid, tripid, blockid, scheduled, onroute, stopid, lat, lon)
        busidlist.append(fleetid)
    print('Populated the realtime structure...')
    print('Scheduled: {0} Unscheduled: {1} Total: {2}; Offroute: {3}'.format(
        count_scheduled, count_unsched, len(busidlist), count_offroute))
    ret = check_for_broken_gtfs()
    if(ret):
        print('CHECKGTFS: GTFS is apparently busted right now')
        data_valid = False
    else:
        print('CHECKGTFS: static GTFS seems fine')
        data_valid = True
    setup_fleetnums()
    print('Fleet number translation list (from nextride) setup: {0} fleet numbers known'.format(
        len(id2fleetnum_dict)))
    return (not ret)
