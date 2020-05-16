# coding=utf8
from __future__ import absolute_import

import socket

from LogHelper import LogHelper
from utils.ConfigHelper import ConfigHelper

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
        self.config_helper = ConfigHelper(logger=logger)
        self.path_and_file_helper = self.config_helper.path_and_file_helper

        self.DEADLINE_SCRIPT_TEMP_DIR = \
            self.path_and_file_helper.join_file_path(
                __file__, '../../../cache_dir', 'deadline'
            )
        self.DEADLINE_SCRIPT_TEMP_DIR = self.path_and_file_helper.get_real_path(self.DEADLINE_SCRIPT_TEMP_DIR)

        self.deadline_parameter_dict = {}
        self.__file_base_name = ''
        self.__job_info_file_path = ''
        self.__plugin_info_file_path = ''
        self.__deadline_command_bin_path = ''
        self.__maya_bin_path = ''
        self.__maya_batch_bin_path = ''

    def load_submit_parameter(self, project_name, scene_file_path):
        all_config = self.config_helper.get_all_config()
        current_project_config_dict = all_config.get(project_name, {})
        layer_config = list(current_project_config_dict.values())[0]

        deadline_command_bin_path = \
            self.config_helper.get_json_value_with_key_path(
                'common_setting.deadline_command_bin_path', '', layer_config
            )
        project_dir = \
            self.config_helper.get_json_value_with_key_path(
                'common_setting.project_dir', '', layer_config
            )
        maya_version = \
            self.config_helper.get_json_value_with_key_path(
                'common_setting.maya_version', '', layer_config
            )
        output_dir = \
            self.config_helper.get_json_value_with_key_path(
                'common_setting.output_dir', '', layer_config
            )

        maya_bin_path = \
            self.config_helper.get_json_value_with_key_path(
                'common_setting.maya_bin_path', '', layer_config
            )

        maya_file_info_file_path = \
            self.config_helper.get_json_value_with_key_path(
                'common_setting.maya_file_info_file_path', '', layer_config
            )

        maya_batch_bin_path = \
            self.config_helper.get_json_value_with_key_path(
                'common_setting.maya_batch_bin_path', '', layer_config
            )

        # read file as config
        maya_file_info = self.path_and_file_helper.read_json_file_to_dict(maya_file_info_file_path, {})
        maya_frame_range = '{frame_start}-{frame_end}'.format(
            maya_file_info.get('frame_start', 1),
            maya_file_info.get('frame_end', 2)
        )

        self.__deadline_command_bin_path = deadline_command_bin_path
        self.__maya_bin_path = maya_bin_path
        self.__maya_batch_bin_path = maya_batch_bin_path

        self.__file_base_name = self.path_and_file_helper.get_file_path_md5(scene_file_path)
        deadline_parameter_dict = {
            'scene_name': self.path_and_file_helper.get_base_name(scene_file_path),
            'scene_file_path': scene_file_path,
            'project_dir': project_dir,
            'maya_version': maya_version,
            'submit_user_name': 'python_submitter',  # fixed submitter name
            'frame_range': maya_frame_range,
            'machine_name': socket.gethostname(),
            'output_dir': output_dir,
        }
        self.deadline_parameter_dict = deadline_parameter_dict

    def __get_maya_frame_start_and_end(self, scene_file_path):
        command = r"""
            import sys
            import os
            import maya.cmds as mc
            mc.file('{file_path}',open=True,force=True,iv=True)
            frame_start = mc.playbackOptions(q=True,animationStartTime=True)
            frame_end = mc.playbackOptions(q=True,animationEndTime=True)
            frame_start = int(frame_start)
            frame_end = int(frame_end)
            print('[config] {{}} {{}} [config]'.format(frame_start,frame_end))
            mc.quit(a=1,f=1,ec=1)
        """.strip().format(
            file_path=self.path_and_file_helper.get_path_to_slash(scene_file_path),
        ).replace('\\', '/')

        command = ';'.join(
            command_line.strip()
            for command_line in command.splitlines()
        )

        formatted_command = \
            r"""  "{maya_bin}" -command "python(\"{command}\");"  """.format(
                maya_bin=self.path_and_file_helper.get_windows_command_exe_path(self.__maya_batch_bin_path),
                command=command,
            ).strip()

        # frame_start_end_list = self.path_and_file_helper.run_command_with_extractor(
        #     formatted_command,
        #     r'\[config\]\s+(\d+)\s(\d+)\s+\[config\]'
        # )

        frame_start_end_list = [[1, 200]]

        frame_start = 0
        frame_end = 0
        try:
            frame_start, frame_end = frame_start_end_list[0]
        except Exception as e:
            self.error('get frame start / end from command falied', e)

        return '{}-{}'.format(frame_start, frame_end)

    def __get_job_info(self):
        job_info_string = JOB_INFO_FORMAT_STRING.format(**self.deadline_parameter_dict)
        return job_info_string

    def __get_plugin_info(self):
        job_info_string = PLUGIN_INFO_FORMAT_STRING.format(**self.deadline_parameter_dict)
        return job_info_string

    def __write_job_and_plugin_file(self):
        self.__job_info_file_path_base_name = '{}_jobInfo.txt'.format(self.__file_base_name)
        self.__plugin_info_file_path_base_name = '{}_pluginInfo.txt'.format(self.__file_base_name)

        # add dir to temp file
        self.__job_info_file_path = self.path_and_file_helper.join_file_path(
            self.DEADLINE_SCRIPT_TEMP_DIR, self.__job_info_file_path_base_name,
        )
        self.__plugin_info_file_path = self.path_and_file_helper.join_file_path(
            self.DEADLINE_SCRIPT_TEMP_DIR, self.__plugin_info_file_path_base_name,
        )

        self.path_and_file_helper.write_content_to_file(self.__job_info_file_path, self.__get_job_info())
        self.path_and_file_helper.write_content_to_file(self.__plugin_info_file_path, self.__get_plugin_info())

    def submit_to_deadline(self):
        self.__write_job_and_plugin_file()
        # todo add run_command to helper
        self.path_and_file_helper.run_command(
            '"{deadline_command_path}" -SubmitMultipleJobs -job {job_info_file_path} {plugin_info_file_path}'.format(
                deadline_command_path=
                self.path_and_file_helper.get_windows_command_exe_path(self.__deadline_command_bin_path),
                job_info_file_path=self.__job_info_file_path,
                plugin_info_file_path=self.__plugin_info_file_path
            )
        )
        # clear file
        self.path_and_file_helper.delete_file(
            self.__job_info_file_path
        )

        self.path_and_file_helper.delete_file(
            self.__plugin_info_file_path
        )


if __name__ == '__main__':
    deadline_helper = DeadlineHelper()
    deadline_helper.load_submit_parameter(
        'DeerRun',
        r"F:\project\EP129_Q001_S001_BGCLR.mb"
    )
    print(deadline_helper.deadline_parameter_dict)
    deadline_helper.submit_to_deadline()
