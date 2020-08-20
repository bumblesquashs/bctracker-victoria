import csv

all_routes = {}
route_number_id = {}

class Route:
    def __init__(self, route_id, number, name):
        self.route_id = route_id
        self.number = number
        self.name = name

        self.trips = []
    
    def __str__(self):
        return f'{self.number} {self.name}'
    
    def __hash__(self):
        return hash(self.route_id)
    
    def __eq__(self, other):
        return self.route_id == other.route_id
    
    def __lt__(self, other):
        return self.number < other.number
    
    def __gt__(self, other):
        return self.number > other.number
    
    @property
    def services(self):
        return set(map(lambda t: t.service, self.trips))

def is_route(route_id):
    return route_id in all_routes

def is_route_number(number):
    return number in route_number_id and route_number_id[number] in all_routes

def get_route(route_id):
    return all_routes[route_id]

def get_route_by_number(number):
    return all_routes[route_number_id[number]]

def get_all_routes():
    return all_routes.values()

def load_routes():
    global all_routes
    all_routes = {}

    global route_number_id
    route_number_id = {}

    csv.read('routes.txt', add_route)

def add_route(values):
    route_id = int(values['route_id'])
    number = int(values['route_short_name'])
    name = values['route_long_name']

    route = Route(route_id, number, name)

    all_routes[route_id] = route
    route_number_id[number] = route_id
