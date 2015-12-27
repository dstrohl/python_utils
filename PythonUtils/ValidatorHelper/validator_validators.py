__all__ = ['ValidateInstance', 'ValidateSubClass',
           'ValidatorBase', 'ValidatorComplexBase',
           'ValidateRegex', 'ValidateEmpty', 'ValidateNotEmpty',
           'ValidateEq', 'ValidateGt', 'ValidateGte', 'ValidateLt', 'ValidateLte',
           'ValidateStartsWith', 'ValidateEndsWith',
           'ValidateTrue', 'ValidateFalse',
           'ValidateMethod', 'ValidateFuncWrapper',
           'ValidateIn', 'ValidateIs',
           'ValidateComp', 'ValidateBetween',
           'ValidateAnd', 'ValidateOr',
           'ValidateMaxLen', 'ValidateMinLen',
           ]

import re
from PythonUtils.ChoicesHelper import ChoicesHelper


class ValidatorBase(object):
    name = ''
    _long_name = ''
    _message = '{value} {passfail_str} {long_name} validation'
    _pass_msg = None
    _fail_msg = None
    _passfail_msg = {
        True: 'PASSED',
        False: 'FAILED'
    }
    _is_isnot_str = {
        True: 'is',
        False: 'is not',
    }
    _passfail_str = {
        True: 'passed',
        False: 'failed',
    }

    def __init__(self, *args, name=None, pass_msg=None, fail_msg=None, invert=False, **kwargs):
        self.invert = invert
        self.name = name or self.name
        self._init_kwargs = kwargs
        self._init_args = args
        self._pass_msg = pass_msg or self._pass_msg or self._message
        self._fail_msg = fail_msg or self._fail_msg or self._message

        self._value = None
        self._was_run = False
        self._last_pf = None
        self._msg_context = {}
        self._run_kwargs = {}
        self._run_context = {}
        self._pass_msg_cache = None
        self._fail_msg_cache = None

    def pass_message(self):
        return self._pass_msg.format(**self._msg_context)

    def fail_message(self):
        return self._fail_msg.format(**self._msg_context)

    def message(self):
        if self._was_run:
            self._init_context()
            self._build_context()
            if self._last_pf:
                if self._pass_msg_cache is None:
                    self._pass_msg_cache = self.pass_message()
                return self._pass_msg_cache
            else:
                if self._fail_msg_cache is None:
                    self._fail_msg_cache = self.fail_message()
                return self._fail_msg_cache
        else:
            raise AttributeError('%s was not yet run' % self.name)

    def msg_dict(self):
        tmp_ret = dict(
            validator=self.name,
            passed=self._last_pf,
            msg=self.message(),
            args=self._run_args,
            kwargs=self._run_kwargs)
        return tmp_ret

    def _init_context(self):

        self._msg_context = self._init_kwargs.copy()
        self._msg_context.update({
            'name': self.name,
            'invert': self.invert,
            'value': self._value,
            'passfail': self._passfail_msg[self._last_pf],
            'passfail_str': self._passfail_str[self._last_pf],
            'is_isnot': self._is_isnot_str[self._last_pf],
            'long_name': self._long_name,
        })
        self._msg_context.update(self._run_kwargs)
        self._msg_context.update(self._run_context)

    def _build_context(self):
        pass

    def validate(self, value, *args, **kwargs):
        raise NotImplementedError

    def add_to_context(self, *args, **kwargs):
        for arg in args:
            self._run_context.update(arg)
        self._run_context.update(kwargs)

    def clear(self):
        self._run_context = {}
        self._was_run = True
        self._pass_msg_cache = None
        self._fail_msg_cache = None

    def __call__(self, value, *args, **kwargs):
        self.clear()
        self._value = value
        if args:
            self._run_args = args
        else:
            self._run_args = self._init_args

        if kwargs:
            self._run_kwargs = self._init_kwargs.copy()
            self._run_kwargs.update(kwargs)
        else:
            self._run_kwargs = self._init_kwargs

        if self.invert:
            self._last_pf = not self.validate(value, *self._run_args, **self._run_kwargs)
        else:
            self._last_pf = self.validate(value, *self._run_args, **self._run_kwargs)
        return self._last_pf

    def __str__(self):
        if self._was_run:
            return self.message()
        else:
            return self.__repr__

    def __repr__(self):
        return 'Validator: [Type: %s, Args: %s]' % (self.name, self._init_args)


class ValidateInstance(ValidatorBase):
    name = 'instance'
    _message = '{value_type} {is_isnot} an instance {ofin} {check_type}'

    def validate(self, value, *args, **kwargs):
        return isinstance(value, args)

    def _build_context(self):
        self._msg_context['value_type'] = self._value.__class__.__name__
        if len(self._init_args) > 1:
            self._msg_context['ofin'] = 'of one of'
            tmp_lst = []
            for arg in self._init_args or self._run_args:
                tmp_type = arg.__class__.__name__
                if tmp_type == 'type':
                    tmp_type = arg.__name__
                tmp_lst.append(tmp_type)
            self._msg_context['check_type'] = ', '.join(tmp_lst)
        else:
            self._msg_context['ofin'] = 'of'
            tmp_type = self._init_args[0].__class__.__name__
            if tmp_type == 'type':
                tmp_type = self._init_args[0].__name__
            self._msg_context['check_type'] = tmp_type


