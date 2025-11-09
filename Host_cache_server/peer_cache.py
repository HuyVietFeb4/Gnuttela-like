import math
import config

# {ultra_id: [id], id: []}
subnetworks = {}

# store all nodes
# {id: {ip, port, location, ultra}}
peers = {}

# node id
peer_id = 0

# multicast groups
# [([ultra_node ids], [ip_octet1, ip_octet2, ip_octet3, ip_octet4], port)]
groups = []

def add_peer(ip, request):
    global peer_id
    port = request.get("port")
    location = request.get("location")
    ultra = request.get('rating') > config.RATING_THRESHOLD
    if ultra:
        subnetworks[peer_id] = []
        add_to_multicast_group(peer_id, location)
    else:
        ultra_peer_found = False
        if len(subnetworks) > 0:
            min_dist = 0
            ultra_peer = None
            for key, value in peers.items():
                if value['ultra'] and len(subnetworks[key]) < config.MAX_CHILDREN:
                    dist = math.dist(location, value['location'])
                    if dist < min_dist:
                        min_dist = dist
                        ultra_peer = key

            if ultra_peer is not None:
                subnetworks[ultra_peer] = peer_id
                ultra_peer_found = True

        if not ultra_peer_found:
            subnetworks[peer_id] = []
            add_to_multicast_group(peer_id, location)

    peers[peer_id] = {"ip": ip, "port": port, "location": location, 'ultra': ultra}
    peer_id += 1
    return peer_id - 1

# return ip, port of multicast group
def get_subnetwork(id):
    if id in subnetworks:
        for ids, ip, port in groups:
            if id in ids:
                return ip, port
    else:
        for ultra_node, children in subnetworks.items():
            if id in children:
                return peers[ultra_node]['ip'], peers[ultra_node]['port']
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
def add_to_multicast_group(id, location):
    min_dist = 0
    final_group = None
    for group in groups:
        if len(group[0]) > config.MULTICAST_SIZE:
            dists = [math.dist(location, _location) for _location in [peers[_id]['location'] for _id in group[0]]]
            avg_dist = sum(dists) / len(dists)
            if min_dist < avg_dist:
                final_group = group
                min_dist = avg_dist

    if final_group is None:
        generate_multicast_group(id)
    else:
        final_group[0].append(id)

# (function not done)
def remove_ultra_peer(ip, port):
    peer = {"ip": ip, "port": port}
    if peer in peers:
        peers[peer] = None
