# coding=utf8
from __future__ import absolute_import
from __future__ import print_function

from collections import OrderedDict

import yaml

from LogHelper import LogHelper
from utils.PathAndFileHelper import PathAndFileHelper


class YamlHelper(LogHelper):
    def __init__(self, logger=None):
        super(YamlHelper, self).__init__(logger=logger)
        self.path_and_file_helper = PathAndFileHelper(logger=logger)

    def ordered_yaml_load(self, yaml_path, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
        class OrderedLoader(Loader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return object_pairs_hook(loader.construct_pairs(node))

        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        with open(yaml_path) as stream:
            return yaml.load(stream, OrderedLoader)

    def ordered_yaml_dump(self, data, stream=None, Dumper=yaml.SafeDumper, **kwds):
        class OrderedDumper(Dumper):
            pass

        def _dict_representer(dumper, data):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                data.items())

        OrderedDumper.add_representer(OrderedDict, _dict_representer)
        return yaml.dump(data, stream, OrderedDumper, **kwds)

    def load_file_to_json(self, yaml_file_path):
        data = {}
        try:
            data = self.ordered_yaml_load(yaml_file_path)
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
        if file_ext_name.lower() in ['yml', 'yaml']:
            config_helper = YamlHelper(logger=self.logger)

        config_json = {}
        if not config_helper:
            self.error('no valid config helper for extension : "{}"'.format(file_ext_name))
        else:
            config_json = config_helper.load_file_to_json(config_file_path)

        return config_json


if __name__ == '__main__':

    path_and_file_helper = PathAndFileHelper()
    config_helper = ConfigHelper(logger=path_and_file_helper.logger)

    config_dir_root = path_and_file_helper.join_file_path(
        __file__, '../../../../config',
        **{PathAndFileHelper.KEY_IS_GET_ABSOLUTE_PATH: True}
    )
    project_list = path_and_file_helper.list_dir(config_dir_root, only_dir=True)
    for project in project_list:
        project_dir = path_and_file_helper.join_file_path(config_dir_root, project)
        maya_batch_config_file_list = path_and_file_helper.list_dir(
            path_and_file_helper.join_file_path(
                project_dir, 'mayabatch',
                **{PathAndFileHelper.KEY_IS_GET_ABSOLUTE_PATH: True}
            )
            , file_filter_list=['*.yml', '*.yaml'], only_file=True
        )
        for maya_batch_config_file in maya_batch_config_file_list:
            print(config_helper.load_config_json_from_file(maya_batch_config_file))

    # print(project_list)
    config_helper = ConfigHelper(logger=path_and_file_helper.logger)
    # config_helper.load_config_json_from_file()
