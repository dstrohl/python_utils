__all__ = ['FlexField', 'ShortStringField', 'BooleanField', 'IntegerField', 'ListOfField', 'DictOfField']
import re
from PythonUtils import make_list
from CompIntel.Core import *
from CompIntel.helpers import ChoicesHelper
from .exceptions import *
from .bases import *
from .base_helpers import *

TRUE_FALSE = {
    'true': True,
    'True': True,
    'false': False,
    'False': False,
    _('Yes'): True,
    _('yes'): True,
    _('No'): False,
    _('no'): False
}


class FlexField(BaseField):
    field_type = 'flex'
    field_type_name = 'Flexible Field'
    tags = ('flex', 'internal_only')


class ListOfField(BaseListField):
    pass


class DictOfField(BaseDictField):
    pass


class ShortStringField(RegexMixin, ChoicesMixin, BaseField):
    field_type = 'short_string'
    field_type_name = 'Short String'
    tags = ('basic', 'leaf')

    detection_rank = 25
    detection_coercable  = True
    detection_coerce_rank = 50

    def __init__(self, max_length=None, min_length=None, **kwargs):
        self.max_length = max_length
        self.min_length = min_length
        self.validators.add(self._string_validate)
        super().__init__(**kwargs)

    def _string_validate(self, value):
        fail_msg = []
        if not isinstance(value, str):
            fail_msg.append(_('is not a string'))
        if self.min_length and len(value) < self.min_length:
            fail_msg.append(_('is too short, min length is ')+str(self.min_length))
        if self.max_length and len(value) > self.max_length:
            fail_msg.append(_('is too long, max length is ')+str(self.max_length))
        return fail_msg

    def is_empty(self, value):
        return value is None or value == ''

    @staticmethod
    def check_datatype(value, try_coercing=False):
        if not try_coercing:
            return isinstance(value, str)
        try:
            tmp = str(value)
        except TypeError:
            return False
        return True


class IntegerField(RegexMixin, ChoicesMixin, BaseField):
    field_type = 'integer'
    field_type_name = 'Integer'
    tags = ('basic', 'leaf')

    detection_rank = 25
    detection_coercable  = True
    detection_coerce_rank = 50

    def __init__(self, max=None, min=None, **kwargs):
        self.max = max
        self.min = min
        self.validators.add(self._int_validate)
        super().__init__(**kwargs)

    def _int_validate(self, value):
        fail_msg = []
        if not isinstance(value, int):
            fail_msg.append(_('is not an integer'))
        if self.min and value < self.min:
            fail_msg.append(_('is too low, min is ')+str(self.min))
        if self.max and value > self.max:
            fail_msg.append(_('is too high, max is ')+str(self.max))
        return fail_msg

    @staticmethod
    def check_datatype(value, try_coercing=False):
        if not try_coercing:
            return isinstance(value, int)
        try:
            tmp = int(value)
        except ValueError:
            return False
        return True
    

class BooleanField(ChoicesMixin, BaseField):
    field_type = 'boolean'
    field_type_name = 'Boolean'
    tags = ('basic', 'leaf')

    detection_rank = 25
    detection_coercable  = True
    detection_coerce_rank = 50


    choices = ChoicesHelper((True, _('Yes')), (False, _('No')))

    comparable = True

    def __init__(self, **kwargs):
        self.validators.add(self._bool_validate)
        super().__init__(**kwargs)

    def _bool_validate(self, value):
        """
        :param value:
        :return: Returns a list of validation errors, or [] (or None) if no errors found.
        """
        fail_msg = []
        if not isinstance(value, bool):
            fail_msg.append(_('value is not boolean'))
        return fail_msg

    @staticmethod
    def check_datatype(value, try_coercing=False):
        """
        Returns true if this can be used as a storage for "value"
        :param value:
        :param bool try_coercing: if set to True, will try casting or otherwise converting the value, if False, will
            only check to see if it works natively.
        :return:
        """
        if not try_coercing:
            return isinstance(value, bool)
        else:
            return isinstance(value, bool) or value in TRUE_FALSE

    def get_compare(self, old_version, new_version):
        old_version = self.choices(old_version)
        new_version = self.choices(new_version)
        msg = _('Old value: %s\nNew Value: %s') % (old_version, new_version)
        return msg


class IdField(BaseField):
    field_type = '_id'
    field_type_name = 'Document ID'

    # Field Type Tags include 'basic', 'internal_only', 'leaf', 'branch', 'flex'
    tags = ['system']
    detection_rank = 100
    detection_coercable  = False
    detection_coerce_rank = 100

    leaf_node = True

    def __init__(self, **kwargs):
        kwargs['name'] = '_id'
        kwargs['verbose_name'] = 'Document ID'
        kwargs['verbose_plural_name'] = 'Document IDs'
        kwargs['build_if_missing'] = False
        kwargs['read_only'] = True
        super().__init__(**kwargs)

