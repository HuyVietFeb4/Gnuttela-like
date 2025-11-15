'''
This file consists of logic to form packet and parse packet from other devices
'''
def packet_format(message_id, payload_type, ttl, hops, payload_length, payload): 
    '''
        to create and format the packet from informations
        input:
            message_id: 16 bytes, uniquely identify the message in the network
            payload_type: 1 byte
                0x00 = Ping
                0x01 = Pong
                0x02 = Bye
                0x40 = Push
                0x80 = Query
                0x81 = Query Hit
            ttl: 1 byte, number of times the message will be forwarded by Gnutella servents before it is removed from the network
            hops: 1 byte, number of times the message has been forwarded.
            payload_length: 4 bytes
            payload: the payload depend on the protocol
        output:
            the packet
    '''

    pass

def packet_parsing(packet):
    '''
        To parse incoming packet
    '''
    pass