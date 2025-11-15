import json

def ingroup_multicast_request(filename):
    return json.dumps({
        "type": "ingroup_request",
        "ip": '',
        "port": '',
        "filename": filename
    }).encode()
# General flow of request file to other peers
# 1. Search for file (Query) to Ultra peer
# 2. Ultra peer check Routing Table build from the bloom filter
# 3. Ultra peer also route the query request to other ultra peers
# 4. If the query is hit in Routing Table, the Ultra Peer will send the query to the leaf peer that have the file
# 5. The leaf peer that have the file will send Query Hit
# 6. The request peer will send connection and handshake request(PUSH protocol or just simple connection)
# 7. File Transfer begin
# 8. Close connections

# Automatic protocol from application
# 1. Ping, to signify the peer is there, send with bloom filter(just for leaf peer) or nothing (for ultra peers to each other)
# 2. Pong, to signify the respond of ping, send with bloom filter(just for ultra peers to leaf peer) or nothing(the rest)


# Functions that need implementation

def packet_reading(packet):
    '''
        to read incoming packet and translating it application supported data format
        input:
            packet: the whole packet
        output:

    '''