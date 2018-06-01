import json, os, requests, sys
from flask import Flask, request, abort, jsonify
from urlparse import urlparse

app = Flask(__name__)
credFile = str('/tmp/creds.json')

@app.route('/payload', methods=['GET', 'POST'])
def webhookServer():

    # Define some vars
    EVENT = None
    GHE_URL = None
    GHE_HOST = None
    TOKEN = None

    # Let's go ahead and make GET requests happy. You could use it to test firewall rules
    if request.method == 'GET':
        return jsonify({'method':'GET','status':'success'}), 200

    # Webhooks will make POST requests
    elif request.method == 'POST':

        print ' '

        EVENT = request.headers.get('X-GitHub-Event')
        print '----------> Received event: ' + EVENT
        debugPrintWebhookJSON(request.json)

        if EVENT == "ping":
            return handle_ping()

        if EVENT == "push":
            return handle_push()

        if EVENT == "delete":
            return handle_delete()

def handle_ping():
    return jsonify({'event':'ping','status':'success'}), 200

def handle_push():
    print 'Event Action: ' + request.json["action"]
    return jsonify({'event':'push','status':'success'}), 200

def handle_delete():
    print 'Event Action: ' + request.json["action"]
    return jsonify({'event':'delete','status':'success'}), 200

def debugPrintWebhookJSON(data):

    # Debug output
    print ' '
    print '======= DEBUG: BEGIN REQUEST JSON ======='
    print(json.dumps(data))
    print '======= DEBUG: END REQUEST JSON ======='
    print ' '

if __name__ == '__main__':
    app.run(host= '127.0.0.1', port=4040)  # Run on the machine's IP address and not just localhost