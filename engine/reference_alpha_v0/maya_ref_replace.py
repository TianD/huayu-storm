# coding=utf8


import os
import re

import maya.cmds as maya_cmds
import pymel.core as pymel_core

# todo remove reload
import LogHelper

reload(LogHelper)

from LogHelper import LogHelper


class PathHelper(LogHelper):
    def __init__(self, logger=None):
        LogHelper.__init__(self, logger)

    def get_base_name(self, file_path):
        return os.path.basename(file_path)


class SceneHelper(LogHelper):
    NAME_SPLITTER = '_'
    EPISODE_SCENE_SHOT_REGX = '(SEA_0[0-9]_T[0-9a-z]+)_(P[0-9a-z]+)_(S[0-9]+_?[0-9]+)'

    def __init__(self, logger=None):
        LogHelper.__init__(self, logger)
        self.path_helper = PathHelper(logger)

        # scene info
        self.episode = ''
        self.scene = ''
        self.shot = ''

    def get_episode_scene_shot_from_filename(self):
        scene_file_path = maya_cmds.file(query=1, exn=1)
        scene_file_name = self.path_helper.get_base_name(scene_file_path)

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
                self.scene = valid_match_list[1]
                self.shot = valid_match_list[2]
            else:
                self.error('no enough match item for episode_scene_shot')
        else:
            self.error('no enough match item for episode_scene_shot')


class ReferenceHelper(LogHelper):
    replace_rules = [
        {'bgclr': 'add_scene'},
        {'chclr': 'add_char/props'},
        {'light': 'config_file'},  # just a maya file
        {'sky': 'config_file'},  # just a maya file
        {'aov': 'config_file'},  # just a maya file
    ]

    def __init__(self, logger=None):
        LogHelper.__init__(self, logger)

    def __reference_filter(self):
        return []

    def get_reference_list(self, reference_filter=[]):
        return pymel_core.listReferences()

    def post_reference(self, reference_source, reference_target):
        return

    def __replace_reference(self, reference_source, reference_target):
        # todo maya replace reference
        reference_replaced = False
        return reference_replaced

    def __get_reference_file_path_with_rules(self, reference_source, rules):
        # todo replace with rules , anim -> rendering , some other
        return reference_source

    def __replace_reference_with_rules(self, reference_source):
        reference_target = \
            self.__get_reference_file_path_with_rules(
                reference_source, self.replace_rules
            )
        self.__replace_reference(reference_source, reference_target)
        # post process
        self.post_reference(reference_source, reference_target)

    def process_all_reference(self):
        reference_list = self.get_reference_list(self.__reference_filter())
        for reference_item in reference_list:
            self.__replace_reference_with_rules(reference_item)


class ReferenceExporter(ReferenceHelper):
    def post_reference(self, reference_source, reference_target):
        super(ReferenceExporter, self).post_reference(reference_source, reference_target)
        # todo , set render setting
        self.debug('set render setting', reference_source, reference_target)
        # todo , export reference file
        self.debug('export reference file', reference_source, reference_target)


if __name__ == '__main__':
    # reference_helper = ReferenceHelper()
    # reference_helper.info(reference_helper.get_reference_list(), **reference_helper.FORMAT_JSON_DICT_KWARG)
    # reference_helper.replace_reference()

    ref_exporter = ReferenceExporter()
    ref_exporter.process_all_reference()
