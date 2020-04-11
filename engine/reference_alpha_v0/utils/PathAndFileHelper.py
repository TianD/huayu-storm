# coding=utf8
from __future__ import absolute_import

import fnmatch
import os

from LogHelper import LogHelper


class PathAndFileHelper(LogHelper):
    def __init__(self, logger=None):
        LogHelper.__init__(self, logger)

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

    def is_dir(self, path):
        return os.path.isdir(path)

    def is_file(self, path):
        return os.path.isfile(path)

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
