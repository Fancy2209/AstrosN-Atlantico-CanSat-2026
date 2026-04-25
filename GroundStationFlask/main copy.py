from threading import Thread
from tinydb import TinyDB
from tinyrecord import transaction
from flask import Flask, jsonify
from flask_queue_sse import ServerSentEvents
from flask_cors import CORS
import serial
import traceback
import time

# PYTHONBUFFERED=TRUE /home/ana/.local/bin/gunicorn main:app --worker-class gevent --bind 192.168.8.195:8080 --enable-stdio-inheritance --log-level "debug"

db = TinyDB('db3.json')
table = db.table('CanSat')

app = Flask(__name__)
sse: ServerSentEvents = None
CORS(app, origins=["*"])

@app.route("/subscribe")
def subscribe():
    global sse

    # create a new server sent events channel
    sse = ServerSentEvents()            
    return sse.response()

@app.route("/db")
def get_db():
    print("DB")
    print(list(table))
    return jsonify(list(table))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)



