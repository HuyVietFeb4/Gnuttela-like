class bloom_table:
    '''
    This class is for ultra peer to keep track of peer bloom filter and it's metadata 
    It will only keep track of the leaf peers that it manage.
    Structure:
        bloom_table = {
            (ip, port): {
                "bloom_filter": <bloom_filter>,
                // other metadata if needed
            }
        }
    '''

    def __init__(self, self_address, self_bloom): # Since ultra peer is an extension of peer, it must include at least it bloom filter data
        self.bloom_table = {self_address: {"bloom_filter": self_bloom}}

    def file_request(self, filename):
        '''
            Iterate through each peer and check if there is, return list of peer that pressumely have it
        '''
        peer_result = []
        for address, info in self.bloom_table.items():
            if info['bloom_filter'].checksumshi(filename):
                peer_result.append(address)

        return peer_result

    def remove_bloom(self, ip, port):
        self.bloom_table.pop((ip, port), "Can't find bloom")