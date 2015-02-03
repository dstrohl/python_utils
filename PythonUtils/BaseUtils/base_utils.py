__author__ = 'dstrohl'
"""
Utilities that need no local imports
"""

__all__ = ['args_handler', 'GenericMeta', 'DictKey2Method', 'AdvDict', 'FilterFieldError', 'Filter', 'DBList',
           'TreeDict', 'TreeItem', 'make_list', 'flatten', 'unpack_class_method', 'get_between', 'get_after',
           'get_before', 'get_not_in', 'get_same', 'get_meta_attrs', 'remove_dupes', 'list_in_list', 'list_not_in_list',
           'count_unique', 'index_of_count', 'ListPlus', 'LookupManager', 'is_iterable', 'is_string', 'if_list',
           'OrderedSet', 'Clicker', 'Flagger', 'swap', 'replace_between', 'format_as_decimal_string',
           'IntelligentFormat', 'find_enclosed', 'find_in', 'check_in', 'elipse_trim', 'concat']

import copy
import sys
import collections
from string import Formatter
from decimal import Decimal

# from PythonUtils.ListUtils.list_plus import ListPlus
# from django.utils.text import slugify
# from PythonUtils.TextUtils import is_string


# ===============================================================================
# Generate Percentages
# ===============================================================================


def generate_percentages(data_array, row_fieldname, data_fieldname, newfieldname=""):
    '''
    assumes data_array will be in the format of:
    [
    { 'row_fieldname' : [{field1:data1, field2,data2, field3:data3},{field1:data1, field2,data2, field3:data3},{field1:data1, field2,data2, field3:data3}]}

    ]
    if no newfieldname, fieldname is replaced with percentages
    if fieldnames are numeric, a set is assumed instead of a dict
    if new_fieldname is numeric, the data will be inserted at that position (zero based).

    '''

    for col in range(len(data_array[1][row_fieldname])):

        col_total = 0
        print('new col')
        for row in range(len(data_array)):
            rec = data_array[row][row_fieldname][col]
            # print( rec )
            col_total = col_total + rec[data_fieldname]
            print(col_total)

        for row in range(len(data_array)):
            rec = data_array[row][row_fieldname][col][data_fieldname]
            try:
                rec_perc = rec / col_total
            except ZeroDivisionError:
                rec_perc = 0

            if newfieldname:
                data_array[row][row_fieldname][col][newfieldname] = rec_perc
            else:
                data_array[row][row_fieldname][col][data_fieldname] = rec_perc


                # print( rec_perc )

    print(data_array)

    return data_array

# ===============================================================================
# Generate Percentages
# ===============================================================================


def args_handler(parent_obj,
                 args=None,
                 attr_list=None,
                 kwargs=None,
                 skip_list=None,
                 skip_startswith='_',
                 overwrite=True,
                 do_not_check_parent_attrs=False):
    """
    Args Handler that will take an args or kwargs list and set contents as attributes.  This also allows some control
    over which values to set

    :param parent_obj: the object that gets the attributes
    :param args: a list from the args parameter
    :param kwargs: a dict from the kwargs parameter
    :param attr_list: a list of the attributes to use, required if args are passed
        * if the attribute '_attr_list' exists in the parent object, this will be used.
        * if an attr_list exists for kwargs dicts, only the keys in the args list will be included.
        * if there are more items in the args list than in the attr list, only the ones in the list will be used.
        * if there are more items in the attr list than in the args list, only the ones in the args list will be used.
        * if both args and kwargs are passed, the attr list will ONLY be used for the args
        * if the same attr is in both args and kwargs, kwargs will take precedence.
        * if the attribute name starts with a /*, (star) it will be required and a AttributeError will be raised
            if it is not found in either the args or kwargs.
        * if a list of tuples can be passed to handle default settings, these should be in the format of:
            ('attribute name',default_setting)
            not all items need to be tuples, you can mix and match strings and tuples for fields with no requirement.
    :param skip_list: a list of attributes to skip
        * if the attribute '_args_skip_list' exists in the parent object, this will be used.
    :param skip_startswith: skip attributes that start with this string (defaults to '_')
        * if the attribute '_args_skip_startswith' exists in the parent object, this will be used.
    :param overwrite: overwrite existing attributes, can be set to False if you do not want to update existing attributes
        * if the attribute '_args_overwrite' exists in the parent object, this will be used.
    :param do_not_check_parent_attrs: will not check parent attributes for skip parameters.  (used when these fields are
        in use in the parent object for something else)
        * this only happens if the parameter is not passed, otherwise the check is skipped.
    """

    def _save(save_arg, save_attr, clean_default=True):
        if _check(save_attr):
            setattr(parent_obj, save_attr, save_arg)
            if clean_default:
                try:
                    del attr_defaults[save_attr]
                except KeyError:
                    pass

    def _check(check_attr, check_present=True):
        if check_present:
            if not check_attr.startswith(skip_startswith) and check_attr not in skip_list:
                return overwrite or not hasattr(parent_obj, check_attr)
            return False
        else:
            return check_attr.startswith(skip_startswith) and check_attr not in skip_list

    def _args_list_iterator():
        for tmp_attr, tmp_arg in zip(attr_list, args):
            try:
                if tmp_attr in kwargs:
                    continue
            except TypeError:
                pass
            _save(tmp_arg, tmp_attr)

    def _args_dict_by_attrs():
        for tmp_attr in attr_list:
            try:
                _save(kwargs[tmp_attr], tmp_attr)
            except KeyError:
                pass

    def _args_dict_iterator(args_dict, clean_default=True):
        for tmp_attr, tmp_arg in args_dict.items():
            _save(tmp_arg, tmp_attr, clean_default)

    if not do_not_check_parent_attrs:
        attr_list = getattr(parent_obj, '_attr_list', attr_list)
        skip_list = getattr(parent_obj, '_args_skip_list', skip_list)
        skip_startswith = getattr(parent_obj, '_args_skip_startswith', skip_startswith)
        overwrite = getattr(parent_obj, '_args_overwrite', overwrite)

    if skip_list is None:
        skip_list = []


    attr_defaults = {}

    # ---- verify required fields and build defaults list from tuples ------
    if attr_list:
        if args:
            arg_cnt = len(args)
        else:
            arg_cnt = 0

        tmp_attr_list = []
        for offset, attr in enumerate(attr_list):
            if isinstance(attr, tuple):
                attr_defaults[attr[0]] = attr[1]
                attr = attr[0]
            attr = str(attr)
            if attr[0] == '*':
                attr = attr[1:]

                attr_found = False
                if attr in kwargs:
                    attr_found = True
                if offset <= arg_cnt:
                    attr_found = True

                if not attr_found:
                    raise AttributeError('ArgsHandler: Required attribute '+attr+' is not found in args or kwargs')

            tmp_attr_list.append(attr)

        attr_list = tmp_attr_list

    if attr_list is None and args:
        raise AttributeError('ArgsHandler: if args are passed, args list must not be empty')

    if kwargs:
        if attr_list and not args:
            _args_dict_by_attrs()
        else:
            _args_dict_iterator(kwargs)

    if args:
        _args_list_iterator()

    _args_dict_iterator(attr_defaults, clean_default=False)

# ===============================================================================
# Generic Meta Object
# ===============================================================================

class GenericMeta(object):

    def get_meta_attrs(self, parent_obj, skip_list = [], skip_startswith = '_', overwrite = True):
        for attr, value in iter(self.__dict__.items()):
            if not attr.startswith(skip_startswith) and attr not in skip_list:
                if not hasattr(parent_obj,attr) or overwrite:
                    setattr(parent_obj,attr,value)

def get_meta_attrs(meta, parent_obj, skip_list = [], skip_startswith = '_', overwrite = True):
    for attr in dir(meta):
        if not attr.startswith(skip_startswith) and attr not in skip_list:
            if not hasattr(parent_obj,attr) or overwrite:
                tmp_value = getattr(meta,attr)
                setattr(parent_obj,attr,tmp_value)


