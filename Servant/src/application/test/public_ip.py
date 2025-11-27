from requests import get

ip = get('https://api.ipify.org').content.decode('utf8')
print('My public IP address is: {}'.format(ip))

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))   # connect to Google DNS
local_ip = s.getsockname()[0]
s.close()

print("Local IP:", local_ip)
