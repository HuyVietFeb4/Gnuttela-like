import os, hashlib, grpc, threading, sys
from concurrent import futures

from Host_cache_server.grpc_bootstrap import bootstrap_pb2
from Host_cache_server.grpc_bootstrap import bootstrap_pb2_grpc
from Servant.src.transport.grpc_peer import peer_pb2
from Servant.src.transport.grpc_peer import peer_pb2_grpc

from Servant.config import peer_settings
from Servant.src.application.bloom import KM_Compact_Refined_BloomFilter
from Servant.src.data_processing.data_processing import data_processing_util
from Host_cache_server import config

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
        return peer_pb2.PeerAddress(ip=ultra_ip, port=ultra_port)

    def ElectLeader(self, request, context):
        return super().ElectLeader(request, context)
    
    def ExitNetwork(self, request, context):
        print(f"Received exit announcement from peer ({request.ip}:{request.port}).")
        self.peer.network_table.remove_peer(request.ip, request.port)
        self.peer.bloom_table.remove_bloom(request.ip, request.port)
        return peer_pb2.Response(msg="Exit successful. See you again.")
    
    def PingBloom(self, request, context):
        peer_ip, peer_port = request.address.ip, request.address.port
        address = (peer_ip, peer_port)
        print(f"Received bloom filter from peer ({peer_ip}:{peer_port}).")
        if address not in self.peer.bloom_table.bloom_table:
            self.peer.bloom_table.bloom_table[address] = KM_Compact_Refined_BloomFilter(peer_settings.FILE_CAPACITY)
        self.peer.bloom_table.bloom_table[address].from_compacted((data_processing_util.compact_bloom_deserializer(request.bloom))['cmBF'])
        return peer_pb2.Response(msg="Received bloom filter successfully.")

class Peer:
    def __init__(self, bloom_filter=None, network_table=None, subnet_id=None, directory=None):
        self.bloom_filter = bloom_filter
        self.network_table = network_table
        self.subnet_id = subnet_id
        self.id = hashlib.sha1(os.urandom(32)).digest()
        self.directory = directory

    def all_files(self):
        return [entry for entry in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, entry))]
    
    def PeerServe(self):
        """
        Initiate gRPC Peer server
        
        :param server_ip: gRPC peer server ip address
        :param server_port: gRPC peer server port number
        :param peer: peer instance
        """
        server_ip, server_port = peer_settings.HOST, peer_settings.PORT
        servicer = PeerServiceServicer(self)
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        peer_pb2_grpc.add_PeerServiceServicer_to_server(servicer, server)
        server.add_insecure_port(f"{server_ip}:{server_port + 1}")
        server.start()
        print(f"gRPC Peer server running on {server_port + 1}")
        FileSystemThread = threading.Thread(target=self.prompt_for_file, args=(server,))
        FileSystemThread.daemon = True
        FileSystemThread.start()
        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            print("Shutting down...")

    def announce_new_peer(self, server_ip, server_port):
        """
        gRPC server call for announce_new_peer
        
        :param server_ip: gRPC peer server ip address
        :param server_port: gRPC peer server port number
        """
        with grpc.insecure_channel(f"{server_ip}:{server_port + 1}") as channel:
            stub = peer_pb2_grpc.PeerServiceStub(channel)
            try:
                response = stub.Announce(peer_pb2.PeerAddress(ip=peer_settings.HOST, port=peer_settings.PORT))
                print(f"Peer ({server_ip}:{server_port}) response:\nUltra peer address: ({response.ip}:{response.port})")
                return response.ip, response.port
            except grpc.RpcError as e:
                print("Synchronization failed:", e.code(), e.details())

    def ping_bloom_filter(self):
        """
        Ping bloom filter on update to ultra node

        :bloom: serialized bloom filter
        """
        ultra = self.network_table.get_ultra_peer()
        with grpc.insecure_channel(f"{ultra[0]}:{ultra[1] + 1}") as channel:
            stub = peer_pb2_grpc.PeerServiceStub(channel)
            try:
                response = stub.PingBloom(peer_pb2.BloomFilter(address=peer_pb2.PeerAddress(ip=peer_settings.HOST, port=peer_settings.PORT), bloom=data_processing_util.compact_bloom_serializer(self.bloom_filter)))
                print(f"Ultra ({ultra[0]}:{ultra[1]}) response: {response.msg}")
            except grpc.RpcError as e:
                print("Synchronization failed:", e.code(), e.details())

    def prompt_for_file(self, server):
        """
        Keep prompting for file from user until quit

        :param server: gRPC Peer server instance
        :param peer: peer instance
        """
        while True:
            try:
                keyword = input("\nEnter the file name you want (or type 'quit' to exit server): ")
                if keyword.lower() == 'quit':
                    print("\nInitiating server shutdown...")
                    [self.exit_network(node[0], node[1]) for node in self.network_table.get_peers_addresses()]
                    self.exit_network(config.SERVER, config.PORT, self.subnet_id)
                    server.stop(grace=5)
                    sys.exit(0)

                if keyword:
                    self.query(keyword)
                    
            except EOFError:
                print("\nInput stream closed. Initiating server shutdown...")
                server.stop(grace=5)
                break

            except KeyboardInterrupt:
                break

    def query(self, keyword):
        pass

    def query_hit(self):
        pass

    def push(self):
        pass

    def exit_network(self, server_ip, server_port, subnet_id=None):
        """
        gRPC client call for exit_network
        
        :param server_ip: gRPC server ip address
        :param server_port: gRPC server port number
        :param subnet_id: peer's subnet id
        """
        with grpc.insecure_channel(f"{server_ip}:{server_port + 1}") as channel:
            stub = peer_pb2_grpc.PeerServiceStub(channel) if subnet_id is None else bootstrap_pb2_grpc.BootstrapStub(channel)
            try:
                response = stub.ExitNetwork(peer_pb2.PeerAddress(ip=peer_settings.HOST, port=peer_settings.PORT)) if subnet_id is None else stub.ExitNetwork(bootstrap_pb2.ExitRequest(ip=peer_settings.HOST, port=peer_settings.PORT, subnetId=subnet_id))
                print(f"({server_ip}:{server_port}) response: {response.msg}")
            except grpc.RpcError as e:
                print("Exit network failed:", e.code(), e.details())