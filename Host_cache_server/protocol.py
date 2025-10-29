import json
import time

from peer_cache import get_ultra_peers

def parse_requests(data):
    return json.loads(data.decode())

def bootstrap_success():
    return json.dumps({
        "type": "bootstrap_response",
        "status": "ok",
        "reason": "",
        "ultra_peers": get_ultra_peers()
    }).encode()

def bootstrap_failed(failure_message):
    return json.dumps({
        "type": "bootstrap_response",
        "status": "failed",
        "reason": failure_message,
        "ultra_peers": []
    }).encode()