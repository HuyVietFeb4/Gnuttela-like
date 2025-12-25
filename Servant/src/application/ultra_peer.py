import grpc, questionary, json

from Servant.src.application.leaf_peer import Peer
from Host_cache_server import config

from Servant.src.transport.grpc_peer import peer_pb2
from Servant.src.transport.grpc_peer import peer_pb2_grpc
from Host_cache_server.grpc_bootstrap import bootstrap_pb2
from Host_cache_server.grpc_bootstrap import bootstrap_pb2_grpc

class UltraPeer(Peer):
    def __init__(self, ip, port, bloom_filter=None, network_table=None, subnet_id=None, bloom_table=None):
        super().__init__(ip, port, bloom_filter, network_table, subnet_id)
        self.bloom_table = bloom_table

    def collect_self(self, keyword):
        files = {}
        for address in self.bloom_table.query(keyword):
            with grpc.insecure_channel(f"{address[0]}:{address[1]}") as channel:
                stub = peer_pb2_grpc.PeerServiceStub(channel)
                try:
                    response = stub.QueryEach(peer_pb2.Query(keyword=keyword))
                    peer_files = response.file_list
                    print(f"({address[0]}:{address[1]}) response: {peer_files}")
                    for peer_file in peer_files:
                        files[peer_file] = address
                except grpc.RpcError as e:
                    print("Query leaf peers failed:", e.code(), e.details())
        
        return files

    def collect_all(self, keyword):
        files = {}
        files |= self.collect_self(keyword)
        with grpc.insecure_channel(f"{config.SERVER}:{config.PORT}") as channel:
            stub = bootstrap_pb2_grpc.BootstrapStub(channel)
            try:
                response = stub.GetUltras(bootstrap_pb2.RequestUltras(peer=bootstrap_pb2.PeerAddress(ip=self.ip, port=self.port)))
                ultras = json.loads(response.nodes.decode('utf-8'))
                print(f"Bootstrap response: {ultras}")
                for subnet_id, ultra in ultras.items():
                    if subnet_id != self.subnet_id:
                        with grpc.insecure_channel(f"{ultra[0]}:{ultra[1]}") as channel:
                            stub = peer_pb2_grpc.PeerServiceStub(channel)
                            try:
                                response = stub.QuerySelf(peer_pb2.Query(keyword=keyword))
                                subnet_files = json.loads(response.files.decode('utf-8'))
                                print(f"({ultra[0]}:{ultra[1]}) response: {subnet_files}")
                                files |= subnet_files
                            except grpc.RpcError as e:
                                print("Query ultra peers failed:", e.code(), e.details())

            except grpc.RpcError as e:
                print("Query all peers failed:", e.code(), e.details())
        
        return files

    def query(self, keyword):
        files = self.collect_all(keyword)
        if not files:
            print("File not found!")
            return
        options = [*files.keys()]
        choice = questionary.select("Which file would you want?", choices=options).ask()
        self.query_hit(choice, files[choice])