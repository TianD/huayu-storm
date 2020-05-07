# coding=utf8
from __future__ import absolute_import

from LogHelper import LogHelper
from utils.PathAndFileHelper import PathAndFileHelper

# jobInfo.job
JOB_INFO_FORMAT_STRING = """
Name={scene_name}
UserName={submit_user_name}
Frames={frame_range}
MachineName={machine_name}
Plugin=MayaBatch
OutputDirectory0={output_dir}
"""

# plugInfo.job
PLUGIN_INFO_FORMAT_STRING = """
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


class DeadlineHelper(LogHelper):

    def __init__(self, logger=None):
        super(DeadlineHelper, self).__init__(logger)
        self.path_and_file_helper = PathAndFileHelper(logger=logger)
        self.deadline_parameter_dict = {}
        self.__file_base_name = ''
        self.__job_info_file_path = ''
        self.__plugin_info_file_path = ''
        self.__deadline_command_path = ''

    def load_job_info(self, scene_file_path):
        self.__file_base_name = self.path_and_file_helper.get_file_path_md5()
        # todo deadline command exe path , read from yaml-config
        deadline_parameter_dict = {
            'scene_name': self.path_and_file_helper.get_base_name(scene_file_path),
            'scene_file_path': scene_file_path,
            'project_dir': '',  # todo read from yaml-config
            'maya_version': '',  # todo read from yaml-config
            'submit_user_name': 'python_submitter',  # fixed submitter name
            'frame_range': '1-129',  # todo read from maya file
            'machine_name': 'machine',  # todo read with api
            'output_dir': 'z:/',  # todo read from yaml-config
        }
        self.deadline_parameter_dict = deadline_parameter_dict

    def __get_job_info(self):
        job_info_string = JOB_INFO_FORMAT_STRING.format(**self.deadline_parameter_dict)
        return job_info_string

    def __get_plugin_info(self):
        job_info_string = PLUGIN_INFO_FORMAT_STRING.format(**self.deadline_parameter_dict)
        return job_info_string

    def __write_job_and_plugin_file(self):
        # todo get base dir for temp job info files
        self.__job_info_file_path = '{}_jobInfo.txt'.format(self.__file_base_name)
        self.__plugin_info_file_path = '{}_pluginInfo.txt'.format(self.__file_base_name)
        self.path_and_file_helper.write_content_to_file(self.__job_info_file_path, self.__get_job_info())
        self.path_and_file_helper.write_content_to_file(self.__plugin_info_file_path, self.__get_plugin_info())

    def submit_to_deadline(self):
        self.__write_job_and_plugin_file()
        self.path_and_file_helper.run_command(
            '{deadline_command_path} -SubmitMultipleJobs -job {job_info_file_path} {plugin_info_file_path}'.format(
                deadline_command_path=self.__deadline_command_path,
                job_info_file_path=self.__job_info_file_path,
                plugin_info_file_path=self.__plugin_info_file_path
            )
        )
