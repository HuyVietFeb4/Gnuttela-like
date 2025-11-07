import socket
import selectors
import config

import protocol
import peer_cache

selector = selectors.DefaultSelector()

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


# Peer will comunicating with the server by json format
# Client request with format
# peer_info = {
#     "type": "bootstrap",
#     "port": <port_number>, 
#     "role": <peer_role>
# }
# Client exit with format
# peer_info = {
#     "type": "exit",
#     "port": <port_number>, 
#     "role": <peer_role>
# }
# Server will send back all of the ultra peer infos to the client who request it 
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
    start_server()