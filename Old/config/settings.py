import socket

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 5050
SERVER_ADDR = (SERVER_IP, SERVER_PORT)
MULTICAST_TTL = 1
REQUEST_PORT = 6439
LISTENING_PORT = 8978
FILE_DIR = 'file_sharing'

ULTRA_PEER_BANDWIDTH_THRESHOLD = {
    "upload": 50,
    "download": 50
} #Upload, Download in Mbps