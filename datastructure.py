from datetime import date
import start as start_mod
from stop_time import load_stop_times

pathprefix = './data/google_transit/'

midday_secs = 43200  # number of secs at midday

tripspath = pathprefix + 'trips.txt'
shapespath = pathprefix + 'shapes.txt'
routespath = pathprefix + 'routes.txt'
stoptimespath = pathprefix + 'stop_times.txt'
stoppath = pathprefix + 'stops.txt'
calendarpath = pathprefix + 'calendar.txt'
calendar_dates_path = pathprefix + 'calendar_dates.txt'
# directionid dict
directionid_dict = {'0': 'Outbound', '1': 'Inbound'}

#calendar constants:
CONST_WEEKDAY = 1
CONST_WEEKDAY_EXCEPT_FRI = 2
CONST_WEEKEND = 3
CONST_MON = 4
CONST_TUES = 5
CONST_WED = 6
CONST_THURS = 7
CONST_FRI = 8
CONST_SAT = 9
CONST_SUN = 10
CONST_SPECIAL = 11

# string like 15:42:52 -> number of seconds since midnight
def hms_to_sec(hms):
    (h, m, s) = hms.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

# get the start time of the trip in seconds for sorting
# put a big number past the end of the day for (invalid) trips with no start time
def trip_to_numseconds(trip):
    if(trip.starttime == 'N/A'):
        return 1000000000
    return hms_to_sec(trip.starttime)

# check if a trip object starts before midday
def trip_is_before_midday(trip):
    return (trip_to_numseconds(trip) < midday_secs)

# the first 4 of these are basically just structs
class Stop:
    def __init__(self, stopid, stopcode, stopname, stoplat, stoplon):
        self.stopid = stopid
        self.stopcode = stopcode
        self.stopname = stopname
        self.stoplat = stoplat
        self.stoplon = stoplon
        self.entries = []  # list of (tripid, triptime) tuple

class StopTime:
    def __init__(self, tripid, stopid, stopname, departtime, stopseq):
        self.tripid = tripid
        self.stopid = stopid
        self.departtime = departtime
        self.stopseq = stopseq
        self.stopname = stopname

class StopEntry:
    def __init__(self, tripid, stoptime):
        self.stoptime = stoptime
        self.tripid = tripid
        self.trip = tripdict[tripid]

class Trip:
    def __init__(self, tripid, routeid, serviceid, routenum, blockid, headsign, starttime, startstopname, directionid, shape_id):
        self.tripid = tripid
        self.routeid = routeid
        self.serviceid = serviceid
        self.routenum = routenum
        self.blockid = blockid
        self.headsign = headsign
        self.starttime = starttime
        self.startstopname = startstopname
        self.directionid = directionid
        self.shape_id = shape_id
        # NOTE: Consolidation isn't used right now. It probably won't be with the new gtfs formats
        # True When identical weekday/weekend trip and blocks are consolidated
        self.use_alt_day_string = False
        # When identical weekday/weekend trip and blocks are consolidated, use this
        self.alt_day_string = ''
        self.stoplist = []  # list of stoptimetuple

class ShapePoint:
    def __init__(self, shape_id, lat, lon, sequence):
        self.shape_id = shape_id
        self.lat = lat
        self.lon = lon
        self.sequence = sequence

# Check if two trips are equivalent (ignoring day, id, blockid)
def compare_trips(trip1, trip2):
    if(trip1.routeid != trip2.routeid
       or trip1.headsign != trip2.headsign
       or trip1.routenum != trip2.routenum
       or trip1.starttime != trip2.starttime
       or trip1.directionid != trip2.directionid
       or trip1.startstopname != trip2.startstopname):
       return False
    else: return True

