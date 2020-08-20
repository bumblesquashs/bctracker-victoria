import csv
from stop import is_stop, get_stop, load_stops
from trip import is_trip, get_trip, load_trips

import formatting

class StopTime:
    def __init__(self, stop_id, trip_id, time, sequence):
        self.stop_id = stop_id
        self.trip_id = trip_id
        self.time = formatting.format_time(time)
        self.seqence = sequence
    
    def __eq__(self, other):
        if self.stop_id == other.stop_id and self.trip_id == other.trip_id:
            return self.seqence == other.sequence
        else:
            return self.time == other.time

    def __lt__(self, other):
        if self.stop_id == other.stop_id and self.trip_id == other.trip_id:
            return self.seqence < other.sequence
        else:
            (sh, sm) = self.time.split(':')
            (oh, om) = other.time.split(':')
            if sh == oh:
                return int(sm) < int(om)
            else:
                return int(sh) < int(oh)
    
    @property
    def stop(self):
        return get_stop(self.stop_id)
    
    @property
    def trip(self):
        return get_trip(self.trip_id)

def load_stop_times():
    load_stops()
    load_trips()
    
    csv.read('stop_times.txt', add_stop_time)

def add_stop_time(values):
    stop_id = int(values['stop_id'])
    if not is_stop(stop_id):
        print(f'Invalid stop id: {stop_id}')
        return
    trip_id = int(values['trip_id'])
    if not is_trip(trip_id):
        print(f'Invalid trip id: {trip_id}')
        return
    time = values['departure_time']
    sequence = int(values['stop_sequence'])

    stop_time = StopTime(stop_id, trip_id, time, sequence)

    stop_time.stop.stop_times.append(stop_time)
    stop_time.trip.stop_times.append(stop_time)