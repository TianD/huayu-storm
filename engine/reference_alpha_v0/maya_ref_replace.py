# coding=utf8


import re

import maya.app.renderSetup.views.overrideUtils as override_utils
import maya.cmds as maya_cmds
import pymel.core as pymel_core

# todo remove reload
import LogHelper

reload(LogHelper)

from LogHelper import LogHelper
from utils.PathAndFileHelper import PathAndFileHelper


class SceneHelper(LogHelper):
    NAME_SPLITTER = '_'
    EPISODE_SCENE_SHOT_REGX = '(SEA_0[0-9]_T[0-9a-z]+)_(P[0-9a-z]+)_(S[0-9]+_?[0-9]+)'  # TODO: 需要提到配置中去

    def __init__(self, logger=None):
        LogHelper.__init__(self, logger)
        self.path_and_file_helper = PathAndFileHelper(logger)

        # scene info
        self.episode = ''
        self.sequence = ''
        self.shot = ''

    def get_episode_sequence_shot_from_filename(self):
        scene_file_path = maya_cmds.file(query=1, exn=1)
        scene_file_name = self.path_and_file_helper.get_base_name(scene_file_path)

        name_item_list = scene_file_name.split(SceneHelper.NAME_SPLITTER)
        if len(name_item_list) > 5:
            scene_info_match_list = \
                re.findall(SceneHelper.EPISODE_SCENE_SHOT_REGX, scene_file_name, re.I)
            self.debug(scene_info_match_list)

            if scene_info_match_list:
                valid_match_list = scene_info_match_list[0]
            else:
                valid_match_list = []
            if len(valid_match_list) >= 3:
                self.episode = valid_match_list[0]
                self.sequence = valid_match_list[1]
                self.shot = valid_match_list[2]
            else:
                self.error('no enough match item for episode_scene_shot')
        else:
            self.error('no enough match item for episode_scene_shot')

    def get_replaced_file_path_on_file_base_name(self, file_path, src_string, dst_string):
        file_base_name = self.path_and_file_helper.get_base_name(file_path)
        file_dir_name = self.path_and_file_helper.get_dir_name(file_path)
        new_file_base_name = file_base_name.replace(src_string, dst_string)
        return self.path_and_file_helper.join_file_path(file_dir_name, new_file_base_name)

    def __set_override_for_render_layer(self, attr_key, attr_value, input_render_layer_name='',
                                        create_if_not_existed=True):
        # layer_name_input = layer_name_input  # "renderSetupLayer2"
        # attr_key = attr_key  # 'defaultResolution.width'
        # attr_value = value  # 2000

        node_name, node_attr = attr_key.split('.')

        render_settings_collection_list = maya_cmds.ls(type='renderSettingsCollection')
        render_settings_collection_existed = False
        for render_settings_collection in render_settings_collection_list:
            render_setup_layer = maya_cmds.listConnections('{}.{}'.format(render_settings_collection, 'parentList'))[0]
            if render_setup_layer == input_render_layer_name:
                render_settings_collection_existed = True
                break
        if not render_settings_collection_existed:
            legacy_render_layer = \
                maya_cmds.listConnections('{}.{}'.format(input_render_layer_name, 'legacyRenderLayer'))[0]
            sys.modules['maya.app.renderSetup.model.renderSetup'].instance(). \
                switchToLayerUsingLegacyName(legacy_render_layer)
            override_utils.createAbsoluteOverride(node_name, node_attr)

        for render_settings_collection in render_settings_collection_list:
            render_setup_layer = maya_cmds.listConnections('{}.{}'.format(render_settings_collection, 'parentList'))[0]
            if render_setup_layer == input_render_layer_name:
                override_node_list = maya_cmds.listConnections('{}.{}'.format(render_settings_collection, 'enabled'))

                set_ok = False
                for override_node in override_node_list:
                    override_node_source_node_name = maya_cmds.getAttr('{}.targetNodeName'.format(override_node))
                    override_node_source_node_attr = maya_cmds.getAttr('{}.attribute'.format(override_node))
                    if True and \
                            override_node_source_node_name == node_name and \
                            override_node_source_node_attr == node_attr:
                        try:
                            self.debug(
                                maya_cmds.getAttr("%s.attribute" % override_node),
                                maya_cmds.getAttr("%s.attrValue" % override_node)
                            )
                            self.debug(
                                maya_cmds.setAttr("%s.attrValue" % override_node, attr_value)
                            )
                            set_ok = True
                        except:
                            pass
                if not set_ok and create_if_not_existed:
                    self.debug(node_name, node_attr)
                    override_utils.createAbsoluteOverride(node_name, node_attr)
                    self.__set_override_for_render_layer(
                        attr_key, attr_value, input_render_layer_name, create_if_not_existed=False
                    )

    DEFAULT_RENDER_LAYER_NAME = 'masterLayer'

    def set_attr_with_command_param_list_batch_list(self, command_param_list_batch_list,
                                                    override_render_layer_name=DEFAULT_RENDER_LAYER_NAME):
        if override_render_layer_name == SceneHelper.DEFAULT_RENDER_LAYER_NAME:
            for command_param_list in command_param_list_batch_list:
                attr_key, attr_value = command_param_list
                maya_cmds.setAttr(attr_key, attr_value)
        else:
            for command_param_list in command_param_list_batch_list:
                attr_key, attr_value = command_param_list
                self.__set_override_for_render_layer(
                    attr_key, attr_value, input_render_layer_name=override_render_layer_name, create_if_not_existed=True
                )


