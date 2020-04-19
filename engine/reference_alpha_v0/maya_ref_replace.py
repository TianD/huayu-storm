# coding=utf8


import re

import maya.cmds as maya_cmds
import maya.mel as maya_mel
import pymel.core as pymel_core

try:
    import maya.app.renderSetup.views.overrideUtils as override_utils
    from maya.app import renderSetup
except:
    pass

# todo remove reload
import LogHelper

reload(LogHelper)

from LogHelper import LogHelper
from utils.PathAndFileHelper import PathAndFileHelper
from utils.ConfigHelper import ConfigHelper

LAYER_MASTER = 'masterLayer'
LAYER_BG_COLOR = 'BGCLR'
LAYER_CHR_COLOR = 'CHCLR'
LAYER_SKY = 'SKY'
LAYER_IDP = 'IDP'
LAYER_LGT = 'LGT'
LAYER_AOV = 'AOV'

LAYER_IDP_AOV_NAME = 'idp'

LAYER_LIST_OF_ALL = [
    LAYER_MASTER,
    LAYER_BG_COLOR,
    LAYER_CHR_COLOR,
    LAYER_SKY,
    LAYER_IDP,
    LAYER_LGT,
    LAYER_AOV,
]

BG_OBJECT_SELECTOR = 'BGCLRRN:*'
LGT_OBJECT_SELECTOR = 'LGTRN:*'
SKY_OBJECT_SELECTOR = 'SKYRN:*'
CHR_OBJECT_SELECTOR = '*:CHR'
PRO_OBJECT_SELECTOR = '*:PRO'
CHRLGT_OBJECT_SELECTOR = 'CHRLGTRN:*'

RENDER_LAYER_RULES = [
    # layer name ,  layer select pattern
    [LAYER_BG_COLOR, [BG_OBJECT_SELECTOR]],
    [LAYER_LGT, [LGT_OBJECT_SELECTOR]],
    [LAYER_SKY, [SKY_OBJECT_SELECTOR]],
    [LAYER_CHR_COLOR, [CHR_OBJECT_SELECTOR, PRO_OBJECT_SELECTOR, CHRLGT_OBJECT_SELECTOR]],
    [LAYER_IDP, [CHR_OBJECT_SELECTOR, PRO_OBJECT_SELECTOR, BG_OBJECT_SELECTOR]],
]

# [CHR_OBJECT_SELECTOR, PRO_OBJECT_SELECTOR, BG_OBJECT_SELECTOR]

REDSHIFT_MATTE_RED = 1
REDSHIFT_MATTE_GREEN = 2
REDSHIFT_MATTE_BLUE = 3

REDSHIFT_ID_1 = REDSHIFT_MATTE_RED
REDSHIFT_ID_2 = REDSHIFT_MATTE_GREEN
REDSHIFT_ID_3 = REDSHIFT_MATTE_BLUE

REDSHIFT_MATTE_ATTR_RED = 'redId'
REDSHIFT_MATTE_ATTR_BLUE = 'greenId'
REDSHIFT_MATTE_ATTR_GREEN = 'blueId'

REDSHIFT_OBJECT_ID_NODE_ID_ATTR = 'objectId'

LAYER_IDP_CONFIG = \
    [
        [CHR_OBJECT_SELECTOR, REDSHIFT_ID_1, REDSHIFT_MATTE_RED, REDSHIFT_MATTE_ATTR_RED],
        [PRO_OBJECT_SELECTOR, REDSHIFT_ID_2, REDSHIFT_MATTE_GREEN, REDSHIFT_MATTE_ATTR_BLUE],
        [BG_OBJECT_SELECTOR, REDSHIFT_ID_3, REDSHIFT_MATTE_BLUE, REDSHIFT_MATTE_ATTR_GREEN],
    ]

KEY_FROM = 'from'
KEY_TO = 'to'
KEY_RENDER_LAYER_NAME = 'layer_name'
KEY_NAMESPACE_NAME = 'namespace_name'

