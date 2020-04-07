# coding=utf8
from __future__ import absolute_import
from __future__ import print_function

import json


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
        print_func = getattr(self.logger, log_type, print)
        print_func(info)

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
