from service import get_service

all_blocks = {}

class Block:
    def __init__(self, block_id, service_id):
        self.block_id = block_id
        self.service_id = service_id

        self.trips = []
    
    def __eq__(self, other):
        return self.block_id == other.block_id
    
    def __lt__(self, other):
        if self.service == other.service:
            return self.block_id < other.block_id
        else:
            return self.service < other.service

    @property
    def service(self):
        return get_service(self.service_id)

    @property
    def routes(self):
        return set(map(lambda t: t.route, self.trips))

    @property
    def routes_string(self):
        return ', '.join(map(lambda r: str(r.number), sorted(self.routes)))
    
    @property
    def start_time(self):
        return sorted(self.trips)[0].start_time

def is_block(block_id):
    return block_id in all_blocks

def get_block(block_id):
    return all_blocks[block_id]

def get_all_blocks():
    return all_blocks.values()

def add_block(block_id, service_id):
    all_blocks[block_id] = Block(block_id, service_id)