# coding=utf8
from __future__ import absolute_import
from __future__ import print_function

import yaml

from LogHelper import LogHelper
from utils.PathAndFileHelper import PathAndFileHelper


class YamlHelper(LogHelper):
    def __init__(self, logger=None):
        super(YamlHelper, self).__init__(logger=logger)
        self.path_and_file_helper = PathAndFileHelper(logger=logger)

    def load_file_to_json(self, yaml_file_path):
        yaml_file_content = self.path_and_file_helper.get_file_content(yaml_file_path)

        data = {}
        try:
            data = yaml.load(yaml_file_content)
        except Exception as e:
            self.error(e)

        return data


class ConfigHelper(LogHelper):
    def __init__(self, logger=None):
        super(ConfigHelper, self).__init__(logger=logger)
        self.path_and_file_helper = PathAndFileHelper(logger=logger)

    def load_config_json_from_file(self, config_file_path):
        file_ext_name = self.path_and_file_helper.get_file_ext(config_file_path)
        config_helper = None
        if file_ext_name.lower in ['yml', 'yaml']:
            config_helper = YamlHelper(logger=self.logger)

        config_json = {}
        if not config_helper:
            self.error('no valid config helper for extension : "{}"'.format(file_ext_name))
        else:
            config_json = config_helper.load_file_to_json(config_file_path)

        return config_json


if __name__ == '__main__':
    pass
