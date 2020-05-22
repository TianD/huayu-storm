# coding=utf8
import os
import re
from collections import OrderedDict

import maya.cmds as maya_cmds
import maya.mel as maya_mel
import pymel.core as pymel_core

from DeadlineHelper import DeadlineHelper

try:
    import yaml
except:
    import yaml_py2 as yaml


def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


yaml.add_representer(OrderedDict, represent_ordereddict)

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

LAYER_NAMESPACE_SUFFIX = 'RN'

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

BG_OBJECT_SELECTOR = '*:SET'
LGT_OBJECT_SELECTOR = 'LGT{}*:*'.format(LAYER_NAMESPACE_SUFFIX)
SKY_OBJECT_SELECTOR = 'SKY{}*:*'.format(LAYER_NAMESPACE_SUFFIX)
CHR_OBJECT_SELECTOR = '*:CHR'
PRO_OBJECT_SELECTOR = '*:PRO'
CHRLGT_OBJECT_SELECTOR = 'CHRLGT*{}:*'.format(LAYER_NAMESPACE_SUFFIX)

# layer order [reversed]
RENDER_LAYER_RULES = [
    # layer name ,  layer select pattern
    [LAYER_LGT, [LGT_OBJECT_SELECTOR] + [CHR_OBJECT_SELECTOR, PRO_OBJECT_SELECTOR, CHRLGT_OBJECT_SELECTOR]],
    [LAYER_SKY, [SKY_OBJECT_SELECTOR]],
    [LAYER_CHR_COLOR, [CHR_OBJECT_SELECTOR, PRO_OBJECT_SELECTOR, CHRLGT_OBJECT_SELECTOR]],
    [LAYER_BG_COLOR, [BG_OBJECT_SELECTOR] + [CHR_OBJECT_SELECTOR, PRO_OBJECT_SELECTOR, CHRLGT_OBJECT_SELECTOR]],
    # [LAYER_IDP, [CHR_OBJECT_SELECTOR, PRO_OBJECT_SELECTOR, BG_OBJECT_SELECTOR]],
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

RENDER_REDSHIFT = 'redshift'
PLUGIN_REDSHIFT = 'redshift4maya.mll'

RENDER_ARNOLD = 'arnold'


class SceneHelper(LogHelper):
    NAME_SPLITTER = '_'

    def __init__(self, logger=None):
        super(SceneHelper, self).__init__(logger=logger)
        self.path_and_file_helper = PathAndFileHelper(logger)

        # scene info
        self.episode = ''
        self.sequence = ''
        self.shot = ''
        self.camera_regex = ''
        # fill epsiode/sequence/shot
        # self.get_episode_sequence_shot_from_filename()

    def load_camera_regex(self, camera_regex):
        self.camera_regex = camera_regex
        self.get_episode_sequence_shot_from_filename()

    def select_with_clear(self, object_pattern):
        maya_cmds.select(cl=True)
        maya_cmds.select(object_pattern)

    def list_with_pattern(self, object_pattern):
        return maya_cmds.ls(object_pattern)

    # ------- reference part ----------
    def get_reference_list(self):
        return pymel_core.listReferences()

    def get_reference_node_list(self, reference_node):
        return reference_node.nodes()

    def list_with_pattern_for_shape_override(self, object_pattern):
        self.debug('[ ready to get  shape_str_list ]', object_pattern)
        selected_items = self.list_with_pattern(object_pattern)
        shape_str_list = []
        for item in selected_items:
            shapes = maya_cmds.listRelatives(item, ad=True, c=True, type="mesh") or []
            shape_str_list += shapes
        self.debug('[ shape_str_list ]', shape_str_list)
        return shape_str_list

    def list_with_reference_pattern(self, reference_pattern):
        reference_list = self.get_reference_list()
        for reference_item in reference_list:
            if reference_pattern in reference_item.path:
                return self.get_reference_node_list(reference_item)
        return []

    def list_with_reference_pattern_for_shape_override(self, reference_pattern):
        node_list = self.list_with_reference_pattern(reference_pattern)
        self.debug('[ ready to get  shape_str_list ]', node_list)
        shape_str_list = []
        for item in node_list:
            if isinstance(item, pymel_core.nodetypes.Mesh):
                shape_str_list.append(item.name())

            shapes = \
                [
                    relative_item.name()
                    for relative_item in pymel_core.listRelatives(item, ad=True, c=True, type="mesh")
                ]
            shape_str_list += shapes
        self.debug('[ shape_str_list ]', shape_str_list)
        return shape_str_list

    def scene_format_dict(self):
        return \
            {
                'episode': int(self.episode),
                'sequence': int(self.sequence),
                'shot': int(self.shot),
            }

    def get_episode_sequence_shot_from_filename(self):
        scene_file_path = maya_cmds.file(query=1, exn=1)
        scene_file_name = self.path_and_file_helper.get_base_name(scene_file_path)

        name_item_list = scene_file_name.split(SceneHelper.NAME_SPLITTER)

        self.debug('[ name_item_list ]', name_item_list)
        if len(name_item_list) >= 3:
            scene_info_match_list = \
                re.findall(self.camera_regex, scene_file_name, re.I)
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

    def get_current_camera(self):
        cam_list = [
            cam.getParent().name()
            for cam in pymel_core.ls('cam*{}*{}*{}*'.format(self.episode, self.sequence, self.shot), type='camera')
        ]
        if len(cam_list) == 1:
            return cam_list[0]
        else:
            return ''

    def set_renderable_camera(self, camera_name):
        cam_list = [
            cam
            for cam in pymel_core.ls(type='camera')
        ]
        for cam in cam_list:
            cam_name = cam.name()
            renderable_attr = "{}.renderable".format(cam_name)
            if cam.getParent().name() == camera_name:
                maya_cmds.setAttr(renderable_attr, True)
            else:
                maya_cmds.setAttr(renderable_attr, False)

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
        try:
            import maya.app.renderSetup.views.overrideUtils as override_utils
            from maya.app import renderSetup
        except:
            pass

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

    KEY_SCRIPT = 'script'
    KEY_RETURN_VALUE = 'return_result'

    def get_value_with_exec(self, code):
        try:
            local_dict = {}
            exec(code, globals(), local_dict)
            return local_dict.get(SceneHelper.KEY_RETURN_VALUE)
        except Exception as e:
            self.debug('[-] exec failed , error : {}'.format(e))
            return

    def __set_override_for_render_layer_for_maya_old(
            self, attr_key, attr_value, input_render_layer_name='',
            create_if_not_existed=True, skip_switch_render_layer=False
    ):
        # layer_name_input = layer_name_input  # "renderSetupLayer2"
        # attr_key = attr_key  # 'defaultResolution.width'
        # attr_value = value  # 2000
        if not skip_switch_render_layer:
            self.set_render_layer_to_current(input_render_layer_name)
        else:
            self.debug('[*] do skip_switch_render_layer')

        if input_render_layer_name != SceneHelper.DEFAULT_RENDER_LAYER_NAME:
            try:
                maya_cmds.editRenderLayerAdjustment(attr_key, layer=input_render_layer_name)
            except Exception as e:
                self.debug(e)

        self.set_attr_with_command_param_list_batch_list(
            [
                [attr_key, attr_value]
            ]
        )

    DEFAULT_RENDER_LAYER_NAME = 'masterLayer'

    def set_attr_with_command_param_list_batch_list(self, command_param_list_batch_list):
        for command_param_list in command_param_list_batch_list:
            attr_key, attr_value = command_param_list
            # if is dict
            #   attr_value =>
            #       script: 'import os\nreturn_value = os.path.dirname('')'
            self.debug('[ready to set ] => ', attr_key, attr_value)

            if isinstance(attr_value, dict) or isinstance(attr_value, OrderedDict):
                script_content = attr_value.get(SceneHelper.KEY_SCRIPT, '')
                if script_content:
                    attr_value = self.get_value_with_exec(script_content)

            if isinstance(attr_value, str):
                attr_type = 'string'
            else:
                attr_type = ''

            if attr_type:
                kwargs = {'type': attr_type}
            else:
                kwargs = {}

            try:
                self.debug('[ set attr ] => {} {}'.format(attr_key, attr_value))
                maya_cmds.setAttr(attr_key, attr_value, **kwargs)
            except Exception as e:
                self.debug('[ set failed ] => caused by ', e)
            finally:
                self.debug('[ set failed ] => ', command_param_list)

    def set_attr_with_command_param_list_batch_list_with_render_layer(
            self,
            command_param_list_batch_list, override_render_layer_name=DEFAULT_RENDER_LAYER_NAME,
            skip_switch_render_layer=False
    ):
        for command_param_list in command_param_list_batch_list:
            attr_key, attr_value = command_param_list
            self.__set_override_for_render_layer_for_maya_old(
                attr_key, attr_value, input_render_layer_name=override_render_layer_name, create_if_not_existed=True,
                skip_switch_render_layer=skip_switch_render_layer
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
            render_layer_name = 'defaultRenderLayer'

        try:
            render_layer = pymel_core.PyNode(render_layer_name)
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
            selected = self.list_with_pattern(object_pattern)
            render_layer.addMembers(selected)
        except Exception as e:
            self.debug('[-] error happened when add objects to render_layer, {} '.format(e))

    def set_render_layer_object_pattern_for_maya_old_with_ref_pattern(self, reference_pattern='', render_layer_name=''):
        """
        :param reference_pattern:
            p*:PRO to select pro
            c*:CHR to select character
        :param render_layer_name:
        :return:
        """
        render_layer = self.__get_render_layer_with_auto_create(render_layer_name)

        # as use *:* this like , if not found , error happened , so try/except to avoid this

        try:
            selected = self.list_with_reference_pattern(reference_pattern)
            render_layer.addMembers(selected)
        except Exception as e:
            self.debug('[-] error happened when add objects to render_layer, {} '.format(e))

    def load_render_plugin(self, plugin_name):
        pymel_core.loadPlugin(plugin_name, quiet=True)
        pymel_core.pluginInfo(plugin_name, edit=True, autoload=True)

    def set_render_layer_to_current(self, render_layer_name):
        render_layer = self.__get_render_layer_with_auto_create(render_layer_name)
        render_layer.setCurrent()

    def save_as(self, file_name):
        maya_cmds.file(rename=file_name)
        maya_cmds.file(force=True, save=True)

    def get_current_scene_name(self):
        scene_file_name = pymel_core.system.sceneName()
        return scene_file_name

    def open_scene_forcelly(self, scene_file_name):
        maya_cmds.file(scene_file_name, open=True, force=True, iv=True)  # ignore version

    def export(self, file_name):
        self.debug('ready to export file: "{}"'.format(file_name))
        scene_file_name = self.get_current_scene_name()
        self.save_as(file_name)
        maya_cmds.file(scene_file_name, open=True, force=True, iv=True)  # ignore version

    def set_current_render(self, render_name):
        self.set_attr_with_command_param_list_batch_list(
            [
                ["defaultRenderGlobals.currentRenderer", render_name]
            ]
        )

        # if render_name == RENDER_ARNOLD:
        # ---------- ensure arnold nodes created ---------------
        # Deletes the render settings window UI completely
        if maya_cmds.window("unifiedRenderGlobalsWindow", exists=True):
            maya_cmds.deleteUI("unifiedRenderGlobalsWindow")

        # Remake the render settings UI
        maya_mel.eval('unifiedRenderGlobalsWindow;')


class SceneHelperForRedshift(SceneHelper):
    def __init__(self, logger=None):
        super(SceneHelperForRedshift, self).__init__(logger=logger)
        self.load_render_plugin()
        self.set_current_render(RENDER_REDSHIFT)

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
        # disable masterLayer
        maya_mel.eval('renderLayerEditorRenderable RenderLayerTab "defaultRenderLayer" "0";')
        # process layers
        for render_layer_select_rule in RENDER_LAYER_RULES:
            layer_name = render_layer_select_rule[0]
            select_pattern_list = render_layer_select_rule[1]
            self.debug('--------------', layer_name)
            # if layer_name == LAYER_IDP:
            for select_pattern in select_pattern_list:
                self.set_render_layer_object_pattern_for_maya_old(
                    object_pattern=select_pattern, render_layer_name=layer_name
                )
                # if layer_name == LAYER_IDP:
                #     self.process_redshift_idp(layer_name)

    def process_redshift_idp(self, layer_name):

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

    def load_render_plugin(self, plugin_name=PLUGIN_REDSHIFT):
        super(SceneHelperForRedshift, self).load_render_plugin(plugin_name)


class ReferenceHelper(LogHelper):

    def __init__(self, logger=None):
        LogHelper.__init__(self, logger=logger)
        self.scene_helper = SceneHelperForRedshift(logger=logger)
        self.config_helper = ConfigHelper(logger=logger)

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


class ReferenceExporter(ReferenceHelper):
    def format_json_dict_with_format_dict(self, json_dict, format_dict):
        yaml_string = yaml.dump(json_dict)
        yaml_string = yaml_string.format(**format_dict)
        return yaml.load(yaml_string)

    def ensure_set_render(self, file_render_setting_dict):
        render_type = file_render_setting_dict.get('render_type')
        render_plugin_name = file_render_setting_dict.get('render_plugin_name')
        self.scene_helper.load_render_plugin(render_plugin_name)
        self.scene_helper.set_current_render(render_type)

    def get_pattern_list_from_selector_list(self, selector_key_list, selector_dict):
        current_pattern_list = []
        for current_selector_key in selector_key_list:
            current_selector = selector_dict.get(current_selector_key)

            if current_selector:
                current_pattern_list.append(current_selector)

        if current_pattern_list == []:
            current_pattern_list = list(selector_dict.values())

        return current_pattern_list

    def submit_to_deadline(self, project_name, scene_file_name):
        deadline_helper = DeadlineHelper(logger=self.logger)
        deadline_helper.load_submit_parameter(project_name, self.scene_helper.get_current_scene_name(), scene_file_name)
        self.debug(deadline_helper.deadline_parameter_dict)
        self.debug('READY submit project : "{}" , file : "{}" to deadeline'.format(project_name, scene_file_name))
        deadline_helper.submit_to_deadline()
        self.debug('DONE submit project : "{}" , file : "{}" to deadeline'.format(project_name, scene_file_name))

    IMPORT_FILE_NAMESPACE_SUFFIX = '_'

    def process_all_config(self, project_name):
        current_scene_file_name = self.scene_helper.get_current_scene_name()

        layer_file_setting = self.config_helper.get_all_config().get(project_name, {})

        layer_file_setting_formatted = OrderedDict()
        # format with regex
        for file_name, file_render_setting_dict in layer_file_setting.items():
            current_key = 'common_setting.episode_scene_shot_regex'
            episode_scene_shot_regex = self.config_helper.get_json_value_with_key_path(
                current_key, {}, file_render_setting_dict
            )
            self.scene_helper.load_camera_regex(episode_scene_shot_regex)

            format_dict = self.scene_helper.scene_format_dict()
            format_dict.update(
                {
                    'project_file_name': current_scene_file_name,
                }
            )
            file_render_setting_dict = \
                self.format_json_dict_with_format_dict(
                    file_render_setting_dict, format_dict
                )

            layer_file_setting_formatted[file_name] = file_render_setting_dict

        for file_name, file_render_setting_dict in layer_file_setting_formatted.items():
            # get selector dict
            # ------------ with ref path -------------
            current_key = 'common_setting.object_selector_with_ref_path'
            selector_dict_with_ref_path = self.config_helper.get_json_value_with_key_path(
                current_key, {}, file_render_setting_dict
            )

            # ------------ no ref path -------------
            current_key = 'common_setting.object_selector'
            selector_dict = self.config_helper.get_json_value_with_key_path(
                current_key, {}, file_render_setting_dict
            )

            # reopen base file
            self.scene_helper.open_scene_forcelly(current_scene_file_name)
            # --------------------- load reference from anim to render -------------------
            # -------------------------------- import files ------------------------------
            current_key = 'common_setting.import_file'
            import_file_list = self.config_helper.get_json_value_with_key_path(
                current_key, [], file_render_setting_dict
            )
            for import_file_layer_name, import_file in import_file_list:
                if os.path.exists(import_file):
                    self.debug('[*] import file')
                    maya_cmds.file(
                        import_file, i=True, f=True,
                        namespace=import_file_layer_name + ReferenceExporter.IMPORT_FILE_NAMESPACE_SUFFIX
                    )
                else:
                    self.debug('[-] import file , not existed : {}'.format(import_file))

            # -------------------------------- set camera --------------------------------
            self.process_camera()
            # -------------------------------- process all layer -------------------------
            output_file_name = file_render_setting_dict.get('output_file_name', '')

            # ---------------------- get maya_info.json path -----------------------------
            current_key = 'common_setting.maya_file_info_file_content_script'
            maya_file_info_file_content_script = self.config_helper.get_json_value_with_key_path(
                current_key, '', file_render_setting_dict
            )

            # -------------------------------- DEBUG LAYER FILE CODE ---------------------
            # if 'IDP' not in output_file_name:
            #     continue

            if output_file_name:
                # -------------------------------- set render ----------------------------
                self.ensure_set_render(file_render_setting_dict)

                # -------------------------------- get layer list ------------------------
                file_render_layer_setting_list = file_render_setting_dict.get('layer_setting', [])
                # reverse layer to make order ok
                file_render_layer_setting_list.reverse()

                for current_render_layer_setting in file_render_layer_setting_list:
                    # ----------------------- process each layer -------------------------

                    current_layer_name = current_render_layer_setting.get('layer_name', '')
                    if current_layer_name:
                        self.debug('[*] start to process layer : {}'.format(current_layer_name))
                        ###### --------------------- write maya_info.json --------------------
                        self.scene_helper.set_attr_with_command_param_list_batch_list(
                            [
                                ['maya_file_info_file_content_script', maya_file_info_file_content_script]
                            ]
                        )

                        ###### --------------------- add objects to layer --------------------
                        # ------------ with ref path -------------
                        __current_selector_key_list = current_render_layer_setting.get('selector_list_with_ref_path',
                                                                                       [])
                        current_select_pattern_list_with_ref_path = self.get_pattern_list_from_selector_list(
                            __current_selector_key_list, selector_dict_with_ref_path
                        )

                        for current_select_pattern_with_ref_path in current_select_pattern_list_with_ref_path:
                            self.scene_helper.set_render_layer_object_pattern_for_maya_old_with_ref_pattern(
                                reference_pattern=current_select_pattern_with_ref_path,
                                render_layer_name=current_layer_name
                            )

                        # ------------ no ref path -------------
                        __current_selector_key_list = current_render_layer_setting.get('selector_list', [])
                        current_select_pattern_list_with_ref_path = self.get_pattern_list_from_selector_list(
                            __current_selector_key_list, selector_dict
                        )

                        for current_select_pattern_with_ref_path in current_select_pattern_list_with_ref_path:
                            self.scene_helper.set_render_layer_object_pattern_for_maya_old(
                                object_pattern=current_select_pattern_with_ref_path,
                                render_layer_name=current_layer_name
                            )

                        # ----------------- DEBUG PART ---------------------------------------
                        # if current_layer_name != LAYER_LGT:
                        #     continue

                        self.scene_helper.set_render_layer_to_current(current_layer_name)
                        skip_switch_render_layer = True
                        ###### --------------------- add objects to layer --------------------

                        current_render_setting_list = [
                            list(current_render_setting_item)
                            for current_render_setting_item in list(
                                (current_render_layer_setting.get('render_setting') or {}).items()
                            )
                        ]

                        self.scene_helper.set_attr_with_command_param_list_batch_list_with_render_layer(
                            current_render_setting_list, current_layer_name,
                            skip_switch_render_layer=skip_switch_render_layer
                        )

                        # set primaryVisibility for objects
                        character_override_selector_list = \
                            current_render_layer_setting.get('character_override_selector_list_with_ref_path', [])
                        # get all attr list : primaryVisibility -> 0 , other -> 1
                        character_override_attr_list = \
                            current_render_layer_setting.get('character_override_attr_list', [])

                        # if current_layer_name == LAYER_BG_COLOR:
                        if character_override_selector_list and character_override_attr_list:
                            self.debug('[get layer] => ', current_layer_name)

                            current_select_pattern_list_with_ref_path = self.get_pattern_list_from_selector_list(
                                character_override_selector_list, selector_dict
                            )

                            character_str_list = []
                            for current_select_pattern_with_ref_path in current_select_pattern_list_with_ref_path:
                                character_str_list += \
                                    self.scene_helper.list_with_reference_pattern_for_shape_override(
                                        current_select_pattern_with_ref_path
                                    )

                            self.debug('[get character_str_list] => ', character_str_list)
                            if character_str_list:
                                command_list = []

                                for character_override_attr in character_override_attr_list:
                                    attr_name = character_override_attr[0]
                                    attr_value = character_override_attr[1]

                                    command_list += [
                                        ['{}.{}'.format(character_str, attr_name), attr_value]
                                        for character_str in character_str_list
                                    ]

                                self.debug('[ command_list ]', command_list)

                                self.scene_helper.set_attr_with_command_param_list_batch_list_with_render_layer(
                                    command_list, current_layer_name,
                                    skip_switch_render_layer=skip_switch_render_layer
                                )
                # -------------------------------- export file ---------------------------
                self.scene_helper.export(output_file_name)
                # -------------------------------- submit file to deadline --------------
                output_scene_file_name = output_file_name
                self.submit_to_deadline(project_name, output_scene_file_name)

    def process_all_render_layer(self):
        return self.scene_helper.process_all_render_layer()

    def process_camera(self):
        current_camera = self.scene_helper.get_current_camera()
        self.scene_helper.set_renderable_camera(current_camera)


if __name__ == '__main__':
    # try:
    #     egg_dir = 'C:/Users/alpha/AppData/Local/JetBrains/Toolbox/apps/PyCharm-P/ch-0/201.6668.115/debug-eggs'
    #     import sys
    #
    #     sys.path.insert(0, egg_dir)
    #     import pydevd_pycharm
    #
    #     pydevd_pycharm.settrace('localhost', port=9000, stdoutToServer=True, stderrToServer=True)
    #
    # except Exception as e:
    #     print('[-] set debug failed')
    import traceback

    from LogHelper import app_logger

    try:
        ref_exporter = ReferenceExporter(logger=app_logger)

        # get project_name from env
        ref_exporter.process_all_config(os.environ.get('PROJECT_NAME'))

        app_logger.debug("[*] all process done")
    except Exception as e:
        app_logger.debug(traceback.format_exc())
        app_logger.debug("[-] some error happened , error : {}".format(e))
