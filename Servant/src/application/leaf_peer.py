class Peer:
    def __init__(self, bloom_filter, list_port, network_table):
        self.bloom_filter = bloom_filter
        self.listening_port = list_port
        self.network_table = network_table

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