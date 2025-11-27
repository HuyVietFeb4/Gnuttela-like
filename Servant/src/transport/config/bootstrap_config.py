import socket

SERVER_PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname()) # Replace with real server address later
SERVER_ADDR = (SERVER_IP, SERVER_PORT)
LISTENING_PORT = None