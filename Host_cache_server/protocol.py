import json
import time

from peer_cache import get_subnetwork

def parse_requests(data):
    return json.loads(data.decode())

def bootstrap_success(id):
    return json.dumps({
        "type": "bootstrap_response",
        "status": "ok",
        "reason": "",
        "subnetwork": get_subnetwork(id)
    }).encode()

def bootstrap_failed(failure_message):
    return json.dumps({
        "type": "bootstrap_response",
        "status": "failed",
        "reason": failure_message,
        "ultra_peers": []
    }).encode()