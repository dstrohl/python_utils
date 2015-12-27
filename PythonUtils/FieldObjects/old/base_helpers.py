__all__ = ['KeyedList', 'RegexMixin', 'ChoicesMixin', 'FieldDataAccess', 'FieldManager', 'ValidatorListHelper',
           'FuncListHelper', 'FuncQueue', 'FuncListBreak', 'ListRecord', 'DictRecord', 'ci_field_manager']

import re
from PythonUtils import make_list, unslugify
from CompIntel.Core import *
from .choices_helper import ChoicesHelper
from .exceptions import *
# from .field_manager import ci_field_manager
from PythonUtils import is_iterable
from copy import copy


class FieldManager(object):

    _fields = None
    _field_choices = None
    _field_ranking = None

    '''
    def __init__(self, *fields):
        self._fields = {}
        self._field_choices = []
        self.register_field(*fields)
        self._field_ranking = []
    '''

    @property
    def fields(self):
        if self._fields is None:
            self._fields = {}
        return self._fields
    
    @property
    def field_choices(self):
        if self._field_choices is None:
            self._field_choices = []
        return self._field_choices

    @property
    def field_ranking(self):
        if self._field_ranking is None:
            self._field_ranking = []
        return self._field_ranking

    def register_fields(self, *fields):
        for field in fields:
            self.fields[field.field_type] = field
            self.field_choices.append((field.field_type, field.field_type_name))
            self.field_ranking.append(dict(
                field_type=field.field_type,
                rank=field.detection_rank,
                coerce=False,
            ))
            if field.detection_coercable:
                self.field_ranking.append(dict(
                    field_type=field.field_type,
                    rank=field.detection_coerce_rank,
                    coerce=True,
                ))
        self.field_ranking.sort(key=lambda k: k['rank'])

    def detect_type(self, sample_data):
        for field in self.field_ranking:
            if self[field['field_type']].check_datatype(sample_data, try_coercing=field['coerce']):
                return field['field_type']
        raise UnknownDataTypeException(sample_data)

    def __getitem__(self, field):
        return self.fields[field]

    def __call__(self, field_type=None, **kwargs):
        tmp_field = self[field_type](**kwargs)
        return tmp_field

ci_field_manager = FieldManager()


class RegexMixin(object):
    regex = None

    def __init__(self, regex=None, **kwargs):
        if regex is not None:
            self.regex = re.compile(regex)
            self.validators.add(self._validate_regex)
        super().__init__(**kwargs)

    def _validate_regex(self, value):
        if self.regex is not None:
            if not isinstance(value, str):
                tmp_str = str(value)
            else:
                tmp_str = value
            if self.regex.fullmatch(tmp_str):
                return
            else:
                return _('does not match regex')
        return


class ChoicesMixin(object):

    def __init__(self,
                 choices=None,
                 choice_allow_edit=False,
                 choice_allow_unmatched=False, **kwargs):

        super().__init__(**kwargs)

        self.choice_allow_edit = choice_allow_edit
        self.choice_allow_unmatched = choice_allow_unmatched

        choices = choices or self.choices

        if choices is not None:
            if isinstance(choices, ChoicesHelper):
                self.choices = choices
            else:
                self.choices = ChoicesHelper(*choices)
            self.validators.add(self._validate_choices)
            # self.conversions.to_user.add(self._choices_update_to_user)

    def _validate_choices(self, value):
        if self.choices is None:
            return
        if self.choice_allow_edit:
            return
        if value in self.choices:
            return
        return _('Not in list of valid choices')

    @property
    def get_choices(self, selected=None):
        if self.choices is not None:
            selected = selected or self.get()
            return self.choices.choices(selected=selected)

    def _choice_user_string(self, value):
        if self.choices is None:
            return value
        else:
            try:
                return self.choices(value)
            except KeyError:
                if self.choice_allow_unmatched:
                    return value
                raise


    def get_user_text(self):
        return self._choice_user_string(self.get())


class FieldDataAccess(object):

    def __get__(self, obj, objtype):
        # return obj.pull_data()
        try:
            return obj._data_obj[obj._data_key]
        except KeyError:
            if obj.build_if_missing:
                obj._data_obj[obj._data_key] = obj.return_if_missing
                return obj._data_obj[obj._data_key]
            else:
                return obj.return_if_missing


    def __set__(self, obj, value):
        # obj.push_data(val)
        obj._data_obj[obj._data_key] = value
        obj.make_dirty()


