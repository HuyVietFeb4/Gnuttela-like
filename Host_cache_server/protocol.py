import json
import time

def parse_requests(data):
    return json.loads(data.decode())

def bootstrap_success():
    return json.dumps({
        "type": "bootstrap_response",
        "status": "ok",
        "reason": "",
    }).encode()

def bootstrap_failed(failure_message):
    return json.dumps({
        "type": "bootstrap_response",
        "status": "failed",
        "reason": failure_message,
        "ultra_peers": []
    }).encode()