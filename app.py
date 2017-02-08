# -*- coding: utf-8 -*-
import os
from flask import Flask, request
from python_mysql_dbconfig import read_config
import FaceBookHelper
from status import status 
app = Flask(__name__)



@app.route('/status', methods=['GET'])
def w_status():
    return status()

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments

    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):

        if not request.args.get("hub.verify_token") == read_config(section="facebook")["verify_token"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    FaceBookHelper.webhook_handler()
    return "ok", 200






if __name__ == '__main__':
    #l = read_config(section="facebook")["verify_token"]
    app.run(debug=True, host= '0.0.0.0')
