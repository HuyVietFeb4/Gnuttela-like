import socket
import json
import config.settings as settings
import random
# Identify bandwidth and assign role
# Just use speedtest library lmao


# Bootstrap request
def request_bootstrap():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(settings.SERVER_ADDR)

        request = {
            "type": "bootstrap",
            "port": settings.LISTENING_PORT,
            "rating": random.randint(1, 5),
            "location": (random.randint(-180, 180), random.randint(-180, 180))
        }

        sock.sendall(json.dumps(request).encode())

        response = sock.recv(4096)
        response = json.loads(response.decode())

        print("Bootstrap response:")
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    request_bootstrap()