def get_meta_attrs2(meta, parent_obj, skip_list = [], skip_startswith = '_', overwrite = True):
    for attr, value in iter(meta.__dict__.items()):
        if not attr.startswith(skip_startswith) and attr not in skip_list:
            if not hasattr(parent_obj,attr) or overwrite:
                setattr(parent_obj,attr,value)


# ===============================================================================
# Generic Meta Object
# ===============================================================================


def quarter_calc(*args):
    arg = []
    for a in args:
        arg.append(int(a))

    if len(args) == 1:
        response_item = {}
        if arg[0] % 1 == 0:
            qtr = arg[0] % 4
            yr = 2000 + ( ( arg[0] - qtr ) / 4 )
            qtr = qtr + 1
            response_item['year'] = yr
            response_item['quarter'] = qtr
            response_item['word'] = '{year}-Q{quarter}'.format(**response_item)

        return response_item


    elif ( len(args) ) == 2:
        response_item = 0
        if arg[0] > 4:
            yr = arg[0]
            qt = arg[1]
        else:
            yr = arg[1]
            qt = arg[0]

        return ( ( yr - 2000 ) * 4 ) + ( qt - 1 )

    return ""


# ===============================================================================
# Dictionary Helper Objects
# ===============================================================================


class DictKey2Method(object):
    """
    creates a dictionary that the keys are available as properties
    """

    def __init__(self, mydict):
        self.mydict = mydict

    def __getattr__(self, item):
        try:
            return self.mydict[item]
        except KeyError:
            raise KeyError(item, ' is not a valid key for this dictionary')

    def __setattr__(self, key, value):
        if key in ('mydict',):
            self.__dict__[key] = value
        else:
            self.mydict[key] = value


class AdvDict(dict):
    """
    A dictionary that allows you to access contents as if they were methods.

    :param property_name: The name of the property to use to access the fields.
        Default = 'key'

    Example:

    >>> d = AdvDict()
    >>> d['one'] = 1
    >>> d['two'] = 2
    >>> d['three'] = 3
    >>> d.key.one
    1

    >>> d = AdvDict(property_name='number')
    >>> d['one'] = 1
    >>> d['two'] = 2
    >>> d['three'] = 3
    >>> d.number.two
    2
    """
    def __init__(self, *args, **kwargs):
        property_name = kwargs.pop('property_name', 'key')
        super(AdvDict, self).__init__(*args, **kwargs)
        setattr(self, property_name, DictKey2Method(self))

# ===============================================================================
# Filter Objects
# ===============================================================================

