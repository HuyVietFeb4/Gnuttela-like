import grpc, threading, builtins,sys
from pathlib import Path

from Servant.src.application.leaf_peer import Peer
from Servant.src.application.ultra_peer import UltraPeer
from Servant.src.application.bloom import KM_Compact_Refined_BloomFilter
from Servant.config import peer_settings
from Servant.src.transport.network_table import network_table
from Host_cache_server import config
from Servant.src.transport.bloom_table import bloom_table
from Servant.test.bloom_test_util import create_keyword_list

from Host_cache_server.grpc_bootstrap import bootstrap_pb2
from Host_cache_server.grpc_bootstrap import bootstrap_pb2_grpc

def smart_print(*args, **kwargs):
    msg = " ".join(map(str, args))
    sys.stdout.write(f"\r\033[K{msg}\n")
    sys.stdout.write("\nEnter the file name you want (or type 'quit' to exit server): ")
    sys.stdout.flush()

builtins.print = smart_print

def request_bootstrap():
    """
    gRPC client call for request_bootstrap
    """
    with grpc.insecure_channel(f"{config.SERVER}:{config.PORT}") as channel:
        stub = bootstrap_pb2_grpc.BootstrapStub(channel)
        try:
            response = stub.RequestBootstrap(bootstrap_pb2.JoinRequest(peer=bootstrap_pb2.PeerAddress(ip=peer_settings.HOST, port=peer_settings.PORT)))
            print(f"Bootstrap response:\nSubnet ID: {response.subnet_id}.\n")
            for node in response.subnet:
                print(f"{node.ip}:{node.port}")
            return response
        except grpc.RpcError as e:
            print("Request bootstrap failed:", e.code(), e.details())

if "__main__" == __name__:
    # Bootstrap
    result = request_bootstrap()

    # Initialize peer
    peer = Peer(peer_settings.HOST, peer_settings.PORT)
    if len(result.subnet) == 1:
        peer = UltraPeer(peer_settings.HOST, peer_settings.PORT)
    peer.subnet_id = result.subnet_id
    peer.network_table = network_table()
    if peer.__class__ == UltraPeer:
        peer.network_table.add_peer(result.subnet[0].ip, result.subnet[0].port, False)
    else:
        [peer.network_table.add_peer(node.ip, node.port, True) for node in result.subnet]
    
    peer.directory = Path(__file__).parent.parent / "files"
    peer.bloom_filter = KM_Compact_Refined_BloomFilter(peer_settings.FILE_CAPACITY)
    [peer.bloom_filter.add(keyword) for filename in peer.all_files() for keyword in create_keyword_list(filename)]

    # Announce new peer with other peers
    if peer.__class__ == Peer:
        for node in peer.network_table.get_peers_addresses(peer.ip, peer.port):
            ultra_ip, ultra_port = peer.announce_new_peer(node[0], node[1])
            peer.network_table.update_peer_role(ultra_ip, ultra_port, False)

        peer.ping_bloom_filter()
    else:
        peer.bloom_table = bloom_table((peer.ip, peer.port), peer.bloom_filter)
    
    # Run PeerService server
    PeerServiceThread = threading.Thread(target=peer.PeerServe, args=(peer.ip, peer.port))
    PeerServiceThread.start()
    try:
        PeerServiceThread.join()
    except KeyboardInterrupt:
        pass
