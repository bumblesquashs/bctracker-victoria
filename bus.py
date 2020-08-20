from bus_range import get_bus_range
from enum import Enum
import json
import urllib.request

all_buses = {}
bus_number_id = {}

class BusStatus(Enum):
    NOT_TRACKING = "Not tracking"
    NOT_IN_SERVICE = "Not in service"
    IN_SERVICE = "In service"

class Bus:
    def __init__(self, bus_id, number):
        self.bus_id = bus_id
        self.number = number

        self.range = get_bus_range(number)
        self.status = BusStatus.NOT_TRACKING
    
    def __str__(self):
        if self.number == -1:
            return 'Unknown'
        return str(self.number)

    def __hash__(self):
        return hash(self.bus_id)

    def __eq__(self, other):
        return self.bus_id == other.bus_id
    
    def __lt__(self, other):
        return self.number < other.number

def is_bus(bus_id):
    return bus_id in all_buses

def is_bus_number(number):
    return number in bus_number_id and bus_number_id[number] in all_buses

def get_bus(bus_id):
    return all_buses[bus_id]

def get_bus_by_number(number):
    return all_buses[bus_number_id[number]]

def get_all_buses():
    return all_buses.values()

def load_buses(bus_data = None):
    global all_buses
    global bus_number_id

    all_buses = {}
    bus_number_id = {}

    if bus_data is None:
        with open('data/nextride/id2fleetnum.json', 'r') as file:
            bus_data = json.load(file)
    
    for data in bus_data.items():
        bus_id = int(data[0])
        number = int(data[1])

        bus = Bus(bus_id, number)

        all_buses[bus_id] = bus
        bus_number_id[number] = bus_id

def update_buses():
    with open('data/nextride/Route.json', 'r') as file:
        routes_data = json.load(file)
    query = ','.join(map(lambda d: str(d['patternID']), routes_data))

    with urllib.request.urlopen('https://nextride.victoria.bctransit.com/api/VehicleStatuses?patternIds=' + query) as response:
        result = response.read()
        json_data = json.loads(result)
    
    try:
        file = open('data/nextride/id2fleetnum.json', 'r')
        bus_data = json.load(file)
        file.close()
    except:
        bus_data = {}
        file.close()
    
    for data in json_data:
        bus_id = str(data['vehicleId'])
        number = str(data['name'])

        bus_data[bus_id] = number
    
    with open('data/nextride/id2fleetnum.json', 'w') as file:
        json.dump(bus_data, file)
    
    load_buses(bus_data)
