class Peer:
    def __init__(self, bloom_filter, ip, port, multicast_ip, multicast_port):
        self.bloom_filter = bloom_filter
        self.ip = ip
        self.port = port
        self.multicast_ip = multicast_ip
        self.multicast_port = multicast_port

    def ping(self):
        pass
    def pong():
        pass
    def download_file():
        pass
    def upload_file():
        pass