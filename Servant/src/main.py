import grpc, threading, os, subprocess, platform
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

def request_bootstrap():
    """
    gRPC client call for request_bootstrap
    """
    with grpc.insecure_channel(f"{config.SERVER}:{config.PORT + 1}") as channel:
        stub = bootstrap_pb2_grpc.BootstrapStub(channel)
        try:
            response = stub.RequestBootstrap(bootstrap_pb2.JoinRequest(ip=peer_settings.HOST, port=peer_settings.PORT))
            print(f"Bootstrap response:\nSubnet ID: {response.subnetId}.")
            for node in response.subnet:
                print(f"{node.ip}:{node.port}")
            return response
        except grpc.RpcError as e:
            print("Request bootstrap failed:", e.code(), e.details())

def open_file_in_default_app(filepath):
    """
    Opens a file using the OS's default application.
    
    :param filepath: path of file to open
    """
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":
        subprocess.run(["open", filepath])
    else:
        subprocess.run(["xdg-open", filepath])

if "__main__" == __name__:
    # Bootstrap
    result = request_bootstrap()

    # Initialize peer
    peer = Peer()
    if len(result.subnet) == 1:
        peer = UltraPeer()
    peer.subnet_id = result.subnetId
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
        for node in peer.network_table.get_peers_addresses():
            ultra_ip, ultra_port = peer.announce_new_peer(node[0], node[1])
            peer.network_table.update_peer_role(ultra_ip, ultra_port, False)

        peer.ping_bloom_filter()
    else:
        peer.bloom_table = bloom_table((peer_settings.HOST, peer_settings.PORT), peer.bloom_filter)
    
    # Run PeerService server
    PeerServiceThread = threading.Thread(target=peer.PeerServe)
    PeerServiceThread.start()
    try:
        PeerServiceThread.join()
    except KeyboardInterrupt:
        pass