class ReferenceHelper(LogHelper):
    KEY_FROM = 'from'
    KEY_TO = 'to'

    REPLACE_RULES = [
        {KEY_FROM: 'anim', KEY_TO: 'render'},
        # {'chclr': 'add_char/props'},
        # {'light': 'config_file'},  # just a maya file
        # {'sky': 'config_file'},  # just a maya file
        # {'aov': 'config_file'},  # just a maya file
    ]

    ADD_RULES = [
        {KEY_FROM: 'anim', KEY_TO: 'scene'},
        {KEY_FROM: 'anim', KEY_TO: 'sky'},
        {KEY_FROM: 'anim', KEY_TO: 'light'},
        # {'chclr': 'add_char/props'},
        # {'light': 'config_file'},  # just a maya file
        # {'sky': 'config_file'},  # just a maya file
        # {'aov': 'config_file'},  # just a maya file
    ]

    def __init__(self, logger=None):
        LogHelper.__init__(self, logger)
        self.scene_helper = SceneHelper(logger=logger)

    def __reference_filter(self):
        return []

    def get_reference_list(self, reference_filter=[]):
        return pymel_core.listReferences()

    def post_reference(self, reference_source, reference_target):
        return

    def __get_reference_file_path_with_rule(self, reference_source, rule):
        # get replaced file name
        new_file_path = ''
        replace_from = rule.get(ReferenceExporter.KEY_FROM, '')
        replace_to = rule.get(ReferenceExporter.KEY_TO, '')
        if replace_from and replace_to:
            new_file_path = \
                self.scene_helper.get_replaced_file_path_on_file_base_name(
                    reference_source, replace_from, replace_to
                )
        return new_file_path

    def __replace_reference_with_rules(self, reference_item):
        reference_source = reference_item.path
        # reference_name_space = reference_item.fullNamespace  # attrs: namespace , fullNamespace
        for rule in ReferenceHelper.REPLACE_RULES:
            reference_target = \
                self.__get_reference_file_path_with_rule(reference_source, rule)
            if self.scene_helper.path_and_file_helper.is_file_exist(reference_target):
                reference_item.replaceWith(reference_target)

    def __create_reference_with_rules(self, reference_source):
        for rule in ReferenceHelper.ADD_RULES:
            reference_target = \
                self.__get_reference_file_path_with_rule(reference_source, rule)
            if self.scene_helper.path_and_file_helper.is_file_exist(reference_target):
                pymel_core.system.createReference(reference_target)

    def process_all_reference(self):
        reference_list = self.get_reference_list(self.__reference_filter())
        reference_path = ''
        for reference_item in reference_list:
            reference_path = reference_item.path
            self.__replace_reference_with_rules(reference_item)

        self.__create_reference_with_rules(reference_source=reference_path)


