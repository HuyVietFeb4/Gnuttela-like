import leaf_peer

class UltraPeer(leaf_peer.Peer):
    def __init__(self, bloom_filter, ip, port, multicast_ip, multicast_port, external_multicast_ip, external_multicast_port):
        super().__init__(bloom_filter, ip, port, multicast_ip, multicast_port)
        self.external_multicast_ip = external_multicast_ip
        self.external_multicast_port = external_multicast_port