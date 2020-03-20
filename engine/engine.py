# coding: utf-8

import glob
import io
import json
import os
import re

import yaml
from flask import Flask, send_file, request
from flask_cors import CORS
from gevent import monkey
from gevent.pywsgi import WSGIServer
from werkzeug.debug import DebuggedApplication
from werkzeug.serving import run_with_reloader

from libs.lucidity import Template

monkey.patch_all()

app = Flask(__name__)
CORS(app)

config_yaml_path = 'E:/Project/huayu-storm/config/dir_template.yml'


def get_first_image_of_dir(dir_path, ext='jpg'):
    files = glob.glob('{}/*.jpg'.format(dir_path))
    if len(files) == 0:
        files = ['']
    return files[0]


@app.route('/api/get_project_list')
def get_project_list():
    config = dict()
    with open(config_yaml_path, 'r') as f:
        config = yaml.load(f)
    temp_dict = {}
    for project, project_config in config.items():
        compositing = project_config.get('compositing')
        comp_dir = re.sub('{[0-9a-zA-Z]*}', '*', compositing)
        dir_list = glob.glob(comp_dir)
        for one_dir in dir_list:
            comp_template = Template('comp_dir', compositing)
            data = comp_template.parse(one_dir.replace('\\', '/'))
            episode = data.get('episode')
            sequence = data.get('sequence')
            shot = data.get('shot')
            temp_dict.setdefault(project, dict()).setdefault(episode, dict()).setdefault(sequence, dict()).setdefault(
                shot, one_dir)
    result = []
    for pk, pv in temp_dict.items():
        pc = [{'label': 'All', 'value': 'all'}]
        pc_full_qc = []
        for ek, ev in pv.items():
            ec = [{'label': 'All', 'value': 'all'}]
            ec_full_qc = []
            for qk, qv in ev.items():
                qc = []
                for sk, sv in qv.items():
                    qc.append(
                        {
                            'label': '%s_%s_%s' % (ek, qk, sk), 'value': sk,
                            'dir': sv, 'preview': get_first_image_of_dir(sv)
                        }
                    )
                ec_full_qc.extend(qc)
                ec.append({'label': qk, 'value': qk, 'shots': qc})
            pc_full_qc.extend(ec_full_qc)
            ec[0].setdefault('shots', ec_full_qc)
            pc.append({'label': ek, 'value': ek, 'children': ec})
        pc[0].setdefault('shots', pc_full_qc)
        result.append({'label': pk, 'value': pk, 'children': pc})
    return json.dumps(result)


DEFAULT_IMAGE = 'E:/huayu-storm/TTT/compositing/EP01/Q01/S01/ttt_EP01_Q01_S01_cp_c001.1001.jpg'


@app.route('/api/get_thumbnail', methods=['get'])
def get_thumbnail():
    request_json = request.args
    file_path = request_json.get('preview') or DEFAULT_IMAGE
    print(request_json)

    file_ext = file_path.split('.')[-1]
    file_base_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        content = f.read()
    return send_file(
        io.BytesIO(content),
        attachment_filename=file_base_name, mimetype='image/{}'.format(file_ext)
    )


if __name__ == '__main__':
    @run_with_reloader
    def run_server():
        http_server = WSGIServer(('0.0.0.0', 5000), DebuggedApplication(app))
        http_server.serve_forever()


    run_server()
