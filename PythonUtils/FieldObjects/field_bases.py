__all__ = ['RegexMixin', 'ChoicesMixin', 'BaseField', '_UNSET', 'StringField', 'IntegerField']

from PythonUtils import make_list, unslugify, UnSet
from PythonUtils.ChoicesHelper import ChoicesHelper
from .field_exceptions import *
from .field_operations import *
from PythonUtils.ConverterHelper import ConverterHelper
from PythonUtils.ValidatorHelper import *
from PythonUtils.Signals import SignalsSystem

_UNSET = UnSet()
converter_helper = ConverterHelper()
field_signal_helper = SignalsSystem()

class RegexMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'match_regex' in kwargs:
            self._validator.add_validators(ValidateRegex(kwargs['match_regex']))


class ChoicesMixin(object):
    _require_choice = True
    choices = None

    def __init__(self, *args, **kwargs):
        """
        :keyword choices:
        :keyword bool choice_require_choice: if True, will validate that the choice is in the choice list
        """
        super().__init__(*args, **kwargs)

        self._require_choice = kwargs.get('require_choice', self._require_choice)
        choices = kwargs.get('choices', self.choices)

        if choices is not None:
            if isinstance(choices, ChoicesHelper):
                self.choices = choices
            else:
                self.choices = ChoicesHelper(*choices)

            if self._require_choice:
                self._validator.add_validators(ValidateIn(self.choices))

            self._signals.to_user.add_function(self._to_user, priority=75)
            self._signals.from_user.add_function(self._from_user, priority=75)

    def get_choices(self, value=None):
        if self.choices is not None:
            value = self._check_default(value)
            return self.choices.choices(selected=value)
        else:
            return None

    @staticmethod
    def _from_user(value, field_rec, *kwargs):
        if field_rec.choices is None:
            return value
        else:
            return field_rec.choices.get(value, default=value, is_display=True)


    @staticmethod
    def _to_user(value, field_rec, *kwargs):
        if field_rec.choices is None:
            return value
        else:
            return field_rec.choices.get(value, default=value)

    def get_user_string(self, value, default=_UNSET):
        if default is _UNSET:
            return self.choices(value)
        else:
            return self.choices.get(value, default=default)


class MinMaxLengthMixin(object):
    _min_len = None
    _max_len = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._min_len = kwargs.get('min_len', self._min_len)
        self._max_len = kwargs.get('max_len', self._max_len)
        if self._min_len is not None:
            self._validator.add_validators(ValidateMinLen(self._min_len))
        if self._max_len is not None:
            self._validator.add_validators(ValidateMaxLen(self._max_len))
    

class MinMaxValueMixin(object):
    _min_value = None
    _max_value = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._min_value = kwargs.get('min', self._min_value)
        self._max_value = kwargs.get('max', self._max_value)
        if self._max_value is not None:
            self._validator.add_validators(ValidateLte(self._max_value))
        if self._min_value is not None:
            self._validator.add_validators(ValidateGte(self._min_value))


