# coding: utf-8
import os
import subprocess
import sys
import time
import traceback

import socketio
import zmq

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
            view = message.get('view')
            key = message.get('key')

            # clear py3 env
            env = os.environ
            env['PYTHONPATH'] = ''

            result = subprocess.call(cmd, shell=True, env=env)
            sio.connect('http://localhost:8001')
            status = 'Failed' if result else 'Finished'
            time.sleep(5)
            sio.emit('finish_job', {'key': key, 'view': view, 'status': status})
            time.sleep(1)
            sio.disconnect()
        except Exception as e:
            print(traceback.format_exc())
            sys.exit()
