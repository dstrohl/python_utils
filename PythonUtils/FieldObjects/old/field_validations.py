from .field_exceptions import *
from PythonUtils import make_list


# <editor-fold desc="Validator Helper">
class ValidatorListHelper(object):

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
    '''
    def run(self, *args, force_append=False, **kwargs):
        tmp_ret_list = []
        for f in self:
            tmp_ret = f(*args, **kwargs)
            if tmp_ret is not None:
                if not force_append and isinstance(tmp_ret, (list, tuple)):
                    tmp_ret_list.extend(tmp_ret)
                else:
                    tmp_ret_list.append(tmp_ret)
        return tmp_ret_list
    '''
    def validate(self, value, validator=None):
        if validator is not None:
            tmp_ret = self._funcs[validator](value)
            if not tmp_ret:
                tmp_ret_list = self._funcs[validator].fail_messages
            else:
                tmp_ret_list = []
        else:
            tmp_ret_list = []
            for f in self:
                tmp_ret = f(value)
                if not tmp_ret:
                    tmp_ret_list.extend(f.fail_messages)
        if tmp_ret_list:
            raise FieldValidationException(fieldname=self.fieldname, failed_steps=tmp_ret_list, value=value)

    def __call__(self, value):
        return self.validate(value)

    def __getitem__(self, item):
        return self._funcs[item]

    def __setitem__(self, key, value):
        tmp_ret = self._funcs[key](value)
        if not tmp_ret:
            raise FieldValidationException(fieldname=self.fieldname,
                                           failed_steps=self._funcs[key].fail_messages,
                                           value=value)


class ValQueue(object):
    def __init__(self, name):
        self.to_db = ValidatorListHelper(name)
        self.from_db = ValidatorListHelper(name)
        self.to_user = ValidatorListHelper(name)
        self.from_user = ValidatorListHelper(name)

# </editor-fold>



# <editor-fold desc="Validators">


class ValidatorBaseClass(object):
    name = ''
    msg = ''
    priority = 10  # lower runs first

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def fail_messages(self, field_name, value):
        return [self.msg.format(field_name=field_name, value=value, **self.kwargs)]

    def __call__(self, value):
        return True



# </editor-fold>
