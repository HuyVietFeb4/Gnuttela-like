import speedtest
import random
from config.settings import ULTRA_PEER_BANDWIDTH_THRESHOLD

def assign_role_based_on_bandwidth(): # in Mbps
    st = speedtest.Speedtest()
    download = st.download() / 1e6
    upload = st.upload() / 1e6

    if download < ULTRA_PEER_BANDWIDTH_THRESHOLD["download"] or upload < ULTRA_PEER_BANDWIDTH_THRESHOLD["upload"]:
        return random.randint(0, 2) # Leaf peer
    else:
        return random.randint(3, 5) # Ultra peer