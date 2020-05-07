# coding=utf8
from __future__ import absolute_import

import os

scene_file_path = ''

deadline_parameter_dict = {
    'scene_name': os.path.basename(scene_file_path),
    'scene_file_path': scene_file_path,
    'project_dir': '',  # todo read from yaml-config
    'maya_version': '',  # todo read from yaml-config
    'submit_user_name': 'python_submitter',  # fixed submitter name
    'frame_range': '1-129',  # todo read from maya file
    'machine_name': 'machine',  # todo read with api
    'output_dir': 'z:/',  # todo read from yaml-config
}

# jobInfo.job
job_info_format_string = """
Name={scene_name}
UserName={submit_user_name}
Frames={frame_range}
MachineName={machine_name}
Plugin=MayaBatch
OutputDirectory0={output_dir}
"""

job_info_string = job_info_format_string.format(**deadline_parameter_dict)

# plugInfo.job
plugin_info_format_string = """
SceneFile={scene_file_path}
Version={maya_version}
Build=64bit
ProjectPath={project_dir}
StrictErrorChecking=True
LocalRendering=False
MaxProcessors=0
FrameNumberOffset=0
OutputFilePath={output_dir}
Renderer=File
StartupScript=
CommandLineOptions=
UseOnlyCommandLineOptions=0
IgnoreError211=False
"""

plugin_info_string = plugin_info_format_string.format(**deadline_parameter_dict)

# todo write file
#   calc file_path as md5 , use md5 as file name 
#   submit command
#       deadlinecommand -SubmitMultipleJobs -job %e_jobInfo.txt %e_plugInfo.txt
