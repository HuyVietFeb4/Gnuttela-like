import sys
sys.path.insert(0, '../config')

import transport.bootstrap as bootstrap
import application.peer_classification as classify
import Host_cache_server.config as bootstrap_config
import application.leaf_peer as leaf_peer
import application.bloom as bloom
import config.peer_settings as peer_settings

if "__main__" == __name__:
    rating = classify.rating_based_on_bandwidth()
    ip, port = bootstrap.request_bootstrap(rating)
    if rating > bootstrap_config.RATING_THRESHOLD:
        ...
    else:
        leaf_peer = leaf_peer.leaf_peer(
            bloom.BloomFilter(peer_settings.CAPACITY, peer_settings.ERROR_RATE),
            peer_settings.HOST,
            peer_settings.PORT,
        )

