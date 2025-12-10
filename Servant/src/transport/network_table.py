import time
import uuid
class network_table:
    '''
    This class is for ultra peer and leaf peer to keep track of peer socket address and types in the network. 
    For leaf peer: it will keep track of other leaf peer socket address in  the same subnetwork
    For ultra peer: it will keep track of other ultra peer and leaf peer in it's subnetwork
    Structure:
        network_table = {
            (ip, port): {
                "role": <role>, (True if leaf, False if ultra)
                // "peer_id": <uuid in the network> 
                "last_seen": <unix-time>
                // More meta data if needed
            }
        }
    '''
    def __init__(self):
        self.network_table = {}

    def add_peer(self, ip, port, role):
        self.network_table[(ip, port)] = {
            "role": role,
            "last_seen":  time.time(),
            #"peer_id": uuid.uuid4()
        }

    def remove_peer(self, ip, port):
        self.network_table.pop((ip, port), "Can't find peer")

    def update_peer_last_seen(self, ip, port):
        if (ip, port) in self.network_table:
            self.network_table[(ip, port)]['last_seen'] = time.time()

    def clear_table(self):
        self.network_table.clear()
    
    def update_peer_role(self, ip, port, role):
        if (ip, port) in self.network_table:
            self.network_table[(ip, port)]['role'] = role

    def get_peer_id(self, ip, port):
        return self.network_table[(ip, port)]['peer_id']
    
    def get_peers_addresses(self):
        return list(self.network_table.keys())[:-1]
    
    def get_ultra_peer(self):
        for key, value in self.network_table.items():
            if value['role'] is False:
                return key