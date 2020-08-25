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

from block import is_block, get_block, get_all_blocks
from bus import BusStatus, is_bus_number, get_bus_by_number, get_all_buses
from bus_history import update_history
from bus_realtime import update_bus_realtime
from route import is_route_number, get_route_by_number, get_all_routes
from stop import is_stop_number, get_stop_by_number
from trip import is_trip, get_trip

PLACEHOLDER = '100000'
rdict = {}     # rdict is routeid -> (routenum, routename, routeid)
reverse_rdict = {} # route num -> routeid
mapbox_api_key = ''

# Web framework code to start the server
def startup():
    global rdict
    global reverse_rdict
    global mapbox_api_key
    print('WEB: initializing the web server!')
    rdict = ds.routedict
    # build a reverse route table for handling web requests (routenum->routeid)
    for route_tuple in rdict.values():
        reverse_rdict[route_tuple[0]] = route_tuple[2]
    # Calls to run the bottle code on the cherrypy server
    cp.config.update('server.conf')
    cp.tree.graft(make_access_log(app, 'logs/access_log.log'), '/')
    mapbox_api_key = cp.config['mapbox_api_key']
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
    return template('home')

@app.route('/routes')
@app.route('/routes/')
def routes():
    return template('routes', routes=get_all_routes())

@app.route('/routes/<number:int>')
def route_number(number):
    if is_route_number(number):
        return template('route', route=get_route_by_number(number))
    return template('error', error=f'Route {number} Not Found')

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

        update_bus_realtime()

        hist.update_last_seen()
        update_history()
    group = request.query.get('group', 'all')

    buses = [bus for bus in get_all_buses() if bus.status != BusStatus.NOT_TRACKING]
    return template('realtime', buses=buses, group=group)

@app.route('/bus')
@app.route('/bus/')
def bus():
    return template('error', error='No Bus Specified')

@app.route('/bus/<number:int>')
def bus(number):
    if is_bus_number(number):
        return template('bus', bus=get_bus_by_number(number))
    return template('error', error=f'Bus {number} Not Found', message='Is this a new bus?')

@app.route('/blocks')
@app.route('/blocks/')
def blocks():
    return template('blocks', blocks=get_all_blocks())

@app.route('/blocks/<block_id:int>')
def blocks(block_id):
    if is_block(block_id):
        return template('block', block=get_block(block_id))
    return template('error', error=f'Block {block_id} Not Found', message='This block may be from an older version of GTFS which is no longer valid')
    
@app.route('/trips/<trip_id:int>')
def trips(trip_id):
    if is_trip(trip_id):
        return template('trip', trip=get_trip(trip_id))
    return template('error', error=f'Trip {trip_id} Not Found', message='This trip may be from an older version of GTFS which is no longer valid')
    
@app.route('/stops/<number:int>')
def stops(number):
    if is_stop_number(number):
        return template('stop', stop=get_stop_by_number(number))
    return template('error', error=f'Stop {number} Not Found')

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
