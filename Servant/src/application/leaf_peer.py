import os, hashlib, grpc, threading, sys, json, questionary, platform, subprocess
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
        ip, port = request.ip, request.port
        ultra = self.peer.network_table.get_ultra_peer()
        print(f"Received exit announcement from peer ({ip}:{port}).")
        self.peer.network_table.remove_peer(ip, port)
        if self.peer.__class__ != Peer:
            self.peer.bloom_table.remove_bloom(ip, port)
        if (ip, port) == ultra:
            LeaderElectionThread = threading.Thread(target=self.peer.leader_election)
            LeaderElectionThread.daemon = True
            LeaderElectionThread.start()
        return peer_pb2.Response(msg="Exit successful. See you again.")
    
    def PingBloom(self, request, context):
        peer_ip, peer_port = request.address.ip, request.address.port
        address = (peer_ip, peer_port)
        print(f"Received bloom filter from peer ({peer_ip}:{peer_port}).")
        if address not in self.peer.bloom_table.bloom_table:
            self.peer.bloom_table.bloom_table[address] = {"bloom_filter": KM_Compact_Refined_BloomFilter(peer_settings.FILE_CAPACITY)}
        self.peer.bloom_table.bloom_table[address]["bloom_filter"].from_compacted((data_processing_util.compact_bloom_deserializer(request.bloom))['cmBF'])
        return peer_pb2.Response(msg="Received bloom filter successfully.")
    
    def QueryFile(self, request, context):
        keyword = request.keyword
        print(f"Received file query: {keyword}")
        files = self.peer.collect_all(keyword)
        return peer_pb2.QueryResult(files=json.dumps(files).encode('utf-8'))
    
    def QuerySelf(self, request, context):
        keyword = request.keyword
        print(f"Received file query: {keyword}")
        files = self.peer.collect_self(keyword)
        return peer_pb2.QueryResult(files=json.dumps(files).encode('utf-8'))
    
    def QueryEach(self, request, context):
        keyword = request.keyword
        print(f"Received file query: {keyword}")
        files = [filename for filename in self.peer.all_files() if keyword.lower() in filename.lower()]
        return peer_pb2.Files(file_list=files)
    
    def DownloadFile(self, request, context):
        filepath = os.path.join(self.peer.directory, request.file)
        try:
            with open(filepath, 'rb') as f:
                while True:
                    piece = f.read(peer_settings.CHUNK)
                    if not piece:
                        break
                    yield peer_pb2.Chunk(buffer=piece)

        except FileNotFoundError:
            print(f"Error: The file '{filepath}' does not exist.")
        except PermissionError:
            print(f"Error: You do not have permission to read '{filepath}'.")
        except OSError as e:
            print(f"A system error occurred: {e}")

    def Bully(self, request, context):
        ip, port = request.peer.ip, request.peer.port
        print(f"Received bully message from peer ({ip}:{port}).")
        if self.peer.id < request.id:
            return peer_pb2.Response(msg="OK")
        return peer_pb2.Response(msg="NO")
    
    def LeaderElection(self, request, context):
        ip, port = request.ip, request.port
        print(f"Received request from new ultra peer ({ip}:{port}).")
        self.peer.network_table.update_peer_role(ip, port, False)
        PingBloomThread = threading.Thread(target=self.peer.ping_bloom_filter)
        PingBloomThread.daemon = True
        PingBloomThread.start()
        return peer_pb2.Response(msg="New ultra accepted.")