class BaseField(object):
    # SET_TO_UNSET = 'replace_with_unset'
    # SET_TO_DEFAULT = 'set_to_default'
    # STORE = 'store'
    # RAISE = 'raise'
    # CONVERT = 'convert'

    # sub-class overrides
    _type_name = 'base'
    _type_long_name = 'base field'

    _default_valid_instances = [str]  # used for validating type and coercing/comparing (unless overridden)

    comparable = True  # can be compared to know if an object changed

    """
    detection rank allows better discrimination between field types:
    Lower rank is selected over higher rank.

    Common ranks include:
        * 10 = specific types like name, email, and phone number
        * 25 = generally specific types like string, int, bool
        * 50 = coerced specific types like str(item), int(item)
        * 75 = flex types that can match almost anything.

    """
    detection_rank = 100
    detection_coercable = True
    detection_coerce_rank = 100
    coerce = str

    leaf_node = True
    
    # kwarg defaults
    _default_empty_value = _UNSET
    _default_save_default = False
    _default_default = _default_empty_value
    _default_required = False
    _default_read_only = False
    _default_validate_type = True
    # _default_none_from_user = _default_default
    _default_user_system = 'sys_dict'
    _default_db_system = 'sys_dict'
    _default_allow_none = False

    # For ConverterHelper conversions
    _local_format = 'str'
    # _none_from_db = _default_empty_value
    # _none_from_db_raise = False

    
    def __init__(self, name=None, **kwargs):
        """
        :param name: The fieldname for this object
        :keyword default: This value will be used if no other value is set.
        :keyword bool read_only: This value can only be set from the db or in code, not by user interaction
        :keyword bool required: If True, this field must be filled in
        :keyword bool save_default: (Default: False) If True, the default value will be saved to the db if empty
        :keyword suggest: If present, will provide a value to be suggested to the user.
        :keyword bool validate_type: (default False) If true, will validate the datatype passed with ``_valid_instance``
        :keyword ValidatorBase validators: these will be added to any other validators needed
        :keyword empty_value: the value considered empty, normally _UNSET, but could be None or ''
        :keyword bool allow_none: (default: False) If True, none can be used as a valid value.
        :keyword Signals field_signal_helper: if set, will override the default field signaling system

        Pre-set signal priorities:
        +--------------------+---------+-----------+-------+---------+
        | Function           | from_db | from_user | to_db | to_user |
        +====================+=========+===========+=======+=========+
        | Raise on Read_Only |         |     10    |       |         |
        +--------------------+---------+-----------+-------+---------+
        | Fix None           |    20   |     20    |       |         |
        +--------------------+---------+-----------+-------+---------+
        | Fix None + convert |    20   |     20    |       |         |
        +--------------------+---------+-----------+-------+---------+
        | Make unset default |         |           |  30   |   30    |
        +--------------------+---------+-----------+-------+---------+
        | Make default unset |         |     30    |       |         |
        +--------------------+---------+-----------+-------+---------+
        | Convert            |    70   |     70    |   70  |   70    |
        +--------------------+---------+-----------+-------+---------+
        | Validate           |         |     90    |       |         |
        +--------------------+---------+-----------+-------+---------+


        """
        
        self._signals = kwargs.get('field_signal_helper', SignalsSystem())
        self._signals.register_signal('from_user', loop_arg=0)        
        self._signals.register_signal('from_db', loop_arg=0)        
        self._signals.register_signal('to_user', loop_arg=0)        
        self._signals.register_signal('to_db', loop_arg=0)        

        # set defaults and base field settings
        self._fieldname = name or self._type_name
        self.suggested_value = kwargs.get('suggest', _UNSET)
        self._valid_instances = self._default_valid_instances.copy()
        self._user_system = kwargs.get('user_system', self._default_user_system)
        self._db_system = kwargs.get('db_system', self._db_system)

        self._converter = converter_helper
        self._validator = Validator(fieldname=name)

        # handle readonly fields
        self._read_only = kwargs.get('read_only', self._default_read_only)
        if self._read_only:
            self._signals.from_user.add_function(raise_on_read_only, priority=10)

        # handle default and empty values
        self._empty_value = kwargs.get('empty_value', self._default_empty_value)
        try:
            self._default = kwargs['default']
            self._signals.from_user.add_function(default_to_unset, priority=30)
            self._signals.to_user.add_function(unset_to_default, priority=30)
            self._has_default = True
            self._save_default = kwargs.get('save_default', self._default_save_default)
            if self._save_default:
                self._signals.to_db.add_function(unset_to_default, priority=30)
                self._signals.from_db.add_function(default_to_unset, priority=30)
        except KeyError:
            self._has_default = False

        # handle None objects
        # self._none_from_user = kwargs.get('none_from_user', self._default_none_from_user)
        # self._signals.from_db.add_function(fix_none_from_db, priority=20)

        self._allow_none = kwargs.get('allow_none', self._default_allow_none)
        if self._allow_none:
            self._valid_instances.append(None.__class__)
        else:
            self._signals.from_user.add_function(none_to_empty, priority=20)
            self._signals.from_db.add_function(none_to_empty, priority=20)

        # setup validators
        self._empty_types = [self._empty_value]

        self._required = kwargs.get('required', self._default_required)
        if self._required:
            self._validator.add_validators(ValidateNotEmpty(*self._empty_types))
        else:
            self._valid_instances.append(self._empty_value.__class__)

        if 'validators' in kwargs:
            self._validator.add_validators(*make_list(kwargs['validators']))

        self._type_validator = ValidateInstance(*self._valid_instances, name='validate_instance')

        self._validate_type = kwargs.get('validate_type', self._default_validate_type)
        if self._validate_type:
            self._validator.add_validators(self._type_validator)

        self._signals.from_user.add_function(validate_from_user, priority=90)

        # setup converters
        self._signals.from_user.add_function(convert_from_user, priority=70)
        self._signals.to_user.add_function(convert_to_user, priority=70)
        self._signals.from_db.add_function(convert_from_db, priority=70)
        self._signals.to_db.add_function(convert_to_db, priority=70)

    '''
    def _make_conv_kwargs(self, kwarg_val):

        tmp_ret = {}
        if kwarg_val == self.STORE:
            tmp_ret['return_none_as'] = None
        elif kwarg_val == self.SET_TO_DEFAULT:
            tmp_ret['return_none_as'] = self._default
        elif kwarg_val == self.SET_TO_UNSET:
            tmp_ret['return_none_as'] = self._empty_value
        elif kwarg_val == self.RAISE:
            tmp_ret['return_none_as'] = None
        return tmp_ret
    '''
    
    def is_empty(self, value):
        for item in self._empty_types:
            if value == item:
                return True
        return False

    def _check_default(self, value):
        if self._has_default and self.is_empty(value):
            value = self._default
        return value

    def to_user(self, value, raw=False, **kwargs):
        if raw:
            return value
        else:
            '''
            value = self._check_default(value)
            to = system or self._user_system
            value = self._converter(value, fr=self._local_format, to=to)
            value = self._to_user_conv(value)
            return value
            '''
            return self._signals.to_user(value, self, **kwargs)

    def from_user(self, value, raw=False, validate=True, **kwargs):
        '''
        if self._read_only:
            raise FieldReadOnlyException(self._fieldname)

        fr = system or self._user_system
        value = self._converter(value, to=self._local_format, fr=fr, **self._from_user_kwargs)
        value = self._from_user_conv(value)

        if validate:
            if self._validator(value):
                if self._has_default and value == self._default:
                    value = self._empty_value
                return value
            else:
                raise FieldValidationException(self._fieldname, self._validator.msgs)
        else:
            return value
        '''

        if raw:
            return value
        else:
            if validate:
                return self._signals.from_user(value, self, **kwargs)
            else:
                return self._signals.from_user(value, self, func_max_pri=89, **kwargs)

    def to_db(self, value, raw=False, **kwargs):
        '''
        if raw:
            return value
        else:
            to = system or self._db_system
            value = self._converter(value, fr=self._local_format, to=to)
            if self._save_default and self.is_empty(value):
                value = self._default
            return value
        '''
        if raw:
            return value
        else:
            return self._signals.to_db(value, self, **kwargs)

    def from_db(self, value, raw=False, **kwargs):
        '''
        if raw:
            return value

        fr = system or self._db_system
        return self._converter(value, to=self._local_format, fr=fr, **self._from_db_kwargs)
        '''
        if raw:
            return value
        else:
            return self._signals.from_db(value, self, **kwargs)

    def _compare(self, a, b):
        return a == b

    def compare(self, a, b, **kwargs):
        """
        :param a:
        :param b:
        :keyword on_error:
            True: will return true if the objects cannot be compared
            False: will return False if the objects cannot be compared
            Not passed: will raise exception if the objects cannot be compared
            (note: based on the ``comparable`` field, func will still raise exception if different types
            of values are compared.)
        :return:
        """
        if not self.comparable:
            if 'on_error' in kwargs:
                return kwargs['on_error']
            else:
                raise UncomparableFieldsException('%s object types cannot be compared' % self._type_name)
        else:
            return self._compare(a, b)

    def valid_object_type(self, value, validate=True):
        if validate and self._validate_type and self._validator(value):
            return True
        elif validate and self._validator(value) and self._type_validator(value):
            return True
        elif self._type_validator(value):
            return True
        return False

    def valid_coerceable_type(self, value, validate=True):
        try:
            tmp_value = self.coerce(value)
        except:
            return False

        if validate:
            return self._validator(tmp_value)

        return False

class StringField(MinMaxLengthMixin, RegexMixin, ChoicesMixin, BaseField):
    # sub-class overrides
    _type_name = 'str'
    _type_long_name = 'String Field'
    detection_rank = 25

    # For ConverterHelper conversions
    _local_format = 'str'
    _user_system = 'sys_dict'
    _db_system = 'sys_dict'


class IntegerField(MinMaxValueMixin, ChoicesMixin, BaseField):
    _type_name = 'int'
    _type_long_name = 'Integer Field'
    detection_rank = 25
    _default_valid_instances = [int]

    # For ConverterHelper conversions
    _local_format = 'int'
    _user_system = 'sys_dict'
    _db_system = 'sys_dict'