class ValidateNotEmpty(ValidatorBase):
    name = 'not_empty'
    _message = '{value} {is_isnot} empty'
    _is_isnot_str = {
        True: 'is not',
        False: 'is',
    }

    def validate(self, value, *args, **kwargs):
        tmp_ret = True
        for arg in args:
            if value is arg:
                tmp_ret = False
                break
        return tmp_ret


class ValidateEmpty(ValidatorBase):
    name = 'empty'
    _message = '{value} {is_isnot} empty'

    def validate(self, value, *args, **kwargs):
        tmp_ret = False
        for arg in args:
            if value is arg:
                tmp_ret = True
                break
        return tmp_ret


class ValidateIn(ValidatorBase):
    name = 'in'
    _message = '{value} {is_isnot} in {check_type}'

    def validate(self, value, *args, **kwargs):
        if isinstance(args[0], (list, tuple, ChoicesHelper)):
            comp_list = args[0]
        else:
            comp_list = args
        return value in comp_list

    def _build_context(self):
        if isinstance(self._run_args[0], (list, tuple)):
            comp_list = self._run_args[0]
        else:
            comp_list = self._run_args

        self._msg_context['check_type'] = repr(comp_list)


class ValidateBetween(ValidatorBase):
    name = 'between'
    _message = '{value} {is_isnot} between {min_val} and {max_val}'

    def validate(self, value, *args, **kwargs):
        return args[0] < value < args[1]

    def _build_context(self):
        self._msg_context['min_val'] = self._run_args[0]
        self._msg_context['max_val'] = self._run_args[1]


class ValidateSubClass(ValidatorBase):
    name = 'instance'
    _pass_msg = '{value_type} is a subclass of {check_type}'
    _fail_msg = '{value_type} is not an subclass of {check_type}'

    def validate(self, value, *args, **kwargs):
        return issubclass(value.__class__, args)

    def _build_context(self):
        self._msg_context['value_type'] = self._value.__class__.__name__
        tmp_type = self._init_args[0].__class__.__name__
        if tmp_type == 'type':
            tmp_type = self._init_args[0].__name__
        self._msg_context['check_type'] = tmp_type


class ValidateEq(ValidatorBase):
    name = 'eq'
    _pass_msg = '{value} {passfail_str} {check_val}'
    _fail_msg = '{value} {passfail_str} {check_val}'

    _passfail_str = {
        True: 'equals',
        False: 'does not equal'
    }

    def validate(self, value, *args, **kwargs):
        return value == args[0]

    def _build_context(self):
        self._msg_context['check_val'] = self._run_args[0]


class ValidateLt(ValidateEq):
    name = 'lt'
    _passfail_str = {
        True: 'less than',
        False: 'not less than'}

    def validate(self, value, *args, **kwargs):
        return value < args[0]


class ValidateGt(ValidateEq):
    name = 'gt'
    _passfail_str = {
        True: 'greater than',
        False: 'not greater than'}

    def validate(self, value, *args, **kwargs):
        return value > args[0]


class ValidateLte(ValidateEq):
    name = 'lte'
    _passfail_str = {
        True: 'less than or equal to',
        False: 'not less than or equal to'}

    def validate(self, value, *args, **kwargs):
        return value <= args[0]


class ValidateGte(ValidateEq):
    name = 'gte'
    _passfail_str = {
        True: 'greater than or equal to',
        False: 'not greater than or equal'}

    def validate(self, value, *args, **kwargs):
        return value >= args[0]


class ValidateStartsWith(ValidateEq):
    name = 'ends'
    _passfail_str = {
        True: 'starts with',
        False: 'does not start with'
    }

    def validate(self, value, *args, **kwargs):
        return value.startswith(args[0])


class ValidateEndsWith(ValidateEq):
    name = 'starts'
    _passfail_str = {
        True: 'ends with',
        False: 'does not end with'
    }

    def validate(self, value, *args, **kwargs):
        return value.endswith(args[0])


class ValidateTrue(ValidateEq):
    name = 'true'
    _passfail_str = {
        True: 'is true',
        False: 'is not true'
    }
    _pass_msg = '{value} {passfail_str}'
    _fail_msg = '{value} {passfail_str}'

    def validate(self, value, *args, **kwargs):
        return bool(value) == True


class ValidateFalse(ValidateTrue):
    name = 'false'
    _passfail_str = {
        True: 'is false',
        False: 'is not false'
    }

    def validate(self, value, *args, **kwargs):
        return bool(value) == False


class ValidateMaxLen(ValidateEq):
    name = 'is'
    _message = '{value} {is_isnot} longer than {check_val}'

    def validate(self, value, *args, **kwargs):
        return len(value) <= args[0]