class FilterFieldError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Filter(object):
    """
    Will provide filtering options.  This is expandable and more filter types can be added below or by subclassing
    if adding filter types, make sure to update the _filter_types property below with the valid filter_type name.
    """

    _filter_types = ('eq', 'ne', 'gt', 'lt', 'in', 'nin', 'gte', 'lte', 'not', 'is', 'instance_of')
    _filter_field_type_options = ('list_field', 'dict_key', 'attribute', 'auto')
    _keep_filter_set_cache = False
    _keep_filter_kwargs_cache = False
    _complex_filter = False

    _filter_field_type = 'auto'
    _list_item_key = '__list_item__'
    _key_enclosure = '__'
    _filter_with = 'and'

    def __call__(self, *args, **kwargs):
        return self.filter_list(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        """
        :param filter_field_type:
        :param list_item_key:
        :param key_enclosure:
        :param filter_with:
        """
        if args or kwargs:
            self._parse_filter_args(args, kwargs)
            if args:
                self._keep_filter_set_cache = True
            if kwargs:
                self._keep_filter_kwargs_cache = True

    def set_filter(self, *args, **kwargs):
        if args or kwargs:
            self._parse_filter_args(args, kwargs)
            if args:
                self._keep_filter_set_cache = True
            if kwargs:
                self._keep_filter_kwargs_cache = True

    def filter_list(self, list_to_filter, *args, **kwargs):
        """

        Returns an iterator from a list passed that is filtered by the filter definition

        :param list_to_filter: the list of items to filter
        :param args: the filter or filter_set
        :param filter_with: ['and'/'or'] defines how multiple filters will be compared.
        :param filter_field_type: can be any of the following:
            * 'auto'        : the system will try to detect what is being filtered itself, if this does not work,
            full control can be had by changing this.
            * 'list_field'  : indicates that this is filtering a simple list.
            * 'dict_key'    : will pass the item key to a dict like object and filter on the returned item.
            * 'attribute'   : will filter based on the attribute of the object in the list as defined in the filter.

        :param list_item_key: if this is a list field, this is the string that will be replaced by the list item
        :param key_enclosure: if dict_key or attribute, this is the
        :return: an iterator that only contains the items filtered.

        Filter definition options:

        * FILTER_BY             : will assume a simple list to filter and will compare each item with the 'eq' filter
        * FIELD_KEY_STRING      : will check using the 'is' filter.
        * ( FIELD_KEY_STRING, ) : same as above, but can be chained in a list
        * FILTER_BY, XX         : will assume a simple list to filter and will compare each item with the passed filter
        * FILTER_BY, FIELD_KEY_STRING  : will compare the field as defined by the key string with the filter by object assuming the 'eq' filter
        * ( FILTER_BY, FILTER_KEY_STRING ) : same as above, but can be chained in a list.
        * FILTER_BY, XX, FIELD_KEY_STRING : will compare the field with the filter object using the passed filter type
        * ( FILTER_BY, XX, FIELD_KEY_STRING ) same as above, but can be chained in a list
        * [ ( FILTER_BY, XX, FIELD_KEY_STRING ), ( FILTER_BY, XX, FIELD_KEY_STRING ), ... ] : will filter using all sets in the list
            combining them using the filter_with logic (and/or).

        * ( FIELD_KEY_STRING, XX )  : Can be used (in or out of a set) for some filter types (boolean checks for the most part, the system does
            not validate this so care should be taken when using this.  it may be better to explicitly pass a None.

        Key:
            XX: Filter type, can be any valid filter type.
            FILTER_BY: the object that is being compared to the list item
            FIELD_KEY_STRING: the field key string that defines how the list item is processed for filtering

        Notes:
            * If the filter by is a list or tuple, it must be defined using a full filter set
              (included in a tuple or list of tuples).
            * If the field_key string matches a filter_type string (unlikely, but possible) you must use a
              full filter set to define the filter.
            * If the list contains dict like objects, or is using attributes of list items, the definition MUST include
              the FIELD_KEY_STRING definition or a FilterFieldError will be raised.
            * The FILTER_BY and FIELD_KEY_STRING items can be reversed if needed (some filter type logic
              might require this)
            * The key_enclosure and list_item_key parameters can be used in the case of conflicts with
              valid data or field names.
            * The most efficient option is to pass a *full* filter_set and define the filter_field_type as this bypasses
              the auto-detect functions.

        Advanced:
            You can pass a dot separated filter_field_type to handle complex combinations.

            In these cases you must also pass a dot separated field_key_string.

            An example of this could be if you have a list of dictionaries, each with an object in the dictionary
            under the key 'data', and you want to filter based on an attribute called 'last_name' of the object.
            you can do the following:

            filter_field_type = 'dict_key.attribute'
            field_key_string = '__data__.__last_name__'
        """

        if args or kwargs:
            self._parse_filter_args(args, kwargs)

        for item in list_to_filter:
            if self.filter_item(item):
                yield item

        self._clear_filter_set_cache()

    def filter_item(self, item, *args, **kwargs):
        clear_cache = False

        if args or kwargs:
            self._parse_filter_args(args, kwargs)
            clear_cache = True

        tmp_ret = self.filter_set_engine(self._make_filter_set(item), self._filter_with)

        if clear_cache:
            self._clear_filter_set_cache()

        return tmp_ret

    def filter_set_engine(self, filter_set, filter_with='and'):
        """ returns a true false based on a filter_set """
        if not isinstance(filter_set, list):
            filter_set = [filter_set]

        for filter_item in filter_set:
            field_1 = filter_item[0]
            filter_type = filter_item[1]
            field_2 = filter_item[2]

            tmp_ret = self.filter_engine(field_1, filter_type, field_2)

            if filter_with == 'and':
                if not tmp_ret:
                    return False
            else:
                if tmp_ret:
                    return True

        if filter_with == 'and':
            return True
        else:
            return False

    def filter_engine(self, field_1, filter_type, field_2):
        """ does the actual filtering of each item """
        if filter_type not in self._filter_types:
            raise FilterFieldError('undefined filter type')
        filter_type = '_'+filter_type
        flt_meth = getattr(self, filter_type)
        return flt_meth(field_1, field_2)

    def clear_filter(self, keep_options=False, keep_filter_set=False):
        """
        Clears out any cached filterset and/or options
        :param keep_options: Will keep memorized options
        :param keep_filter_set: Will keep cached filterset
        """
        self._keep_filter_kwargs_cache = keep_options
        self._keep_filter_set_cache = keep_filter_set
        self._clear_filter_set_cache()

    def _clear_filter_set_cache(self):
        if not self._keep_filter_set_cache:
            self._filter_set_cache = None
            self._complex_filter = False
        if not self._keep_filter_kwargs_cache:
            self._filter_field_type = 'auto'
            self._list_item_key = '__list_item__'
            self._key_enclosure = '__'
            self._filter_with = 'and'

    def _is_field(self, item):
        if item == self._list_item_key:
            return True
        try:
            if item.startswith(self._key_enclosure) and item.endswith(self._key_enclosure):
                return True
        except TypeError:
            pass
        return False

    def _parse_filter_args(self, args, kwargs):

        if kwargs:
            self._filter_field_type = kwargs.get('filter_field_type', self._filter_field_type)
            if '.' in self._filter_field_type:
                self._filter_field_type = self._filter_field_type.split('.')
                for f in self._filter_field_type:
                    if f not in self._filter_field_type_options:
                        raise FilterFieldError('Filter field type '+f+' not valid')
                self._complex_filter = True
            else:
                self._complex_filter = False
                if self._filter_field_type not in self._filter_field_type_options:
                    print(self._filter_field_type)
                    raise FilterFieldError('Filter field type '+self._filter_field_type+' not valid')

            self._list_item_key = kwargs.get('list_item_key', self._list_item_key)
            self._key_enclosure = kwargs.get('key_enclosure', self._key_enclosure)
            self._filter_with = kwargs.get('filter_with', self._filter_with)

        if args:
            if len(args) == 1:
                if isinstance(args[0], (list, tuple)):
                    filter_sets = args[0]
                else:
                    filter_sets = [(self._list_item_key, 'eq', args[0])]
                    self._filter_field_type = 'list_field'

            elif len(args) == 2:
                filter_sets = [(args[0], args[1])]

            elif len(args) == 3:
                filter_sets = [(args[0], args[1], args[2])]

            else:
                raise FilterFieldError('Too many filter fields passed')

            if not isinstance(filter_sets, list):
                filter_sets = [filter_sets]

            self._filter_set_cache = []
            for filter_item in filter_sets:
                if self._complex_filter and len(filter_item) != 3:
                    raise FilterFieldError('Complex filters must have full filter_sets defined')
                if len(filter_item) == 1:
                    if self._is_field(filter_item[0]):
                        tmp_filter = (filter_item[0], 'is', None)
                    else:
                        tmp_filter = (filter_item[0], 'eq', self._list_item_key)
                elif len(filter_item) == 2:
                    if self._is_type(filter_item[0]):
                        if self._is_field(filter_item[1]):
                            tmp_filter = (filter_item[1], filter_item[0], None)
                            self._filter_field_type = 'list_field'
                        else:
                            tmp_filter = (filter_item[1], filter_item[0], self._list_item_key)
                    elif self._is_type(filter_item[1]):
                        if self._is_field(filter_item[0]):
                            tmp_filter = (None, filter_item[1], filter_item[0])
                            self._filter_field_type = 'list_field'
                        else:
                            tmp_filter = (self._list_item_key, filter_item[1], filter_item[0])
                    else:
                        tmp_filter = (filter_item[0], 'eq', filter_item[1])
                elif len(filter_item) == 3:
                    if self._complex_filter:
                        tmp_filter = (self._make_complex_field(filter_item[0]),
                                      filter_item[1],
                                      self._make_complex_field(filter_item[2]))
                    else:
                        tmp_filter = filter_item
                    if tmp_filter[1] not in self._filter_types:
                        raise AttributeError('filter comparison '+tmp_filter.__repr__+' not defined')
                else:
                    raise AttributeError('incorrect set passed to filter: '+filter_item.__repr__)

                self._filter_set_cache.append(tmp_filter)


    def _make_complex_field(self, field):
        if self._is_field(field):
            tmp_ret = field.split('.')
            if len(tmp_ret) == len(self._filter_field_type):
                return tmp_ret
            raise FilterFieldError('Filter_key_field must have the name number of elements as the filter_field_type')
        return field

    def _make_filter_set(self, item, filter_set=None):
        """ Replaces the keystrigns in a filterset with the item as needed """
        tmp_ret = []
        if filter_set:
            tmp_filter_set = filter_set
        else:
            tmp_filter_set = self._filter_set_cache

        for flt in tmp_filter_set:
            field_1 = self._get_field(item, flt[0])
            comparator = flt[1]
            field_2 = self._get_field(item, flt[2])
            tmp_ret.append((field_1, comparator, field_2))
        return tmp_ret

    def _get_field_detail(self, list_item, filter_item, field_type):
        """ gets the replacement field from the item, either itself, a dict, or attribute """

        raw_key = filter_item[2:len(filter_item)-2]

        if field_type == 'list_field':
            return list_item
        elif field_type == 'dict_key':
            return list_item[raw_key]
        elif field_type == 'attribute':
            return getattr(list_item, raw_key)
        else:
            try:
                if not self._complex_filter:
                    self._filter_field_type = 'dict_key'
                return list_item[raw_key]
            except TypeError:
                if not self._complex_filter:
                    self._filter_field_type = 'attribute'
                return getattr(list_item, raw_key)
            except AttributeError:
                if not self._complex_filter:
                    self._filter_field_type = 'list_field'
                return list_item

    def _get_field(self, list_item, filter_item):
        if filter_item == self._list_item_key:
            return list_item

        if self._complex_filter:
            tmp_item = list_item
            for field_type, flt_item in zip(self._filter_field_type, filter_item):
                tmp_item = self._get_field_detail(tmp_item, flt_item, field_type)

            return tmp_item

        else:
            if self._is_field(filter_item):
                return self._get_field_detail(list_item, filter_item, self._filter_field_type)
            else:
                return filter_item

    def _is_type(self, item):
        return item in self._filter_types

    def _is_field_or_type(self, item):
        return self._is_field(item) or self._is_type(item)

    @staticmethod
    def _eq(field_1, field_2):
        return field_1 == field_2

    @staticmethod
    def _ne(field_1, field_2):
        return field_1 != field_2

    @staticmethod
    def _gt(field_1, field_2):
        return field_1 > field_2

    @staticmethod
    def _lt(field_1, field_2):
        return field_1 < field_2

    @staticmethod
    def _in(field_1, field_2):
        return field_1 in field_2

    @staticmethod
    def _nin(field_1, field_2):
        return field_1 not in field_2

    @staticmethod
    def _gte(field_1, field_2):
        return field_1 >= field_2

    @staticmethod
    def _lte(field_1, field_2):
        return field_1 <= field_2

    @staticmethod
    def _not(field_1, field_2):
        if not field_1:
            return True
        else:
            return False

    @staticmethod
    def _is(field_1, field_2):
        if field_1:
            return True
        else:
            return False

    @staticmethod
    def _instance_of(field_1, field_2):
        return isinstance(field_1, field_2)

# ===============================================================================
# a list that allows for lookups more like a dictionary.
# ===============================================================================


class DBList():
    '''
    this is a list type object that also allows for lookups like a dictionary
    this assumes a list of dictionary entries.

    NOTE: if there are dupe items (by defined key) in the starting list, only the last one will be kept.

    '''
    internal_dict = {}


    def __init__( self,
                 starting_list,
                 dict_key,
                 ):
        for item in starting_list:
            self.internal_dict[item[dict_key]] = item

    def __iter__( self, key ):
        return self.internal_dict[key]

    def get_list( self ):
        return self.internal_dict.items()

    def get_dict( self ):
        return self.internal_dict

# ===============================================================================
# general list utilities.
# ===============================================================================



def make_list(in_obj):
    """
    Will take in an object, and if it is not already a list, it will convert it to one.
    :param in_obj:
    :return:
    """
    if is_string(in_obj):
        return [in_obj]
    else:
        return in_obj


def flatten(l, ltypes=(list, tuple), force=None):
    """
    Will flatten lists and tuples to a single level

    from: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html

    :param l: list or tuple to be flattened
    :param ltypes: the types of items allowed to be flattened, default = (list, tuple)
    :param force: forces return to be of this type.
    :return: single level list or tuple (same as what went in)
    """
    if is_string(l):
        if force is None:
            return []
        elif force == list:
            return [l]
        elif force == tuple:
            return tuple(l,)
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    if force is None:
        return ltype(l)
    else:
        return force(l)


def unpack_class_method(class_object_list, method, ret_type=str, args_list=[], kwargs_dict={}):
    """
    This will iterate through a list of objects and pull a value from each one, even if the items are functions.

    :param class_object_list: A list of objects
    :param method: the method to pull from (string)
    :param return_type: what type of data is expected to be returned. this should be a function/class that will convert
        to the type desired.
        for example, the default is str, but int, float are also options.
    :param args_list: if the method is a function, a list of arguments to pass
    :param kwargs_dict: if the method is a function, a dict of keyword arguments to pass.
    :return:
    """
    tmpretset = []
    class_object_list = flatten(class_object_list)
    for obj in class_object_list:
        func = getattr(obj, method, None)
        if callable(func):
            tmpret = ret_type(func(*args_list, **kwargs_dict))
        else:
            tmpret = ret_type(func)
        tmpretset.append(tmpret)
    return tmpretset


def get_same(l1, l2):
    """
    Returns a list with any items that are the same in both lists

    :param l1:
    :param l2:
    :return:
    """
    tmp_list = []
    for li in l1:
        if li in l2:
            tmp_list.append(li)
    return tmp_list


def get_not_in(check_for, check_in):
    """
    Returns a list of items that are NOT in another list

    :param check_for: a list of items to check for
    :param check_in: a list to check
    :return: a list of the items in "check_in" that are NOT in "check_for"
    """
    tmp_list = []
    for li in check_for:
        if li not in check_in:
            tmp_list.append(li)
    return tmp_list


def remove_dupes(l1):
    """
    Returns a list with any duplicates removed.
    (while order is maintained, which duplicate is removed is not controllable)
    :param l1:
    :return:
    """
    return list(set(l1))

# ===============================================================================
# checking for the presence (or absence) of lists in other lists
# ===============================================================================

def list_in_list(is_this, in_this):
    is_this = make_list(is_this)
    for item in is_this:
        if item in in_this:
            return True
    return False


def list_not_in_list(is_this, not_in_this):
    is_this = make_list(is_this)
    for item in is_this:
        if item in not_in_this:
            return False
    return True

# ===============================================================================
# Utility counts unique values in a list or dict
# ===============================================================================


def count_unique(data_in, dict_key=None, on_key_error='raise'):
    """
    :param data_in: list or tuple of items to be counted
    :param dict_key: if data_in is a list of dict's, this is the key for which item to compare
    :param on_key_error:
        what to do if there is a KeyError when looking up the dict_key:
        * 'raise' = (default) Raises KeyError
        * 'skip' = skips KeyErrors
        * 'count' = counts KeyErrors as 1
    :return: integer

    """

    tmp_list = []

    if not isinstance(data_in, (list, tuple)):
        raise TypeError('count_unique requires a list or tuple, not a '+type(data_in).__name__)

    if dict_key:
        for item in data_in:
            try:
                tmp_list.append(item[dict_key])
            except KeyError:
                if on_key_error == 'raise':
                    raise KeyError('count_unique: dict key "'+dict_key+'" not found')
                elif on_key_error == 'count':
                    tmp_list.append('__<no_key_item>__')

    else:
        tmp_list = data_in

    return len(set(tmp_list))

# ===============================================================================
# Advanced List Object
# ===============================================================================


class ListPlus(list):
    """
    adds some additional features to the list object.
        ListPlus.add             : allows insert new records past the existing last record
        ListPlus.update          : allows updating records or adding them past the existing last record
        ListPlus[key] = value    : sale as list2.update though uses list key notation
        ListPlus.get             : allows for setting a default response instead of generating an error if rec does not exist.
    """

    def _update_function(self, curr_obj, new_obj ):
        """
        Allows overriding to allow for manipulating or validating updated information if needed'

        this is called anytime something is updated (not for new records though)

        :param curr_obj: this passes the current object in the list
        :param new_obj: this passes the new object
        :return: returns the object to be saved.
        """
        return new_obj

    def add(self, i, x, **kwargs):
        """
        Will add any needed items to a list to add the new item at the indexed spot.

        :param i: list offset to add item to.
            If this is lower than or equal to the size fo the list, the items will be added directly to the end.
            If this is larger than the list length, new items will be added to the list to pad it out long enough
            to reach this length.
        :param x: the new item to add to the list
        :param new_item_default: the default item that will be added as padding if needed.
            this overrides the class setting if present.
        """
        # print( 'l:', l )
        # print( 'i:', i )
        new_item_default = kwargs.get('new_item_default', self.new_item_default)
        if i >= len(self):
            l = len(self)
            mt_items = i - l
            for ni in range(mt_items):
                self.append(new_item_default)
            self.append(x)
        else:
            self.insert(i, x)

    def set_new_item_default(self, new_item_default):
        """
        This sets the default new item object for when blank items must be added
        :param new_item_default: the item that will be used for blank new items.
        """
        self._new_item_default = new_item_default

    @property
    def new_item_default(self):
        try:
            return self._new_item_default
        except AttributeError:
            self.set_new_item_default(None)
            return self._new_item_default

    def update(self, i, x, **kwargs):
        """
        Updates a specific item at a specific offset, if that item does not exist, padding items will
        be added to the list lengthen it.

        :param i: list offset to update.
        :param x: the new item to update in the list
        :param new_items_default: the default item that will be added as padding if needed,
        this overrides the class setting if present
        """
        new_item_default = kwargs.get('new_item_default', self.new_item_default)

        try:
            tmp_value = self._update_function(copy.deepcopy(self[i]), x)
        except (IndexError, TypeError):
            tmp_value = self._update_function(None, x)

        try:
            self[i] = tmp_value
        except IndexError:
            l = len(self)
            mt_items = i - l
            for ni in range(mt_items):
                self.append(new_item_default)
            self.append(tmp_value)

    def get(self, *args):
        i = args[0]
        if len(args) == 1:
            return self[i]
        elif len(args) == 2:
            try:
                return self[i]
            except IndexError:
                return args[1]
        else:
            raise TypeError('ListPlus takes at most 2 arguments, '+str(len(args))+' given')

    '''
    def __setitem__(self, i, x):
        if isinstance(i, int):
            self.update(i, x)
        else:
            raise TypeError('ListPlus indices must be integers, not '+type(i).__name__)
    '''

# ===============================================================================
# Lookup Manager
# ===============================================================================

LookupTuple = collections.namedtuple('LookupTuple', ['stored', 'display', 'reference'])


class LookupItem(LookupTuple):

    '''
    def __init__(self, *args, **kwargs):
        super(LookupItem, self).__init__(*args, **kwargs)
        if not self.reference:
            self.reference = copy.deepcopy(self.stored)
        self.reference = slugify(self.reference)
    '''
    def __str__(self):
        return self.stored


class LookupManager(object):


    def __init__(self, lookup_list):
        """
        :param lookup_list:
                lookup list is a list of tuples (stored_value, display_value [, referenced_name] ):
                    stored value = the value that would be stored in the db
                    representative value = the value that is used for display
                    referenced value is the name used in coding (if not present stored_value is used)
        :param case_sensitive:
                determines if lookups are case sensitive or not.
        """
        self.stored_dict = {}
        self.display_dict = {}
        self.reference_dict = {}
        self.data_list = []
        self.lookup_list = []
        self.master_dict = {}

        for l in lookup_list:

            tmp_l = LookupItem(*l)

            self.stored_dict[tmp_l.stored] = tmp_l
            self.display_dict[tmp_l.display] = tmp_l
            self.reference_dict[slugify(tmp_l.reference)] = tmp_l
            self.data_list.append(tmp_l)
            self.lookup_list.append( (tmp_l.stored, tmp_l.display ))
            self.master_dict[tmp_l.stored] = tmp_l
            self.master_dict[tmp_l.display] = tmp_l
            self.master_dict[slugify(tmp_l.reference)] = tmp_l

    def __iter__(self):
        for i in self.lookup_list:
            yield i

    def __getattr__(self, item):
        return self.reference_dict[item]

    def __getitem__(self, item):
        return self.master_dict[item]

    def get_by_stored(self,item):
        return self.stored_dict[item]

    def get_by_display(self, item):
        return self.display_dict[item]

# ===============================================================================
# Ordered Set
# ===============================================================================


"""
An OrderedSet is a custom MutableSet that remembers its order, so that every
entry has an index that can be looked up.

Based on a recipe originally posted to ActiveState Recipes by Raymond Hettiger,
and released under the MIT license.

Rob Speer's changes are as follows:

    - changed the content from a doubly-linked list to a regular Python list.
      Seriously, who wants O(1) deletes but O(N) lookups by index?
    - add() returns the index of the added item
    - index() just returns the index of an item
    - added a __getstate__ and __setstate__ so it can be pickled
    - added __getitem__
"""

SLICE_ALL = slice(None)


def is_iterable(obj):
    """
    Are we being asked to look up a list of things, instead of a single thing?
    We check for the `__iter__` attribute so that this can cover types that
    don't have to be known by this module, such as NumPy arrays.

    Strings, however, should be considered as atomic values to look up, not
    iterables.

    We don't need to check for the Python 2 `unicode` type, because it doesn't
    have an `__iter__` attribute anyway.
    """
    return hasattr(obj, '__iter__') and not isinstance(obj, str)


class OrderedSet(collections.MutableSet):
    """
    An OrderedSet is a custom MutableSet that remembers its order, so that
    every entry has an index that can be looked up.
    """
    def __init__(self, iterable=None):
        self.items = []
        self.map = {}
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        """
        Get the item at a given index.

        If `index` is a slice, you will get back that slice of items. If it's
        the slice [:], exactly the same object is returned. (If you want an
        independent copy of an OrderedSet, use `OrderedSet.copy()`.)

        If `index` is an iterable, you'll get the OrderedSet of items
        corresponding to those indices. This is similar to NumPy's
        "fancy indexing".
        """
        if index == SLICE_ALL:
            return self
        elif hasattr(index, '__index__') or isinstance(index, slice):
            result = self.items[index]
            if isinstance(result, list):
                return OrderedSet(result)
            else:
                return result
        elif is_iterable(index):
            return OrderedSet([self.items[i] for i in index])
        else:
            raise TypeError("Don't know how to index an OrderedSet by %r" %
                    index)

    def copy(self):
        return OrderedSet(self)

    def __getstate__(self):
        if len(self) == 0:
            # The state can't be an empty list.
            # We need to return a truthy value, or else __setstate__ won't be run.
            #
            # This could have been done more gracefully by always putting the state
            # in a tuple, but this way is backwards- and forwards- compatible with
            # previous versions of OrderedSet.
            return (None,)
        else:
            return list(self)

    def __setstate__(self, state):
        if state == (None,):
            self.__init__([])
        else:
            self.__init__(state)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        """
        Add `key` as an item to this OrderedSet, then return its index.

        If `key` is already in the OrderedSet, return the index it already
        had.
        """
        if key not in self.map:
            self.map[key] = len(self.items)
            self.items.append(key)
        return self.map[key]
    append = add

    def index(self, key):
        """
        Get the index of a given entry, raising an IndexError if it's not
        present.

        `key` can be an iterable of entries that is not a string, in which case
        this returns a list of indices.
        """
        if is_iterable(key):
            return [self.index(subkey) for subkey in key]
        return self.map[key]

    def discard(self, key):
        raise NotImplementedError(
            "Cannot remove items from an existing OrderedSet"
        )

    def __iter__(self):
        return iter(self.items)

    def __reversed__(self):
        return reversed(self.items)

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and self.items == other.items
        return set(self) == set(other)


#===============================================================================
# counter Class
#===============================================================================

class ClickItem(object):

    def __init__(self,
                 clicker,
                 name,
                 initial=None,
                 step=None,
                 max_value=None,
                 min_value=None,
                 console_format=None,
                 return_format=None,
                 return_every=None,
                 rollover=None,
                 rollunder=None):
        self._clicker = clicker
        self._name = name
        self._initial = initial
        self._step = step
        self._max_value = max_value
        self._min_value = min_value
        self._console_format = console_format
        self._format = return_format
        self._return_every = return_every
        self._rollover = rollover
        self._rollunder = rollunder

        self._current = self.initial

    def _change(self, change_by):
        change_by = int(change_by) * self.step
        self._current += change_by
        while self._current > self.max_value or self._current < self.min_value:
            if self._current > self.max_value:
                if self.rollover:
                    extra = self._current - self.max_value - 1
                    self._current = self.min_value + extra
                else:
                    self._current = self.max_value
            elif self._current < self.min_value:
                if self.rollunder:
                    extra = self.min_value - self._current - 1
                    self._current = self.max_value - extra
                else:
                    self._current = self.min_value

    def a(self, num_to_add=1):
        self.add(num_to_add)

    def add(self, num_to_add=1):
        self._change(num_to_add)
        return self

    def __iadd__(self, other):
        return self.add(other)

    def __add__(self, other):
        return self.add(other)

    def sub(self, num_to_sub=1):
        self._change(num_to_sub*-1)
        return self

    def __isub__(self, other):
        return self.sub(other)

    def __sub__(self, other):
        return self.sub(other)

    def __int__(self):
        return self._current

    def __repr__(self):
        'CounterItem: {} Current Count: {}'.format(self.name, self.get)
        return

    def __bool__(self):
        return self.get == self.initial

    def __len__(self):
        return self.max_value - self.min_value

    def __call__(self, increment=1):
        self._change(increment)
        return self.get

    @property
    def get(self):
        return self._current

    @property
    def perc(self):
        ran = self.max_value - self.min_value
        dist = self.get - self.min_value
        return ran / dist * 100

    def __str__(self):
        return self.return_format.format(self._dict)

    @property
    def _dict(self):
        tmp_dict = {'counter': self.get,
                    'min': self.min_value,
                    'max': self.max_value,
                    'name': self.name,
                    'perc': self.perc}
        return tmp_dict

    @property
    def get_console(self):
        return self.console_format.format(self._dict)

    def reset(self, new_value=None):
        if new_value:
            self._current = new_value
        else:
            self._current = self.initial
        return self

    @property
    def name(self):
        return self._name

    def _check_and_return(self, attr):
        local_attr = '_'+attr
        if getattr(self, local_attr):
            return getattr(self, local_attr)
        else:
            return getattr(self._clicker, attr)

    @property
    def initial(self):
        return self._check_and_return('initial')

    @property
    def step(self):
        return self._check_and_return('step')

    @property
    def max_value(self):
        return self._check_and_return('max_value')

    @property
    def min_value(self):
        return self._check_and_return('min_value')

    @property
    def console_format(self):
        return self._check_and_return('console_format')

    @property
    def return_format(self):
        return self._check_and_return('return_format')

    @property
    def return_every(self):
        tmp_ret = self._check_and_return('return_every')
        if tmp_ret >= 1 or tmp_ret == 0:
            return tmp_ret
        else:
            ran = self.max_value - self.min_value
            return round(ran * tmp_ret)

    @property
    def rollover(self):
        return self._check_and_return('rollover')

    @property
    def rollunder(self):
        return self._check_and_return('rollunder')


class Clicker():
    '''
    Arguments:
        initial = initial counter number
        echo = print each set to console
        step = print only on increments of x
        name = name of clicker
        max = max number (when set, echo will return %xx)
        format = format to use for echo, default = '{name} : {counter}'
    '''

    default_name = '__default__'

    def __init__(self, **kwargs):

        self._counters = {}

        self.initial = kwargs.get('initial', 0)
        self.step = kwargs.get('step', 1)
        self.max_value = kwargs.get('max_value', sys.maxsize)
        self.min_value = kwargs.get('min_value', 0)
        self.console_format = kwargs.get('console_format', '{counter}')
        self.format = kwargs.get('return_format', '{counter')
        self.return_every = kwargs.get('return_every', 1)
        self.rollover = kwargs.get('rollover', False)
        self.rollunder = kwargs.get('rollunder', False)
        self.autoadd = kwargs.get('autoadd', True)
        self.autoadd_name_prefix = kwargs.get('AutoCounter_', True)

        self.add_counter(self.default_name)
        self._default_counter = self._counters[self.default_name]

    def add_counter(self, name, **kwargs):
        self._counters[name] = ClickItem(self, name, **kwargs)

    def del_counter(self, name):
        del self._counters[name]

    def __getattr__(self, item):
        return getattr(self._default_counter, item)

    def __getitem__(self, item):
        if self.autoadd:
            if item not in self:
                self.add_counter(item)
        return self._counters[item]

    def __contains__(self, item):
        return item in self._counters

    def __len__(self):
        return len(self._counters)

    def __delitem__(self, key):
        del self._counters[key]

    def __call__(self, *args):
        tmp_name = self.default_name
        tmp_change = 1
        if args:
            if isinstance(args[0], str):
                tmp_name = args[0]
                if len(args) == 2:
                    tmp_change = args[1]
            else:
                tmp_change = args[0]
        tmp_cnt = self[tmp_name]

        return tmp_cnt(tmp_change)

#===============================================================================
# Flag Manager
#===============================================================================


class FlagList(object):
    def __init__(self):
        self._flags = []
    def add(self,flag):
        if flag not in self._flags:
            self._flags.append(flag)
    def rem(self,flag):
        if flag in self._flags:
            self.flags.remove(flag)
    def __contains__(self, item):
        return item in self._flags
    def __bool__(self):
        if self._flags:
            return True
        else:
            return False
    def __call__(self, add_rem_flags = None):
        if add_rem_flags:
            tmp_flags = add_rem_flags.split()
            for f in tmp_flags:
                if f[0] == '-':
                    self.rem(f[1:])
                elif f[0] == '+':
                    self.add(f[1:])
                else:
                    self.add(f)
        return self._flags


class Flagger(object):
    def __init__(self):
        self._include = FlagList()
        self._exclude = FlagList()
        self._current = FlagList()

    @property
    def inc(self):
        return self._include

    @property
    def exc(self):
        return self._exclude

    @property
    def cur(self):
        return self._current

    @property
    def check(self):
        tmp_ret = False
        if self.inc:
            if list_in_list(self.cur, self.inc):
                tmp_ret = True
        else:
            tmp_ret = True

        if self.exc:
            if list_in_list(self.cur, self.exc):
                tmp_ret = False
        return tmp_ret

    def __call__(self, current=None, include=None, exclude=None, **kwargs):
        if kwargs:
            current=kwargs.get('c',current)
            include=kwargs.get('i',include)
            exclude=kwargs.get('e',exclude)
        if current:
            self.cur(current)
        if include:
            self.inc(include)
        if exclude:
            self.exc(exclude)

        return self.check

#===============================================================================
# swap tool
#===============================================================================


def swap(item, opt1=True, opt2=False):
    if item == opt1:
        return opt2
    elif item == opt2:
        return opt1
    else:
        raise AttributeError(str(item)+' not in available options')


#===============================================================================
# text utils
#===============================================================================


def replace_between(instring, start_key, end_key, replace, keep_keys=False, offset_count=1, count=9999):
    """
    Replace text between two keys, optionally including the keys themselves.

    :param instring: The string to search
    :param start_key: The starting boundary key
    :param end_key: The ending boundary key
    :param replace: The string to put between the boundary keys
    :param keep_keys: True/False: include the key strings in the replacement
    :param count: replace up to this many instances
    :param offset_count: start replacing after this many instances
    :return: String
    """
    instring = str(instring)

    if start_key not in instring:
        return instring

    start_pos = 0
    curs_pos = 0
    found = 0
    start_key_len = len(start_key)
    end_key_len = len(end_key)
    outstring = ''

    start_pos = index_of_count(instring, find=start_key, offset_count=offset_count, start=0)

    while True:

        if count <= found or start_pos == -1:
            break

        end_pos = instring.find(end_key, start_pos+start_key_len)

        if end_pos == -1:
            break

        if keep_keys:
            suffix = instring[end_pos:end_pos+end_key_len]
            outstring = outstring + instring[curs_pos:start_pos+start_key_len] + replace + suffix
            curs_pos = end_pos+end_key_len

        else:
            outstring = outstring + instring[curs_pos:start_pos] + replace
            curs_pos = end_pos+end_key_len

        found = found+1

        start_pos = instring.find(start_key, curs_pos)

    return outstring+instring[curs_pos:]

def index_of_count(instring, find, offset_count=1, start=0):
    if instring:
        offset_loc = start
        current_off = 0
        for i in range(offset_count):
            offset_loc = instring.find(find, current_off)
            if offset_loc > -1:
                if i == offset_count-1:
                    return offset_loc
                current_off = offset_loc+1
            else:
                return current_off
        return offset_loc
    return -1


def get_before(instring, find, offset_count=1):
    offset_loc = index_of_count(instring, find, offset_count)

    if offset_loc != -1:
        return instring[:offset_loc]
    return instring


def get_after(instring, find, offset_count=1):
    offset_len = len(find)
    offset_loc = index_of_count(instring, find, offset_count)

    if offset_loc != -1:
        return_size = offset_loc+offset_len
        return instring[return_size:]
    return instring


def get_between(instring, start_key, end_key):
    return get_after(get_before(instring, end_key), start_key)


# ===============================================================================
# Format number as clean string
# ===============================================================================

import re
from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return str(delim.join(result))

# ===============================================================================
# Format number as clean string
# ===============================================================================


def format_as_decimal_string(num, max_decimal_points=6):
    if isinstance(num, str):
        if num.isnumeric():
            num = Decimal(num)
        else:
            return ''

    if (num % 1 == 0) or (num > 100):
        return '{:,.0f}'.format(num)
    else:
        tmp_dec_pl = '{}'.format(max_decimal_points)
        tmp_format = '{0:.' + tmp_dec_pl + 'g}'
        tmp_num_str = tmp_format.format(num)
        tmp_num_str = tmp_num_str.rstrip('0').rstrip('.')
        return tmp_num_str


# ===============================================================================
# Advanced Formatter
# ===============================================================================


class FormatField(object):
    init_max_length = None
    min_length = 10
    do_not_show_length = 4
    pad_to_max = False
    justification = 'left'
    end_string = ''
    padding_string = ' '
    trim_string = '+'
    trim_priority = 1

    current_max_length = None
    ignore_min = False

    current_string = ''
    field_dict = {}
    format_string = ''
    rendered_string = ''

    curr_length = 0

    _length_ok = False

    def __init__(self,
                 name,
                 format_string,
                 field_def_dict,
                 initial_string = None,
                ):

        self.name = name
        self.format_string = format_string
        if initial_string:
            self.initial_string = initial_string
            self.current_string = initial_string
            self._try_format()


        self.init_max_length = field_def_dict.get('max_length', self.init_max_length)
        self.min_length = field_def_dict.get('min_length', self.min_length)
        self.do_not_show_length = field_def_dict.get('do_not_show_length', self.do_not_show_length)
        self.pad_to_max = field_def_dict.get('pad_to_max', self.pad_to_max)
        self.justification = field_def_dict.get('justification', self.justification)
        self.end_string = field_def_dict.get('end_string', self.end_string)
        self.padding_string = field_def_dict.get('padding_string', self.padding_string)
        self.trim_string = field_def_dict.get('trim_string', self.trim_string)
        self.trim_priority = field_def_dict.get('trim_priority', self.trim_priority)

    def __str__(self):
        return self.current_string

    @property
    def rendered_str(self):
        self._try_format()
        return self.rendered_string

    def _update_field_dict(self):
        self.field_dict = {}
        self.field_dict[self.name] = self.current_string

    def _try_format(self):
        self._update_field_dict()

        # print(self.field_dict)
        # print(self.format_string)

        if self.current_max_length == 0:
            self.rendered_string = ''
            self.curr_length = 0
        else:
            self.rendered_string = self.format_string.format(**self.field_dict)
            self.curr_length = len(self.rendered_string)

        if self.current_max_length:
            self._length_ok = self.curr_length <= self.current_max_length
            return

        self._length_ok = True

        # print('-- Format --')

        # print('current  : ', self.current_string)
        # print('rendered : ', self.rendered_string)
        # print('length   : ', self.curr_length)


        # print('------------')




    def max_length(self, max_len = None , ignore_min = None):
        if max_len:
            self.current_max_length = max_len

        if ignore_min != None:
            self.ignore_min = ignore_min

        if ignore_min:
            if self.current_max_length <= self.do_not_show_length:
                self.current_max_length = 0
        else:
            if self.current_max_length <= self.min_length:
                self.current_max_length = self.min_length


        self._try_format()
        return self._length_ok

    def set_string(self, initial_string):
        self.initial_string = initial_string
        self.current_string = initial_string
        self._try_format()
        return self._length_ok

    @property
    def length_ok(self):
        self._try_format()
        return self._length_ok

    def _pad_me(self):
        # print('max:', self.current_max_length)
        # print('pad:', self.pad_to_max)
        if self.current_max_length and self.pad_to_max:
            self._try_format()

            pad_needed = self.current_max_length - self.curr_length
            # print('needed', pad_needed)

            if pad_needed > 0:

                tmp_padding = self.padding_string
                if self.justification == 'left':
                    if pad_needed <= 2:
                        tmp_padding = ' '
                    self.current_string = self.current_string + ' '
                    self.current_string = self.current_string.ljust(self.current_max_length, tmp_padding)

                elif self.justification == 'right':
                    if pad_needed <= 4:
                        tmp_padding = ' '
                    self.current_string = ' ' + self.current_string
                    self.current_string = self.current_string.rjust(self.current_max_length, tmp_padding)


                elif self.justification == 'center':
                    if pad_needed <= 2:
                        tmp_padding = ' '
                    self.current_string = ' ' + self.current_string + ' '
                    self.current_string = self.current_string.center(self.current_max_length, tmp_padding)
            self._try_format()


    def _trim_me(self, max_length = None, ignore_min = None):

        # print('trim to:', max_length)

        if max_length or ignore_min:
            self.max_length(max_length, ignore_min)

        if self.current_max_length:
            if self.curr_length >= self.current_max_length:
                if self.current_max_length == 0:
                    self.current_string = ''
                else:
                    # print ('cur max length: ', self.current_max_length)
                    self.current_string = self.initial_string[:self.current_max_length - 1] + self.trim_string

        self._try_format()



class FormatFullString(FormatField):

    full_rendered_string = ''
    full_format_string = ''
    field_list = []

    def set_string(self, field_list):
        self.field_list = field_list
        self._try_format()
        return self._length_ok

    def _update_field_dict(self):

        self.field_dict = {}
        for f in self.field_list:
            self.field_dict[f.name] = f.current_string




class PriGroup(object):
    field_list = []
    priority = 0

    total_current_length = 0
    total_max_current_length = 0
    total_min_length = 0



    def __init__(self, new_field = None):
        if new_field:
            self.add(new_field)


    def add(self, new_field):
        self.field_list.append(new_field)
        self.priority = new_field.trim_priority

    def _recalc(self):

        for f in self.field_list:
            self.total_current_length = self.total_current_length + f.current_length
            self.total_max_current_length = self.total_max_current_length + f.current_max_length
            self.total_min_length = self.total_min_length + f.min_length


# ===============================================================================
# IF List (not sure what I did this one for
# ===============================================================================


class if_list(ListPlus):
    def _update_function(self, old, new):
        if old:
            old.add(new)
            return old
        else:
            tmp_new = PriGroup(new)
            return tmp_new


# ===============================================================================
# intelligenr formatter (works to keep a set of fields in a fixed space)
# ===============================================================================


class IntelligentFormat(object):
    fields_list = []
    priority_list = if_list()
    fields_dict = {}
    full_string_rec = None


    def __init__(self, length_limits_dict, format_str, fields_dict = None):
        field_names = find_enclosed(format_str, '{', '}', ignore_after = ':')
        field_formats = find_enclosed(format_str, '{', '}')

        for field_name, format_string in zip(field_names, field_formats):
            field_def = length_limits_dict.get(field_name, {})

            initial_string = None
            if fields_dict:
                initial_string = fields_dict.get(field_name, None)

            tmp_field = FormatField(
                                field_name,
                                format_string,
                                field_def,
                                initial_string)
            self.fields_list.append(tmp_field)
            self.fields_dict[field_name] = tmp_field

            self.priority_list.update(tmp_field.trim_priority, tmp_field, [])

        self.full_string_rec = FormatFullString(
                                                '__full_string__',
                                                format_string,
                                                fields_dict['__full_string__'],
                                               )
        self.full_string_rec.set_string(self.fields_list)


class IntelligentFormatOld(object):
    default_dict = {
                    'max_length': None,
                    'min_length': 10,
                    'do_not_show_length': 4,
                    'pad_to_max': False,
                    'justification':'left',
                    'end_string': '',
                    'padding_string': ' ',
                    'trim_string': '+',
                    'trim_priority': 1, }

    fields_dict = {}
    fields_def_dict = {}
    priority_list = if_list()
    max_pri_depth = 0
    template_overhead = 0

    field_list = []




    def __init__(self, length_limits_dict, format_str, fields_dict = None , **kwargs):

        field_names = find_enclosed(format_str, '{', '}', ignore_after = ':')
        field_formats = find_enclosed(self.format_str, '{', '}')

        for field_name, field_format in zip(field_names, field_formats):
            field_def = length_limits_dict.get(field_name, {})



        self.length_limits_dict = length_limits_dict
        self.format_str = format_str

        self.generate_field_limits_dict()

        if fields_dict:
            self.fields_dict = fields_dict
        elif kwargs:
            self.fields_dict = kwargs






    def generate_field_limits_dict(self):

        self.full_fields_list = find_enclosed(self.format_str, '{', '}', ignore_after = ':')


        self.full_string_limits = copy.deepcopy(self.default_dict)
        self.full_string_limits.update(self.length_limits_dict.get('__full_string__', {}))

        self.fields_def_dict = {}
        tmp_fields_dict = {}
        self.priority_list.clear()

        for field in self.full_fields_list:
            tmp_limits_dict = copy.deepcopy(self.default_dict)
            tmp_limits_dict.update(self.length_limits_dict.get(field, {}))
            self.fields_def_dict[field] = tmp_limits_dict
            tmp_pri = self.fields_def_dict[field]['trim_priority']
            self.priority_list.update(tmp_pri, field, [])
            tmp_fields_dict[field] = ''

        self.max_pri_depth = len(self.priority_list)

        # print(tmp_fields_dict)

        tmp_str = self.format_str.format(**tmp_fields_dict)
        self.template_overhead = len(tmp_str)


    def format(self, fields_dict = None, **kwargs):

        max_length = 0
        format_overhead = 0
        pri_0_length = 0

        rem_space_avail = 0

        if fields_dict:
            self.fields_dict = fields_dict
        elif kwargs:
            self.fields_dict = kwargs

        self._verify_fields()

        # trim to field level max's
        self._trim_fields()

        # apply padding to pri 0 fields so we get their sixzes right
        self._pad_fields(set_num = 0)


        if self._check_formatted():
            pass
            # return self._final_format_step()



        # self.orig_fields_dict = copy.deepcopy(self.fields_dict)



    def _pad_fields(self, field = None, set_num = None):
        if field:
            tmp_field = self.fields_dict[field]
            tmp_max = self.fields_def_dict[field]['max_length']
            if tmp_max and self.fields_def_dict[field]['pad_to_max']:
                pad_needed = len(tmp_field) - tmp_max

                if pad_needed > 0:

                    tmp_padding = str(self.fields_def_dict[field]['padding_string'])
                    tmp_just = self.fields_def_dict[field]['justification']

                    if tmp_just == 'left':
                        if pad_needed <= 2:
                            tmp_padding = ' '
                        tmp_field = tmp_field + ' '
                        tmp_field = tmp_field.ljust(tmp_max, tmp_padding)

                    elif tmp_just == 'right':
                        if pad_needed <= 4:
                            tmp_padding = ' '
                        tmp_field = ' ' + tmp_field
                        tmp_field = tmp_field.rjust(tmp_max, tmp_padding)


                    elif tmp_just == 'center':
                        if pad_needed <= 2:
                            tmp_padding = ' '
                        tmp_field = ' ' + tmp_field + ' '
                        tmp_field = tmp_field.center(tmp_max, tmp_padding)

        elif set_num:
            for fieldname in self.priority_list[set_num]:
                self._trim_fields(field = fieldname)
        else:
            for fieldname in self.full_fields_list:
                self._trim_fields(field = fieldname)




    def _trim_fields(self, field = None, set_num = None, max_len = None, ignore_min = False):
        if field:
            if max_len:
                tmp_max = max_len
            else:
                tmp_max = self.fields_def_dict[field]['max_length']
            if len(self.fields_dict[field]) >= tmp_max:
                self.fields_dict[field] = self.fields_dict[field][:tmp_max - 1] + self.fields_def_dict[field]['trim_string']


        elif set_num:
            for fieldname in self.priority_list[set_num]:
                self._trim_fields(field = fieldname, max = max, ignore_min = ignore_min)
        else:
            for fieldname in self.full_fields_list:
                self._trim_fields(field = fieldname, max = max, ignore_min = ignore_min)



    def _get_priority_set_nums (self, pri_set):

        set_text_len = 0
        set_min_len = 0
        set_max_len = 0

        for field in self.priority_list[pri_set]:
            tmp_t, tmp_min, tmp_max = self._get_field_nums(field)
            set_text_len = set_text_len + tmp_t
            set_min_len = set_min_len + tmp_min
            set_max_len = set_max_len + tmp_max

        return set_text_len, set_min_len, set_max_len


    def _get_field_nums(self, field_name):
        tmp_text_len = len(self.fields_dict[field_name])
        tmp_min_len = self.fields_def_dict[field_name]['min_length']
        tmp_max_len = self.fields_def_dict[field_name]['max_length']
        return tmp_text_len, tmp_min_len, tmp_max_len



    def _verify_fields(self):

        try_again = False

        if not self.fields_dict:
            raise ValueError('Fields Dictionary not defined')

        for field in self.full_fields_list:
            try:
                tmp_fld = self.fields_def_dict[field]
            except KeyError:
                self.generate_field_limits_dict()
                try_again = True
                break

        if try_again:
            for field in self.full_fields_list:
                if field not in self.fields_dict:
                    raise ValueError('fields in dict do not match template')


    def _final_format_step(self):
        pass

    def _format_str (self):
        self.formatted_str = self.format_str.format(**self.fields_dict)
        self.formatted_str_len = len(self.formatted_str)
        if self.full_string_limits['max_length']:
            self.length_ok = self.formatted_str_len <= self.full_string_limits['max_length']
        else:
            self.length_ok = True

    def _formatted_length(self):
        self._format_str()
        return self.formatted_str_len

    def _check_formatted(self):
        self._format_str()
        return self.length_ok


def find_enclosed(in_string, start, end, include_all = True, default = '' , ignore_after = None):
    all_returns = []

    if not isinstance(in_string, str):
        in_string = str(in_string)

    empty_ret = False
    if not check_in(in_string, start, end):
        empty_ret = True

    if not empty_ret:
        if include_all:
            while check_in(in_string, start, end):
                found_string, in_string = find_in(in_string, start, end, ignore_after)
                all_returns.append(found_string)
            return all_returns
        else:
            found_str, remaining_str = find_in(in_string, start, end, ignore_after)
            return found_str

    else:
        if include_all:
            return [default, ]
        else:
            return default


def find_in(in_string, start, end, ignore_after):
    before_start, after_start = in_string.split(start, 1)
    found_str, remaining_str = after_start.split(end, 1)
    if ignore_after:
        try:
            found_str, junk_str = found_str.split(ignore_after, 1)
        except ValueError:
            pass

    return found_str, remaining_str


def check_in(in_string, start, end):
    if start not in in_string:
        return False

    if end not in in_string:
        return False

    return True


# ===============================================================================
# text / string utils
# ===============================================================================


def is_string(in_obj):
    return isinstance(in_obj, str )


def elipse_trim(instr, trim_length, elipse_string='...'):
    """
    Makes sure strings are less than a specified length, and adds an elipse if it needed to trim them.

    :param instr: The String to trim
    :param trim_length: The max length, INCLUDING the elipse
    :param elipse_string: the string used for the elipse.  Default: '...'
    :return: Trimmed string
    """
    instr = str(instr)
    str_len = trim_length-len(elipse_string)
    if len(instr) > trim_length:
        return '{}{}'.format(instr[:str_len], elipse_string)
    else:
        return instr


def concat(*args, separator=' ', trim_items=True):
    """
    Concatenates strings or lists of strings

    :param args: strings or lists / sets of strings
    :param separator: the string that will be used between strings.  Default: ' '
    :param trim: True/False, trim strings before concatenating.
    :return: string created from contents passed
    """
    tmp_str = ""



    for arg in args:
        if is_string(arg):
            if trim_items:
                arg = arg.strip()
            tmp_str = tmp_str + separator + str(arg)
            tmp_str = tmp_str.strip()
        else:
            try:
                for x in range(len(arg)):
                    tmp_str = tmp_str + separator + str(arg[x])
                    tmp_str = tmp_str.strip()

            except TypeError:
                tmp_str = str(arg)

    return tmp_str

# ===============================================================================
# Tree dictionary
# ===============================================================================


class TreeItem():
    _key = ''
    _parent = None
    _children = []
    _item_dict = {}

    def __init__( self,
                 key = '',
                 parent = None,
                 children = {},
                 item = {} ):
        self._key = key
        self._parent = parent
        self._children = children
        self._item_dict = item


class TreeDict():

    _root_dict = {}
    _root_node = TreeItem( key = 'root'
                          )

    def __init__( self,
                 initial_list,
                 key_field = 'key',
                 parent_key = 'parent',
                 children_field = 'children',
                 ):
        self._initial_list = initial_list
        self._key_field = key_field
        self._parent_key = parent_key
        self._children_field = children_field

        for item in initial_list:
            self._add_to_tree( item )


    def _search_tree( self, key, dict_tree ):
        if key in dict_tree:
            return dict_tree[key]
        else:
            for item in iter( dict_tree.values() ):
                if item._children:
                    return self._search_tree( key, item._children )
        return None

    def _add_to_tree( self, node_dict ):
        parent_node = None
        if node_dict[self._parent_key]:
            parent_node = self._search_tree( node_dict[self._parent_key], self._root_node._children )

        if not parent_node:
            parent_node = self._root_node

        parent_node._children[node_dict[self._key_field]] = TreeItem( key = node_dict[self._key_field],
                                                                      parent = parent_node,
                                                                      children = {},
                                                                      item = node_dict,
                                                                )

    def add_list( self, list_in ):
        for item in list_in:
            self._add_to_tree( item )


    def _get_dnk( self, dict_list ):
        tmp_list = []
        for item in iter( dict_list.values() ):
            if item._children:
                children_list = self._get_dnk( item._children )
            else:
                children_list = []

            tmp_dict = {}
            tmp_dict.update( item._item_dict )
            tmp_dict[self._children_field] = children_list

            tmp_list.append( tmp_dict )

        return tmp_list

    def get_dict_no_key( self ):
        return self._get_dnk( self._root_node._children )
