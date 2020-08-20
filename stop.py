import csv

all_stops = {}
stop_number_id = {}

class Stop:
    def __init__(self, stop_id, number, name, lat, lon):
        self.stop_id = stop_id
        self.number = number
        self.name = name
        self.lat = lat
        self.lon = lon

        self.stop_times = []
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return self.stop_id == other.stop_id
    
    @property
    def services(self):
        return set(map(lambda s: s.trip.service, self.stop_times))

def is_stop(stop_id):
    return stop_id in all_stops

def is_stop_number(number):
    return number in stop_number_id and stop_number_id[number] in all_stops

def get_stop(stop_id):
    return all_stops[stop_id]

def get_stop_by_number(number):
    return all_stops[stop_number_id[number]]

def load_stops():
    global all_stops
    all_stops = {}

    global stop_number_id
    stop_number_id = {}

    csv.read('stops.txt', add_stop)

def add_stop(values):
    stop_id = int(values['stop_id'])
    number = int(values['stop_code'])
    name = values['stop_name']
    lat = values['stop_lat']
    lon = values['stop_lon']

    stop = Stop(stop_id, number, name, lat, lon)

    all_stops[stop_id] = stop
    stop_number_id[number] = stop_id