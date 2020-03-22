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
import subprocess

from libs import utils
from libs.lucidity import Template
from libs.AdvFormatter import AdvFormatter
from libs import clique


fmt = AdvFormatter()
monkey.patch_all()

app = Flask(__name__)
CORS(app)

config_yaml_path = 'E:/Project/huayu-storm/config/dir_template.yml'


def get_preview_cache_path(origin_image_path):
    NEW_FORMAT_EXT = 'jpg'

    converter_bin = utils.get_sibling_file_path(__file__,'../bin/ffmpeg.exe')
    preview_width = 640
    preview_path =  utils.get_file_new_ext_path(origin_image_path,NEW_FORMAT_EXT)
    utils.ensure_file_dir_exists(preview_path)

    command_arg_dict = {
        'ffmpeg_bin':utils.get_file_native_abs_path(converter_bin),
        'origin_image_path':utils.get_file_native_abs_path(origin_image_path),
        'preview_width':preview_width,
        'preview_path':utils.get_file_native_abs_path(preview_path),
    }
    CONVERT_COMMAND = \
        '{ffmpeg_bin} -i "{origin_image_path}" -vs scale={preview_width}:-1 {preview_path}'.format(**command_arg_dict)
    child = subprocess.Popen('ping -c4 blog.linuxeye.com',shell=True)
    child.wait()
    return preview_path


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
    config = dict()
    with open(config_yaml_path, 'r') as f:
        config = yaml.load(f)
    temp_dict = {}
    for project, project_config in config.items():
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


DEFAULT_IMAGE = 'E:/huayu-storm/TTT/compositing/EP01/Q01/S01/ttt_EP01_Q01_S01_cp_c001.1001.jpg'


@app.route('/api/get_thumbnail')
def get_thumbnail():
    request_json = request.args
    file_path = request_json.get('preview') or DEFAULT_IMAGE
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
        temp_data = []
        for collection in collections:
            temp_str = collection.format()
            temp_str = temp_str.replace('\\', '/').split(key_dir)[-1][1:]
            temp_data.append(temp_str)
        for remainder in remainders:
            remainder = remainder.replace('\\', '/').split(key_dir)[-1][1:]
            temp_data.append(remainder)
        dataSource.append({'key': str(i), 'type': key, 'path': temp_data})
    return json.dumps(dataSource)


if __name__ == '__main__':
    @run_with_reloader
    def run_server():
        http_server = WSGIServer(('0.0.0.0', 5000), DebuggedApplication(app))
        http_server.serve_forever()


    run_server()
