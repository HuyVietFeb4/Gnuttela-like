from Servant.src.application.leaf_peer import Peer

class UltraPeer(Peer):
    def __init__(self, bloom_filter=None, network_table=None, subnet_id=None):
        super().__init__(bloom_filter, network_table, subnet_id)