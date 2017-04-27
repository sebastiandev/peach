import sys
import os


def load_module(path):
    return __import__(path, globals(), locals(), [path.split('.')[-1]], -1)


def module_path(module_name):
    if isinstance(module_name, str) and '.py' in module_name:
        path = os.path.realpath(module_name)

    else:
        module_name = module_name.__module__ if not isinstance(module_name, str) else module_name
        path = os.path.realpath(sys.modules[module_name].__file__)

    return path


def module_dir(module_name):
    return os.path.dirname(module_path(module_name))


def load_resource_class(class_path):
    try:
        parts = class_path.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)

        for comp in parts[1:]:
            m = getattr(m, comp)
    except:
        m = None

    return m


class ObjectDict(dict):

    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            raise AttributeError("%s doesn't have attribute '%s'" % (self.__class__.__name__, key))

    def __setattr__(self, name, val):
        self[name] = ObjectDict(**val) if type(val) is dict else val


