# coding=utf8
from __future__ import absolute_import

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


if __name__ == '__main__':
    path_and_file_helper = PathAndFileHelper()
    file_path = path_and_file_helper.join_file_path(
        __file__, '../../../../',
        **{PathAndFileHelper.KEY_IS_GET_ABSOLUTE_PATH: True}
    )
    print(file_path)