class DictRecord(object):

    def __init__(self,
                 *fields,
                 parent=None,
                 data_in=None,
                 locked=False,
                 **kwargs):

        self._field_order_ = []

        self.parent_ = parent

        self._data_ = data_in
        self._locked_ = locked
        self._to_from_db_ = False
        self._dirty_ = False

        self._fields_ = {}
        self._to_from_db_ = True
        for field in fields:
            self.add_field(force=True, **field)

        self._to_from_db_ = False
        self._dirty_ = False

    def _get_field_(self, **kwargs):
        kwargs['parent'] = self
        kwargs['data_obj'] = self._data_
        return ci_field_manager(**kwargs)

    def add_field(self, name=None, value=None, force=False, **kwargs):
        if name is None:
            raise AttributeError('Name must be defined')
        if name not in self:        # Check to see if the field exists
            if self._locked_ and not force:
                raise AddFieldDisallowedException(name)
            else:
                if 'field_type' not in kwargs:
                    kwargs['field_type'] = ci_field_manager.detect_type(value)
                self._fields_[name] = self._get_field_(name=name, **kwargs)
                self._field_order_.append(name)

        if value is not None:
            self._fields_[name].set(value)
        elif self._fields_[name].build_if_missing and name not in self._data_:
            self._data_[name] = self._fields_[name].return_if_missing
        self._dirty_ = True

    def rem_field(self, key, keep_default=True):
        if key not in self:
            raise FieldDoesNotExistException(key)

        if self._fields_[key].default is None or not keep_default:
            del self._fields_[key]
            self._field_order_.remove(key)
            try:
                del self._data_[key]
            except KeyError:
                pass
        else:
            self._data_[key] = self._fields_[key].default

        self._dirty_ = True

    def update(self, *new_data):
        for data in new_data:
            for key, item in data.items():
                self.add_field(key, item)

    def pop(self, key, default=None, keep_default=False):
        tmp_ret = self.get(key, default)
        if key in self:
            self.rem_field(key, keep_default=keep_default)
        return tmp_ret

    def clear(self):
        for field in self.keys():
            self.rem_field(field)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def copy(self):
        tmp_ret = {}
        for key, field in self._fields_.items():
            tmp_ret[key] = field.get()
        return tmp_ret

    def items(self):
        tmp_ret = []
        for field in self._field_order_:
            tmp_ret.append((field, self._fields_[field].get()))
        return tmp_ret

    def keys(self):
        return copy(self._field_order_)

    def values(self):
        tmp_ret = []
        for field in self._field_order_:
            tmp_ret.append(self._fields_[field].get())
        return tmp_ret

    def __call__(self, key):
        return self._fields_[key]

    def __getitem__(self, key):
        try:
            return self._fields_[key].get()
        except KeyError:
            raise UnknownFieldException(key)

    def __setitem__(self, key, value):
        try:
            return self.add_field(name=key, value=value)
        except AddFieldDisallowedException:
            raise UnknownFieldException(key)

    def __len__(self):
        return len(self._fields_)

    def __iter__(self):
        for key in self._field_order_:
            yield key

    def __delitem__(self, key):
        self.rem_field(key, keep_default=False)

    def __contains__(self, key):
        return key in self._fields_


class KeyedList(object):

    def __init__(self, source_list=None):
        self._last_key_num = -1
        self._data = {}
        self._keys = []

        if source_list is None:
            self._source_list = []
        else:
            self._source_list = source_list
        for i in self._source_list:
            self.append(i, in_source=True)

    def get_key(self):
        self._last_key_num += 1
        return self._last_key_num

    def push(self):
        # tmp_list = []
        # for value in self:
        #     tmp_list.append(value)
        self._source_list.clear()
        self._source_list.extend(list(self))

    def append(self, item, in_source=False, key=None):
        if key is not None:
            key = key
        else:
            key = self.get_key()

        self._data[key] = item
        self._keys.append(key)
        if not in_source:
            self._source_list.append(item)
        return key


    def extend(self, *lists):
        for l in lists:
            for i in l:
                self.append(i)

    def keys(self):
        for key in self._keys:
            yield key, self._data[key]

    def reverse(self):
        self._keys.reverse()
        self._source_list.reverse()

    def __delitem__(self, key):
        del self._data[key]
        self._keys.remove(key)
        self.push()

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        if key in self._data:
            self._data[key] = value
            self.push()
        else:
            raise IndexError('no item for key %s' % key)

    def __iter__(self):
        for key in self._keys:
            yield self._data[key]