class ReferenceExporter(ReferenceHelper):
    LAYER_MASTER = 'masterLayer'
    LAYER_BG_COLOR = 'BGCLR'
    LAYER_CHR_COLOR = 'CHCLR'
    LAYER_SKY = 'SKY'
    LAYER_IDP = 'IDP'
    LAYER_LGT = 'LGT'

    LAYER_LIST_OF_ALL = [
        LAYER_MASTER,
        LAYER_BG_COLOR,
        LAYER_CHR_COLOR,
        LAYER_SKY,
        LAYER_IDP,
        LAYER_LGT,
    ]

    def layer_process(self, layer_name):
        if layer_name in ReferenceExporter.LAYER_LIST_OF_ALL:
            if layer_name == ReferenceExporter.LAYER_MASTER:
                pass
            elif layer_name == ReferenceExporter.LAYER_BG_COLOR:
                # todo import bg color file
                pass
            elif layer_name == ReferenceExporter.LAYER_CHR_COLOR:
                pass
            elif layer_name == ReferenceExporter.LAYER_SKY:
                # todo import sky file
                pass
            elif layer_name == ReferenceExporter.LAYER_IDP:
                # todo set idp for chr / bg
                pass
            elif layer_name == ReferenceExporter.LAYER_LGT:
                # todo import lgt file
                pass
        else:
            self.error('not valid layer : {}'.format(layer_name))

    def export_all(self):
        # todo , set common render setting
        self.scene_helper.set_attr_with_command_param_list_batch_list([('defaultResolution.width', 1920)])
        # todo , replace reference
        # xx_anim -> xx_render
        self.process_all_reference()
        #   add scene as bg
        #   add char / props
        # todo , if layer in [ BGCLR, CHCLR , SKY ] , import layer file into current file
        #   override render layer
        #           if BGCLR:
        #               set CHCLR -> [override] Primary Visiblity : off
        # todo , if layer in [ IDP ] , create idp layer
        #   override render layer
        #   Puzzle Matte , rename to idp
        #       CHCLR -> [aov]  , id : 1 [R]
        #       BGCLR -> Puzzle Matte , id : 2 [G]
        #       PRO -> Puzzle Matte , id : 3 [B]
        #           rsCreateAov -type  "Puzzle Matte";
        #           # get node with ls , set ls(type='RedshiftAOV')[0].name => idp
        #           # >>>> cmds.setAttr(cmds.ls(type='RedshiftAOV')[0]+'.name' , 'dddd',type='string')
        #           # setAttr -type "string" rsAov_PuzzleMatte.name "idp";
        #           setAttr "rsAov_PuzzleMatte.redId" 1;
        #           setAttr "rsAov_PuzzleMatte.greenId" 2;
        #           setAttr "rsAov_PuzzleMatte.blueId" 3;
        #           setAttr "rsAov_PuzzleMatte.mode" 1;
        # todo , if layer in [ LGT ]
        #   override render layer
        for override_layer_name in ['BGColor', 'CHColor']:
            command_param_list = [('defaultResolution.width', 1920)]
            self.scene_helper.set_attr_with_command_param_list_batch_list(
                command_param_list, override_render_layer_name=override_layer_name
            )

        # self.debug('set render setting', reference_source, reference_target)
        # todo , export reference file
        # self.debug('export reference file', reference_source, reference_target)


if __name__ == '__main__':
    egg_dir = 'C:/Users/alpha/AppData/Local/JetBrains/Toolbox/apps/PyCharm-P/ch-0/201.6668.115/debug-eggs'
    import sys

    sys.path.insert(0, egg_dir)

    # pydevd_pycharm.settrace('localhost', port=9000, stdoutToServer=True, stderrToServer=True)

    reference_helper = ReferenceHelper()
    reference_helper.process_all_reference()
    # reference_helper.info(reference_helper.get_reference_list(), **reference_helper.FORMAT_JSON_DICT_KWARG)
    # reference_helper.replace_reference()

    # ref_exporter = ReferenceExporter()
    # ref_exporter.process_all_reference()
