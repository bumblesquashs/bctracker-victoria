from stop import is_stop, get_stop
from trip import is_trip, get_trip
from bus import Bus, BusStatus, update_buses, load_buses, is_bus, get_bus

import wget
import time
import protobuf.data.gtfs_realtime_pb2 as rt

update_time = time.time()
is_valid = True

class BusRealtime:
    def __init__(self, trip_id, stop_id):
        self.trip_id = trip_id
        self.stop_id = stop_id
    
    @property
    def trip(self):
        return get_trip(self.trip_id)
    
    @property
    def at_stop(self):
        return self.stop_id is not None
    
    @property
    def stop(self):
        return get_stop(self.stop_id)

def get_update_time():
    return time.strftime("%B %-d, %Y at %H:%M", time.localtime(update_time))

def get_is_valid():
    return is_valid

def update_bus_realtime(should_update_buses=True):
    if should_update_buses:
        update_buses()
    else:
        load_buses()
    
    global update_time
    update_time = time.time()

    path = f'data/realtime_downloads/gtfsrt_vehiclepos{str(int(update_time))}_test.bin'
    
    wget.download('http://victoria.mapstrat.com/current/gtfrealtime_VehiclePositions.bin', path)

    with open(path, 'rb') as file:
        feed_message = rt.FeedMessage()
        feed_message.ParseFromString(file.read())

    for data in feed_message.entity:
        bus_data = data.vehicle
        bus_id = int(bus_data.vehicle.id)

        if is_bus(bus_id):
            bus = get_bus(bus_id)
        else:
            bus = Bus(bus_id, -1)
        
        try:
            trip_data = bus_data.trip
            trip_id = trip_data.trip_id

            if trip_data.schedule_relationship == 0 and trip_id != '' and is_trip(int(trip_id)):
                bus.status = BusStatus.IN_SERVICE
                if bus_data.stop_id == '' or not is_stop(int(bus_data.stop_id)):
                    bus.realtime = BusRealtime(int(trip_id), None)
                else:
                    bus.realtime = BusRealtime(int(trip_id), int(bus_data.stop_id))
            else:
                bus.status = BusStatus.NOT_IN_SERVICE
        except AttributeError:
            bus.status = BusStatus.NOT_IN_SERVICE
        
        try:
            bus.lat = bus_data.position.latitude
            bus.lon = bus_data.position.longitude
        except AttributeError:
            bus.lat = 0
            bus.lon = 0
