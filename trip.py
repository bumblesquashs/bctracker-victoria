import csv
from block import is_block, get_block, add_block
from route import is_route, get_route, load_routes
from service import is_service, get_service, load_services
from enum import Enum

all_trips = {}

class Direction(Enum):
    OUTBOUND = 'Outbound'
    INBOUND = 'Inbound'
    UNKNOWN = 'Unknown'

class Trip:
    def __init__(self, trip_id, route_id, service_id, block_id, direction_id, shape_id, headsign):
        self.trip_id = trip_id
        self.route_id = route_id
        self.block_id = block_id
        self.service_id = service_id
        self.headsign = headsign

        self.stop_times = []

        if direction_id == 0:
            self.direction = Direction.OUTBOUND
        elif direction_id == 1:
            self.direction = Direction.INBOUND
        else:
            self.direction = Direction.UNKNOWN
    
    def __str__(self):
        return self.headsign
    
    def __eq__(self, other):
        return self.trip_id == other.trip_id
    
    def __lt__(self, other):
        return self.stop_times[0] < other.stop_times[0]
    
    @property
    def route(self):
        return get_route(self.route_id)
    
    @property
    def block(self):
        return get_block(self.block_id)
    
    @property
    def service(self):
        return get_service(self.service_id)
    
    @property
    def start_time(self):
        return self.stop_times[0].time

def is_trip(trip_id):
    return trip_id in all_trips

def get_trip(trip_id):
    return all_trips[trip_id]

def load_trips():
    load_routes()
    load_services()

    global all_trips
    all_trips = {}

    csv.read('trips.txt', add_trip)

def add_trip(values):
    trip_id = int(values['trip_id'])
    route_id = int(values['route_id'])
    if not is_route(route_id):
        print(f'Invalid route id: {route_id}')
        return
    service_id = int(values['service_id'])
    if not is_service(service_id):
        print(f'Invalid service id: {service_id}')
        return
    block_id = int(values['block_id'])
    if not is_block(block_id):
        add_block(block_id, service_id)
    direction_id = int(values['direction_id'])
    shape_id = int(values['shape_id'])
    headsign = values['trip_headsign']

    trip = Trip(trip_id, route_id, service_id, block_id, direction_id, shape_id, headsign)

    all_trips[trip_id] = trip

    trip.block.trips.append(trip)
    trip.route.trips.append(trip)
