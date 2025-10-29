import socket
import json
import config.settings as settings
# Identify bandwidth and assign role

# Bootstrap request
def request_bootstrap():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(settings.SERVER_ADDR)

        request = {
            "type": "bootstrap",
            "port": settings.REQUEST_PORT,
            "role": "ultra_peer"
        }

        sock.sendall(json.dumps(request).encode())

        response = sock.recv(4096)
        response = json.loads(response.decode())

        print("Bootstrap respone:")
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    request_bootstrap()