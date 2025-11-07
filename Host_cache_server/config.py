import socket
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)
BOOTSTRAP_STATUS = ["accept", "reject"]
MAX_PEERS = 100
RATING_THRESHOLD = 2
MAX_CHILDREN = 2
MULTICAST_SIZE = 2