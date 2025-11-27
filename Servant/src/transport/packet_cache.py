class packet_cache:
    '''
    This class is for ultra peer to keep track of already processed packets.
    Structure:
        bloom_table = {
            peer_id: {
                "bloom_filter": <bloom_filter>,
                // other metadata if needed
            }
        }
    '''
    def __init__(self):
        self.packet_list = []

    def check_and_add(self, packet: bytes):
        '''
        Input: the packet in bytes
        Output: 
            True: already processed
            False: not yet processed, add to cache
        '''
        packet_hash_value = packet[:16]
        if packet_hash_value not in self.packet_list:
            self.packet_list.append(packet_hash_value)
            return False
        return True
    
    def clear_cache(self):
        self.packet_list.clear()