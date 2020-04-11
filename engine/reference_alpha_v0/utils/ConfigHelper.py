# coding=utf8
from __future__ import absolute_import
from __future__ import print_function

import yaml

from LogHelper import LogHelper
from utils.PathAndFileHelper import PathAndFileHelper


class YamlHelper(LogHelper):
    def __init__(self, logger=None):
        super(YamlHelper, self).__init__(logger=logger)
        self.path_and_file_helper = PathAndFileHelper(logger)

    def load_yaml_file_to_json(self, yaml_file_path):
        yaml_file_content = self.path_and_file_helper.get_file_content(yaml_file_path)

        data = {}
        try:
            data = yaml.load(yaml_file_content)
        except Exception as e:
            self.error(e)

        return data


class ConfigHelper(LogHelper):
    pass


if __name__ == '__main__':
    pass