REPLACE_RULES = [
    {KEY_FROM: 'anim', KEY_TO: 'render'},
    # {'chclr': 'add_char/props'},
    # {'light': 'config_file'},  # just a maya file
    # {'sky': 'config_file'},  # just a maya file
    # {'aov': 'config_file'},  # just a maya file
]

KEY_LAYER_PROCESS_FUNC = 'key_replace_func'
KEY_REPLACE_PARAMS = 'key_replace_params'

IMPORT_FILE_PATH_LIST_FOR_LAYER_SCENE = [
    r"E:\codeLib\___test___\my_proj\py_scripts\pipeline_code\project\SCN.mb"  # scene , import sky file content
]

IMPORT_FILE_PATH_LIST_FOR_LAYER_LIGTH = [
    r"E:\codeLib\___test___\my_proj\py_scripts\pipeline_code\project\LGT.mb"  # scene , import sky file content
]
IMPORT_FILE_PATH_LIST_FOR_LAYER_SKY = [
    r"E:\codeLib\___test___\my_proj\py_scripts\pipeline_code\project\Sky.mb"  # sky , import sky file content
]
IMPORT_FILE_PATH_LIST_FOR_LAYER_CHCOLOR = [
    r"E:\codeLib\___test___\my_proj\py_scripts\pipeline_code\project\CHLGT.mb"  # chrlight , in layer chcolor
]
IMPORT_FILE_PATH_LIST_FOR_LAYER_AOV = [
    r"E:\codeLib\___test___\my_proj\py_scripts\pipeline_code\project\AOV.mb"  # Aov
]

PLUGIN_REDSHIFT = 'redshift4maya.mll'


