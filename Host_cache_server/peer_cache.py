ultra_peers = []

def add_ultra_peer(ip, port):
    ultra_peers.append({"ip": ip, "port": port})

def get_ultra_peers():
    return ultra_peers

def remove_ultra_peer(ip, port):
    peer = {"ip": ip, "port": port}
    if peer in ultra_peers:
        ultra_peers.remove(peer)
