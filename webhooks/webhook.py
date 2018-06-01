import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
credFile = str('/tmp/creds.json')

API_KEY = "4d52b63c-f73a-4c27-8104-a3142512c517"
LOGSET_ID = "c5838fd4-1d3d-4104-8293-87b72ddc5ef4"
GET_LOGSET_URL = "https://rest.logentries.com/management/logsets/{0}"
LOG_URL = "https://rest.logentries.com/management/logs"
LOG_NAME_PATTERN = "exchange:{0}"


@app.route('/payload', methods=['GET', 'POST'])
def webhookServer():
    if request.method == 'GET':
        return jsonify({'method': 'GET', 'status': 'success'}), 200
    # Webhooks will make POST requests
    elif request.method == 'POST':
        EVENT = request.headers.get('X-GitHub-Event')
        print '----------> Received event: ' + EVENT
        if EVENT == "ping":
            return handle_ping()
        if EVENT == "push":
            return handle_push()
        if EVENT == "delete":
            return handle_delete()



def handle_ping():
    return jsonify({'event': 'ping', 'status': 'success'}), 200


def handle_push():
    new_log_created = False
    name = branch_name()
    if get_log(name) is None:
        # create Log
        new_log_created = not (create_log(LOG_NAME_PATTERN.format(name)) is None)
    return jsonify({'event': 'push', 'status': 'success', 'log_created': new_log_created}), 200


def handle_delete():
    deleted = False
    log = get_log(branch_name())
    if not (log is None):
        deleted = delete_log(log["id"])
    return jsonify({'event': 'push', 'status': 'success', 'log_deleted': deleted}), 200


def get_log(branch_name):
    headers = {
        'x-api-key': API_KEY,
        "Content-Type": "application/json"
    }
    url = GET_LOGSET_URL.format(LOGSET_ID)
    resp = requests.get(url, headers=headers).json()
    for log in resp['logset']['logs_info']:
        if LOG_NAME_PATTERN.format(branch_name) == log['name']:
            print "Found log for branch {0}: {1}".format(branch_name, log)
            return log
    print "No log found for branch {0}".format(branch_name)
    return None


def create_log(name):
    headers = {
        'x-api-key': API_KEY,
        "Content-Type": "application/json"
    }
    body = json.dumps({"log": {"name": name, "source_type": "token", "logsets_info": [{"id": LOGSET_ID}]}},
                      separators=(',', ':'))
    print "Sending to Logentries: {0}".format(body)
    r = requests.post(LOG_URL, data=body, headers=headers)
    print "Create log result:", r.status_code, r.content
    token = r.json()['log']['tokens'][0]
    print "Created log token:{0}".format(token)
    return token


def delete_log(log_id):
    headers = {'x-api-key': API_KEY}
    url = LOG_URL + "/" + log_id
    print "Sending DELETE to {0}".format(url)
    r = requests.delete(url, headers=headers)
    print "Delete log result:", r.status_code, r.content
    return r.status_code == 204


def branch_name():
    ref = request.json['ref'].replace("refs/heads/", "")
    print "Fetched branch name: " + ref
    return ref


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4041)  # Run on the machine's IP address and not just localhost
