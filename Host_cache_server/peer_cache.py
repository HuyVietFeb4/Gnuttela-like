import math
from Host_cache_server import config

# {subnet_id: [(ip, port)]}
subnetworks = {}

# store all nodes
# {id: {ip, port, location, ultra}}
peers = {}

# node id
peer_id = 0

# subnetwork id
subnet_id = 0

# multicast groups
# [([ultra_node ids], [ip_octet1, ip_octet2, ip_octet3, ip_octet4], port, in)]
# in=True if internal multicast group
# in=False if external multicast group
groups = []

def add_peer(ip, port):
    global subnet_id
    for _subnet_id, subnet in subnetworks.items():
        if len(subnet) < config.MAX_NODES:
            subnet.append((ip, port))
            return _subnet_id, subnet
    
    subnetworks[subnet_id] = [(ip, port)]
    subnet_id += 1
    return subnet_id - 1, subnetworks[subnet_id - 1]

# return ip, port of multicast group
def get_subnetwork(id):
    if id in subnetworks:
        for ids, ip, port in groups:
            if id in ids:
                return ip, port
    else:
        for ultra_node, children in subnetworks.items():
            if id in children:
                for group in groups:
                    if group[3] is True and ultra_node in group[0]:
                        # multicast ip, multicast port, ultra node ip, ultra node port
                        return group[1], group[2], peers[ultra_node]['ip'], peers[ultra_node]['port']
    return None, None

def generate_multicast_group(id):
    group = None
    if len(groups) < 1:
        group = (id, [224, 1, 1, 1], 50000)
    else:
        ip, port = groups[-1]
        for i in range(-1, -4, -1):
            if i == -4:
                ip[i] = 224 if ip[i] == 239 else ip[i] + 1
                break
            if ip[i] < 255:
                ip[i] += 1
                break
            else:
                ip[i] = 1

        group = ([id], ip, port + 1)

    groups.append(group)
    return group

# Add new subnetwork to multicast group
def add_to_multicast_group(id, location, typ):
    if typ:
        generate_multicast_group(id, True)
    min_dist = 0
    final_group = None
    for group in groups:
        if group[3] is False and len(group[0]) > config.MULTICAST_SIZE:
            dists = [math.dist(location, _location) for _location in [peers[_id]['location'] for _id in group[0]]]
            avg_dist = sum(dists) / len(dists)
            if min_dist < avg_dist:
                final_group = group
                min_dist = avg_dist

    if final_group is None:
        generate_multicast_group(id, False)
    else:
        final_group[0].append(id)

# (function not done)
def remove_ultra_peer(ip, port):
    peer = {"ip": ip, "port": port}
    if peer in peers:
        peers[peer] = None
