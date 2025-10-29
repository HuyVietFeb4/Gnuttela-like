import socket

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 5050
SERVER_ADDR = (SERVER_IP, SERVER_PORT)

REQUEST_PORT = 6439
LISTENING_PORT = 8978