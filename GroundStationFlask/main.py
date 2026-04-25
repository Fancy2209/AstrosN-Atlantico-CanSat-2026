from threading import Thread
from tinydb import TinyDB
from tinyrecord import transaction
from flask import Flask, jsonify
from flask_queue_sse import ServerSentEvents
from flask_cors import CORS
import serial
import traceback

# PYTHONBUFFERED=TRUE /home/ana/.local/bin/gunicorn main:app --worker-class gevent --bind 192.168.8.195:8080 --enable-stdio-inheritance --log-level "debug"

db = TinyDB('db.json')
table = db.table('CanSat')
uart = serial.Serial('/dev/serial0', 9600)

def serial_reader():
    while True:
        try:
            line = uart.readline()
            if len(line) > 0:
                print(line)
                print(line[:1])
                if line.startswith(b'0') or line.startswith(b'1'):
                    line = line.decode()
                    print(line)

                    # I did an oopsie daisy on the groundstation
                    parts = line.split(", ")

                    with transaction(table) as tr:
                        if len(parts) == 6:
                            ret = {
                                'packetKind': parts[0],
                                'time': parts[1],
                                'temp': parts[2],
                                'press': parts[3],
                                'humidity': parts[4],
                                'rssi': parts[5]
                            }
                            if sse:
                                sse.send(ret)
                            tr.insert(ret)
                        else:
                            ret = {
                                'packetKind': parts[0],
                                'time': parts[1],
                                'temp': parts[2],
                                'press': parts[3],
                                'humidity': parts[4],
                                'stabilityClassifier': parts[5],
                                'linAccX': parts[6],
                                'linAccY': parts[7],
                                'linAccZ': parts[8],
                                'qR': parts[9],
                                'qY': parts[10],
                                'qJ': parts[11],
                                'qK': parts[12],
                                'rssi': parts[13],
                            }
                            if sse:
                                sse.send(ret)
                            tr.insert(ret)
        except Exception as e:
            traceback.print_exc()

try:
    thr = Thread(target=serial_reader, daemon=True)
    thr.start()
except:
    thr = Thread(target=serial_reader, daemon=False)
    thr.start()


app = Flask(__name__)
sse: ServerSentEvents = None
CORS(app)

@app.route("/subscribe")
def subscribe():
    global sse

    # create a new server sent events channel
    sse = ServerSentEvents()

    return sse.response()

@app.route("/db")
def get_db():
    print("DB")
    with 
    print(list(table))
    return jsonify(list(table))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)



