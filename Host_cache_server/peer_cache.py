import math
from Host_cache_server import config

# {subnet_id: [(ip, port)]}
subnetworks = {}

# store all ultra nodes
# {subnet_id: (ip, port)}
ultra_peers = {}

# subnetwork id
subnet_id = 0

def add_peer(ip, port):
    global subnet_id
    for _subnet_id, subnet in subnetworks.items():
        if len(subnet) < config.MAX_NODES:
            subnet.append((ip, port))
            return _subnet_id, subnet
    
    subnetworks[subnet_id] = [(ip, port)]
    add_ultra_peer(ip, port, subnet_id)
    subnet_id += 1
    return subnet_id - 1, subnetworks[subnet_id - 1]

def remove_peer(ip, port, _subnet_id):
    subnetworks[_subnet_id].remove((ip, port))

def add_ultra_peer(ip, port, subnet_id):
    ultra_peers[subnet_id] = (ip, port)