class ListRecord(object):
    def __init__(self,
                 field=None,
                 parent=None,
                 data_in=None,
                 max_len=None):

        self.parent_ = parent

        self._fields_ = {}

        self._data_ = KeyedList(data_in)

        self._dirty_ = False

        self._field_type_ = field
        self._field_type_['parent'] = self
        self._field_type_['data_obj'] = self._data_

        self._to_from_db_ = False
        self._max_len_ = max_len

        for k in self._k:
            self._add_field(k)

    '''
    def _get_field_(self, key):
        return ci_field_manager(data_key=key, **self._field_type_)
    '''

    def append(self, value):
        if self._max_len_ is not None and len(self) == self._max_len_:
            raise MaxListLenException(self._max_len_)
        # key = self._data_.append(value)
        key = self._data_.append(None)
        self._add_field(key)
        self._fields_[key].set(value)
        self._dirty_ = True
        return key

    def _add_field(self, key):
        self._fields_[key] = ci_field_manager(data_key=key, **self._field_type_)

    def push(self):
        self._data_.push()

    def extend(self, *items):
        for l in items:
            for i in l:
                self.append(i)

    def _rem_key(self, key):
        del self._fields_[key]
        del self._data_[key]
        self._dirty_ = True

    @property
    def _k(self):
        return self._data_._keys

    def _keyed_list(self):
        tmp_list = []
        for k in self._k:
            tmp_list.append((k, self._fields_[k].get()))
        return tmp_list

    def index(self, index):
        return self._data_[self._k[index]]

    def pop(self, index=None):
        if index is None:
            index = len(self._k)-1
        tmp_item = self.index(index)
        self.remove(index)
        return tmp_item

    def remove(self, index):
        self._rem_key(self._k[index])

    def count(self, value=None):
        if value is None:
            return len(self)
        tmp_ret = 0
        for item in self:
            if item == value:
                tmp_ret += 1
        return tmp_ret

    def fields(self):
        for i in self._fields_.values():
            yield i

    def sort(self):
        tmp_list = self._keyed_list()
        tmp_list.sort(key=lambda k: k[1])
        tmp_new_keys = []
        for k in tmp_list:
            tmp_new_keys.append(k[0])
        self._data_._keys = tmp_new_keys

    def insert(self, index, value):
        tmp_key = self.append(value)
        tmp_key = self._k.pop()
        self._k.insert(index, tmp_key)

    def reverse(self):
        self._k.reverse()

    def __iter__(self):
        for f in self._fields_.values():
            yield f.get()

    def __len__(self):
        return len(self._fields_)

    def __contains__(self, item):
        for i in self:
            if i == item:
                return True
        return False

    def __getitem__(self, item):
        tmp_keys = self._k[item]
        if isinstance(tmp_keys, (tuple, list)):
            tmp_ret = []
            for k in tmp_keys:
                tmp_ret.append(self._fields_[k].get())
            return tmp_ret
        else:
            return self._fields_[tmp_keys].get()

    def __setitem__(self, key, value):
        tmp_keys = self._k[key]
        if isinstance(tmp_keys, (tuple, list)):
            if not is_iterable(value):
                raise TypeError('can only assign an iterable when used with slicing notation')
            tmp_keys.reverse()
            for i in range(len(value)):
                try:
                    tmp_k = tmp_keys.pop()
                    self._fields_[tmp_k].set(value[i])

                except IndexError:
                    self.append(value[i])
        else:
            self._fields_[tmp_keys].set(value)

    def __delitem__(self, key):
        tmp_keys = self._k[key]
        if isinstance(tmp_keys, (tuple, list)):
            for k in tmp_keys:
                self._rem_key(k)
        else:
            self._rem_key(tmp_keys)
