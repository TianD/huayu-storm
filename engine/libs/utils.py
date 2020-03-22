import hashlib
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


def get_file_new_path_with_new_dir_and_new_ext(file_path, new_dir, new_ext, use_md5_name=False):
    if use_md5_name:
        new_file_base_name = '{}.{}'.format(get_string_hash(file_path), new_ext)
    else:
        new_file_name = get_file_new_ext_path(file_path, new_ext)
        new_file_base_name = os.path.basename(new_file_name)
    return os.path.join(new_dir, new_file_base_name)


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


def get_string_hash(string):
    md5 = hashlib.md5()
    md5.update(string)
    return md5.hexdigest()


def get_preview_cache_path(origin_image_path):
    NEW_FORMAT_EXT = 'jpg'
    CACHE_PATH = '../cache_dir'
    PREVIEW_WIDTH = 640

    preview_path = \
        get_file_new_path_with_new_dir_and_new_ext(origin_image_path, CACHE_PATH, NEW_FORMAT_EXT, use_md5_name=True)
    ensure_file_dir_exists(preview_path)
    preview_path = get_file_native_abs_path(preview_path)

    if not is_file_exits(preview_path):
        converter_bin = get_sibling_file_path(__file__, '../../bin/ffmpeg.exe')

        command_arg_dict = {
            'ffmpeg_bin': get_file_native_abs_path(converter_bin),
            'origin_image_path': get_file_native_abs_path(origin_image_path),
            'preview_width': PREVIEW_WIDTH,
            'preview_path': preview_path,
        }
        CONVERT_COMMAND = \
            '"{ffmpeg_bin}" -i "{origin_image_path}" -vf scale={preview_width}:-1 "{preview_path}"'.format(
                **command_arg_dict)
        child = subprocess.Popen(CONVERT_COMMAND, shell=False)
        child.wait()
    return preview_path


if __name__ == '__main__':
    get_preview_cache_path(
        r'E:\codeLib\___test___\my_proj\huayu_project\huayu-storm\examples\huayu-storm\TTT\compositing\EP01\Q01\S01\ttt_EP01_Q01_S01_cp_c001.1002.jpg'
    )
