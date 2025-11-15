import socket
from config import bootstrap_config as bootstrap_config
import random
import json

def request_bootstrap(rating):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(bootstrap_config.SERVER_ADDR)

        request = {
            "type": "bootstrap",
            "port": bootstrap_config.LISTENING_PORT,
            "rating": rating,
            "location": (random.randint(-180, 180), random.randint(-180, 180))
        }

        sock.sendall(json.dumps(request).encode())

        response = sock.recv(4096)
        response = json.loads(response.decode())

        print("Bootstrap response:")
        print(json.dumps(response, indent=2))

        if rating > config.RATING_THRESHOLD:
            global multicast_ip, multicast_port
            multicast_ip = response.get['subnetwork'][0]
            multicast_port = response.get['subnetwork'][1]
        else:
            global ultra_ip, ultra_port
            ultra_ip = response.get['subnetwork'][0]
            ultra_port = response.get['subnetwork'][1]