from packet import packet_util
from data_processing import data_processing_util

if __name__ == "__main__":
    # Build a packet
    descriptor_id = b"1234567890abcdef"  # 16 bytes
    payload = data_processing_util.read_file('''./ADAM A METHOD FOR STOCHASTIC OPTIMIZATION.pdf''')
    pkt = packet_util.packet_formation(descriptor_id, 1, 5, payload)

    # Parse it back
    parsed = packet_util.packet_parser(pkt)