import munch
import start
import logging
import requestlogger
import realtime as rt
import cherrypy as cp
import history as hist
import logging.handlers
import datastructure as ds
import businfotable as businfo
import scrape_fleetnums as scrape
from bottle import route, run, request, template, Bottle, static_file

PLACEHOLDER = '100000'
rdict = {}     # rdict is routeid -> (routenum, routename, routeid)
reverse_rdict = {} # route num -> routeid

# Web framework code to start the server
def startup():
    global rdict
    global reverse_rdict
    print('WEB: initializing the web server!')
    rdict = ds.routedict
    # build a reverse route table for handling web requests (routenum->routeid)
    for route_tuple in rdict.values():
        reverse_rdict[route_tuple[0]] = route_tuple[2]
    # Calls to run the bottle code on the cherrypy server
    cp.config.update('server.conf')
    cp.tree.graft(make_access_log(app, 'logs/access_log.log'), '/')
    cp.log('Whaaat? here we go')
    cp.server.start() #That's it for our startup code

# =============================================================
# Web framework: assign routes - its all Server side rendering
# =============================================================
app = Bottle()

@app.route('/style/<filename:path>')
def style(filename):
    return static_file(filename, root='./style')

@app.route('/img/<filename:path>')
def style(filename):
    return static_file(filename, root='./img')

@app.route('/')
def index():
    if 'munch' in request.query:  # for the refresh data thing
        print('Oi! gotta munch')
        valid = munch.munch()
        if((not valid) and start.RELOAD_ENABLED):
            start.download_and_restart()
    return template('home')

@app.route('/routes')
@app.route('/routes/')
def routes():
    return template('routes', rdict=rdict)

@app.route('/routes/<routenum:int>')
def route_number(routenum):
    try:
        this_route = reverse_rdict[str(routenum)]
    except KeyError:
        return template('error', error='Route {0} Not Found'.format(routenum))
    try:
        trip_list = ds.route_triplistdict[this_route]
    except:
        return template('error', error='Route {0} Not Found'.format(routenum))
    day_triplistdict = {}
    day_order = []
    for trip in trip_list:
        if(ds.days_of_week_dict[trip.serviceid]) == 'INVALID':
            continue
        if(trip.use_alt_day_string):
            keystr = trip.alt_day_string
        else:
            keystr = ds.days_of_week_dict_longname[trip.serviceid]
        if(keystr in day_triplistdict.keys()):
            day_triplistdict[keystr].append(trip)
        else:
            day_triplistdict[keystr] = [trip]
    for key in day_triplistdict:
        day_order.append(key)
    day_order.sort(key = lambda x: ds.service_order_dict.setdefault(day_triplistdict[x][0].serviceid, 10000)) #sort by first trip's service id, any unfound keys last
    return template('route', day_triplistdict=day_triplistdict, day_order=day_order, routenum=routenum, routename=rdict[this_route][1])

@app.route('/history')
@app.route('/history/')
def history():
    return template('history')

@app.route('/realtime')
@app.route('/realtime/')
def realtime():
    if 'rt' in request.query:
        rt.download_lastest_files()
        valid = rt.load_realtime()
        if((not valid) and start.RELOAD_ENABLED):
            start.download_and_restart()
        hist.update_last_seen()
    group = request.query.get('group', 'all')

    rtbuslist = []
    for busid in rt.rtvehicle_dict:
        bus = rt.rtvehicle_dict[busid]
        try:
            # if we know the real time translation, add it here
            fleet_num = rt.id2fleetnum_dict[busid]
            bus.fleetnum = fleet_num
            bus.unknown_fleetnum_flag = False
        except KeyError:
            bus.fleetnum = PLACEHOLDER
        rtbuslist.append(bus)
        # now - sort that list however we please
    rtbuslist.sort(key=lambda x: int(x.fleetnum))
    return template('realtime', time_string=rt.get_data_refreshed_time_str(), rtbuslist=rtbuslist, tripdict=ds.tripdict, stopdict=ds.stopdict, group=group, rdict=rdict)

@app.route('/map')
@app.route('/map/')
def map():
    rtbuslist = []
    for busid in rt.rtvehicle_dict:
        bus = rt.rtvehicle_dict[busid]
        try:
            # if we know the real time translation, add it here
            fleet_num = rt.id2fleetnum_dict[busid]
            bus.fleetnum = fleet_num
            bus.unknown_fleetnum_flag = False
        except KeyError:
            bus.fleetnum = PLACEHOLDER
        rtbuslist.append(bus)
    rtbuslist.sort(key=lambda x: int(x.fleetnum))
    return template('map', rtbuslist=rtbuslist)

@app.route('/bus')
@app.route('/bus/')
def bus():
    return template('error', error='No Bus Specified')

@app.route('/bus/<fleetnum:int>')
def bus_number(fleetnum):
    if(not businfo.is_known_bus(str(fleetnum))):
        return template('error', error='Unknown Bus {0}'.format(fleetnum), message='Is this a new bus?')
    return template('bus', fleetnum=str(fleetnum))

@app.route('/blocks')
@app.route('/blocks/')
def blocks():
    return template('blocks')

@app.route('/blocks/<blockid:int>')
def block_id(blockid):
    try:
        triplist = ds.blockdict[str(blockid)].triplist
    except KeyError:
        return template('error', error='Block {0} Not Found'.format(blockid), message='This block may be from an older version of GTFS which is no longer valid')
    return template('block', blockid=blockid, triplist=triplist)

@app.route('/trips/<tripid:int>')
def trip_id(tripid):
    try:
        trip = ds.tripdict[str(tripid)]
    except KeyError:
        return template('error', error='Trip {0} Not Found'.format(tripid), message='This trip may be from an older version of GTFS which is no longer valid')
    return template('trip', tripid=tripid, trip=trip)

@app.route('/stops/<stopcode:int>')
def stop_number(stopcode):
    try:
        # grab the stop object from the stopcode
        stop = ds.stopdict[ds.stopcode2stopnum[str(stopcode)]]
    except KeyError:
        return template('error', error='Stop {0} Not Found'.format(stopcode))

    service_day = request.query.service

    entries = stop.entries
    day_entries = {}
    for entry_tuple in entries:
        entry = ds.StopEntry(entry_tuple[0], entry_tuple[1])
        trip = entry.trip
        if(ds.days_of_week_dict[trip.serviceid]) == 'INVALID':
            continue

        if(trip.use_alt_day_string):
            keystr = trip.alt_day_string
        else:
            keystr = ds.days_of_week_dict_longname[trip.serviceid]

        if(keystr in day_entries.keys()):
            day_entries[keystr].append(entry)
        else:
            day_entries[keystr] = [entry]
    day_order = []
    for day_str in day_entries:
        day_order.append(day_str)
    day_order.sort(key = lambda x: ds.service_order_dict.setdefault(day_entries[x][0].trip.serviceid, 10000))
    return template('stop', stop=stop, day_order=day_order, day_entries=day_entries)

@app.route('/about')
@app.route('/about/')
def about():
    return template('about')

@app.route('/admin/reload-server')
def restart():
    print('Attempting to reload the server')
    if(start.RELOAD_ENABLED):
        start.download_and_restart()
    return('Lol you should never see this')

#use cherrypy server - setup logging
def make_access_log(app, filepath, when='d', interval=7, **kwargs):
    if filepath is not None:
        handlers = [logging.handlers.TimedRotatingFileHandler(
        filepath, when, interval, **kwargs)]
    else:
        handlers = [logging.StreamHandler()]
    return requestlogger.WSGILogger(app, handlers, requestlogger.ApacheFormatter())
