import os
import hashlib

class Peer:
    def __init__(self, bloom_filter=None, network_table=None, subnet_id=None, directory=None):
        self.bloom_filter = bloom_filter
        self.network_table = network_table
        self.subnet_id = subnet_id
        self.id = hashlib.sha1(os.urandom(32)).digest()
        self.directory = directory

    def all_files(self):
        return [entry for entry in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, entry))]

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