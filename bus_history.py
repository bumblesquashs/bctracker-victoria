from bus import BusStatus, is_bus, get_bus, get_all_buses
from bus_realtime import get_is_valid
import os
import json
from datetime import date, datetime, timedelta

class History:
    def __init__(self, bus_id, block_id, date, routes_string):
        self.bus_id = bus_id
        self.block_id = block_id
        self.date = date
        self.routes_string = routes_string
    
    def __eq__(self, other):
        return self.bus_id == other.bus_id and self.block_id == other.block_id and self.date == other.date
    
    def __lt__(self, other):
        if self.bus_id == other.bus_id:
            return self.date < other.date
        return self.bus < other.bus
    
    @property
    def bus(self):
        return get_bus(self.bus_id)

def update_history():
    if get_is_valid():
        buses = filter(lambda b: b.status != BusStatus.NOT_TRACKING, get_all_buses())
        for bus in buses:
            path = f'data/history/{bus.bus_id}.json'
            if os.path.isfile(path):
                with open(path, 'r') as file:
                    json_data = json.load(file)
                save_required = False
            else:
                json_data = {
                    'bus_id': bus.bus_id,
                    'last_seen': '',
                    'block_history': []
                }
                save_required = True
            
            service_day = str(get_service_day())
            if json_data['last_seen'] != service_day:
                json_data['last_seen'] = service_day
                save_required = True

            if bus.status == BusStatus.IN_SERVICE:
                block_history = json_data['block_history']
                block = bus.realtime.trip.block
                new_data = True
                for block_data in block_history:
                    if block_data['block_id'] == block.block_id or block_data['date'] == service_day:
                        new_data = False
                        break
                
                if new_data:
                    block_history.append({
                        'block_id': block.block_id,
                        'date': service_day,
                        'routes': block.routes_string
                    })
                    json_data['block_history'] = block_history
                    save_required = True
            
            if save_required:
                with open(path, 'w') as file:
                    json.dump(json_data, file)

def get_history(bus_id):
    path = f'data/history/{bus_id}.json'
    if is_bus(bus_id) and os.path.isfile(path):
        with open(path, 'r') as file:
            json_data = json.load(file)
        last_seen = json_data['last_seen']
        block_history = []
        block_history_data = json_data['block_history']
        count = 0
        for block_data in block_history_data:
            block_id = block_data['block_id']
            date = block_data['date']
            routes_string = block_data['routes']

            block_history.append(History(bus_id, block_id, date, routes_string))
            count += 1
            if count == 20:
                break
        block_history.reverse()
        return (last_seen, block_history)
    return ('', [])
                
def get_service_day():
    hour = datetime.now().hour
    today = date.today()
    if hour < 5:
        return today - timedelta(days = 1)
    else:
        return today