class Peer:
    def __init__(self, ip, port, bloom_filter=None, network_table=None, subnet_id=None, directory=None):
        self.ip = ip
        self.port = port
        self.bloom_filter = bloom_filter
        self.network_table = network_table
        self.subnet_id = subnet_id
        self.id = hashlib.sha1(os.urandom(32)).digest()
        self.directory = directory

    def all_files(self):
        return [entry for entry in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, entry))]
    
    def PeerServe(self, server_ip, server_port):
        """
        Initiate gRPC Peer server
        
        :param server_ip: gRPC peer server ip address
        :param server_port: gRPC peer server port number
        :param peer: peer instance
        """
        servicer = PeerServiceServicer(self)
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        peer_pb2_grpc.add_PeerServiceServicer_to_server(servicer, server)
        server.add_insecure_port(f"{server_ip}:{server_port}")
        server.start()
        print(f"gRPC Peer server running on {server_port}")
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
        with grpc.insecure_channel(f"{server_ip}:{server_port}") as channel:
            stub = peer_pb2_grpc.PeerServiceStub(channel)
            try:
                response = stub.Announce(peer_pb2.PeerAddress(ip=self.ip, port=self.port))
                print(f"Peer ({server_ip}:{server_port}) response:\nUltra peer address: ({response.ip}:{response.port})\n")
                return response.ip, response.port
            except grpc.RpcError as e:
                print("Synchronization failed:", e.code(), e.details())

    def ping_bloom_filter(self):
        """
        Ping bloom filter on update to ultra node

        :bloom: serialized bloom filter
        """
        ultra = self.network_table.get_ultra_peer()
        with grpc.insecure_channel(f"{ultra[0]}:{ultra[1]}") as channel:
            stub = peer_pb2_grpc.PeerServiceStub(channel)
            try:
                response = stub.PingBloom(peer_pb2.BloomFilter(address=peer_pb2.PeerAddress(ip=self.ip, port=self.port), bloom=data_processing_util.compact_bloom_serializer(self.bloom_filter)))
                print(f"Ultra ({ultra[0]}:{ultra[1]}) response: {response.msg}")
            except grpc.RpcError as e:
                print("Ping Bloom Filter failed:", e.code(), e.details())

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
                    [self.exit_network(node[0], node[1]) for node in self.network_table.get_peers_addresses(self.ip, self.port)]
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

    def open_file_in_default_app(self, filepath):
        """
        Opens a file using the OS's default application.
        
        :param filename: name of file to open
        """
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":
            subprocess.run(["open", filepath])
        else:
            subprocess.run(["xdg-open", filepath])
    
    def query(self, keyword):
        ultra = self.network_table.get_ultra_peer()
        with grpc.insecure_channel(f"{ultra[0]}:{ultra[1]}") as channel:
            stub = peer_pb2_grpc.PeerServiceStub(channel)
            try:
                response = stub.QueryFile(peer_pb2.Query(keyword=keyword))
                files = json.loads(response.files.decode('utf-8'))
                print(f"Ultra ({ultra[0]}:{ultra[1]}) response: {files}")
                if not files:
                    print("File not found!")
                    return
                options = [*files.keys()]
                choice = questionary.select("Which file would you want?", choices=options).ask()
                self.query_hit(choice, files[choice])
            except grpc.RpcError as e:
                print("Query failed:", e.code(), e.details())

    def query_hit(self, filename, address):
        if address[0] == self.ip and address[1] == self.port:
            self.open_file_in_default_app(os.path.join(self.directory, filename))
            return
        with grpc.insecure_channel(f"{address[0]}:{address[1]}") as channel:
            stub = peer_pb2_grpc.PeerServiceStub(channel)
            try:
                response = stub.DownloadFile(peer_pb2.FileName(file=filename))
                print(f"Ultra ({address[0]}:{address[1]}) response: ...")
                filepath = os.path.join(self.directory, filename)
                with open(filepath, 'wb') as f:
                    [f.write(chunk.buffer) for chunk in response]
                self.open_file_in_default_app(filepath)
            except grpc.RpcError as e:
                print("Query hit failed:", e.code(), e.details())

    def leader_election(self):
        ok_count = 0
        peers = self.network_table.get_peers_addresses(self.ip, self.port)
        for address in peers:
            with grpc.insecure_channel(f"{address[0]}:{address[1]}") as channel:
                stub = peer_pb2_grpc.PeerServiceStub(channel)
                try:
                    response = stub.Bully(peer_pb2.BullyRequest(peer=peer_pb2.PeerAddress(ip=self.ip, port=self.port), id=self.id))
                    msg = response.msg
                    print(f"({address[0]}:{address[1]}) response: {msg}")
                    if msg == "OK":
                        ok_count += 1
                except grpc.RpcError as e:
                    print("Bully failed:", e.code(), e.details())

        if ok_count == len(peers):
            self.network_table.update_peer_role(self.ip, self.port, False)
            from Servant.src.application.ultra_peer import UltraPeer
            from Servant.src.transport.bloom_table import bloom_table
            self.__class__ = UltraPeer
            self.bloom_table = bloom_table((self.ip, self.port), self.bloom_filter)
            for address in peers:
                with grpc.insecure_channel(f"{address[0]}:{address[1]}") as channel:
                    stub = peer_pb2_grpc.PeerServiceStub(channel)
                    try:
                        response = stub.LeaderElection(peer_pb2.PeerAddress(ip=self.ip, port=self.port))
                        print(f"({address[0]}:{address[1]}) response: {response.msg}")
                    except grpc.RpcError as e:
                        print("Leader election failed:", e.code(), e.details())

            with grpc.insecure_channel(f"{config.SERVER}:{config.PORT}") as channel:
                stub = bootstrap_pb2_grpc.BootstrapStub(channel)
                try:
                    response = stub.NewUltra(bootstrap_pb2.NewUltraRequest(peer=bootstrap_pb2.PeerAddress(ip=self.ip, port=self.port), id=self.subnet_id))
                    print(f"({config.SERVER}:{config.PORT}) response: {response.msg}")
                except grpc.RpcError as e:
                    print("New ultra failed:", e.code(), e.details())

    def exit_network(self, server_ip, server_port, subnet_id=None):
        """
        gRPC client call for exit_network
        
        :param server_ip: gRPC server ip address
        :param server_port: gRPC server port number
        :param subnet_id: peer's subnet id
        """
        with grpc.insecure_channel(f"{server_ip}:{server_port}") as channel:
            stub = peer_pb2_grpc.PeerServiceStub(channel) if subnet_id is None else bootstrap_pb2_grpc.BootstrapStub(channel)
            try:
                response = stub.ExitNetwork(peer_pb2.PeerAddress(ip=self.ip, port=self.port)) if subnet_id is None else stub.ExitNetwork(bootstrap_pb2.ExitRequest(peer=bootstrap_pb2.PeerAddress(ip=self.ip, port=self.port), subnet_id=subnet_id))
                print(f"({server_ip}:{server_port}) response: {response.msg}")
            except grpc.RpcError as e:
                print("Exit network failed:", e.code(), e.details())