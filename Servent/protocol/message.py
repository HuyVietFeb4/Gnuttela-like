import json

def ingroup_multicast_request(filename):
    return json.dumps({
        "type": "ingroup_request",
        "ip": '',
        "port": '',
        "filename": filename
    }).encode()