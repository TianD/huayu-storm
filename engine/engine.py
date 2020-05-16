# coding: utf-8

import glob
import inspect
import io
import json
import os
import re
import sys

__file__ = os.path.abspath(inspect.getsourcefile(lambda: 0))

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

config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')

DEFAULT_IMAGE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public/default.png')

ZMQ_CONTEXT = zmq.Context()
ZMQ_SOCKET = ZMQ_CONTEXT.socket(zmq.PUSH)
ZMQ_SOCKET.connect("tcp://localhost:5555")


def get_frames_list(format_image_path):
    reformat_image_path = re.sub("({[0-9a-zA-Z]*}|%\d+d)", '*', format_image_path)
    files = glob.glob(reformat_image_path)
    collections, _ = clique.assemble(files)
    if collections:
        return collections[0].format('"{head}{padding}{tail} {range}"')


def get_first_image_of_dir(**shot_info):
    thumb_path = _format_template_path('compositing', **shot_info)
    format_thumb_path = fmt.format(thumb_path, **shot_info)
    reformat_thumb_path = re.sub("({[0-9a-zA-Z]*}|%\d+d)", '*', format_thumb_path)
    files = glob.glob(reformat_thumb_path)
    if len(files) == 0:
        files = ['']
    return files[0]


def get_nuke_project(**shot_info):
    format_nuke_path = _format_template_path('nuke', **shot_info)
    reformat_nuke_path = re.sub("({[0-9a-zA-Z]*}|%\d+d)", '*', format_nuke_path)
    files = glob.glob(reformat_nuke_path)
    if len(files) == 0:
        files = ['']
    return os.path.basename(files[0])


def _format_template_path(template_code, **shot_info):
    shot_config = shot_info.get('config')
    template_dir = shot_config.get(template_code, {}).get('dir')
    template_file = shot_config.get(template_code, {}).get('file')
    template_path = '%s/%s' % (template_dir, template_file)
    format_template_path = fmt.format(template_path, **shot_info)
    return format_template_path


@app.route('/api/get_project_list')
def get_project_list():
    project_list = os.listdir(config_dir)
    result = [{'value': project} for project in project_list]
    return json.dumps(result)


@app.route('/api/get_shot_list', methods=['POST'])
def get_shot_list():
    project = json.loads(request.data)
    if not project.get('value'):
        return json.dumps([])
    temp_dict = {}
    project = project.get('value')
    project_config_path = os.path.join(config_dir, project, 'dir_template.yml')
    with open(project_config_path, 'r') as f:
        project_config = yaml.load(f)
    anim = project_config.get('anim') or {}
    anim_dir = anim.get('dir')
    try:
        format_anim_dir = re.sub("{[0-9a-zA-Z_]*}", '*', anim_dir)
    except:
        return json.dumps([])
    dir_list = glob.glob(format_anim_dir)
    for one_dir in dir_list:
        anim_template = Template('anim_dir', anim_dir)
        data = anim_template.parse(one_dir.replace('\\', '/'))
        episode = data.get('episode')
        sequence = data.get('sequence')
        shot = data.get('shot')
        temp_dict.setdefault(episode, dict()). \
            setdefault(sequence, dict()). \
            setdefault(shot, project_config)

    result = []
    pc = {'label': 'All', 'value': 'all'}
    pc_full_qc = []
    for ek, ev in temp_dict.items():
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
                        'project': project,
                        'episode': ek,
                        'sequence': qk,
                        'config': sv,
                        'status': 'Ready',
                        'preview': get_first_image_of_dir(shot=sk,
                                                          project=project,
                                                          episode=ek,
                                                          sequence=qk,
                                                          config=sv),
                        'nuke_project': get_nuke_project(project=project,
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
        result.append({'label': ek, 'value': ek, 'children': ec})
    pc.setdefault('shots', pc_full_qc)
    result.append(pc)
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
            temp_dir = os.path.dirname(temp_str)
            temp_file = os.path.basename(temp_str)
            dataSource.append(
                {'key': str(i), 'type': key, 'path': temp_file, 'dir': temp_dir, 'index': i, 'rowSpan': length})
        for j, remainder in enumerate(remainders):
            temp_dir = os.path.dirname(remainder)
            temp_file = os.path.basename(remainder)
            dataSource.append(
                {'key': str(i), 'type': key, 'path': temp_file, 'dir': temp_dir, 'index': j, 'rowSpan': length})
    return json.dumps(dataSource)


@app.route('/api/nuke_setup_process', methods=['POST'])
def nuke_setup_process():
    shot_info = json.loads(request.data)
    project = shot_info.get('project')
    nuke_config_path = os.path.join(config_dir, project, 'nukebatch/config.yml')
    with open(nuke_config_path, 'r') as f:
        nuke_config = yaml.load(f)
    nuke_exe = nuke_config.get('nuke_exe') or '{nuke_exe}'
    format_nuke_template_path = _format_template_path('nuke_template', **shot_info)
    py_cmd = nuke_config.get('py_cmd') or '{py_cmd}'
    py_cmd = os.path.join(config_dir, project, 'nukebatch', py_cmd)
    nuke_data = nuke_config.get('data') or {}
    nuke_cmd = nuke_config.get('nuke_cmd')
    image_config = shot_info.get('config', {}).get('images')
    image_path = os.path.join(image_config.get('dir'), image_config.get('file')).replace('\\', '/')
    new_nuke_data = {}
    for key, value in nuke_data.items():
        if key.endswith('_layer'):
            format_image_path = fmt.format(image_path, layer=value, **shot_info)
            reformat_image_path = get_frames_list(format_image_path)
            new_nuke_data.setdefault('%s_path' % key, reformat_image_path)
        else:
            new_nuke_data.setdefault(key, value)

    format_nuke_path = _format_template_path('nuke', **shot_info)
    compositing_path = _format_template_path('compositing', **shot_info)
    format_command = fmt.format(nuke_cmd,
                                nuke_exe=nuke_exe,
                                nuke_template=format_nuke_template_path,
                                py_cmd=py_cmd,
                                write_output_path=compositing_path,
                                nuke_save_path=format_nuke_path,
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
    output_file = _format_template_path(output_template_code, **data)
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

    file_path = shot_info.get('name')
    script_path = os.path.join(__file__, '..', r'reference_alpha_v0\maya_ref_replace.py')
    maya_bin = r"C:\Program Files\Autodesk\Maya2017\bin\maya.exe"
    project_name = shot_info.get('project_name', 'DeerRun')

    command = r"""
        import sys
        import os
        import maya.cmds as mc
        mc.file('{file_path}',open=True,force=True,iv=True)
        os.environ['PROJECT_NAME']='{project_name}'
        sys.path.insert(0,os.path.dirname('{script_path}'))
        execfile('{script_path}')
        mc.quit(a=1,f=1,ec=1)
        """.strip().format(
        file_path=file_path, project_name=project_name, script_path=script_path
    ).replace('\\', '/')

    command = ';'.join(
        command_line.strip()
        for command_line in command.splitlines()
    )

    formatted_command = \
        r"""  "{maya_bin}" -command "python(\"{command}\");quit -f;"  """.format(
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