class ValidateMinLen(ValidateEq):
    name = 'is'
    _message = '{value} {is_isnot} shorter than {check_val}'

    def validate(self, value, *args, **kwargs):
        return len(value) >= args[0]


class ValidateIs(ValidateEq):
    name = 'max_len'
    _message = '{value} {is_isnot} {check_val}'

    def validate(self, value, *args, **kwargs):
        return value is args[0]


class ValidateFuncWrapper(ValidatorBase):
    name = 'func'
    long_name = 'wrapped function'

    def validate(self, value, *args, **kwargs):
        return bool(args[0](value))


class ValidateMethod(ValidatorBase):
    name = 'meth'
    long_name = 'method wrapper'

    def validate(self, value, *args, **kwargs):
        tmp_item = getattr(value, args[0])
        if callable(tmp_item):
            return bool(tmp_item())
        else:
            return bool(tmp_item)


class ValidateRegex(ValidateEq):
    name = 'regex'
    _pass_msg = '{value} matches regex {check_val}'
    _fail_msg = '{value} does not match regex {check_val}'

    def __init__(self, *args, **kwargs):
        self._regex = None
        if args:
            if isinstance(args[0], re._pattern_type):
                self._regex = args[0]
            else:
                self._regex = re.compile(args[0])
            super().__init__(*args, **kwargs)

    def validate(self, value, *args, **kwargs):
        if args:
            if isinstance(args[0], re._pattern_type):
                self._regex = args[0]
            else:
                self._regex = re.compile(args[0])

        if not isinstance(value, str):
            value = str(value)
        else:
            value = value
        return bool(self._regex.fullmatch(value))


class ValidatorComplexBase(ValidatorBase):
    _msg_surround_pre = '('
    _msg_surround_post = ')'
    _msg_sep = ' AND '
    _and = True

    def __init__(self, *args, invert=False, **kwargs):
        super().__init__(*args, invert=invert, **kwargs)
        self._name = ''

        self._validators = {}
        self._validator_names = []

        self.add_validators(*args)

    def add_validators(self, *validators):
        for validator in validators:
            if validator.name in self._validator_names:
                validator.name = validator.name+str(len(self._validators)+2)
            self._validators[validator.name] = validator
            self._validator_names.append(validator.name)

        self._name = self._msg_sep.join(self._validator_names)
        self._name = self._name.replace(' ', '_')

    def pass_message(self, prefix=True):
        tmp_msg = []
        for val in self._validator_names:
            tmp_msg.append(self._validators[val].message(prefix=False))
        return self._prefix_msg+self._msg_surround_pre+self._msg_sep.join(tmp_msg)+self._msg_surround_post

    fail_message = pass_message

    def _init_context(self):
        pass

    def _build_context(self):
        pass

    def validate(self, value, *args, **kwargs):
        self._pass_msg_cache = None
        self._fail_msg_cache = None
        self._was_run = True
        tmp_pf_list = []
        for val in self._validator_names:
            tmp_args = []
            tmp_kwargs = {}
            if val in kwargs:
                tmp_ka = kwargs[val]
                if isinstance(tmp_ka, dict):
                    tmp_kwargs = tmp_ka
                elif isinstance(tmp_ka, (list, tuple)):
                    tmp_args = tmp_ka
                else:
                    tmp_args = [tmp_ka]
            tmp_pf_list.append(self._validators[val](value, *tmp_args, **tmp_kwargs))

        if self._and:
            self._last_pf = True
            for t in tmp_pf_list:
                if not t:
                    self._last_pf = False
                    break
        else:
            self._last_pf = False
            for t in tmp_pf_list:
                if t:
                    self._last_pf = True
                    break

        if self.invert:
            self._last_pf = not self._last_pf

        return self._last_pf

    __call__ = validate

    def __repr__(self):
        return 'Validator: [Type: %s]' % self.name


class ValidateAnd(ValidatorComplexBase):
    pass


class ValidateOr(ValidatorComplexBase):
    _msg_sep = ' OR '
    _and = False

COMP_LOOKUP = {
    'eq': {'val': ValidateEq, 'inv': False},
    'neq': {'val': ValidateEq, 'inv': True},
    'lt': {'val': ValidateLt, 'inv': False},
    'lte': {'val': ValidateLte, 'inv': False},
    'gt': {'val': ValidateGt, 'inv': False},
    'gte': {'val': ValidateGte, 'inv': False},
}

class ValidateComp(ValidatorComplexBase):

    def __init__(self, *args, invert=False, **kwargs):
        validators = []
        for val_key, arg in kwargs.items():
            tmp_val_rec = COMP_LOOKUP[val_key]
            tmp_kwargs = {'invert': tmp_val_rec['inv']}
            if isinstance(arg, dict):
                tmp_kwargs.update(arg)
            elif isinstance(arg, (list, tuple)):
                tmp_args = arg
            else:
                tmp_args = [arg]
            validators.append(tmp_val_rec['val'](*tmp_args, **tmp_kwargs))

        super().__init__(*validators, invert=invert)
