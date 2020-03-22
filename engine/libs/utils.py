import os

def get_file_dir(file_path):
    return os.path.dirname(file_path)

def get_sibling_file_path(file_path,sibling_file_name):
    return \
        os.path.join(
            get_file_dir(file_path),
            sibling_file_name
        )

def get_file_new_ext_path(file_path,new_ext):
    file_path_list = file_path.split('.')
    file_path_list[-1] = new_ext
    return '.'.join(file_path_list)

def get_file_abs_path(file_path):
    return os.path.abspath(file_path)

def get_file_native_abs_path(file_path):
    return get_file_abs_path(file_path).replace('/','\\')

def ensure_file_dir_exists(file_path):
    try:
        os.makedirs(os.path.dirname(file_path)
    except:
        pass