import socket
import struct
import json
import os
import subprocess
import config.settings as settings
import random
import Host_cache_server.config as config
import protocol.message as message
# Identify bandwidth and assign role
# Just use speedtest library lmao

multicast_ip = ''
multicast_port = None

ultra_ip = ''
ultra_port = None

# Bootstrap request
def request_bootstrap():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(settings.SERVER_ADDR)
        rating = random.randint(1, 5)

        request = {
            "type": "bootstrap",
            "port": settings.LISTENING_PORT,
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

def multicast(filename):
    global multicast_ip, multicast_port
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        ttl = struct.pack('b', settings.MULTICAST_TTL)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        sock.sendto(message.ingroup_multicast_request(filename), (multicast_ip, multicast_port))
        print(f"Sent file request to {multicast_ip}:{multicast_port}")

def request_file(filename):
    if multicast_port is not None:
        multicast(filename)

def open_file(filename):
    filepath = os.path.join(settings.FILE_DIR, filename)
    try:
        if os.name == 'nt':  # Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # macOS, Linux
            subprocess.run(['xdg-open', filepath])
        else:
            print("Unsupported operating system.")
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        request_file(filename)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    request_bootstrap()
    while True:
        file = input("What file do you want?: ")
        open_file(file)