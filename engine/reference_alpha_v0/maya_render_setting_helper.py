# coding=utf8
from LogHelper import LogHelper

MAYA_RENDER_REDSHIFT = 'redshift'
MAYA_RENDER_ARNOLD = 'arnold'


class MayaRenderSettingHelper(LogHelper):
    def set_common__file_output(
            self,
            file_name_prefix='', image_format='', bits_per_channel='',
            compression='', force_combine_beauty_and_AOVS_into_single_file='',
            animation='', start_frame='', end_frame='', frame_padding=''
    ):
        pass

    def set_common__renderable_cameras(self, renderable_camera=''):
        pass

    def set_common__resolution(self, presets):
        pass

    def set_common__misc(self, enable_default_light):
        pass


class RedShiftRenderSettingHelper(MayaRenderSettingHelper):
    def set_aov(self, mode_enabled=False):
        pass

    def set_output__unified_sampling(self, min_samples, max_samples, adaptive_error_threshold):
        pass

    def set_gi__general(self, primary_gi_engine, secondary_gi_engine):
        pass

    def set_opt__maximum_trace_depth(self, reflection, refraction, combined):
        pass

    def set_system__material_override(self, enabled=False):
        pass

    def set_object_id_for_selected_objects(self, object_id, selection_list):
        """
        :param object_id:  range in => [1,999]
        :param selection_list:
        :return:
        """
        # todo create rsObjectId node
        #   redshift menu => [ Redshift -> Object Properties -> Create Redshift Object Id Node for Selection ]
        #   in render setting -> AOV -> AOVs -> (select) Puzzle Matte , rename to : idp
        #                     -> AOV -> Processing -> Puzzle Matte ->
        #                                       Mode: Object ID , Red ID : 1 , Green ID : 2 , Blue ID : 3
        #                                       [ ]Reflect/Refract IDs
        pass
