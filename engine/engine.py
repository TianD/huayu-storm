# coding: utf-8

import glob
import io
import json
import os
import re
import sys

import yaml
import zmq
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


def get_nuke_project(**shot_info):
    shot_config = shot_info.get('config')
    nuke_dir = shot_config.get('nuke', {}).get('dir')
    nuke_file = shot_config.get('nuke', {}).get('file')
    nuke_path = '%s/%s' % (nuke_dir, nuke_file)
    format_nuke_path = fmt.format(nuke_path, **shot_info)
    format_nuke_path = re.sub("({[0-9a-zA-Z]*}|%\d+d)", '*', format_nuke_path)
    files = glob.glob(format_nuke_path)
    if len(files) == 0:
        files = ['']
    return os.path.basename(files[0])


@app.route('/api/get_project_list')
def get_project_list():
    temp_dict = {}
    for project in os.listdir(config_dir):
        project_config_path = os.path.join(config_dir, project, 'dir_template.yml')
        with open(project_config_path, 'r') as f:
            project_config = yaml.load(f)
        anim = project_config.get('anim') or {}
        anim_dir = anim.get('dir')
        try:
            format_anim_dir = re.sub("{[0-9a-zA-Z_]*}", '*', anim_dir)
        except:
            continue
        dir_list = glob.glob(format_anim_dir)
        for one_dir in dir_list:
            anim_template = Template('anim_dir', anim_dir)
            data = anim_template.parse(one_dir.replace('\\', '/'))
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
                                                              config=sv),
                            'nuke_project': get_nuke_project(project=pk,
                                                             episode=ek,
                                                             sequence=qk,
                                                             shot=sk,
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
    file_info = json.loads(request.data)
    project = file_info.get('project')
    seq2mov_config_path = os.path.join(config_dir, project, 'seq2mov.yml')
    dir_config_path = os.path.join(config_dir, project, 'dir_template.yml')
    with open(dir_config_path, 'r') as f:
        dir_config = yaml.load(f)
    with open(seq2mov_config_path, 'r') as f:
        seq2mov_config = yaml.load(f)
    ffmpeg_exe = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bin/ffmpeg.exe')
    ffmpeg_exe = ffmpeg_exe.replace('\\', '/')
    cmd = seq2mov_config.get('ffmpeg_cmd')
    input_file = file_info.get('name').replace('\\', '/')
    input_template_code = seq2mov_config.get('input_file_template')
    output_template_code = seq2mov_config.get('output_file_template')
    input_template_path = '%s/%s' % (dir_config.get(input_template_code, {}).get('dir'),
                                     dir_config.get(input_template_code, {}).get('file'))
    input_template = Template(input_template_code, input_template_path)
    data = input_template.parse(input_file)
    output_template_path = '%s/%s' % (dir_config.get(output_template_code, {}).get('dir'),
                                      dir_config.get(output_template_code, {}).get('file'))
    output_file = fmt.format(output_template_path, **data)
    format_command = fmt.format(cmd, ffmpeg_exe=ffmpeg_exe, input_file=input_file, output_file=output_file)
    ZMQ_SOCKET.send_json({'format_command': format_command, 'key': file_info.get('key'), 'view': 'seq2movbatch'})
    return json.dumps({'status': 'Queued'})


@app.route('/api/maya_layer_process', methods=['POST'])
def maya_layer_process():
    """
    shot_info = {
        u'status': u'Ready',
        u'id': 1,
        u'key': 0,
        u'name': u'E:\\codeLib\\___test___\\my_proj\\huayu_project\\huayu-storm\\src\\components\\Overview.js'
    }
    """
    shot_info = json.loads(request.data)
    # project = shot_info.get('project')
    # maya_config_path = os.path.join(config_dir, project, 'mayabatch/config.yml')
    # with open(maya_config_path, 'r') as f:
    #     maya_config = yaml.load(f)
    # maya_exe = maya_config.get('maya_exe') or '{maya_exe}'
    # maya_template = maya_config.get('maya_template') or '{maya_template}'
    # py_cmd = maya_config.get('py_cmd') or '{py_cmd}'
    # maya_data = maya_config.get('data') or {}
    # maya_cmd = maya_config.get('maya_cmd')
    # image_config = shot_info.get('config', {}).get('images')
    # image_path = os.path.join(image_config.get('dir'), image_config.get('file')).replace('\\', '/')
    # new_maya_data = {}
    # for key, value in maya_data.items():
    #     if key.endswith('_layer'):
    #         format_image_path = fmt.format(image_path, layer=value, **shot_info)
    #         new_maya_data.setdefault('%s_path' % key, format_image_path)
    #     else:
    #         new_maya_data.setdefault(key, value)

    # format_command = fmt.format(maya_cmd,
    #                             maya_exe=maya_exe,
    #                             maya_template=maya_template,
    #                             py_cmd=py_cmd,
    #                             **new_maya_data)

    file_path = shot_info.get(
        'name', r'E:\codeLib\___test___\my_proj\py_scripts\pipeline_code\DR_EP129_Q001_S001_an_c003.mb'
    )
    script_path = r'E:\codeLib\___test___\my_proj\huayu_project\huayu-storm\engine\reference_alpha_v0'
    maya_bin = r"C:\Program Files\Autodesk\Maya2017\bin\maya.exe"

    command = r"""
        import maya.cmds as mc
        mc.file('{file_path}',open=True,force=True,iv=True)
        import sys
        import os
        sys.path.insert(0,os.path.dirname('{script_path}'))
        execfile('{script_path}')
        """.strip().format(file_path=file_path, script_path=script_path).replace('\\', '/')

    command = ';'.join(
        command_line.strip()
        for command_line in command.splitlines()
    )

    formatted_command = \
        r"""  "{maya_bin}" -command "python(\"{command}\")  """.format(
            maya_bin=maya_bin.replace('/', '\\'),
            command=command,
        ).strip()

    print(formatted_command)

    ZMQ_SOCKET.send_json(
        {
            'format_command': formatted_command, 'key': shot_info.get('key'), 'view': 'mayabatch'
        }
    )
    return json.dumps({'status': 'Queued'})


@app.route('/api/file_collections', methods=['POST'])
def get_file_collections():
    dir_list = json.loads(request.data)
    result = []
    for d in dir_list:
        collections, remainders = clique.assemble(os.listdir(d))
        for collection in collections:
            collection.padding = len(str(list(collection.indexes)[-1]))
            temp = os.path.join(d, collection.format('{head}{padding}{tail}'))
            result.append(temp)
    return json.dumps(result)


if __name__ == '__main__':
    @run_with_reloader
    def run_server():
        http_server = WSGIServer(('0.0.0.0', 5000), DebuggedApplication(app))
        http_server.serve_forever()


    run_server()
