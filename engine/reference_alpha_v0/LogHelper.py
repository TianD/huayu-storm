# coding=utf8
from __future__ import absolute_import
from __future__ import print_function

import json
import logging.handlers
import os
import sys

import inspect
import traceback


# Set up logger with appropriate handler
LOG_FILENAME = os.path.join(os.environ['appdata'], 'maya', os.path.basename(sys.argv[0]) + '.log')

log_file_dir = os.path.dirname(LOG_FILENAME)
if not os.path.isdir(log_file_dir):
    os.mkdir(log_file_dir)

app_logger = logging.getLogger()
app_logger.setLevel(logging.DEBUG)

# file size
__size_byte = 1
__size_mb = 1024 * 1024 * __size_byte
file_size_mb = 30 * __size_mb

log_file_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=file_size_mb, backupCount=5)
log_file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s")
)
app_logger.addHandler(log_file_handler)

std_handler = logging.StreamHandler()
std_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)-10s - %(filename)-20s[:%(lineno)d] - %(message)s")
)
app_logger.addHandler(std_handler)


class LogHelper(object):
    LogTypeInfo = 'info'
    LogTypeDebug = 'debug'
    LogTypeWarning = 'warn'
    LogTypeError = 'error'

    KEY_FORMAT_AS_JSON = 'format_as_json'
    FORMAT_JSON_DICT_KWARG = {KEY_FORMAT_AS_JSON: True}

    def __init__(self, logger=None):
        self.logger = logger

    def _log(self, log_type, info):
        current_stack = '' #' '.join(self.__get_stack().splitlines())
        print_func = getattr(self.logger, log_type, self.__print)
        print_func(info + ' ==> stack detail:' + current_stack)

    def __print(self, content):
        print(content)

    def __get_stack(self):
        try:
            frame = inspect.currentframe()
            stack_trace = traceback.format_stack(frame)
            return '\n'.join(stack_trace)
        except:
            return ''

    def __combine_args_kwargs(self, *args, **kwargs):
        return_string = ''
        if kwargs.get(LogHelper.KEY_FORMAT_AS_JSON):
            try:
                kwargs.pop(LogHelper.KEY_FORMAT_AS_JSON)
                args_string = ''
                for arg in args:
                    try:
                        if isinstance(arg, list):
                            __current_arg_string = '----list-start----' + '\n'
                            for __arg_item in arg:
                                __current_arg_string += '\t' + repr(__arg_item) + '\n'
                            __current_arg_string += '----list-end----' + '\n'
                        else:
                            __current_arg_string = json.dumps(arg, indent=2)
                    except:
                        __current_arg_string = repr(arg)
                    args_string += __current_arg_string + '\n'

                return_string = args_string + json.dumps(kwargs, indent=2)
            except Exception as e:
                pass
        if return_string == '':
            args = [repr(arg) for arg in args]
            return_string += ' '.join(args)

            kwargs = [repr(key) + ' => ' + repr(value) for key, value in kwargs.items()]
            return_string += ' '.join(kwargs)
        return return_string

    def info(self, *args, **kwargs):
        self._log(self.LogTypeInfo, self.__combine_args_kwargs(*args, **kwargs))

    def debug(self, *args, **kwargs):
        self._log(self.LogTypeDebug, self.__combine_args_kwargs(*args, **kwargs))

    def warn(self, *args, **kwargs):
        self._log(self.LogTypeWarning, self.__combine_args_kwargs(*args, **kwargs))

    def error(self, *args, **kwargs):
        self._log(self.LogTypeError, self.__combine_args_kwargs(*args, **kwargs))


if __name__ == '__main__':
    class MyLog(LogHelper):
        pass


    log = MyLog()
    log.warn('123', 123123)
    log.info('123', 123123, [12, 34], **{log.KEY_FORMAT_AS_JSON: True})
