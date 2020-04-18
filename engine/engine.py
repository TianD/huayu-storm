# coding: utf-8

import glob
import io
import json
import os
import re
import sys

import zmq
import yaml
from flask import Flask, send_file, request
from flask_cors import CORS
from gevent import monkey
from gevent.pywsgi import WSGIServer
from werkzeug.debug import DebuggedApplication
from werkzeug.serving import run_with_reloader

sys.path.insert(0, './libs')

from libs import clique
from libs import utils
from libs.AdvFormatter import AdvFormatter
from libs.lucidity import Template

fmt = AdvFormatter()
monkey.patch_all()

app = Flask(__name__)
CORS(app)

config_dir = os.path.join(os.path.dirname(__file__), '../config')

DEFAULT_IMAGE = os.path.join(os.path.dirname(__file__), '../public/default.png')

ZMQ_CONTEXT = zmq.Context()
ZMQ_SOCKET = ZMQ_CONTEXT.socket(zmq.PUSH)
ZMQ_SOCKET.connect("tcp://localhost:5555")


def get_first_image_of_dir(**shot_info):
    shot_config = shot_info.pop('config')
    thumb_dir = shot_config.get('compositing', {}).get('dir')
    thumb_file = shot_config.get('compositing', {}).get('file')
    thumb_path = '%s/%s' % (thumb_dir, thumb_file)

    format_thumb_path = fmt.format(thumb_path, **shot_info)
    format_thumb_path = re.sub("({[0-9a-zA-Z]*}|%\d+d)", '*', format_thumb_path)
    files = glob.glob(format_thumb_path)
    if len(files) == 0:
        files = ['']
    return files[0]


@app.route('/api/get_project_list')
def get_project_list():
    temp_dict = {}
    for project in os.listdir(config_dir):
        project_config_path = os.path.join(config_dir, project, 'dir_template.yml')
        with open(project_config_path, 'r') as f:
            project_config = yaml.load(f)
        compositing = project_config.get('compositing') or {}
        comp_dir = compositing.get('dir')
        format_comp_dir = re.sub("{[0-9a-zA-Z]*}", '*', comp_dir)
        dir_list = glob.glob(format_comp_dir)
        for one_dir in dir_list:
            comp_template = Template('comp_dir', comp_dir)
            data = comp_template.parse(one_dir.replace('\\', '/'))
            episode = data.get('episode')
            sequence = data.get('sequence')
            shot = data.get('shot')
            temp_dict.setdefault(project, dict()). \
                setdefault(episode, dict()). \
                setdefault(sequence, dict()). \
                setdefault(shot, project_config)

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
                            'label': '%s_%s_%s' % (ek, qk, sk),
                            'key': '%s_%s_%s' % (ek, qk, sk),
                            'shot': sk,
                            'project': pk,
                            'episode': ek,
                            'sequence': qk,
                            'config': sv,
                            'status': 'Ready',
                            'preview': get_first_image_of_dir(shot=sk,
                                                              project=pk,
                                                              episode=ek,
                                                              sequence=qk,
                                                              config=sv)
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


@app.route('/api/get_thumbnail')
def get_thumbnail():
    request_json = request.args
    file_path = request_json.get('preview') or DEFAULT_IMAGE
    # get file preview path
    file_path = utils.get_preview_cache_path(file_path)

    file_ext = file_path.split('.')[-1]
    file_base_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        content = f.read()
    return send_file(
        io.BytesIO(content),
        attachment_filename=file_base_name, mimetype='image/{}'.format(file_ext)
    )


@app.route('/api/get_detail', methods=['POST'])
def get_detail():
    request_data = json.loads(request.data)
    shot_config = request_data.get('config') or {}
    dataSource = []
    i = 0
    for key, value in shot_config.items():
        i += 1
        dir_template = value.get('dir')
        file_template = value.get('file')
        path_template = '%s/%s' % (dir_template, file_template)
        key_path = fmt.format(path_template, **request_data)
        key_dir = fmt.format(dir_template, **request_data)
        format_key_path = re.sub("({[0-9a-zA-Z]*}|%\d+d)", '*', key_path)
        files = glob.glob(format_key_path)
        collections, remainders = clique.assemble(files)
        length = len(collections) + len(remainders)
        for i, collection in enumerate(collections):
            temp_str = collection.format()
            temp_str = temp_str.replace('\\', '/').split(key_dir)[-1][1:]
            dataSource.append(
                {'key': str(i), 'type': key, 'path': temp_str, 'dir': key_dir, 'index': i, 'rowSpan': length})
        for j, remainder in enumerate(remainders):
            remainder = remainder.replace('\\', '/').split(key_dir)[-1][1:]
            dataSource.append(
                {'key': str(i), 'type': key, 'path': remainder, 'dir': key_dir, 'index': j, 'rowSpan': length})
    return json.dumps(dataSource)


@app.route('/api/nuke_setup_process', methods=['POST'])
def nuke_setup_process():
    shot_info = json.loads(request.data)
    project = shot_info.get('project')
    nuke_config_path = os.path.join(config_dir, project, 'nukebatch/config.yml')
    with open(nuke_config_path, 'r') as f:
        nuke_config = yaml.load(f)
    nuke_exe = nuke_config.get('nuke_exe') or '{nuke_exe}'
    nuke_template = nuke_config.get('nuke_template') or '{nuke_template}'
    py_cmd = nuke_config.get('py_cmd') or '{py_cmd}'
    nuke_data = nuke_config.get('data') or {}
    nuke_cmd = nuke_config.get('nuke_cmd')
    image_config = shot_info.get('config', {}).get('images')
    image_path = os.path.join(image_config.get('dir'), image_config.get('file')).replace('\\', '/')
    new_nuke_data = {}
    for key, value in nuke_data.items():
        if key.endswith('_layer'):
            format_image_path = fmt.format(image_path, layer=value, **shot_info)
            new_nuke_data.setdefault('%s_path' % key, format_image_path)
        else:
            new_nuke_data.setdefault(key, value)

    format_command = fmt.format(nuke_cmd,
                                nuke_exe=nuke_exe,
                                nuke_template=nuke_template,
                                py_cmd=py_cmd,
                                **new_nuke_data)
    ZMQ_SOCKET.send_json({'format_command': format_command, 'key': shot_info.get('key'), 'view': 'nukebatch'})
    return json.dumps({'status': 'Queued'})


@app.route('/api/seq2mov_process', methods=['POST'])
def seq2mov_process():
    return json.dumps({'status': 'Queued'})


@app.route('/api/maya_layer_process', methods=['POST'])
def maya_layer_process():
    return json.dumps({'status': 'Queued'})


if __name__ == '__main__':
    @run_with_reloader
    def run_server():
        http_server = WSGIServer(('0.0.0.0', 5000), DebuggedApplication(app))
        http_server.serve_forever()

    run_server()