class Block:
    def __init__(self, blockid):
        self.blockid = blockid
        self.triplist = []
        self.serviceid = 0
        # When identical weekday/weekend trip and blocks are consolidated, use this
        self.use_alt_day_string = False
        # When identical weekday/weekend trip and blocks are consolidated, use this
        self.alt_day_string = ''

    # Returns the set of route number strings that are in this block (no duplicates)
    def get_block_routes(self):
        unique_routes = []
        for trip in self.triplist:
            if trip.routenum not in unique_routes:
                unique_routes.append(trip.routenum)
        return unique_routes

    # Returns the start time string of this block
    def get_block_start_time(self):
        if(len(self.triplist) == 0):
            return ''
        return self.triplist[0].starttime

    # Returns the length of this block in hours - this is stored in the bus history
    def get_block_length(self):
        if(len(self.triplist) == 0):
            return ''
        start_hour = int(self.get_block_start_time().split(':')[0])
        end_hour = int(self.triplist[-1].stoplist[-1].departtime
        .split(':')[0])
        return str(end_hour - start_hour)

    # Currently unused but nice for debug - prints out all the trips of the block
    def pretty_print(self):
        if(trip_is_before_midday(self.triplist[0])):
            print(days_of_week_dict[self.serviceid] +
                  ' AM Block (id: ' + self.blockid + ')')
        else:
            print(days_of_week_dict[self.serviceid] +
                  ' PM Block (id: ' + self.blockid + ')')
        print('Routes: ' + str(self.get_block_routes()))
        print('================================')
        for trip in self.triplist:
            print(trip.starttime + ' | ' + trip.headsign +
                  ' (Trip ID: ' + trip.tripid + ')')
        print('================================')


# global dicts of all the data, for exporting
blockdict = {}  # dict of block id-> block obj
tripdict = {}  # dict of trip id -> trip info object
route_triplistdict = {}  # dict of route id -> list of trips for that route
routedict = {}  # dict of routeid -> route info tuple
stopcode2stopnum = {}  # dict of stop code -> stopnum
stopdict = {}  # dict of stopid -> stop obj

all_points = [] # All points used for plotting routes on maps

# small dicts just to deal with date shenanigans
# the days of week stuff can handle more weird date cases than it needs, but is still missing some support
days_of_week_dict = {}  # service_id -> string for day of week
days_of_week_dict_longname = {}  # service_id -> long string for day of week
service_order_dict = {} # service_id -> display order (monday first, sunday last, etc) for sorting later
dow_number_dict = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}

# ------------------------------------------ #
#  Some setup code that gets run on import   #
# ------------------------------------------ #
def get_today_str():
    return str(date.today()).replace('-', '')

today = get_today_str()

this_sheet_enddate = ''

