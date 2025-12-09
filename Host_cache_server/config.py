import subprocess
SERVER = subprocess.run("hostname -I", shell=True, capture_output=True, text=True).stdout.split(" ")[0]
PORT = 5050
ADDR = (SERVER, PORT)
BOOTSTRAP_STATUS = ["accept", "reject"]
MAX_PEERS = 100
RATING_THRESHOLD = 2
MAX_NODES = 3
MULTICAST_SIZE = 2