# coding=utf8
from __future__ import absolute_import

import fnmatch
import hashlib
import json
import os
import re
import subprocess

from LogHelper import LogHelper


class PathAndFileHelper(LogHelper):
    def __init__(self, logger=None):
        LogHelper.__init__(self, logger)

    def get_app_dir_root(self):
        return \
            self.join_file_path(
                __file__, '../../../..',
                **{PathAndFileHelper.KEY_IS_GET_ABSOLUTE_PATH: True}
            )

    def get_temp_dir(self):
        return \
            self.join_file_path(
                self.get_app_dir_root(),
                **{PathAndFileHelper.KEY_IS_GET_ABSOLUTE_PATH: True}
            )

    def get_temp_dir_for_maya(self):
        return \
            self.join_file_path(
                self.get_temp_dir(), 'maya_config',
                **{PathAndFileHelper.KEY_IS_GET_ABSOLUTE_PATH: True}
            )

    def get_path_to_slash(self, path_string):
        return path_string.replace('\\', '/')

    def get_path_to_back_slash(self, path_string):
        return path_string.replace('/', '\\')

    get_windows_command_exe_path = get_path_to_back_slash

    def ensure_dir_exists(self, dir_path):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

    def ensure_file_dir_exits(self, file_path):
        file_path_dir = self.get_dir_name(file_path)
        self.ensure_dir_exists(file_path_dir)

    def get_file_path_md5(self, file_path):
        md5_handler = hashlib.md5()
        md5_handler.update(file_path.encode(encoding='utf8'))
        md5_string = md5_handler.hexdigest()
        return md5_string

    def write_content_to_file(self, file_path, content):
        self.ensure_file_dir_exits(file_path)

        with open(file_path, 'w') as f:
            f.write(content)

    def get_dir_name(self, file_path):
        return os.path.dirname(file_path)

    def get_base_name(self, file_path):
        return os.path.basename(file_path)

    def get_file_ext(self, file_path):
        return file_path.split('.')[-1]

    def get_file_content(self, file_path):
        content = ''
        try:
            with open(file_path) as f:
                content = f.read()
        except Exception as e:
            self.error(e)

        return content

    KEY_IS_GET_ABSOLUTE_PATH = 'GET_ABSOLUTE_PATH'

    def join_file_path(self, *args, **kwargs):
        is_get_absolute = kwargs.get(PathAndFileHelper.KEY_IS_GET_ABSOLUTE_PATH, False)
        joined_file_path = os.path.join(*args)
        if is_get_absolute:
            joined_file_path = os.path.abspath(joined_file_path)
        return joined_file_path

    def get_real_path(self, *args):
        return os.path.realpath(*args)

    def delete_file(self, file_path):
        if self.is_file(file_path):
            os.remove(file_path)

    def is_dir(self, path):
        return os.path.isdir(path)

    def is_file(self, path):
        return os.path.isfile(path)

    is_file_existed = is_file

    KEY_CURRENT_IS_FILE = 'KEY_CURRENT_IS_FILE'
    KEY_CURRENT_IS_DIR = 'KEY_CURRENT_IS_DIR'
    KEY_CURRENT_IS_UNKNOWN = 'KEY_CURRENT_IS_UNKNOWN'

    def is_file_or_dir(self, path):
        current_is = PathAndFileHelper.KEY_CURRENT_IS_UNKNOWN
        if self.is_dir(path):
            current_is = PathAndFileHelper.KEY_CURRENT_IS_DIR
        elif self.is_file(path):
            current_is = PathAndFileHelper.KEY_CURRENT_IS_FILE

        return current_is

    def is_same_file(self, file_a, file_b):
        return os.path.realpath(file_a) == os.path.realpath(file_b)

    def is_different_file(self, file_a, file_b):
        return not self.is_same_file(file_a, file_b)

    def list_dir(self, dir_path, file_filter_list=[], only_dir=False, only_file=False):
        return_path_list = []
        if self.is_dir(dir_path):
            all_path_list = os.listdir(dir_path)

            for path in all_path_list:
                __origin_path = path
                path = self.join_file_path(dir_path, path)
                current_path = ''
                if only_dir and self.is_dir(path):
                    current_path = path
                elif only_file and self.is_file(path):
                    current_path = path

                if only_dir == only_file == False:
                    current_path = path

                if current_path:
                    matched = False
                    # filter list enabled
                    if len(file_filter_list) > 0:
                        for file_filter in file_filter_list:
                            matched_list = fnmatch.filter([__origin_path], file_filter)
                            if len(matched_list) > 0:
                                matched = True
                                break
                        if not matched:
                            current_path = ''
                            continue

                if current_path:
                    return_path_list.append(current_path)
        else:
            self.warn('current path is not dir : {}'.format(dir_path))

        return return_path_list

    def run_command(self, command):
        env = os.environ
        env['PYTHONPATH'] = ''
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, env=env)
        print(process.wait())

    def run_command_with_extractor(self, command, extractor_regex_string):

        env = os.environ
        env['PYTHONPATH'] = ''

        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, env=env)

        regex_pattern = re.compile(extractor_regex_string)
        extracted_list = []
        while True:
            current_line = process.stdout.readline()
            if not current_line:
                break
            else:
                extracted_list = regex_pattern.findall(current_line.decode('utf-8'))
                if len(extracted_list) > 0:
                    break
        process.wait()
        return extracted_list

    def read_json_file_to_dict(self, json_file_path, default_value={}):
        try:
            with open(json_file_path, 'r') as f:
                json_file_content = f.read()
        except Exception as e:
            self.debug('read json file : {} , error : {}'.format(json_file_path, e))
            json_file_content = '{}'

        try:
            json_file_dict = json.loads(json_file_content)
        except Exception as e:
            self.debug('read json file : {} , error : {}'.format(json_file_path, e))
            json_file_dict = default_value or {}

        return json_file_dict


if __name__ == '__main__':
    path_and_file_helper = PathAndFileHelper()
    file_path = path_and_file_helper.join_file_path(
        __file__, '../../../../config',
        **{PathAndFileHelper.KEY_IS_GET_ABSOLUTE_PATH: True}
    )
    print(file_path)

    config_file_list = path_and_file_helper.list_dir(
        file_path, ['T*', '*{*'], only_file=True
    )
    print(config_file_list)

    # test write content to file
    path_and_file_helper.write_content_to_file('c:/abc/adf/adf.cxt', '123132\ndfdasf')
    print(
        path_and_file_helper.read_json_file_to_dict('c:/abc.json')
    )
