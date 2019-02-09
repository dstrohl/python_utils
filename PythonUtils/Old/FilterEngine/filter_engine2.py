__author__ = 'dstrohl'


# ===============================================================================
# Filter Objects
# ===============================================================================

class FilterFieldError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FilterFieldForcePass(Exception):
    pass


class FilterFieldForceFail(Exception):
    pass


class EqFilter(object):
    filter_key = 'eq'
    filter_name = 'Equals'

    def __init__(self, match=None, field_name=None, field_type=None, rev=False):
        self.match = match
        self.field_name = field_name
        self.field_type = field_type
        self.rev = rev

    def _filter(self, rec_value):
        return rec_value == self.match

    def _convert_value(self, value):
        if self.field_type is not None:
            return self.field_type(value)
        else:
            return value

    def _get_rec_value(self, record):
        tmp_ret = None

        if self.field_name is not None:
            try:
                tmp_ret = record[self.field_name]
            except (TypeError, KeyError):
                if hasattr(record, self.field_name):
                    tmp_ret = getattr(record, self.field_name)
                    if callable(tmp_ret):
                        tmp_ret = tmp_ret()

            if tmp_ret is None:
                raise FilterFieldError('%s could not be found in %r' % (self.field_name, record))
        else:
            tmp_ret = record

        tmp_ret = self._convert_value(tmp_ret)

        return tmp_ret

    def __call__(self, record):
        if not self.rev:
            return self._filter(self._get_rec_value(record))
        else:
            return not self._filter(self._get_rec_value(record))

    def __str__(self):
        return '<%s> %s %r' % (self.field_name, self.filter_name, self.match)

    def __repr__(self):
        return 'FILTER: '+str(self)

class NeFilter(EqFilter):
    filter_key = 'ne'
    filter_name = 'Not Equals'

    def _filter(self, rec_value):
        return rec_value != self.match


class GtFilter(EqFilter):
    filter_key = 'gt'
    filter_name = 'Greater Than'

    def _filter(self, rec_value):
        return rec_value > self.match


class LtFilter(EqFilter):
    filter_key = 'lt'
    filter_name = 'Less Than'

    def _filter(self, rec_value):
        return rec_value < self.match


class InFilter(EqFilter):
    filter_key = 'in'
    filter_name = 'In'

    def _filter(self, rec_value):
        return rec_value in self.match


class GteFilter(EqFilter):
    filter_key = 'gte'
    filter_name = 'Grater Than or Equals'

    def _filter(self, rec_value):
        return rec_value >= self.match


class LteFilter(EqFilter):
    filter_key = 'lte'
    filter_name = 'Less Than or Equals'

    def _filter(self, rec_value):
        return rec_value <= self.match


class StartsWithFilter(EqFilter):
    filter_key = 'startswith'
    filter_name = 'Starts With'

    def _convert_value(self, value):
        return str(value)

    def _filter(self, rec_value):
        return rec_value.startswith(self.match)


class EndsWithFilter(EqFilter):
    filter_key = 'endswith'
    filter_name = 'Ends With'

    def _convert_value(self, value):
        return str(value)

    def _filter(self, rec_value):
        return rec_value.endswith(self.match)


class NotFilter(EqFilter):
    filter_key = 'not'
    filter_name = 'Not'

    def _filter(self, rec_value):
        if not rec_value:
            return True
        else:
            return False


class IsFilter(EqFilter):
    filter_key = 'is'
    filter_name = 'Is'

    def _filter(self, rec_value):
        if rec_value:
            return True
        else:
            return False


class InstanceFilter(EqFilter):
    filter_key = 'instance'
    filter_name = 'Is Instance Of'

    def _filter(self, rec_value):
        return isinstance(rec_value, self.match)

FILTER_LIST = (
    EqFilter,
    NeFilter,
    GtFilter,
    GteFilter,
    LtFilter,
    LteFilter,
    InFilter,
    NotFilter,
    IsFilter,
    InstanceFilter,
    StartsWithFilter,
    EndsWithFilter,
)




class FilterItem(object):

    def __init__(self, *filters, filter_by='and', dummy=None):
        """
        filters must each be one of:

            a tuple in the format of:
                ('fieldname', 'comparator', 'compare_value', converter),

            a dictionary of keys from:
                'fieldname',
                'comparator',
                'compare_value',
                'converter'
        """
        self.filters = []
        self.filter_by = filter_by
        self.dummy = dummy
        self.passthrough = False

        if filters:
            for f in filters:
                if isinstance(f, dict):
                    self.filters.append(self._get_filter(**f))
                elif isinstance(f, (list, tuple)):
                    self.filters.append(self._get_filter(*f))
                else:
                    raise AttributeError('Invalid filter argument: %r' % f)
            dummy = None
        else:
            if dummy is None:
                raise AttributeError('No filter passed')
            self.passthrough = True


    def _get_filter(self, fieldname=None, comparator=None, compare_value=None, converter=None):

        if comparator.startswith('not') and not comparator == 'not':
            comparator = comparator[3:].strip('_- ')
            reverse = True
        else:
            reverse = False

        for f in FILTER_LIST:
            if comparator == f.filter_key:
                return f(match=compare_value, field_name=fieldname, field_type=converter, rev=reverse)
        raise FilterFieldError('No matching comparator to: %s' % comparator)

    def filter(self, record):
        if self.passthrough:
            return self.dummy

        if self.filter_by == 'and':
            tmp_ret = True
            for f in self.filters:
                if not f(record):
                    return False
        else:
            tmp_ret = False
            for f in self.filters:
                if f(record):
                    return True
        return tmp_ret

    def __call__(self, record):
        return self.filter(record)


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
    _handle_lookup_errors_by = 'fail'

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
        :param handle_lookup_errors_by: How to handle lookup errors on dict / classes,
            * 'raise'  : {DEFAULT} will raise normal errors when attributes or keys are not present.
            * 'fail'   : will continue to process, but will treat missing attribs/keys as match failures.
            * 'pass'   : will continue to process, but will treat missing attribs/keys as match successes.
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

        try:
            tmp_ret = self.filter_set_engine(self._make_filter_set(item), self._filter_with)
        except FilterFieldForceFail:
            tmp_ret = False
        except FilterFieldForcePass:
            tmp_ret = True

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
            self._handle_lookup_errors_by = kwargs.get('handle_lookup_errors_by', self._handle_lookup_errors_by)

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

        try:
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
        except (KeyError, AttributeError):
            if self._handle_lookup_errors_by == 'raise':
                tmp_error_msg = 'FilterFieldError: {} is not in {}'.format(raw_key, list_item)
                raise FilterFieldError(tmp_error_msg)
            elif self._handle_lookup_errors_by == 'fail':
                raise FilterFieldForceFail
            elif self._handle_lookup_errors_by == 'pass':
                raise FilterFieldForcePass

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

