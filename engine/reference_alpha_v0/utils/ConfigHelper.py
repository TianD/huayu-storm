# coding=utf8
from __future__ import absolute_import
from __future__ import print_function

import inspect
import os

__file__ = os.path.abspath(inspect.getsourcefile(lambda: 0))

import json
from collections import OrderedDict

try:
    import yaml
except:
    import yaml_py2 as yaml

from LogHelper import LogHelper
from utils.PathAndFileHelper import PathAndFileHelper


# yaml ordered dumps / loads
def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


yaml.add_representer(OrderedDict, represent_ordereddict)


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
            config_json = config_helper.load_file_to_json(config_file_path) or {}

        return config_json

    def show_json(self, json_dict):
        print(json.dumps(json_dict, indent=2))

    def get_json_value_with_key_path(self, key_path, default_value, json_dict):
        try:
            key_list = key_path.split('.')
            if len(key_list) > 1:
                value = self.get_json_value_with_key_path(
                    '.'.join(key_list[1:]), default_value, json_dict.get(key_list[0])
                )
            else:
                value = json_dict.get(key_list[0]) or default_value
        except Exception as e:
            self.error(e)
            value = default_value
        return value

    def get_all_config(self):
        config_dir_root = self.path_and_file_helper.join_file_path(
            __file__, '../../../../config',
            **{PathAndFileHelper.KEY_IS_GET_ABSOLUTE_PATH: True}
        )
        project_list = self.path_and_file_helper.list_dir(config_dir_root, only_dir=True)

        all_layer_setting_dict = OrderedDict()
        return_all_layer_setting_dict = OrderedDict()
        for project in project_list:
            project_dir = self.path_and_file_helper.join_file_path(config_dir_root, project)
            maya_batch_config_file_list = self.path_and_file_helper.list_dir(
                self.path_and_file_helper.join_file_path(
                    project_dir, 'mayabatch',
                    **{PathAndFileHelper.KEY_IS_GET_ABSOLUTE_PATH: True}
                )
                , file_filter_list=['*.yml', '*.yaml'], only_file=True
            )

            common_config_dict = OrderedDict()
            for maya_batch_config_file in maya_batch_config_file_list:
                maya_batch_config_file_base_name = self.path_and_file_helper.get_base_name(maya_batch_config_file)

                config_json = self.load_config_json_from_file(maya_batch_config_file)
                # self.show_json(config_json)

                # get "__*common*.yml" files
                if maya_batch_config_file_base_name.startswith('__') and 'common' in maya_batch_config_file_base_name:
                    common_config_dict[maya_batch_config_file_base_name] = config_json
                else:
                    all_layer_setting_dict[maya_batch_config_file] = config_json

            project_name = self.path_and_file_helper.get_base_name(project_dir)
            return_all_layer_setting_dict[project_name] = OrderedDict()
            for layer_setting_file_base_name, layer_setting_dict in all_layer_setting_dict.items():
                layer_setting_basic_config_file_name = layer_setting_dict.get('basic_config', '')
                if layer_setting_basic_config_file_name:
                    current_common_config_dict = \
                        common_config_dict.get(layer_setting_basic_config_file_name, OrderedDict())

                    layer_setting_dict['common_setting'] = \
                        current_common_config_dict.get('common_setting', OrderedDict())

                    # update override to basic config
                    render_type = layer_setting_dict.get('render_type')
                    render_plugin_name = layer_setting_dict.get('render_plugin_name')
                    if render_type and render_plugin_name:
                        layer_setting_dict['render_type'] = render_type
                        layer_setting_dict['render_plugin_name'] = render_plugin_name
                    else:
                        # get common render type / plugin_name
                        render_type = current_common_config_dict.get('render_type', '')
                        render_plugin_name = current_common_config_dict.get('render_plugin_name', '')

                        layer_setting_dict['render_type'] = render_type
                        layer_setting_dict['render_plugin_name'] = render_plugin_name

                    common_layer_setting = current_common_config_dict.get('layer_setting', [])
                    layer_setting_dict['layer_setting'] = common_layer_setting + layer_setting_dict['layer_setting']

                    layer_setting_file_base_name = self.path_and_file_helper.get_base_name(layer_setting_file_base_name)
                    return_all_layer_setting_dict[project_name][layer_setting_file_base_name] = \
                        json.loads(json.dumps(layer_setting_dict))

        # format temp_dir_name
        return_all_layer_setting_dict_string = yaml.dump(return_all_layer_setting_dict)
        return_all_layer_setting_dict_string = return_all_layer_setting_dict_string.replace(
            '{temp_dir_name}',
            self.path_and_file_helper.get_path_to_slash(
                self.path_and_file_helper.get_temp_dir()
            )
        )
        return_all_layer_setting_dict = yaml.load(return_all_layer_setting_dict_string)
        # self.show_json(all_layer_setting_dict)
        return return_all_layer_setting_dict


if __name__ == '__main__':
    config_helper = ConfigHelper()
    config_helper.show_json(config_helper.get_all_config())
