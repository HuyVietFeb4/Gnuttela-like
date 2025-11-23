import struct
import json
class packet_util:
    @staticmethod
    def packet_formation(descriptor_id: bytes, payload_descriptor, ttl, payload: bytes) -> bytes:
        header = (
            descriptor_id +
            struct.pack('B', payload_descriptor) +
            struct.pack('B', ttl) +
            struct.pack('B', 0) +
            struct.pack('>I', len(payload))
        )
        return header + payload
    @staticmethod
    def packet_parser(packet: bytes):
        descriptor_id = packet[:16]
        payload_descriptor = struct.unpack('B', packet[16:17])[0]
        ttl = struct.unpack('B', packet[17:18])[0]
        hops = struct.unpack('B', packet[18:19])[0]
        payload_length = struct.unpack('>I', packet[19:23])[0]

        payload_content_raw_bytes = packet[23:23+payload_length]

        return {
            "descriptor_id": descriptor_id,
            "payload_descriptor": payload_descriptor,
            "ttl": ttl,
            "hops": hops,
            "payload_length": payload_length,
            "payload": payload_content_raw_bytes
        }