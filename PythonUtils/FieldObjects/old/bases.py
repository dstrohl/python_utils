__all__ = ['KeyedList', 'BaseField', 'BaseDictField', 'BaseListField', 'ci_field_manager']

import re
from PythonUtils import make_list, unslugify
# from CompIntel.Core import *
from PythonUtils.ChoicesHelper import ChoicesHelper
from .exceptions import *
# from CompIntel.Core.mongo.fields import ci_field_manager
from .base_helpers import *



class BaseField(object):
    field_type = ''
    field_type_name = ''

    # Field Type Tags include 'basic', 'internal_only', 'leaf', 'branch', 'flex'
    tags = None

    default = None
    suggest = None
    choices = None
    _data_ = FieldDataAccess()

    _data_obj = None
    _data_key = None

    '''
    validators = FuncListHelper()
    to_mongo_modifiers = FuncListHelper()
    from_mongo_modifiers = FuncListHelper()
    to_user_modifiers = FuncListHelper()
    from_user_modifiers = FuncListHelper()
    '''

    _conversions_ = None
    _validators_ = None

    comparable = True

    """
    detection rank allows better descrimination between field types:
    Lower rank is selected over higher rank.

    Common ranks include:
        * 10  = specific types like name, email, and phone number
        * 25  = generally specific types like string, int, bool
        * 50  = coerced specific types like str(item), int(item)
        * 75 = flex types that can match almost anything.

    """
    detection_rank = 100
    detection_coercable  = False
    detection_coerce_rank = 100

    leaf_node = True

    def __init__(self,
                 name,
                 parent,
                 data_obj,
                 data_key=None,
                 required=False,
                 verbose_name=None,
                 verbose_plural_name=None,
                 help_text=None,
                 default=None,
                 build_if_missing=False,
                 return_if_missing=None,
                 read_only=False,
                 suggest=None,):
        self.build_if_missing = build_if_missing
        self.return_if_missing = return_if_missing or default

        self._read_only = read_only

        self._data_obj = data_obj

        if data_key is None:
            self._data_key = name
        else:
            self._data_key = data_key

        self.name = name
        self.required = required

        if verbose_name:
            self.verbose_name = verbose_name
        else:
            self.verbose_name = unslugify(name)

        self.verbose_plural_name = verbose_plural_name or self.verbose_name+'s'
        self.help_text = help_text or ''
        self.parent = parent
        self._to_from_db = False
        if required:
            self.validators.add(self._validate_required)

        if read_only:
            self.validators.add(self._validate_read_only)

        if default is not None:
            self.default = default
            self.suggest = default
            # self.conversions.to_db.add(self._return_default, priority=1)
            self.conversions.from_user.add(self._return_default, priority=1)

        elif self.choices is not None:
            if self.choices.default is not None:
                self.default = self.choices.default

        if self.default is None and suggest is not None:
            self.suggest = suggest

        if self.suggest is not None:
            self.conversions.to_user.add(self._suggest_to_user, priority=2)

    def match_tags(self, *tags):
        for tag in tags:
            if tag[0] == '-':
                if tag[1:] in self.tags:
                    return False
            else:
                if tag not in self.tags:
                    return False
        return True

    @property
    def conversions(self):
        if self._conversions_ is None:
            self._conversions_ = FuncQueue()
        return self._conversions_

    @property
    def validators(self):
        if self._validators_ is None:
            self._validators_ = ValidatorListHelper()
        return self._validators_

    def validate(self, value):
        fail_msg = self.validators.run(value)
        if fail_msg:
            raise FieldValidationException(self.name, fail_msg, value)

    @property
    def to_from_db(self):
        try:
            return self.parent._to_from_db_
        except AttributeError:
            return self._to_from_db

    def get(self, raw=False):
        """
        Gets info from the python object for the user or the db.
        :param raw:
        :return:
        """
        if raw:
            return self._data_

        if self.to_from_db:
            if self.conversions.to_db.has_ops:
                return self.conversions.to_db(self._data_)
            return self._data_
        else:
            if self.conversions.to_user.has_ops:
                return self.conversions.to_user(self._data_)
            return self._data_

    def set(self, value, raw=False, skip_validation=False):
        """
        Set info to the python object from the user OR the db.
        :param value:
        :param raw:
        :return:
        """
        if raw:
            self._data_ = value
        else:
            if self.to_from_db:
                self._data_ = self.conversions.from_db(value)

            else:
                if not skip_validation:
                    self.validate(value)
                tmp_value = self.conversions.from_user(value)
                if self.comparable:
                    if not self.compare(self._data_, tmp_value):
                        self._data_ = tmp_value
                        self.make_dirty()
                else:
                    self._data_ = tmp_value
                    self.make_dirty()

    def make_dirty(self):
        self.parent._dirty = True

    def is_empty(self, value):
        return value is None

    # ---------------------------------------------
    #  Conversions
    # ---------------------------------------------

    def _suggest_to_user(self, value):
        if self.is_empty(value):
            if self.suggest is None:
                return None
            else:
                return self.suggest
        return value

    def _return_default(self, value):
        if self.default and self.is_empty(value):
            raise FuncListBreak(self.default)
        return value

    def _validate_read_only(self, value):
        return ''



    def _validate_required(self, value):
        if self.is_empty(value):
            return _('is required (and nothing was entered)')


    '''
    def to_user(self, value):
        return self.conversions.to_user.run_modify(value)

    def from_user(self, value, raw=False, skip_validate=False):
        if raw:
            return value

        if self.default and self.is_empty(value):
            return self.default
        else:
            value = self.conversions.from_user.run_modify(value)

        if not skip_validate:
            self.validate(value)
        return value

    def to_db(self, value):
        if self.default and self.is_empty(value):
            return self.default
        elif self.conversions.to_db.has_ops:
            return self.conversions.to_db.run_modify(value)
        else:
            return value

    def from_db(self, value, raw=False):
        if raw:
            return value

        value = self.conversions.from_db.run_modify(value)
        return value

    '''
    def compare(self, old_version, new_version):
        return old_version == new_version

    def get_compare(self, old_version, new_version):
        msg = _('Old value: %s\nNew Value: %s') % (old_version, new_version)
        return msg

    @staticmethod
    def check_datatype(value, try_coercing=False):
        """
        Returns true if this can be used as a storage for "value"
        :param value:
        :param bool try_coercing: if set to True, will try casting or otherwise converting the value, if False, will
            only check to see if it works natively.
        :return:
        """
        return False

    def __repr__(self):
        tmp_str = '{}: {}'.format(self.__class__.__name__, self.name)
        return tmp_str


class BaseListField(BaseField):
    pass


class BaseDictField(BaseField):
    pass