# all of these loading functions try to follow the GTFS spec
# this function is actually the worst - its AWFUL.
# I could try to clean it up, but this is a messy task no matter how I can think to do it
def populate_calendar():
    global days_of_week_dict
    global this_sheet_enddate
    global days_of_week_dict_longname
    global service_order_dict

    days_of_week_dict = {}
    service_order_dict = {}
    days_of_week_dict_longname = {}

    special_serviceid_dict = {}
    special_serviceid_dict_short = {}
    with open(calendar_dates_path, 'r') as caldate_f:
        colnames = caldate_f.readline().rstrip().split(',')
        for line in caldate_f:
            items = line.rstrip().split(',')
            date = items[colnames.index('date')]
            date = date[0:4] + '-' + date[4:6] + '-' + date[6:]
            exception_type = items[colnames.index('exception_type')]
            service_id = items[colnames.index('service_id')]
            if(exception_type == '1'):
                special_serviceid_dict[service_id] = 'Special: ' + date + ' only'
                special_serviceid_dict_short[service_id] = date

    with open(calendarpath, 'r') as cal_f:
        colnames = cal_f.readline().rstrip().split(',')
        for line in cal_f:
            items = line.rstrip().split(',')
            start_date = items[colnames.index('start_date')]
            end_date = items[colnames.index('end_date')]
            service_id = items[colnames.index('service_id')]
            if int(start_date) > int(today) or int(end_date) < int(today):
                # This serviceid is NOT for this SHEET... oh boy
                days_of_week_dict[service_id] = 'INVALID'
                days_of_week_dict_longname[service_id] = 'INVALID'
                continue
            this_sheet_enddate = end_date
            # so gross
            ismonday = items[colnames.index('monday')]
            istuesday = items[colnames.index('tuesday')]
            iswednesday = items[colnames.index('wednesday')]
            isthursday = items[colnames.index('thursday')]
            isfriday = items[colnames.index('friday')]
            issaturday = items[colnames.index('saturday')]
            issunday = items[colnames.index('sunday')]
            # oh my god why
            if(issunday == '1' and issaturday == '1'):
                days_of_week_dict[service_id] = 'Weekends'
                days_of_week_dict_longname[service_id] = 'Weekends'
                service_order_dict[service_id] = CONST_WEEKEND
                continue
            if(ismonday == '1' and istuesday == '1' and iswednesday == '1' and isthursday == '1' and isfriday == '1'):
                days_of_week_dict[service_id] = 'Weekdays'
                days_of_week_dict_longname[service_id] = 'Weekdays'
                service_order_dict[service_id] = CONST_WEEKDAY
                continue
            if(ismonday == '1' and istuesday == '1' and iswednesday == '1' and isthursday == '1' and isfriday == '0'):
                days_of_week_dict[service_id] = 'Mon-Thu'
                days_of_week_dict_longname[service_id] = 'Weekdays except Friday'
                service_order_dict[service_id] = CONST_WEEKDAY_EXCEPT_FRI
                continue
            if(ismonday == '1'):
                days_of_week_dict[service_id] = 'Mon'
                days_of_week_dict_longname[service_id] = 'Mondays'
                service_order_dict[service_id] = CONST_MON
                continue
            if(istuesday == '1'):
                days_of_week_dict[service_id] = 'Tue'
                days_of_week_dict_longname[service_id] = 'Tuesdays'
                service_order_dict[service_id] = CONST_TUES
                continue
            # don't do this to me... so much repetition
            if(iswednesday == '1'):
                days_of_week_dict[service_id] = 'Wed'
                days_of_week_dict_longname[service_id] = 'Wednesdays'
                service_order_dict[service_id] = CONST_WED
                continue
            if(isthursday == '1'):
                days_of_week_dict[service_id] = 'Thu'
                days_of_week_dict_longname[service_id] = 'Thursdays'
                service_order_dict[service_id] = CONST_THURS
                continue
            if(isfriday == '1'):
                days_of_week_dict[service_id] = 'Fri'
                days_of_week_dict_longname[service_id] = 'Fridays'
                service_order_dict[service_id] = CONST_FRI
                continue
            if(issaturday == '1'):
                days_of_week_dict[service_id] = 'Sat'
                days_of_week_dict_longname[service_id] = 'Saturdays'
                service_order_dict[service_id] = CONST_SAT
                continue
            # please stop
            if(issunday == '1'):
                days_of_week_dict[service_id] = 'Sun'
                days_of_week_dict_longname[service_id] = 'Sundays'
                service_order_dict[service_id] = CONST_SUN
                continue
            try:
                days_of_week_dict[service_id] = special_serviceid_dict_short[service_id]
                days_of_week_dict_longname[service_id] = special_serviceid_dict[service_id]
            except KeyError:
               days_of_week_dict[service_id] = 'Special (id: ' + service_id + ')'
               days_of_week_dict_longname[service_id] = 'Special (id: ' + \
                  service_id + ')'
            try:
               # service order dict is to sort the different service_ids when rendering
               # so for any serviceid that didn't match the above, ensure they all go at the end
               service_order_dict[service_id] = 9001 + int(service_id)
            except ValueError:
               # just in case
               service_order_dict[service_id] = CONST_SPECIAL

