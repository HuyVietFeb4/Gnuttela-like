import os
import hashlib

class Peer:
    def __init__(self, bloom_filter=None, network_table=None, subnet_id=None):
        self.bloom_filter = bloom_filter
        self.network_table = network_table
        self.subnet_id = subnet_id
        self.id = hashlib.sha1(os.urandom(32)).digest()

    def ping(self):
        pass
    def pong(self):
        pass
    def query(self):
        pass
    def query_hit(self):
        pass
    def push(self):
        pass