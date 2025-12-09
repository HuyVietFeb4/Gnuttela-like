import subprocess

ERROR_RATE = 0.01
FILE_CAPACITY = 1000
PORT = 8001
HOST = subprocess.run("hostname -I", shell=True, capture_output=True, text=True).stdout.split(" ")[0]