# coding=utf8

from string import Formatter


class AdvFormatter(Formatter):
    def get_value(self, key, args, kwargs):
        try:
            if isinstance(key, str):
                return kwargs.get(key) or '{%s}' % key
            elif isinstance(key, int):
                return args[key] or '{%s}' % key
            else:
                return super(AdvFormatter, self).get_value(key, args, kwargs)
        except:
            return '{%s}' % key


if __name__ == '__main__':
    string = "{number_of_sheep} sheep {has} run away"
    other_dict = {'number_of_sheep': 'a'}
    fmt = AdvFormatter()
    print(fmt.format(string, **other_dict))
