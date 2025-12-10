import subprocess, os
from pathlib import Path

ERROR_RATE = 0.01
FILE_CAPACITY = 1000
PORT = 8001
HOST = subprocess.run("hostname -I", shell=True, capture_output=True, text=True).stdout.split(" ")[0]
FILE_DIRECTORY = Path(__file__).parent.parent / "files"
FILES = [entry for entry in os.listdir(FILE_DIRECTORY) if os.path.isfile(os.path.join(FILE_DIRECTORY, entry))]