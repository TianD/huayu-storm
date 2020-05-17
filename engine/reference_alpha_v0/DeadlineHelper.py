# coding=utf8
from __future__ import absolute_import

import re
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

    NAME_SPLITTER = '_'

    def get_episode_sequence_shot_from_filename(self, file_regex, scene_file_path):
        scene_file_name = self.path_and_file_helper.get_base_name(scene_file_path)

        name_item_list = scene_file_name.split(DeadlineHelper.NAME_SPLITTER)

        episode = None
        sequence = None
        shot = None

        self.debug('[ name_item_list ]', name_item_list)
        if len(name_item_list) >= 3:
            scene_info_match_list = \
                re.findall(file_regex, scene_file_name, re.I)
            self.debug(scene_info_match_list)

            if scene_info_match_list:
                valid_match_list = scene_info_match_list[0]
            else:
                valid_match_list = []
            if len(valid_match_list) >= 3:
                episode = valid_match_list[0]
                sequence = valid_match_list[1]
                shot = valid_match_list[2]
            else:
                self.error('no enough match item for episode_scene_shot')
        else:
            self.error('no enough match item for episode_scene_shot')

        return episode, sequence, shot

    def load_submit_parameter(self, project_name, scene_file_path_of_origin, scene_file_path):
        all_config = self.config_helper.get_all_config()

        current_project_config_dict = all_config.get(project_name, {})
        layer_config = list(current_project_config_dict.values())[0]

        episode_scene_shot_regex = \
            self.config_helper.get_json_value_with_key_path(
                'common_setting.episode_scene_shot_regex', '', layer_config
            )

        episode, sequence, shot = \
            self.get_episode_sequence_shot_from_filename(episode_scene_shot_regex, scene_file_path_of_origin)

        format_dict = {
            'project_file_name': self.path_and_file_helper.get_path_to_slash(scene_file_path_of_origin),
            'episode': episode or 1,
            'sequence': sequence or 1,
            'shot': shot or 1,
        }

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

        maya_file_info_file_path = self.config_helper.get_value_with_exec(
            self.config_helper.format_json_with_format_dict(maya_file_info_file_path, format_dict)
        )

        # read file as config
        maya_file_info = self.path_and_file_helper.read_json_file_to_dict(maya_file_info_file_path, {})
        maya_frame_range = '{frame_start}-{frame_end}'.format(
            frame_start=maya_file_info.get('frame_start', 1),
            frame_end=maya_file_info.get('frame_end', 2)
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
        r"F:\project\EP129_Q001_S001_BGCLR.mb",
        r"F:\project\EP129_Q001_S001_BGCLR.mb"
    )
    print(deadline_helper.deadline_parameter_dict)
    deadline_helper.submit_to_deadline()
