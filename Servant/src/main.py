import grpc, threading, sys
from concurrent import futures

from Servant.src.application.leaf_peer import Peer
from Servant.src.application.ultra_peer import UltraPeer
from Servant.src.application.bloom import BloomFilter
from Servant.config import peer_settings
from Servant.src.transport.network_table import network_table
from Host_cache_server import config

from Host_cache_server.grpc_bootstrap import bootstrap_pb2
from Host_cache_server.grpc_bootstrap import bootstrap_pb2_grpc
from Servant.src.transport.grpc_peer import peer_pb2
from Servant.src.transport.grpc_peer import peer_pb2_grpc

def request_bootstrap():
    """
    gRPC client call for request_bootstrap
    """
    with grpc.insecure_channel(f"{"192.168.1.6"}:{config.PORT + 1}") as channel:
        stub = bootstrap_pb2_grpc.BootstrapStub(channel)
        try:
            response = stub.RequestBootstrap(bootstrap_pb2.JoinRequest(ip=peer_settings.HOST, port=peer_settings.PORT))
            print(f"Bootstrap response:\nSubnet ID: {response.subnetId}.")
            for node in response.subnet:
                print(f"{node.ip}:{node.port}")
            return response
        except grpc.RpcError as e:
            print("Request bootstrap failed:", e.code(), e.details())

class PeerServiceServicer(peer_pb2_grpc.PeerServiceServicer):
    """
    gRPC peer server class
    """
    def __init__(self, peer):
        super().__init__()
        self.peer = peer

    def Announce(self, request, context):
        print(f"Received join announcement from leaf peer ({request.ip}:{request.port}).")
        self.peer.network_table.add_peer(request.ip, request.port, True)
        ultra_ip, ultra_port = self.peer.network_table.get_ultra_peer()
        return peer_pb2.UltraPeerAddress(ip=ultra_ip, port=ultra_port)

    def ElectLeader(self, request, context):
        return super().ElectLeader(request, context)
    
    def ExitNetwork(self, request, context):
        print(f"Received exit announcement from peer ({request.ip}:{request.port}).")
        self.peer.network_table.remove_peer(request.ip, request.port)
        return peer_pb2.ExitResponse(msg="Exit successful. See you again.")

def PeerServe(server_ip, server_port, peer):
    """
    Initiate gRPC Peer server
    
    :param server_ip: gRPC peer server ip address
    :param server_port: gRPC peer server port number
    :param peer: peer instance
    """
    servicer = PeerServiceServicer(peer)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    peer_pb2_grpc.add_PeerServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"{server_ip}:{server_port + 1}")
    server.start()
    print(f"gRPC Peer server running on {server_port + 1}")
    FileSystemThread = threading.Thread(target=prompt_for_file, args=(server, peer))
    FileSystemThread.daemon = True
    FileSystemThread.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down...")

def announce_new_peer(server_ip, server_port):
    """
    gRPC server call for announce_new_peer
    
    :param server_ip: gRPC peer server ip address
    :param server_port: gRPC peer server port number
    """
    with grpc.insecure_channel(f"{server_ip}:{server_port + 1}") as channel:
        stub = peer_pb2_grpc.PeerServiceStub(channel)
        try:
            response = stub.Announce(peer_pb2.NewPeerAddress(ip=peer_settings.HOST, port=peer_settings.PORT))
            print(f"Peer ({server_ip}:{server_port}) response:\nUltra peer address: ({response.ip}:{response.port})")
            return response.ip, response.port
        except grpc.RpcError as e:
            print("Synchronization failed:", e.code(), e.details())

def prompt_for_file(server, peer):
    """
    Keep prompting for file from user until quit

    :param server: gRPC Peer server instance
    :param peer: peer instance
    """
    while True:
        try:
            filename = input("\nEnter the file name you want (or type 'quit' to exit server): ")
            if filename.lower() == 'quit':
                print("\nInitiating server shutdown...")
                [exit_network(node[0], node[1]) for node in peer.network_table.get_peers_addresses()]
                exit_network(config.SERVER, config.PORT, peer.subnet_id)
                server.stop(grace=5)
                sys.exit(0)

            if filename:
                find_file(filename)
                
        except EOFError:
            print("\nInput stream closed. Initiating server shutdown...")
            server.stop(grace=5)
            break

        except KeyboardInterrupt:
            break

def find_file(filename):
    pass

def exit_network(server_ip, server_port, subnet_id=None):
    """
    gRPC client call for exit_network
    
    :param server_ip: gRPC server ip address
    :param server_port: gRPC server port number
    :param subnet_id: peer's subnet id
    """
    with grpc.insecure_channel(f"{server_ip}:{server_port + 1}") as channel:
        stub = peer_pb2_grpc.PeerServiceStub(channel) if subnet_id is None else bootstrap_pb2_grpc.BootstrapStub(channel)
        try:
            response = stub.ExitNetwork(peer_pb2.NewPeerAddress(ip=peer_settings.HOST, port=peer_settings.PORT)) if subnet_id is None else stub.ExitNetwork(bootstrap_pb2.ExitRequest(ip=peer_settings.HOST, port=peer_settings.PORT, subnetId=subnet_id))
            print(f"({server_ip}:{server_port}) response: {response.msg}")
        except grpc.RpcError as e:
            print("Exit network failed:", e.code(), e.details())

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
    
    peer.bloom_filter = BloomFilter(peer_settings.FILE_CAPACITY)
    [peer.bloom_filter.add(filename) for filename in peer_settings.FILES]
    
    # Announce new peer with other peers
    if peer.__class__ == Peer:
        for node in peer.network_table.get_peers_addresses():
            ultra_ip, ultra_port = announce_new_peer(node[0], node[1])
            peer.network_table.update_peer_role(ultra_ip, ultra_port, False)
    
    # Run PeerService server
    PeerServiceThread = threading.Thread(target=PeerServe, args=(peer_settings.HOST, peer_settings.PORT, peer))
    PeerServiceThread.start()
    try:
        PeerServiceThread.join()
    except KeyboardInterrupt:
        pass
