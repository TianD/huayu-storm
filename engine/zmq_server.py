# coding: utf-8
import sys
import time
import traceback
import subprocess
import zmq
import socketio

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind('tcp://127.0.0.1:5555')
sio = socketio.Client(engineio_logger=True)

if __name__ == '__main__':
    while True:
        try:
            message = socket.recv_json()
            print(message)
            cmd = message.get('format_command')
            result = subprocess.call(cmd, shell=True)
            sio.connect('http://localhost:8001')
            sio.emit('finish_job', cmd)
            time.sleep(1)
            sio.disconnect()
        except Exception as e:
            print(traceback.format_exc())
            sys.exit()

