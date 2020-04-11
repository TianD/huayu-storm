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

    def get_file_content(self, file_path):
        content = ''
        try:
            with open(file_path) as f:
                content = f.read()
        except Exception as e:
            self.error(e)

        return content

    def join_file_path(self, *args):
        return os.path.join(args)
