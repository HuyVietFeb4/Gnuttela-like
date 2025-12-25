import socket, selectors, grpc, threading, json
from concurrent import futures

from Host_cache_server import protocol, peer_cache, config
from Host_cache_server.grpc_bootstrap import bootstrap_pb2_grpc
from Host_cache_server.grpc_bootstrap import bootstrap_pb2

selector = selectors.DefaultSelector()

# gRPC Boostrap server run on port
class BootstrapServicer(bootstrap_pb2_grpc.BootstrapServicer):
    def RequestBootstrap(self, request, context):
        ip = request.peer.ip
        port = request.peer.port
        print(f"Received bootstrap request from peer ({ip}:{port})")
        subnet_id, subnet = peer_cache.add_peer(ip, port)
        routing_table = [bootstrap_pb2.PeerAddress(ip=_ip, port=_port) for _ip, _port in subnet]
        return bootstrap_pb2.JoinResponse(subnet_id=subnet_id, subnet=routing_table)
    
    def ExitNetwork(self, request, context):
        ip = request.peer.ip
        port = request.peer.port
        print(f"Received exit announcement from peer ({ip}:{port}).")
        peer_cache.remove_peer(ip, port, request.subnet_id)
        return bootstrap_pb2.ExitResponse(msg="Exit successful. See you again.")
    
    def GetUltras(self, request, context):
        print(f"Received request to get ultra list from ({request.peer.ip}:{request.peer.port})")
        return bootstrap_pb2.UltrasResponse(nodes=json.dumps(peer_cache.ultra_peers).encode('utf-8'))
    
def BootstrapServe():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bootstrap_pb2_grpc.add_BootstrapServicer_to_server(BootstrapServicer(), server)
    server.add_insecure_port(f"{config.SERVER}:{config.PORT}")
    server.start()
    print(f"gRPC Bootstrap server running on {config.SERVER}:{config.PORT}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down...")

def accept(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)
    selector.register(conn, selectors.EVENT_READ, handle_request)
    print(f"Accepted connection from {addr}")

def handle_request(conn):
    try:
        data = conn.recv(1024)
        if not data:
            selector.unregister(conn)
            conn.close()
            return
        request = protocol.parse_requests(data)
        if request.get("type") == "bootstrap":
            id = peer_cache.add_peer(conn.getpeername()[0], request)

            # Assume that everything is okay
            # Return multicast ip address and port
            response = protocol.bootstrap_success(id)
            conn.sendall(response)
        
        elif request.get("type") == "exit":
            peer_cache.remove_ultra_peer(conn.getpeername()[0], request.get("port"))

    except Exception as e:
        print("Error:",  e)
    finally:
        selector.unregister(conn)
        conn.close()

def start_server():
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind(config.ADDR)
    listening_socket.listen()
    print(f"Server start, listening on {config.ADDR}")
    listening_socket.setblocking(False)
    selector.register(listening_socket, selectors.EVENT_READ, accept)

    while True:
        events = selector.select(timeout=None)
        for key, mask in events:
            callback = key.data
            callback(key.fileobj)


# Peer will communicate with the server by json format
# Client request with format
# peer_info = {
#     "type": "bootstrap",
#     "port": <port_number>, # Port number that peer use to listen to other peer request
#     "role": <peer_role>
# }
# Client exit with format
# peer_info = {
#     "type": "exit",
#     "port": <port_number>, 
#     "role": <peer_role>
# }
# Server will send back all the ultra peer infos to the client who request it
# respond = {
#     "type": "bootstrap_response",
#     "status": <reasons>,
#     "timestamp": <unix timestamp>,
#     "ultra_peers": [
#     {"ip": "192.168.1.2", "port": 6346},
#     {"ip": "192.168.1.3", "port": 6346}
#   ]
# }

if __name__ == "__main__":
    BootstrapThread = threading.Thread(target=BootstrapServe)
    BootstrapThread.start()
    try:
        BootstrapThread.join()
    except KeyboardInterrupt:
        pass
    #start_server()