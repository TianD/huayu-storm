# coding=utf8
from __future__ import absolute_import

deadline_parameter_dict = {
    'scene_name': '',
    'scene_file_path': '',
    'project_dir': '',
    'maya_version': '',  # 2017
    'submit_user_name': 'python_submitter',
    'frame_range': '1-129',
    'machine_name': 'machine',
    'output_dir': 'z:/',
}

# jobInfo.job
job_info_string = """
Name={scene_name}
UserName={submit_user_name}
Frames={frame_range}
MachineName={machine_name}
Plugin=MayaBatch
OutputDirectory0={output_dir}
""".format(**deadline_parameter_dict)

# plugInfo.job
plugin_info_string = """
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
""".format(**deadline_parameter_dict)
