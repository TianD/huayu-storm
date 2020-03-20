# coding: utf-8

import re
import glob
import yaml
import json
from flask import Flask
from flask_cors import CORS
from libs.lucidity import Template

app = Flask(__name__)
CORS(app)

config_yaml_path = 'E:/Project/huayu-storm/config/dir_template.yml'


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
            temp_dict.setdefault(project, dict()).setdefault(episode, dict()).setdefault(sequence, dict()).setdefault(shot, one_dir)
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
                    qc.append({'label': '%s_%s_%s' % (ek, qk, sk), 'value': sk, 'dir': sv})
                ec_full_qc.extend(qc)
                ec.append({'label': qk, 'value': qk, 'shots': qc})
            pc_full_qc.extend(ec_full_qc)
            ec[0].setdefault('shots', ec_full_qc)
            pc.append({'label': ek, 'value': ek, 'children': ec})
        pc[0].setdefault('shots', pc_full_qc)
        result.append({'label': pk, 'value': pk, 'children': pc})
    return json.dumps(result)


@app.route('/api/get_thumbnail', methods=['POST'])
def get_thumbnail():
    return 'E:/huayu-storm/TTT/compositing/EP01/Q01/S01/ttt_EP01_Q01_S01_cp_c001.1001.jpg'




if __name__ == '__main__':
    app.run()