class SceneHelper(LogHelper):
    NAME_SPLITTER = '_'
    EPISODE_SCENE_SHOT_REGX = '(SEA_0[0-9]_T[0-9a-z]+)_(P[0-9a-z]+)_(S[0-9]+_?[0-9]+)'  # TODO: 需要提到配置中去

    def __init__(self, logger=None):
        super(SceneHelper, self).__init__(logger=logger)
        self.path_and_file_helper = PathAndFileHelper(logger)

        # scene info
        self.episode = ''
        self.sequence = ''
        self.shot = ''

    def select_with_clear(self, object_pattern):
        maya_cmds.select(cl=True)
        maya_cmds.select(object_pattern)

    def list_with_pattern(self, object_pattern):
        return maya_cmds.ls(object_pattern)

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

    def get_file_path_with_replace_on_file_base_name(self, file_path, src_string, dst_string):
        file_base_name = self.path_and_file_helper.get_base_name(file_path)
        file_dir_name = self.path_and_file_helper.get_dir_name(file_path)
        new_file_base_name = file_base_name.replace(src_string, dst_string)
        return self.path_and_file_helper.join_file_path(file_dir_name, new_file_base_name)

    def __set_override_for_render_layer_for_maya_new(self, attr_key, attr_value, input_render_layer_name='',
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
                    self.__set_override_for_render_layer_for_maya_new(
                        attr_key, attr_value, input_render_layer_name, create_if_not_existed=False
                    )

    def __set_override_for_render_layer_for_maya_old(
            self, attr_key, attr_value, input_render_layer_name='', create_if_not_existed=True
    ):
        # layer_name_input = layer_name_input  # "renderSetupLayer2"
        # attr_key = attr_key  # 'defaultResolution.width'
        # attr_value = value  # 2000
        self.set_render_layer_to_current(input_render_layer_name)
        if input_render_layer_name != SceneHelper.DEFAULT_RENDER_LAYER_NAME:
            maya_cmds.editRenderLayerAdjustment(attr_key)
        self.set_attr_with_command_param_list_batch_list(
            [
                [attr_key, attr_value]
            ]
        )

    DEFAULT_RENDER_LAYER_NAME = 'masterLayer'

    def set_attr_with_command_param_list_batch_list(self, command_param_list_batch_list):
        for command_param_list in command_param_list_batch_list:
            attr_key, attr_value = command_param_list

            if isinstance(attr_value, str):
                attr_type = 'string'
            else:
                attr_type = ''

            if attr_type:
                kwargs = {'type': attr_type}
            else:
                kwargs = {}

            self.debug(attr_key, attr_value, **kwargs)

            try:
                maya_cmds.setAttr(attr_key, attr_value, **kwargs)
            finally:
                self.debug('failed on:', command_param_list)

    def set_attr_with_command_param_list_batch_list_with_render_layer(
            self,
            command_param_list_batch_list, override_render_layer_name=DEFAULT_RENDER_LAYER_NAME
    ):
        for command_param_list in command_param_list_batch_list:
            attr_key, attr_value = command_param_list
            self.__set_override_for_render_layer_for_maya_old(
                attr_key, attr_value, input_render_layer_name=override_render_layer_name, create_if_not_existed=True
            )

    def set_render_layer_with_object_pattern_for_maya_new(self, bject_pattern='', render_layer_name=''):
        # renderSetup.model.renderSetup.initialize() , # this will cause renderSetup destroyed after this
        render_setup = renderSetup.model.renderSetup.instance()
        try:
            render_layer = render_setup.getRenderLayer(render_layer_name)
        except:
            render_layer = render_setup.createRenderLayer(render_layer_name)
        collection = render_layer.createCollection(render_layer_name + '_collection')
        collection.getSelector().setPattern('|*')

    def __get_render_layer_with_auto_create(self, render_layer_name):
        if render_layer_name == SceneHelper.DEFAULT_RENDER_LAYER_NAME:
            render_layer_name = pymel_core.nodetypes.RenderLayer.defaultRenderLayer().name()

        try:
            render_layer = pymel_core.nodetypes.RenderLayer.findLayerByName(render_layer_name)
        except:
            render_layer = pymel_core.rendering.createRenderLayer(name=render_layer_name, empty=True)

        return render_layer

    def set_render_layer_object_pattern_for_maya_old(self, object_pattern='', render_layer_name=''):
        """
        :param object_pattern:
            p*:PRO to select pro
            c*:CHR to select character
        :param render_layer_name:
        :return:
        """
        render_layer = self.__get_render_layer_with_auto_create(render_layer_name)

        # as use *:* this like , if not found , error happened , so try/except to avoid this

        try:
            self.select_with_clear(object_pattern)
            selected = maya_cmds.ls(sl=True)
            render_layer.addMembers(selected)
        except:
            pass

    def load_plugin(self, plugin_name):
        maya_cmds.loadPlugin(plugin_name)

    def set_render_layer_to_current(self, render_layer_name):
        render_layer = self.__get_render_layer_with_auto_create(render_layer_name)
        render_layer.setCurrent()

    def save_as(self, file_name):
        maya_cmds.file(rename=file_name)
        maya_cmds.file(force=True, save=True)

    def export(self, file_name):
        scene_file_name = pymel_core.system.sceneName()
        self.save_as(file_name)
        maya_cmds.file(scene_file_name, open=True, force=True)


class SceneHelperForRedshift(SceneHelper):
    def __init__(self, logger=None):
        super(SceneHelperForRedshift, self).__init__(logger=logger)
        self.load_plugin()
        self.set_attr_with_command_param_list_batch_list(
            [
                ["defaultRenderGlobals.currentRenderer", "redshift"]
            ]
        )

    def create_idp_with_type_and_name(self, name=''):
        """
        :param type: "Puzzle Matte"
        :param name:
        :return:
        """
        # create rsObjectId node
        #   redshift menu => [ Redshift -> Object Properties -> Create Redshift Object Id Node for Selection ]
        #   in render setting -> AOV -> AOVs -> (select) Puzzle Matte , rename to : idp
        #                     -> AOV -> Processing -> Puzzle Matte ->
        #                                       Mode: Object ID , Red ID : 1 , Green ID : 2 , Blue ID : 3
        #                                       [ ]Reflect/Refract IDs
        maya_mel.eval('rsCreateAov -type  "{node_type}"'.format(node_type="Puzzle Matte"))
        idp_node_name = maya_cmds.ls(type='RedshiftAOV')[-1]
        self.debug('---------------', idp_node_name)
        # get node with ls , set ls(type='RedshiftAOV')[0].name => idp
        self.set_attr_with_command_param_list_batch_list(
            [
                [idp_node_name + '.name', name]
            ]
        )
        # mode: 1 => object id mode
        self.set_attr_with_command_param_list_batch_list(
            [
                [idp_node_name + '.mode', 1]
            ]
        )
        return idp_node_name

    # todo extract to SceneHelperForRedshift
    def process_all_render_layer(self):
        for render_layer_select_rule in RENDER_LAYER_RULES:
            layer_name = render_layer_select_rule[0]
            select_pattern_list = render_layer_select_rule[1]
            self.debug('--------------', layer_name)
            # if layer_name == LAYER_IDP:
            for select_pattern in select_pattern_list:
                self.set_render_layer_object_pattern_for_maya_old(
                    object_pattern=select_pattern, render_layer_name=layer_name
                )
            if layer_name == LAYER_IDP:
                #   Puzzle Matte , rename to idp
                #       CHCLR -> [aov]  , id : 1 [R]
                #       BGCLR -> Puzzle Matte , id : 2 [G]
                #       PRO -> Puzzle Matte , id : 3 [B]
                #           rsCreateAov -type  "Puzzle Matte";
                #           # get node with ls , set ls(type='RedshiftAOV')[0].name => idp
                #           # >>>> cmds.setAttr(cmds.ls(type='RedshiftAOV')[0]+'.name' , 'dddd',type='string')
                #           # setAttr -type "string" rsAov_PuzzleMatte.name "idp";
                #           setAttr "rsAov_PuzzleMatte.mode" 1;
                #           setAttr "rsAov_PuzzleMatte.redId" 1;
                #           setAttr "rsAov_PuzzleMatte.greenId" 2;
                #           setAttr "rsAov_PuzzleMatte.blueId" 3;
                self.set_render_layer_to_current(layer_name)
                idp_node_name = self.create_idp_with_type_and_name(name=LAYER_IDP_AOV_NAME)

                for config in LAYER_IDP_CONFIG:
                    selector = config[0]
                    object_id = config[1]
                    matte_color = config[2]
                    aov_attr = config[3]
                    self.select_with_clear(selector)
                    # create object id node with add objects
                    maya_mel.eval('redshiftCreateObjectIdNode()')
                    # get object_id node
                    object_id_node_name = maya_cmds.ls(type="RedshiftObjectId")[-1]
                    self.set_attr_with_command_param_list_batch_list(
                        [
                            ['{}.{}'.format(object_id_node_name, REDSHIFT_OBJECT_ID_NODE_ID_ATTR), object_id]
                        ]
                    )

                    # set idp object id for color
                    self.set_attr_with_command_param_list_batch_list(
                        [
                            ['{}.{}'.format(idp_node_name, aov_attr), object_id]
                        ]
                    )

    def load_plugin(self, plugin_name=PLUGIN_REDSHIFT):
        super(SceneHelperForRedshift, self).load_plugin(plugin_name)


class ReferenceHelper(LogHelper):

    def __init__(self, logger=None):
        LogHelper.__init__(self, logger)
        self.scene_helper = SceneHelperForRedshift(logger=logger)
        self.config_helper = ConfigHelper(logger=logger)

        self.ADD_RULES = [
            {
                KEY_RENDER_LAYER_NAME: LAYER_BG_COLOR,
                KEY_NAMESPACE_NAME: LAYER_BG_COLOR + 'RN',
                KEY_LAYER_PROCESS_FUNC: self.get_file_path_list_from_shot_file_for_scene,
                KEY_REPLACE_PARAMS: {}
            },
            {
                KEY_RENDER_LAYER_NAME: LAYER_SKY,
                KEY_NAMESPACE_NAME: LAYER_SKY + 'RN',
                KEY_LAYER_PROCESS_FUNC: self.get_file_path_list_from_shot_file_for_sky,
                KEY_REPLACE_PARAMS: {}
            },
            {
                KEY_RENDER_LAYER_NAME: LAYER_LGT,
                KEY_NAMESPACE_NAME: LAYER_LGT + 'RN',
                KEY_LAYER_PROCESS_FUNC: self.get_file_path_list_from_shot_file_for_light,
                KEY_REPLACE_PARAMS: {}
            },
            {
                KEY_RENDER_LAYER_NAME: LAYER_CHR_COLOR,
                KEY_NAMESPACE_NAME: LAYER_CHR_COLOR + 'RN',
                KEY_LAYER_PROCESS_FUNC: self.get_file_path_list_from_shot_file_for_character,
                KEY_REPLACE_PARAMS: {}
            },
            {
                KEY_RENDER_LAYER_NAME: LAYER_AOV,
                KEY_NAMESPACE_NAME: LAYER_AOV + 'RN',
                KEY_LAYER_PROCESS_FUNC: self.get_file_path_list_from_shot_file_for_aov,
                KEY_REPLACE_PARAMS: {}
            },
            # {'chclr': 'add_char/props'},
            # {'light': 'config_file'},  # just a maya file
            # {'sky': 'config_file'},  # just a maya file
            # {'aov': 'config_file'},  # just a maya file
        ]

    def __reference_filter(self):
        return []

    def get_reference_list(self, reference_filter=[]):
        return pymel_core.listReferences()

    def post_reference(self, reference_source, reference_target):
        return

    def __get_reference_file_path_with_rule(self, reference_source, rule):
        # get replaced file name
        new_file_path = ''
        replace_from = rule.get(KEY_FROM, '')
        replace_to = rule.get(KEY_TO, '')
        replace_func = rule.get(KEY_LAYER_PROCESS_FUNC, None)

        if replace_func:
            print(rule)
            new_file_path = replace_func()
        else:
            if replace_from and replace_to:
                new_file_path = \
                    self.scene_helper.get_file_path_with_replace_on_file_base_name(
                        reference_source, replace_from, replace_to
                    )
        return new_file_path

    def __replace_reference_with_rules(self, reference_item):
        reference_source = reference_item.path
        # reference_name_space = reference_item.fullNamespace  # attrs: namespace , fullNamespace
        for rule in REPLACE_RULES:
            reference_target = \
                self.__get_reference_file_path_with_rule(reference_source, rule)
            if self.scene_helper.path_and_file_helper.is_file_existed(reference_target) and \
                    self.scene_helper.path_and_file_helper.is_different_file(
                        reference_source, reference_target,
                    ):
                reference_item.replaceWith(reference_target)

    def __add_reference_with_rules(self, reference_source):
        for rule in self.ADD_RULES:
            namespace_name = rule.get(KEY_NAMESPACE_NAME, '')
            if namespace_name:
                kwargs = {'namespace': namespace_name}
            else:
                kwargs = {}
            reference_target_list = \
                self.__get_reference_file_path_with_rule(reference_source, rule)
            for reference_target in reference_target_list:
                if self.scene_helper.path_and_file_helper.is_file_existed(reference_target):
                    pymel_core.system.createReference(reference_target, **kwargs)

    def get_file_path_list_from_shot_file_for_sky(self):
        return IMPORT_FILE_PATH_LIST_FOR_LAYER_SKY

    def get_file_path_list_from_shot_file_for_scene(self):
        return IMPORT_FILE_PATH_LIST_FOR_LAYER_SCENE

    def get_file_path_list_from_shot_file_for_light(self):
        return IMPORT_FILE_PATH_LIST_FOR_LAYER_LIGTH

    def get_file_path_list_from_shot_file_for_character(self):
        return IMPORT_FILE_PATH_LIST_FOR_LAYER_CHCOLOR

    def get_file_path_list_from_shot_file_for_aov(self):
        return IMPORT_FILE_PATH_LIST_FOR_LAYER_AOV

    def process_all_reference(self):
        reference_list = self.get_reference_list(self.__reference_filter())
        reference_path = ''
        # replace
        for reference_item in reference_list:
            reference_path = reference_item.path
            self.__replace_reference_with_rules(reference_item)

        # add reference
        self.__add_reference_with_rules(reference_source=reference_path)


class ReferenceExporter(ReferenceHelper):
    def process_all_config(self):
        layer_render_setting = self.config_helper.export_config().get('{project}')
        for file_name, file_render_setting_dict in layer_render_setting.items():
            output_file_name = file_render_setting_dict.get('output_file_name', '')
            if output_file_name:
                file_render_layer_setting_list = file_render_setting_dict.get('layer_setting', [])

                for file_render_layer_setting in file_render_layer_setting_list:
                    current_layer_name = file_render_layer_setting.get('layer_name', '')

                    if current_layer_name:
                        current_render_setting_list = [
                            list(current_render_setting_item)
                            for current_render_setting_item in list(
                                file_render_layer_setting.get('render_setting', '').items()
                            )
                        ]
                        self.scene_helper.set_attr_with_command_param_list_batch_list_with_render_layer(
                            current_render_setting_list, current_layer_name
                        )
            self.scene_helper.export(output_file_name)

    def process_all_render_layer(self):
        return self.scene_helper.process_all_render_layer()

    def process_all_layer_override_attr(self):
        for override_layer_name in [LAYER_BG_COLOR]:
            command_param_list = [('defaultResolution.width', 1111)]
            self.scene_helper.set_attr_with_command_param_list_batch_list_with_render_layer(
                command_param_list, override_render_layer_name=override_layer_name
            )

    def export_all(self):
        # xx_anim -> xx_render
        #   add scene as bg
        #   add char / props
        self.process_all_reference()
        # create render layer
        self.process_all_render_layer()

        self.process_all_config()

        # todo set current camera with file name

        # todo , if layer in [ BGCLR, CHCLR , SKY ] , import layer file into current file
        #   override render layer
        #           if BGCLR:
        #               set CHCLR -> [override] Primary Visiblity : off
        # todo , if layer in [ LGT ]
        #   override render layer
        # for override_layer_name in ['BGColor', 'CHColor']:
        #     command_param_list = [('defaultResolution.width', 1920)]
        #     self.scene_helper.set_attr_with_command_param_list_batch_list_with_render_layer(
        #         command_param_list, override_render_layer_name=override_layer_name
        #     )

        # self.debug('set render setting', reference_source, reference_target)
        # todo , export reference file
        # self.debug('export reference file', reference_source, reference_target)


if __name__ == '__main__':
    try:
        egg_dir = 'C:/Users/alpha/AppData/Local/JetBrains/Toolbox/apps/PyCharm-P/ch-0/201.6668.115/debug-eggs'
        import sys

        sys.path.insert(0, egg_dir)
        import pydevd_pycharms
        pydevd_pycharm.settrace('localhost', port=9000, stdoutToServer=True, stderrToServer=True)
    except:
        pass

    # reference_helper = ReferenceHelper()
    # reference_helper.process_all_reference()
    # reference_helper.info(reference_helper.get_reference_list(), **reference_helper.FORMAT_JSON_DICT_KWARG)
    # reference_helper.replace_reference()

    ref_exporter = ReferenceExporter()

    # ref_exporter.process_all_reference()
    # ref_exporter.process_all_render_layer()
    ref_exporter.process_all_config()
