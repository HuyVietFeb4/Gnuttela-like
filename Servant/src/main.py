import sys
sys.path.insert(0, '../config')

import transport.bootstrap as bootstrap
import application.peer_classification as classify
import Host_cache_server.config as bootstrap_config
from application.leaf_peer import Peer
from application.ultra_peer import UltraPeer
from application.bloom import BloomFilter
import config.peer_settings as peer_settings

if "__main__" == __name__:
    peer = None
    # True if leaf, False if ultra
    peer_type = None
    rating = classify.rating_based_on_bandwidth()
    result = bootstrap.request_bootstrap(rating)
    if rating > bootstrap_config.RATING_THRESHOLD:
        peer_type = False
        peer = UltraPeer(
            BloomFilter(peer_settings.FILE_CAPACITY, peer_settings.ERROR_RATE),
            peer_settings.HOST,
            peer_settings.PORT,
            result[0],
            result[1],
            result[2],
            result[3]
        )
    else:
        peer_type = True
        peer = Peer(
            BloomFilter(peer_settings.FILE_CAPACITY, peer_settings.ERROR_RATE),
            peer_settings.HOST,
            peer_settings.PORT,
            result[0],
            result[1]
        )

