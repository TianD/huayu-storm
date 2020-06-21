# coding: utf-8
import os
import subprocess
import sys
import time
import traceback

import socketio
import zmq

sys.path.insert(0, './reference_alpha_v0')
from LogHelper import app_logger

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind('tcp://127.0.0.1:5555')
sio = socketio.Client(engineio_logger=True)

if __name__ == '__main__':

    while True:
        try:
            message = socket.recv_json()
            if not message:
                continue
            # app_logger.debug(message)
            cmd = message.get('format_command')
            view = message.get('view')
            key = message.get('key')
            time.sleep(5)

            # clear py3 env
            env = os.environ
            env['PYTHONPATH'] = ''

            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, env=env)
            app_logger.debug(result)
            sio.connect('http://localhost:8001')
            status = 'Failed' if result else 'Finished'
            status = 'Finished'
            app_logger.debug(status)
            sio.emit('finish_job', {'key': key, 'view': view, 'status': status})
            app_logger.debug('Has finished.')
            time.sleep(1)
            sio.disconnect()
        except Exception as e:
            status = 'Failed'
            app_logger.debug(result)
            app_logger.debug(traceback.format_exc())
            sio.emit('finish_job', {'key': key, 'view': view, 'status': status})
            time.sleep(1)
            sio.disconnect()
            # sys.exit()

