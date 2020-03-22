import os
import subprocess


def get_file_dir(file_path):
    return os.path.dirname(file_path)


def get_sibling_file_path(file_path, sibling_file_name):
    return \
        os.path.join(
            get_file_dir(file_path),
            sibling_file_name
        )


def get_file_new_ext_path(file_path, new_ext):
    file_path_list = file_path.split('.')
    file_path_list[-1] = new_ext
    return '.'.join(file_path_list)


def get_file_abs_path(file_path):
    return os.path.abspath(file_path)


def get_file_native_abs_path(file_path):
    return get_file_abs_path(file_path).replace('/', '\\')


def ensure_file_dir_exists(file_path):
    try:
        os.makedirs(os.path.dirname(file_path))
    except:
        pass


def is_file_exits(file_path):
    return os.path.isfile(file_path)


def get_preview_cache_path(origin_image_path):
    NEW_FORMAT_EXT = 'preview.jpg'

    preview_path = get_file_new_ext_path(origin_image_path, NEW_FORMAT_EXT)
    ensure_file_dir_exists(preview_path)

    if not is_file_exits(preview_path):
        converter_bin = get_sibling_file_path(__file__, '../bin/ffmpeg.exe')
        preview_width = 640

        command_arg_dict = {
            'ffmpeg_bin': get_file_native_abs_path(converter_bin),
            'origin_image_path': get_file_native_abs_path(origin_image_path),
            'preview_width': preview_width,
            'preview_path': get_file_native_abs_path(preview_path),
        }
        CONVERT_COMMAND = \
            '{ffmpeg_bin} -i "{origin_image_path}" -vs scale={preview_width}:-1 {preview_path}'.format(
                **command_arg_dict)
        child = subprocess.Popen(CONVERT_COMMAND, shell=True)
        child.wait()
    return preview_path