# this loads in all the data and sets up the global dicts
def start():
    load_stop_times()

    # these are just used internally to this function
    blocklistdict = {}  # dict of block id->list of trips in the block
    firststoptimes_dict = {}  # dict of trip id -> StopTime object
    # list of stop times just used internally
    stoptime_list = []

    # deal with our nasty globals - its nice if they're global, but we want to clear them every time we restart
    global blockdict
    blockdict = {}  # clear it

    # before we start, deal with the days of the week nonsense
    # NOTE: This function is AWFUL
    populate_calendar()

    # first, make a dict of stops with stops.txt
    with open(stoppath, 'r') as stops_f:
        # in the GTFS standard, the column order can CHANGE!!!!
        # list of the column names, column order is in the first line
        colnames = stops_f.readline().split(',')
        for line in stops_f:
            items = line.rstrip().split(',')
            stopid = items[colnames.index('stop_id')]
            stopcode = items[colnames.index('stop_code')]
            stopname = items[colnames.index('stop_name')]
            stoplat = items[colnames.index('stop_lat')]
            stoplon = items[colnames.index('stop_lon')]
            stopdict[stopid] = Stop(stopid, stopcode, stopname, stoplat, stoplon)

    # fill in the backwards dict here
    for stop in stopdict.values():
        stopcode2stopnum[stop.stopcode] = stop.stopid

    # next, make a dict of routes
    with open(routespath, 'r') as routes_f:
        # in the GTFS standard, the column order can CHANGE!!!!
        # list of the column names, column order is in the first line
        colnames = routes_f.readline().split(',')

        for line in routes_f:  # reads only the other lines
            items = line.rstrip().split(',')
            routeid = items[colnames.index('route_id')]
            routenum = items[colnames.index('route_short_name')]
            routename = items[colnames.index('route_long_name')]
            route_tuple = (routenum, routename, routeid)
            routedict[routeid] = route_tuple

    # now, make a dict of tripids -> start of that trip using the stop times
    # also, make a list of stoptime objects that will get used to fill out each trip
    with open(stoptimespath, 'r') as stoptimes:
        colnames = stoptimes.readline().split(',')  # column order is in the first line

        timesdict = {}  # clear it
        for line in stoptimes:
            items = line.rstrip().split(',')
            tripid = items[colnames.index('trip_id')]
            depart_time = items[colnames.index('departure_time')]
            stopid = items[colnames.index('stop_id')]
            stopseq = items[colnames.index('stop_sequence')]
            stopname = stopdict[stopid].stopname

            st = StopTime(tripid=tripid, stopid=stopid, stopname=stopname,
                          departtime=depart_time, stopseq=stopseq)
            # set the trip's depart time as the depart time from the first stop
            if(stopseq == '1'):
                firststoptimes_dict[tripid] = st
            # add this as a stop time object to the stop time list
            stoptime_list.append(st)
    
    with open(shapespath, 'r') as points:
        colnames = points.readline().rstrip().split(',')
        for line in points:
            items = line.rstrip().split(',')
            shape_id = items[colnames.index('shape_id')]
            lat = items[colnames.index('shape_pt_lat')]
            lon = items[colnames.index('shape_pt_lon')]
            sequence = items[colnames.index('shape_pt_sequence')]
            point = ShapePoint(shape_id, lat, lon, sequence)
            all_points.append(point)

    # make a dict of trips, and then a dict of blocks
    with open(tripspath, 'r') as trips:
        colnames = trips.readline().split(',')
        trip_pop_count = 0
        total_trip_count = 0
        for line in trips:
            total_trip_count += 1
            items = line.rstrip().split(',')
            routeid = items[colnames.index('route_id')]
            serviceid = items[colnames.index('service_id')]
            if days_of_week_dict[serviceid] == 'INVALID':
                continue  # skip trips not from this sheet
            trip_pop_count += 1
            tripid = items[colnames.index('trip_id')]
            headsign = items[colnames.index('trip_headsign')]
            directionid = items[colnames.index('direction_id')]
            blockid = items[colnames.index('block_id')]
            routenum = routedict[routeid][0]  # find route number this way
            depart_time = 'N/A'
            first_stop_name = 'N/A'
            try:
                depart_time = firststoptimes_dict[tripid].departtime
                first_stop_name = firststoptimes_dict[tripid].stopname
            except KeyError:
                print('Stop times key error for tripid {0}!'.format(tripid))
            shape_id = items[colnames.index('shape_id')]
            trip_obj = Trip(routeid=routeid, tripid=tripid, blockid=blockid, routenum=routenum, headsign=headsign,
                            starttime=depart_time, startstopname=first_stop_name, serviceid=serviceid, directionid=directionid, shape_id=shape_id)
            tripdict[tripid] = trip_obj

            # add this to a block dict to form the block structure
            if blockid in blocklistdict.keys():
                blocklistdict[blockid].append(tripid)
            else:
                blocklistdict[blockid] = [tripid]
    print('Number of trips read: {0} number of valid trips: {1}'.format(
        total_trip_count, trip_pop_count))
    print('Number of blocks read: ' + str(len(blocklistdict.keys())))

    # prune the trip and block dicts - consolidate identical weekday blocks
    # this pruning loop does actually detect the identical trips but is not enabled:
    # victoria decided to combine mon - thurs schedules anyway so this is less of a need.
    # Besides, the logic for actually consolidating the blocks is probably very gross
    if(start_mod.COMBINE_WEEKDAYS):
        for tripid in tripdict:
            trip = tripdict[tripid]
            for other_tripid in tripdict:
                other_trip = tripdict[other_tripid]
                if(compare_trips(trip, other_trip)):
                    print('Found equivalent trips! Tripids: {0} {1}'.format(tripid, other_tripid))

    # now, make a block object for each block
    blocklist = []
    for key in blocklistdict:
        new_block = Block(key)
        for tripid in blocklistdict[key]:  # for each trip in this block
            # add that trip tuple to the block object
            new_block.triplist.append(tripdict[tripid])
            # now, sort that trip list
            new_block.triplist.sort(key=trip_to_numseconds)
        # take serviceid of first trip
        new_block.serviceid = new_block.triplist[0].serviceid
        if(len(new_block.triplist) == 0):
            print('Error! this block is empty... (has no trips??)')
            continue
        # update the block list and dict
        blocklist.append(new_block)
        blockdict[key] = new_block

    # fill in the trip objects for the route_triplistdict
    # maintain a list of trips for each routeid
    for trip in tripdict.values():
        if trip.routeid in route_triplistdict:
            route_triplistdict[trip.routeid].append(trip)
        else:
            route_triplistdict[trip.routeid] = [trip]

    print('Beginning trip->stop list population...')
    for st in stoptime_list: # this is a big list
        try:
            tripdict[st.tripid].stoplist.append(st)
        except KeyError:  # for handling those stoptimes for trips not in this sheet
            pass          # (double sheet gtfs files will have trips from two sheets)
    for trip in tripdict.values():
        # sort the stoplist by stopseq didnt work so use departtime?
        trip.stoplist.sort(key=lambda x: hms_to_sec(x.departtime))

    print('Beginning stop->trip list population...')
    for st in stoptime_list:
        # maintain these two lists in parallel (I know, I know...)
        stop = stopdict[st.stopid]
        # check for trips that arent from this sheet - dont want to put those in
        if(st.tripid not in tripdict):
            continue
        stop.entries.append((st.tripid, st.departtime))
    for stop in stopdict.values():
        # sort trip tuple list by time
        stop.entries.sort(key=lambda x: hms_to_sec(x[1]))

    print('Beginning trip list, block list day-consolidation...')

    # done with setup
    print('Backend setup done!')
