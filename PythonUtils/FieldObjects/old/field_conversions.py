from .field_exceptions import *


# <editor-fold desc="Validator Helper">


class FuncListHelper(object):

    def __init__(self, name):
        self.fieldname = name
        self._funcs = {}
        self._func_list = []
        self.has_ops = False

    def add(self, *functions):
        for f in functions:
            self._funcs[f.name] = f
            self._func_list.append({'func': f, 'pri': f.priority})
        self.has_ops = True
        self._func_list.sort(key=lambda func: func['pri'])

    def __iter__(self):
        for f in self._func_list:
            yield f['func']

    def convert(self, value, converter=None):
        if converter is not None:
            return self._funcs[converter](value)
        else:
            for f in self:
                value = f(value)
                if self._funcs[converter].stop_processing:
                    return value
            return value

    def __call__(self, value, **kwargs):
        return self.convert(value, **kwargs)

    def __getitem__(self, item):
        return self._funcs[item]


class FuncQueue(object):
    def __init__(self, name):
        self.to_db = FuncListHelper(name)
        self.from_db = FuncListHelper(name)
        self.to_user = FuncListHelper(name)
        self.from_user = FuncListHelper(name)
# </editor-fold>


# <editor-fold desc="Validators">

class ConverterBaseClass(object):
    name = ''
    msg = ''
    priority = 10  # lower runs first

    def __init__(self):
        self.stop_processing = False

    def __call__(self, value):
        return value



# </editor-fold>


