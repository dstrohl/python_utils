__author__ = 'dstrohl'
"""
A collection of simple(ish) functions and classes.
"""

__all__ = ['args_handler', 'GenericMeta', 'DictKey2Method', 'AdvDict', 'DBList', 'UnSet', '_UNSET', 'max_len',
           'TreeDict', 'TreeItem', 'make_list', 'flatten', 'unpack_class_method', 'get_between', 'get_after',
           'get_before', 'get_not_in', 'get_same', 'get_meta_attrs', 'remove_dupes', 'list_in_list', 'list_not_in_list',
           'count_unique', 'index_of_count', 'ListPlus', 'LookupManager', 'is_iterable', 'is_string', 'Error', 'Path',
           'OrderedSet', 'swap', 'replace_between', 'format_as_decimal_string', 'MultiLevelDictManager', 'unslugify',
           'elipse_trim', 'concat', 'generate_percentages', 'convert_to_boolean', 'slugify', 'merge_dictionaries',
           'merge_list', 'Clicker', 'NextItem', 'generate_list_perc', 'quartiles', 'quarter_calc', 'MathList', 'simple_kwarg_handler',
           'SimpleDataClass', 'BasicTreeNode', 'DictOfDict', 'DictOfList', 'PERC_RET', 'format_percentage', 'MathListRecords',
           'MATHLIST_OUTLIERS', 'ClickItem']

import copy
import sys
import collections
from decimal import Decimal
from math import fsum
import statistics
from enum import Enum

# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# region Basic utils

# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

# ===============================================================================
# max_len
#  ===============================================================================


def max_len(*items_in, field_key=None) -> int:
    """
    Returns the length of the longest item

    :param items_in: the items or lists to compare.
    :param field_key: if a key is passed, the length will use that on each item assuming it's a dict like object to
        generate the list.
    :return: returns the max length.

    examples:

        >>> max_len('1', '22', '333')
        3

        >>> max_len(['1', '22', '333'], ['1'], ('1', '22', '333', '4444'))
        4

        >>> d1 = {'t1': ('1', '22', '333', '4444')}
        >>> d2 = {'t1': ('1', '22')}
        >>> d3 = {'t1': ('1', '22', '333')}

        >>> max_len(d1, d2, d3, field_key='t1')
        4
    """
    ret_max = 0
    if field_key is None:
        for l in items_in:
            l = make_list(l)
            for i in l:
                ret_max = max(ret_max, len(i))
    else:
        for l in items_in:
            ret_max = max(ret_max, len(l[field_key]))
    return ret_max


# ===============================================================================
# Error Class
# ===============================================================================

class Error(Exception):
    """Base class for custom exceptions."""

    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__


# ===============================================================================
# UnSet Class
# ===============================================================================

class UnSet(object):
    """
    Used in places to indicated an unset condition where None may be a valid option

    .. note:: *I borrowed the concept from* :py:mod:`configparser` *module*

    Example:
        For an example of this, see :py:class:`MultiLevelDictManager.get`

    if "_UNSET" is used (an instantiated version of thsi) can be used like:

    a = _UNSET
    b = _UNSET

    a == b
    a is b
    a is _UNSET

    """
    UnSetValidationString = '_*_This is the Unset Object_*_'

    def __repr__(self):
        return 'Empty Value'

    def __str__(self):
        return 'Empty Value'

    def __eq__(self, other):
        return isinstance(other, UnSet)


_UNSET = UnSet()


# ===============================================================================
# Path Class
# ===============================================================================


class Path(object):
    """
    A class for managing a path, this could be a file path, but it is more aimed at a path through modules
    or dictionaries.

    Examples:


        p = path()


    """
    _default_key_sep = '.'
    _parsed_path_obj = collections.namedtuple('parsed_path', ('is_root', 'up_levels', 'path'))

    def __init__(self, path='', key_sep=None, key_xform=None, validate_func=None,
                 raise_on_neg_path=False):
        """
        :param path: The current path to be set, this can be a text string, or it can be another :class:`path`
            object.  if this is a path object and other items are not specified, key_sep is set from the
            path object
        :param key_sep: a string used to separate parts of the path, if None, will use the first non-alpha-numeric
        char found. if none found, will use self._default_key_sep (normally set to ".")
        :param key_xform: a function that all keys will be run through, can be something like "string.lower")
        :param validate_func: will be called for each path change to verify that the resulting item is a valid path.
            this is passed the list of path elements and if there is a problem it's the functions's responsibility to
            raise an exception.
        :param raise_on_neg_path: if True, will raise an IndexError if a Path.cd("..") is tried and there is no higher
            path key available.
        """

        self._path = []
        self._validate_func = validate_func
        self._raise_on_neg_path = raise_on_neg_path
        self._key_xform_func = key_xform

        if isinstance(path, self.__class__):
            self.key_sep = key_sep or path.key_sep
        else:
            if key_sep is None:
                for c in path:
                    if not c.isalnum():
                        self.key_sep = c
                        break
                if self.key_sep is None:
                    self.key_sep = self._default_key_sep
            else:
                self.key_sep = key_sep
        self.cd(path)

    def _key_xform(self, path_in):
        if self._key_xform_func is None:
            return str(path_in)
        else:
            return self._key_xform_func(path_in)

    def cd(self, path):
        old_path = self._path.copy()
        # print(f"change dir to {path}")
        if not isinstance(path, self._parsed_path_obj):
            path = self._parse_path_in(path)

        # print(f'new path: {path}')

        if path.is_root:
            self._path.clear()

        if path.up_levels:
            try:
                for x in range(path.up_levels):
                    self._path.pop()
            except IndexError:
                if self._raise_on_neg_path:
                    raise

        self._path.extend(path.path)

        if self._validate_func is not None:
            try:
                self._validate_func(self._path)
            except Exception:
                self._path = old_path
                raise

        return self

    def copy(self, path=None, cd='', class_obj=None, **kwargs):
        """
        Creates an new path object from this one
        :param path: What is the new root path.  if None, will use current one
        :param cd: change directory of new object
        :param key_sep: new key seperator
        :param class_obj: What class object to use.
        """
        class_obj = class_obj or self.__class__

        path = path or self

        kwargs['key_sep'] = kwargs.get('key_sep', self.key_sep)
        kwargs['key_xform'] = kwargs.get('key_xform', self._key_xform)
        kwargs['validate_func'] = kwargs.get('validate_func', self._validate_func)
        kwargs['raise_on_neg_path'] = kwargs.get('raise_on_neg_path', self._raise_on_neg_path)

        tmp_ret = class_obj(path, **kwargs)
        return tmp_ret.cd(cd)

    def _parse_path_in(self, path, as_string=False, is_root=None):
        # print(f"parsing path {path}")
        if isinstance(path, self.__class__):
            if is_root is None:
                is_root = True
            if as_string:
                return self._parsed_path_obj(is_root, 0, self.key_sep.join(path._path))
            else:
                return self._parsed_path_obj(is_root, 0, path._path)

        if not isinstance(path, str):
            try:
                path = self.key_sep.join(list(path))
            except Exception:
                raise TypeError('unable to compare a path with type %s  / %r' % (path.__class__.__name__, path))

        s_count = 0

        while path and path[0] == self.key_sep:
            # print(f'removing header: {path[0]} from "{path}"')
            s_count += 1
            path = path[1:]
            # print(f'new path: {path}')

        if is_root is None:
            if s_count == 1:
                is_root = True
            else:
                is_root = False

        if s_count > 1:
            up_count = s_count - 1
        else:
            up_count = 0

        path = path.rstrip(self.key_sep)
        path = self._key_xform(path)

        if not as_string and path:
            path = path.split(self.key_sep)

        return self._parsed_path_obj(
            is_root=is_root,
            up_levels=up_count,
            path=path
        )

    def path_from(self, key):
        return self[self.find(key):]

    def path_to(self, key):
        return self[:self.find(key)+1]

    def find(self, key, start=0, end=-1):
        key = self._key_xform(key)
        return self._path.index(key, start, end)

    def to_string(self, key_sep=None, leading=True, trailing=False):
        """
        Returns a string format of the path.
        :param key_sep: allows over-writing of the key sep
        :param leading: include key_sep at beginning
        :param trailing: include key_sep at end.
        :return:
        """

        key_sep = key_sep or self.key_sep

        if leading:
            tmp_ret = key_sep
        else:
            tmp_ret = ''

        tmp_ret += key_sep.join(self._path)

        if trailing:
            tmp_ret += key_sep

        return tmp_ret

    def __contains__(self, item):
        try:
            self.find(item)
            return True
        except ValueError:
            return False

    def __call__(self, new_path=''):
        return self.cd(new_path)

    def __str__(self):
        return self.to_string()

    def __len__(self):
        return len(self._path)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._path[item]
        elif isinstance(item, slice):
            tmp_path = self._path[item]
            tmp_ret = self.copy(tmp_path)
            return tmp_ret
        else:
            raise TypeError('path indices must be integers or slices')

    def __iter__(self):
        for i in self._path:
            yield i

    def _make_comp(self, other):
        # print('testing comparison')
        return self._parse_path_in(other, as_string=True).path,  self.to_string(leading=False, trailing=False)

    def __eq__(self, other):
        if isinstance(other, int):
            return len(self) == other
        else:
            other, me = self._make_comp(other)

        return other == me

    def __gt__(self, other):
        if isinstance(other, int):
            return len(self) > other
        else:
            other, me = self._make_comp(other)
        return me.startswith(other) and not other == me

    def __lt__(self, other):
        if isinstance(other, int):
            return len(self) < other
        else:
            other, me = self._make_comp(other)
        return other.startswith(me) and not other == me

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        if isinstance(other, int):
            return len(self) <= other
        else:
            other, me = self._make_comp(other)
        return other.startswith(me) or other == me

    def __ge__(self, other):
        if isinstance(other, int):
            return len(self) >= other
        else:
            other, me = self._make_comp(other)
        return me.startswith(other) or other == me

    def __bool__(self):
        if self._path:
            return True
        else:
            return False

    def __add__(self, other):
        tmp_ret = self.copy()
        other = self._parse_path_in(other, is_root=False)
        # print(f"other path: {other}")
        return tmp_ret.cd(other)

    def __iadd__(self, other):
        other = self._parse_path_in(other, is_root=False)
        return self.cd(other)

    def _merge_list(self, other):
        other = self._parse_path_in(other).path
        me = self._path

        # print(f' combining lists for: {other}')
        # print(f'                 and: {me}')
        combined = merge_list(me, other)

        return combined

    def __and__(self, other):
        tmp_ret = self.copy()
        path = self._parsed_path_obj(
            is_root=True,
            up_levels=0,
            path=self._merge_list(other)
        )
        return tmp_ret.cd(path)

    def __iand__(self, other):
        path = self._parsed_path_obj(
            is_root=True,
            up_levels=0,
            path=self._merge_list(other)
        )
        return self.cd(path)

    __repr__ = __str__

# ===============================================================================
# swap tool
# ===============================================================================


def swap(item: any, opt1: any = True, opt2: any = False)-> any:
    """
    This will take an item and swap it for another item.  By default this is True/False, so if True is passed, False
    is returned.  However, any pair of items can be passed and swapped

    This is used to simplify coding when you dot'n want to do lots of if **not** that and the variable can be
    permenantly changed, or when you are swapping non-boolean values.

    :param item: the item to swap
    :param opt1: (default = True) option 1
    :param opt2: (default = False) option 2
    :return: the option that is not used.

    Examples:
        >>> swap(True)
        False
        >>> swap(False)
        True
        >>> swap('Blue', 'Blue', 'Red')
        'Red'

    """
    if item == opt1:
        return opt2
    elif item == opt2:
        return opt1
    else:
        raise AttributeError(str(item) + ' not in available options')


class NextItem(collections.UserList):
    """
    on calling, will return the current item, then increment a pointer to the next one.
    you can include an offset on calling to tell NextItem how far to increment.

    Examples:
        >>> tn = NextItem([10, 20, 30, 40])

        >>> tn()
        10
        >>> tn(2)
        20
        >>> tn()
        40
        >>> tn()
        10
        >>> tn(-1)
        20
        >>> tn(0)
        10
        >>> tn(-10)
        10
        >>> tn(0)
        30
    """

    def __init__(self, *args, initial_offset=0):
        self.offset = initial_offset
        super(NextItem, self).__init__(*args)

    def __call__(self, offset_change: int = 1) -> any:
        # print(f'offset: {self.offset}')
        tmp_ret = self.data[self.offset]

        self.offset += offset_change
        while self.offset >= len(self):
            self.offset = self.offset - len(self)

        while self.offset < 0:
            self.offset = self.offset + len(self)

        return tmp_ret


# endregion
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
# region Calculator utils
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

# ===============================================================================
# Calculate Quartiles
# ===============================================================================

def quartiles(data_in):
    tmp_data = list(data_in)
    tmp_data.sort()
    tmp_median = statistics.median(tmp_data)
    tmp_len = len(tmp_data)
    tmp_split = int(tmp_len / 2)
    if tmp_len % 2 == 0:
        tmp_upper = tmp_data[tmp_split:]
        tmp_lower = tmp_data[:tmp_split]
    else:
        tmp_upper = tmp_data[tmp_split+1:]
        tmp_lower = tmp_data[:tmp_split]

    q1 = statistics.median(tmp_lower)
    q3 = statistics.median(tmp_upper)
    return q1, tmp_median, q3

# ===============================================================================
# Generate Percentages
# ===============================================================================
# ===============================================================================
# Format Percentage
# ===============================================================================


class PERC_RET(Enum):
    """

    Enumerates standard percentage returns.

    assuming the passed field is 0.2456

    - PERC_RET.AS_INT:  returns 25
    - PERC_RET.AS_FLOAT:  returns 0.2456
    - PERC_RET.AS_FLOAT_PERC:  returns 24.56
    - PERC_RET.AS_STR_INT:  returns '25%'
    - PERC_RET.AS_STR_DOT_2:  returns '25.56%'

    """
    AS_INT = 'int'
    AS_FLOAT = 'float'
    AS_FLOAT_PERC = 'float-perc'
    AS_STR_INT = 'str'
    AS_STR_DOT_2 = 'str-float'


def format_percentage(perc, perc_format=PERC_RET.AS_INT):
    """
    Handles convering and formatting of percentages.

    :param perc: is the percentage, normally expected in float form.
    :param perc_format: is a flag enum `py:class:PERC_RET` that tells the function how to format it.
        Can also be a format string for more complex string formatting.
    :return:
    """
    if perc_format is PERC_RET.AS_STR_INT:
        return '{0:.0%}'.format(perc)

    elif perc_format == PERC_RET.AS_STR_DOT_2:
        perc *= 100
        return ('{0:.{precision}f}%'.format(perc, precision=2))

    elif perc_format == PERC_RET.AS_INT:
        perc *= 100
        return int(perc)

    elif perc_format == PERC_RET.AS_FLOAT:
        return perc

    elif perc_format == PERC_RET.AS_FLOAT_PERC:
        perc *= 100
        return perc

    elif isinstance(perc_format, str) and '{' in perc_format:
        return perc_format.format(perc)

    else:
        raise AttributeError('Unknown Percentage Forat: %r' % perc_format)


class MATHLIST_OUTLIERS(Enum):
    """

    Enumerates static options for otlier support in MathList.

    - MATHLIST_OUTLIERS.NO_OUTLIERS = will not filter any outliers
    - MATHLIST_OUTLIERS.ALL_OUTLIERS = will filter all outliers
    - MATHLIST_OUTLIERS.MINOR_OUTLIERS = Same as above for filtering, for listing of outliers this will
        only list the minor ones.  (since for filtering, major outliers are also minor ones.
    - MATHLIST_OUTLIERS.MAJOR_OUTLIERS = will only filter major outliers.

    """
    NO_OUTLIERS = 0
    ALL_OUTLIERS = 3
    MINOR_OUTLIERS = 1
    MAJOR_OUTLIERS = 2



class MathList(object):
    """
    This object operates like a list, but can perform math functions on it's members.

    Normal list functions will occur on all members, but if inc_outliers is set to other than "all", all math
    functions will exclude outliers.

    You can also remove the outliers by running "rem_outliers", or generate a list of them using "list_outliers".

    Iterating will iterate over all objects UNTIL either "calculate_outliers" is called, or any of the the math
    functions are called, then, if outliers are excluded, it will only iterate over the non-outliers until the cache
    is cleared.

    Math functions will be cached along with the list of outliers for performance.  doing anythign that modifes the
        list contents will clear the cache and the next math function will start to recreate it.

    supports most math lib, and statistics lib functions on the list of values:  (for docs, see the python docs on the function)
        As Properties:
            MathList.sum: sum,
            MathList.fsum: fsum,
            MathList.min: min,
            MathList.max: max,
            MathList.mean: statistics.mean,
            MathList.harmonic_mean: statistics.harmonic_mean,
            MathList.median: statistics.median,
            MathList.median_low: statistics.median_low,
            MathList.median_high: statistics.median_high,
            MathList.mode: statistics.mode,
            MathList.pstdev: statistics.pstdev,
            MathList.pvariance: statistics.pvariance,
            MathList.stdev: statistics.stdev,
            MathList.variance: statistics.variance,
        As Method:
            MathList.median_grouped(interval=1): statistics.median_grouped,


    """

    filter_outliers = MATHLIST_OUTLIERS.NO_OUTLIERS

    minor_outlier_IQR_mult = 1.5
    major_outlier_IQR_mult = 3.0

    default_perc_format = PERC_RET.AS_INT

    OUTLIERS = MATHLIST_OUTLIERS

    MATH_FUNCTIONS = {
        'sum': sum,
        'fsum': fsum,
        'min': min,
        'max': max,
        'mean': statistics.mean,
        'harmonic_mean': statistics.harmonic_mean,
        'median': statistics.median,
        'median_low': statistics.median_low,
        'median_high': statistics.median_high,
        'median_grouped': statistics.median_grouped,
        'mode': statistics.mode,
        'pstdev': statistics.pstdev,
        'pvariance': statistics.pvariance,
        'stdev': statistics.stdev,
        'variance': statistics.variance,
    }
    CACHE_CLEARERS = [
        'append',
        'insert',
        'pop',
        'remove',
        'extend',
        'clear',
    ]

    def __init__(self, init_data=None, **kwargs):
        self._cache_ = {}
        self._kwargs = kwargs
        if init_data is not None:
            self._data = list(init_data)
        else:
            self._data = []

        simple_kwarg_handler(self, kwargs, raise_on_unknown=True)

        if self.filter_outliers == MATHLIST_OUTLIERS.MINOR_OUTLIERS:
            self.filter_outliers = MATHLIST_OUTLIERS.ALL_OUTLIERS

    @property
    def has_float(self):
        if 'has_float' not in self._cache_:
            self._init_cache()
            self._cache_['has_float'] = False
            for x in self:
                if isinstance(x, float):
                    self._cache_['has_float'] = True
                    break
        return self._cache_['has_float']

    @property
    def has_int(self):
        if 'has_int' not in self._cache_:
            self._init_cache()
            self._cache_['has_int'] = False
            for x in self:
                if isinstance(x, int):
                    self._cache_['has_int'] = True
                    break

        return self._cache_['has_int']

    @property
    def has_dec(self):
        if 'has_dec' not in self._cache_:
            self._init_cache()
            self._cache_['has_dec'] = False
            for x in self:
                if isinstance(x, Decimal):
                    self._cache_['has_dec'] = True
                    break
        return self._cache_['has_dec']

    def _calc_types(self):
        if 'outliers' not in self._cache_:
            self._init_cache()
            self._cache_['has_int'] = False
            self._cache_['has_float'] = False
            self._cache_['has_dec'] = False
            for x in self:
                if isinstance(x, int):
                    self._cache_['has_int'] = True
                elif isinstance(x, float):
                    self._cache_['has_float'] = True
                elif isinstance(x, Decimal):
                    self._cache_['has_dec'] = True

    def set_outlier_filter(self, filter_outliers):
        """
        Allows resetting the filter outliers level.

        If this is changed, the cache is cleared.

        :param filter_outliers:
        :return:
        """
        if filter_outliers != self.filter_outliers:
            self.clear_cache()
            self.filter_outliers = filter_outliers

    def rem_outliers(self):
        """
        Will remove any outliers as defined in the init "filter_outliers" option.

        Note, removing outliers will recalculate the outliers, and may cause additional outliers to appear.

        :return:
        """
        self._init_cache()
        self.set_data(list(self))

    def list_outliers(self, include_outliers=None):
        """
        Returns a list of the outliers in the data set.
        
        :param include_outliers: if None, uses the defined "filter_outliers" from the class setup, otherwise can be
            used to determine which outliers will be present.
        :return: 
        """
        if include_outliers is None:
            include_outliers = self.filter_outliers
        outliers = self._calc_outliers(filter_outliers=include_outliers)
        tmp_ret = []
        for i in outliers:
            tmp_ret.append(self[i])
        return tmp_ret

    def set_data(self, data):
        """
        Allows you to reset (or set) the data.  will clear existing data prior to setting.
        
        * Cache Clearing Action
        :param data: an iterable of the data you wish to use.
        :return: 
        """
        self.clear()
        self._data.extend(data)

    def clear_cache(self):
        if self._cache_:
            self._cache_.clear()

    def _get_cache(self, key, **kwargs):
        if 'outliers' not in self._cache_:
            self._init_cache()
        if key not in self._cache_:
            if key in ['pstdev', 'pvariance']:
                kwargs['mu'] = self.mean
            elif key in ['stdev', 'variance']:
                kwargs['xbar'] = self.mean
            func_name = kwargs.pop('func_name', key)
            self._cache_[key] = self.MATH_FUNCTIONS[func_name](self, **kwargs)
        return self._cache_[key]

    def _init_cache(self):
        if 'outliers' not in self._cache_:
            self._cache_['outliers'] = self._calc_outliers()

    def _calc_fences(self):
        # https: // www.wikihow.com / Calculate - Outliers
        q1, q2, q3 = quartiles(self._data)
        iqr = q3 - q1
        major_distance = iqr * self.major_outlier_IQR_mult
        minor_distance = iqr * self.minor_outlier_IQR_mult
        self._cache_['inner_fence_low'] = q1 - minor_distance
        self._cache_['inner_fence_high'] = q3 + minor_distance
        self._cache_['outer_fence_low'] = q1 - major_distance
        self._cache_['outer_fence_high'] = q3 + major_distance

        # print('<major-low> %s <minor-low> %s <in> %s <minor-high> %s <major-high>' % (
        #    self._cache_['outer_fence_low'],
        #    self._cache_['inner_fence_low'],
        #    self._cache_['inner_fence_high'],
        #    self._cache_['outer_fence_high'])
        # )

    def _calc_outliers(self, filter_outliers=None):
        filter_outliers = filter_outliers or self.filter_outliers

        if filter_outliers == MATHLIST_OUTLIERS.NO_OUTLIERS:
            return []

        if 'outer_fence_low' not in self._cache_:
            self._calc_fences()

        tmp_ret = []

        if filter_outliers == MATHLIST_OUTLIERS.ALL_OUTLIERS:
            for i, x in enumerate(self._data):
                if x <= self._cache_['inner_fence_low'] or  x >= self._cache_['inner_fence_high']:
                    tmp_ret.append(i)

        elif filter_outliers == MATHLIST_OUTLIERS.MAJOR_OUTLIERS:
            for i, x in enumerate(self._data):
                if x <= self._cache_['outer_fence_low'] or  x >= self._cache_['outer_fence_high']:
                    tmp_ret.append(i)

        elif filter_outliers == MATHLIST_OUTLIERS.MINOR_OUTLIERS:

            for i, x in enumerate(self._data):
                if self._cache_['inner_fence_low'] >= x > self._cache_['outer_fence_low']:
                    tmp_ret.append(i)
                elif self._cache_['inner_fence_high'] <= x < self._cache_['outer_fence_high']:
                    tmp_ret.append(i)
        return tmp_ret

    def __iter__(self):
        if 'outliers' in self._cache_:
            for i, x in enumerate(self._data):
                if i not in self._cache_['outliers']:
                    yield x
        else:
            for x in self._data:
                yield x

    def __len__(self):
        if 'outliers' in self._cache_:
            if 'len' not in self._cache_:
                self._cache_['len'] = len(self._data) - len(self._cache_['outliers'])
            return self._cache_['len']
        return len(self._data)

    def __add__(self, other):
        tmp_data = self._data + other
        tmp_item = self.copy()
        tmp_item.set_data(tmp_data)
        return tmp_item

    def __iadd__(self, other):
        self._data += other
        return self

    def __mul__(self, other):
        tmp_data = self._data * other
        tmp_item = self.copy()
        tmp_item.set_data(tmp_data)
        return tmp_item

    def __imul__(self, other):
        self._data *= other
        return self

    def __eq__(self, other):
        return self._data == other

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self.clear_cache()
        self._data[key] = value

    def __contains__(self, item):
        return item in self._data

    def __delitem__(self, item):
        self.clear_cache()
        del self._data[item]

    def __call__(self, item):
        self.append(item)
        return len(self._data)

    def copy(self):
        return self.__class__(self._data, **self._kwargs)

    # The below return a value list
    # -------------------------------------------------------------------------

    def calc_list(self,
                  fields=None,
                  format_dict=None,
                  func_dict=None,
                  perc_return=PERC_RET.AS_INT,
                  return_row_as=None,
                  force_total=None,
                  row_num_offset=0,
                  start_at=None,
                  end_at=None,
                  inc_header=False,
                  interval=None):
        """
        returns a list of rows of data with various calculations.

        :param fields: Can be one or more of:

            value: the value of the item in the list.
            row_num: a number starting at row_num_offset
            running_sum: the total of the values to this row
            perc_rows_done: the percentage that it is based on the row number
            running_perc_value_done: the percentage that this row is towards the total
            perc_of_total: the percentage that this row is of the overall total
            difference_from_mean: a number indicating how far from the mean value this one is
            difference_from_median:  a number indicating how far from the median value this one is
            outlier_flag: a string indicating if it a major outlier or minor outlier
            running_mean: a running average at this point of time
            running_median: a running median at this point in time
            running_min: a running min value
            running_max: a running max value
            running_change: a running number of the change from the last one.
            running_perc_change: a running percentage of the change from the last value
            *: any other field name will assume that there is a function in the function_dict to calculate this.

            (if no fields are passed, "value" is used as the single default field)
        :param format_dict: a dict to format the numbers, the keys of the dict are the fields.
            any fields that do not have matching keys will be returned as their native type.
            fields that contain a string will be formatted using that string as a format code
            fields that contain an object will be passed the value into that object.  for example a field with int will be
                passed as int(value).
        :param func_dict: a dict of functions that each value will be run through to modify the return.
            each function will be called as follows: func(value, field_name, row_num, forced_total, self) and should return only one value.
            if the function returns None, then that row is skipped (even if other fields have values)
        :param return_row_as: can be any of:
            'dict': will return the row as a dict object with the keys being the field names.
            'list': will return the row as a list of objects in the order of the fields as passed.
            'named': will return the row as a named tuple
            object: will return the row as the object passed, each row will be instantiated with the fields as kwargs
                for the object.
            None: will return a single value if one field is used, or a list of multiple fields are passed.
        :param perc_return: Handle formatting of percentage returns, can be a dict or string, uses PERC_RET enum or a
            format string.  If a string, will use that option for all pecentages, if a dict, the keys are for the field
            names with the values in that key being the format code for that field.
        :param end_at: uses slice notation
        :param start_at: uses slice notation
        :param row_num_offset: only for the row_number field, will offset the numbers by this number.  does not impact start or end at values.
        :param force_total:  allows forcing a total that is different from the calculated total.  only used for percentage calculations.
        :param inc_header: only for list returns, will include a row in the beginning listing the fields.
        :param interval: only returns every x item.
        :return:

        Note: functions are performed before formatting.
            - start_at and end_at only impact the returned rows, all calculations are based on all values still.
        """
        fields = fields or ['value']
        fields = make_list(fields)
        func_dict = func_dict or {}
        format_dict = format_dict or {}
        total = force_total or self.sum
        tmp_ret = []
        running_total = 0
        if 'perc_rows_done' in fields:
            row_count = len(self)
        else:
            row_count = 0

        if 'outlier_flag' in fields and 'outer_fence_low' not in self._cache_:
            self._calc_fences()

        if return_row_as is None and len(fields) > 1:
            return_row_as = 'list'

        elif isinstance(return_row_as, str) and return_row_as == 'named':
            return_row_as = collections.namedtuple('return_row_as', field_names=fields)

        past_data = []
        running_min = sys.maxsize
        running_max = 0
        last_value = 0
        first_rec = True

        if not isinstance(perc_return, dict):
            perc_return = {
                'perc_rows_done': perc_return,
                'running_perc_value_done': perc_return,
                'perc_of_total': perc_return,
                'running_perc_change': perc_return
            }

        if return_row_as == 'list' and inc_header:
            tmp_ret.append(fields.copy())

        for index, row_value in enumerate(self):
            tmp_row = {}
            offset_index = index + row_num_offset

            if 'running_median' in fields:
                past_data.append(row_value)

            running_min = min(running_min, row_value)
            running_max = max(running_max, row_value)
            running_total += row_value

            skip_fields = False

            if interval is not None:
                if (index + 1) % interval != 0:
                    skip_fields = True

            if not skip_fields:
                for field in fields:
                    if field == 'value':
                        field_val = row_value
                    elif field == 'row_num':
                        field_val = offset_index
                    elif field == 'running_sum':
                        field_val = running_total
                    elif field == 'perc_rows_done':
                        field_val = (index + 1) / row_count

                    elif field == 'running_perc_value_done':
                        # print('running_total: %s' % running_total)
                        # print('total: %s' % total)
                        field_val = running_total / total

                    elif field == 'perc_of_total':
                        field_val = row_value / total

                    elif field == 'difference_from_mean':
                        field_val = row_value - self.mean

                    elif field == 'difference_from_median':
                        field_val = row_value - self.median
                        # print('row_value: %s' % row_value)
                        # print('median: %s' % self.median)

                    elif field == 'outlier_flag':
                        if row_value < self._cache_['outer_fence_low'] or row_value > self._cache_['outer_fence_high']:
                            field_val = 'major'
                        elif row_value < self._cache_['inner_fence_low'] or row_value > self._cache_['inner_fence_high']:
                            field_val = 'minor'
                        else:
                            field_val = ''

                    elif field == 'running_mean':
                        field_val = running_total / (index + 1)

                    elif field == 'running_median':
                        if first_rec:
                            field_val = row_value
                        else:
                            field_val = statistics.median(past_data)

                    elif field == 'running_min':
                        field_val = running_min

                    elif field == 'running_max':
                        field_val = running_max

                    elif field == 'running_perc_change':
                        change_val = row_value - last_value
                        if last_value == 0:
                            if change_val == 0:
                                field_val = 0
                            else:
                                field_val = 1
                        else:
                            field_val = change_val / last_value

                    elif field == 'running_change':
                        field_val = row_value - last_value

                    else:
                        if field not in func_dict:
                            raise AttributeError('unknown field (%s) passed with no associated function' % field)
                        field_val = None

                    if field in func_dict:
                        field_val = func_dict[field](
                            value=field_val,
                            field_name=field,
                            row_num=index,
                            forced_total=force_total,
                            math_list=self)

                    if field in perc_return:
                        field_val = format_percentage(field_val, perc_return[field])
                    elif 'perc' in field:
                        field_val = format_percentage(field_val, self.default_perc_format)

                    if field in format_dict:
                        if isinstance(format_dict[field], str):
                            field_val = format_dict[field].format(field_val)
                        else:
                            field_val = format_dict[field](field_val)

                    tmp_row[field] = field_val

                if return_row_as is None:
                    tmp_ret.append(tmp_row[fields[0]])

                elif isinstance(return_row_as, str):
                    if return_row_as == 'list':
                        tmp_row_list = []
                        for field in fields:
                            tmp_row_list.append(tmp_row[field])
                        tmp_ret.append(tmp_row_list)
                    elif return_row_as == 'dict':
                        tmp_ret.append(tmp_row)
                    else:
                        raise AttributeError('invalid "return_row_as" value of %s' % return_row_as)
                else:
                    tmp_obj = return_row_as(**tmp_row)
                    tmp_ret.append(tmp_obj)

            last_value = row_value
            first_rec = False

        tmp_ret = tmp_ret[start_at:end_at]

        return tmp_ret

    # the below return single values
    # -------------------------------------------------------------------------

    def __getattr__(self, item):
        # print('checking for attr: %s' % item)
        if item in self.MATH_FUNCTIONS:
            return self._get_cache(item)
        if item in self.CACHE_CLEARERS:
            self.clear_cache()
        return getattr(self._data, item)

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return 'MathList(%s)' % self._data

    @property
    def sum(self):
        if self.has_float:
            return self._get_cache('fsum')
        else:
            return self._get_cache('sum')

    def median_grouped(self, interval=1):
        cache_name = 'median_grouped_' + str(interval)
        return self._get_cache(cache_name, func_name='median_grouped', interval=interval)

# ===============================================================================
# MathList Record Handler
# ===============================================================================

class MathListRecords(object):
    """
    a consolidator class that allows handling multiple MathList objects based on records.

    """
    mathlist_obj = MathList

    def __init__(self, field_defaults=None, mathlist_kwargs=None, group_fields=None, value_fields=None):

        self.lists = DictOfDict()
        self.lists.sub_type = MathList

        self.field_defaults =  field_defaults or {}
        self.mathlist_kwargs = mathlist_kwargs or {}


    def add_rec(self, record_in):



# ===============================================================================
# Generate Percentages
# ===============================================================================

def generate_list_perc(data_in, precision=0, ret_as=int, ret_perc=True, total=None):
    if total is None:
        total = 0
        for item in data_in:
            total += item

    tmp_ret = []

    if total == 0:
        raise ZeroDivisionError('Total cannot be zero for percentage generation')

    for item in data_in:
        tmp_perc = item / total

        if ret_as is str:
            if ret_perc:
                tmp_ret.append('{0:.{precision}%}'.format(tmp_perc, precision=precision))
            else:
                tmp_perc *= 100
                tmp_ret.append('{0:.{precision}f}'.format(tmp_perc, precision=precision))

        elif ret_as is int:
            tmp_perc *= 100
            tmp_ret.append(int(tmp_perc))
        elif ret_as is float:
            if ret_perc:
                tmp_perc *= 100
            tmp_ret.append(tmp_perc)
        else:
            raise ValueError('ret_as type invalid')
    return tmp_ret


def generate_percentages(data_array, key_fieldname=None, access_fieldname=None, value_fieldname='value',
                         perc_fieldname='perc', precision=0, ret_as=int, ret_perc=True):
    """

    Computes percentage of the total column per item and adds it to the array (or replaces an existing field.)

    assumes data_array will be in the format of:
    ::
        [
        { 'row_fieldname' : [{field1:data1, field2,data2, field3:data3},{field1:data1, field2,data2, field3:data3},{field1:data1, field2,data2, field3:data3}]}

        ]
    ::

    * if no newfieldname, fieldname is replaced with percentages
    * if fieldnames are numeric, a set is assumed instead of a dict
    * if new_fieldname is numeric, the data will be inserted at that position (zero based).
    """

    key_lookup = DictOfList()

    if perc_fieldname is None:
        perc_fieldname = value_fieldname

    for rec_index, rec in enumerate(data_array):
        if access_fieldname:
            rec = rec[access_fieldname]

        key_counter = 0

        for item in rec:
            if key_fieldname is None:
                if value_fieldname is None:
                    key_lookup[key_counter].append(item)
                else:
                    key_lookup[key_counter].append(item[value_fieldname])
            else:
                key_lookup[item[key_fieldname]].append(item[value_fieldname])
            key_counter += 1

    for perc_key in key_lookup.keys():
        tmp_set = generate_list_perc(key_lookup[perc_key], precision=precision, ret_as=ret_as, ret_perc=ret_perc)
        key_lookup[perc_key] = tmp_set

    for rec_index, rec in enumerate(data_array):
        if access_fieldname:
            rec = rec[access_fieldname]

        key_counter = 0

        for item in rec:
            if key_fieldname is None:
                if perc_fieldname is None:
                    # item =
                    key_lookup[key_counter].append(item)
                else:
                    key_lookup[key_counter].append(item[value_fieldname])
            else:
                key_lookup[item[key_fieldname]].append(item[value_fieldname])
            key_counter += 1

    return data_array

'''
def generate_percentages(data_array, row_fieldname, data_fieldname, newfieldname=""):
    """

    Computes percentage of the total column per item and adds it to the array (or replaces an existing field.)

    assumes data_array will be in the format of:
    ::
        [
        { 'row_fieldname' : [{field1:data1, field2,data2, field3:data3},{field1:data1, field2,data2, field3:data3},{field1:data1, field2,data2, field3:data3}]}

        ]
    ::

    * if no newfieldname, fieldname is replaced with percentages
    * if fieldnames are numeric, a set is assumed instead of a dict
    * if new_fieldname is numeric, the data will be inserted at that position (zero based).
    """

    for col in range(len(data_array[1][row_fieldname])):

        col_total = 0
        # print('new col')
        for row in range(len(data_array)):
            rec = data_array[row][row_fieldname][col]
            # print( rec )
            col_total = col_total + rec[data_fieldname]
            # print(col_total)

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

    # print(data_array)

    return data_array
'''

# ===============================================================================
# Quarter Calc  (not flexible enough to use broadly at this point)
# ===============================================================================

#: TODO make this work for more options

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



# endregion
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
# region Dictionary utils
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# ===============================================================================
# merges dictionaries recursively.
# ===============================================================================

def merge_dictionaries(*args, depth=0, max_depth=10):
    tmp_out_dict = {}

    if depth == max_depth:
        raise AttributeError('Merge dictionaries recussion depth max reached!')

    for arg in args:
        if is_iterable(arg):
            depth += 1
            tmp_out_dict.update(merge_dictionaries(arg, depth))

        elif isinstance(arg, dict):
            tmp_out_dict.update(arg)

        else:
            raise TypeError('Merge dictionaries only accepts iterables of dictionaries')

    return tmp_out_dict


# ===============================================================================
# Multilevel dictionary
# ===============================================================================


class MultiLevelDictManager(object):
    """
    This provides a dictionary view that can be accessed via a :py:class:`Path` object or string.

    Examples:
        >>> mld = MultiLevelDictManager()

        >>> test_dict = {
                'level': '1',
                'l2a': {
                    'level': '2a',
                    'l3aa': {
                        'level': '3aa',
                        'l4aaa': {'level': '4aaa'},
                        'l4aab': {'level': '4aab'}},
                    'l3ab': {
                        'level': '3ab',
                        'l4aba': {'level': '4aba'},
                        'l4abb': {'level': '4abb'}}},
                'l2b': {
                    'level': '2b',
                    'l3ba': {
                        'level': '3ba',
                        'l4baa': {'level': '4baa'},
                        'l4bab': {'level': '4bab'}},
                    'l3bb': {
                        'level': '3bb',
                        'l4bba': {'level': '4bba'},
                        'l4bbb': {'level': '4bbb'}}}
                }


        >>> mldm = MultiLevelDictManager(test_dict)

        >>> mldm.cd['level']
        1

        >>>mldm['.l2a.level']
        '2a'

        >>>mldm('.l2a.')
        >>>mldm.get('level')
        '2a'

        >>>mldm.cd('.l2b.l3bb')
        >>>mldm['..level']
        '2b'

        >>>mldm.cd('.l2b.l3bb.l4bbb')
        >>>mldm['....level']
        '1'

        >>>mldm.cd('.l2b.l3bb.14bbb')
        >>>mldm['......level']
        '1'

        >>>mldm.cd('.l2b.l3bb.l4bbb')
        >>>mldm.get('......leddvel', 'noanswer')
        'noanswer'

        >>>mldm.cd('.l2b.l3bb.l4bbb')
        >>>mldm.pwd
        'l2b.l3bb.l4bbb'

        >>>mldm.cd('.')
        >>>mldm.get('l2b.l3bb.l4bbb.level', cwd=True)
        '4bbb'

        >>>mldm.get('..level', cwd=True)
        '3bb'


    """
    dict_db = None
    key_sep = '.'

    def __init__(self,
                 dict_db=None,
                 current_path='',
                 key_sep='.'):
        """
        :param dict_db: the dictionary to use for lookups.  The keys for this must be strings.
        :param current_path: the current path string (see :py:class:`Path` for more info on path strings)
        :param key_sep: the string to use to seperate the keys in the path, by default '.'
        """
        self.dict_db = dict_db
        if isinstance(current_path, str):
            current_path += key_sep
        self.path = Path(current_path, key_sep=key_sep)
        # self.key_sep = key_sep

    def load(self,
             dict_db,
             current_path=''):
        """
        Allows you to load a new dictionary, the path will be reset unless passed
        :param dict_db: The new dictionary for lookups
        :param current_path: The new path to use (will be reset to '.' unless passed)
        """
        self.dict_db = dict_db
        self.path(current_path)

    def cd(self, key):
        """
        Change directory path to a new path string (key)

        :param key: the new path string to chance to, see :py:class:`Path` for info on path strings
        :return:
        """
        self.path.cd(key)
        # self._pwd = self._parse_full_path(key)

    def get(self, key, default=_UNSET, cwd=False):
        """
        will get the data from the specified path string

        :param key: The path string to use (see :py:class:`Path` for info on path strings)
        :param default: if passed, a default to return if the key is not found at any level.
        :param cwd: Will change the current path to the path of the key passed.
        """

        cur_resp = self.dict_db
        tmp_path = Path(self.path, key)
        # key_path = self._parse_full_path(key)

        for k in tmp_path:
            try:
                cur_resp = cur_resp[k]
            except KeyError:
                if default is not _UNSET:
                    return default
                else:
                    msg = 'Key: "{}" not found in dict: {}'.format(k, self.dict_db)
                    raise KeyError(msg)
            except TypeError:
                msg = "parameter passed is not a dict or does not implement key lookups"
                raise TypeError(msg)

        if cwd:
            self.path = tmp_path

        return cur_resp

    def cwd(self, key):
        """
        Changes the current working directory to the passed path string (key).

        This is a shortcut for having to pass a path with a '.' at the end to signify a path

        :param key: The path string to use (see :py:class:`Path` for info on path strings)
        """
        self.path.cwd(key)

    @property
    def pwd(self):
        """
        Returns the current working directory and item (if present)
        """

        return self.path.path_str()
        # return self.key_sep.join(self._pwd)

    def __getitem__(self, item):
        return self.get(item)

    def __repr__(self):
        return 'MultiLevelLookupDict: current_path:{}  Dict:{}'.format(self.path, self.dict_db)

    __call__ = get


# ===============================================================================
# Dictionary Helper Objects
# ===============================================================================


class DictKey2Method(object):
    """
    Helper utility to allow dict keys to be accessed by attrs.

    Example:

        >>> d = {'one': 1, 'two': 2}
        >>> dk2m = DictKey2Method(d)
        >>> dk2m.one
        1
        >>> dk2m.two
        2
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

    This uses the :py:class:`DictKey2Method` class and wraps it in a :py:class:`dict`.  This also forces the method
    lookups to use a special method name, thus minimizing conflicts with the existing dict methods.

    :param property_name: The name of the property to use to access the fields. (Default = 'key')

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
# Tree dictionary
# ===============================================================================


class TreeItem():
    _key = ''
    _parent = None
    _children = []
    _item_dict = {}

    def __init__(self,
                 key='',
                 parent=None,
                 children={},
                 item={}):
        self._key = key
        self._parent = parent
        self._children = children
        self._item_dict = item


class TreeDict():
    _root_dict = {}
    _root_node = TreeItem(key='root'
    )

    def __init__(self,
                 initial_list,
                 key_field='key',
                 parent_key='parent',
                 children_field='children'):
        self._initial_list = initial_list
        self._key_field = key_field
        self._parent_key = parent_key
        self._children_field = children_field

        for item in initial_list:
            self._add_to_tree(item)


    def _search_tree(self, key, dict_tree):
        if key in dict_tree:
            return dict_tree[key]
        else:
            for item in iter(dict_tree.values()):
                if item._children:
                    return self._search_tree(key, item._children)
        return None

    def _add_to_tree(self, node_dict):
        parent_node = None
        if node_dict[self._parent_key]:
            parent_node = self._search_tree(node_dict[self._parent_key], self._root_node._children)

        if not parent_node:
            parent_node = self._root_node

        parent_node._children[node_dict[self._key_field]] = TreeItem(key=node_dict[self._key_field],
                                                                     parent=parent_node,
                                                                     children={},
                                                                     item=node_dict,
        )

    def add_list(self, list_in):
        for item in list_in:
            self._add_to_tree(item)


    def _get_dnk(self, dict_list):
        tmp_list = []
        for item in iter(dict_list.values()):
            if item._children:
                children_list = self._get_dnk(item._children)
            else:
                children_list = []

            tmp_dict = {}
            tmp_dict.update(item._item_dict)
            tmp_dict[self._children_field] = children_list

            tmp_list.append(tmp_dict)

        return tmp_list

    def get_dict_no_key(self):
        return self._get_dnk(self._root_node._children)


# ===============================================================================
# Tree Node
# ===============================================================================

class BasicTreeNode():
    """
    This is a basic tree node, it can be created, then child nodes can be added, removed, etc.
    """
    key = ''
    data = None
    parent = None
    children = None
    ucid = 0
    path_sep = '.'
    my_path = ''
    root = False

    def __init__(self,
                 tree=None,
                 key=None,
                 parent=None,
                 data=_UNSET):
        self.tree = tree
        self.parent = parent
        self.children = {}
        self.data = data
        self.key = self._make_child_key(key)

        if parent is None:
            self.root = True
            self.my_path = self.key
        else:
            self.my_path = self.parent.path + self.path_sep + self.key

    def add_child(self, node=None, key=None, data=_UNSET):
        if node is None:
            key = self._make_child_key(key)
            self.children[key] = self.__class__(self.tree, key, self, data)
        else:
            self.children[node.key] = node

    def rem_child(self, node=None, key=None):
        if node is not None:
            key = node.key
        del self.children[key]

    def child(self, key):
        return self.children[key]

    @property
    def siblings(self):
        return self.parent._my_kids_sibs(self)

    def _my_kids_sibs(self, child):
        for i in self.children:
            if i != child:
                yield i

    def _make_child_key(self, key):
        if not self.root:
            if key is None:
                self.parent._ucid += 1
                return str(self.parent._ucid)
            else:
                return key
        else:
            if key is None:
                return '0'
            else:
                return key

    def __getitem__(self, item):
        return self.child(item)

    def __bool__(self):
        return self.data is not _UNSET

    def __delitem__(self, key):
        self._rem_child_entry(key)

    def __repr__(self):
        return 'TreeNode: '+self.my_path

    def __call__(self):
        return self.data


# ===============================================================================
# Tree Node
# ===============================================================================

class DictOfDict(collections.UserDict):
    """
    This is a quick dict utility that assumes that all sub fields are dicts, and if you do a
    a lookup on a field which is not there, it will create it as a dict.

    this is mostly intended for cases where you have a dict in a dict and you want to lookup on the
    second level regularly.
    """
    sub_type = dict
    sub_type_kwargs = None

    def __getattr__(self, item):
        if item not in self:
            if self.sub_type_kwargs is not None:
                self[item] = self.sub_type(**self.sub_type_kwargs)
            else:
                self[item] = self.sub_type()

        return super(DictOfDict, self).__getattr__(item)


class DictOfList(DictOfDict):

    """
    same as above but this auto-creates things as lists.
    """
    sub_type = list


# endregion
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
# region List utils
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************



# ===============================================================================
# merge list
# ===============================================================================

def merge_list(list_a: list, list_b: list) -> list:
    """
    Merge_list will merge two lists together, but will combine any overlapping sections.

    :param list_a: first list to compare, this is the root list
    :param list_b: second list to merge onto the end of list_a
    :return: a merged list  consisting of list a + the non-overlapping parts of list_b

    examples:

    >>> merge_list([1,2,3,4], [1,2,3,4])
    [1,2,3,4]

    >>> merge_list([1,2,3,4], [2,3,4,5])
    [1,2,3,4,5]

    >>> merge_list([1,2,3,4], [1,2,3])
    [1,2,3,4,1,2,3]  # note that the second is nto any valid ending of the first.

    >>> merge_list([1,2,3,4], [5,6,7,8])
    [1,2,3,4,5,6,7,8]

    Note that we are checking for the sequence of values, so duplicate values will not count for overlap
    >>> merge_list([1,2,3,4], [1,3,4,5])
    [1,2,3,4,1,3,4,5]

    """
    list_a = list(list_a)
    list_b = list(list_b)

    offset = len(list_a) - len(list_b)
    if offset < 0:
        offset = 0

    while offset < len(list_a):
        for a, b in zip(list_a[offset:], list_b):
            print(f'comparing {a} and {b}')
            if a != b:
                print('  not equal')
                break
        else:
            if offset == 0:
                if len(list_a) > len(list_b):
                    return list_a
                else:
                    return list_b
            list_1 = list_a[:offset]
            list_2 = list_b
            tmp_ret = list_1 + list_2
            print(f'good comparison, offset = {offset}')
            print(f'   list_1: {list_1!r}')
            print(f'   list_2: {list_2!r}')
            return tmp_ret
        offset += 1

    return list_a + list_b


# ===============================================================================
# a list that allows for lookups more like a dictionary.
# ===============================================================================


class DBList(object):
    """
    This is a list type object that also allows for lookups like a dictionary based on stored dict keys.

    The only way this works if if dictionaries are stored in the list, each with a key matching the key string.

    NOTE: if there are dupe items (by defined key) in the starting list, only the last one will be kept.

    :param starting_list: A list of dictionaries, each must contain a key matching the "dict_key" field
    :param dict_key: the key used to find the keys for looking up the dictionaries.

    Example:

        >>> dict_list = [{'name':'john','age':21},{'name':'jane','age':22}]
        >>> dl = DBList(dict_list, 'name')
        >>> dl['john']
        {'name':'john','age':21}
        >>> dl['jane']['age']
        22

    """

    internal_dict = {}

    #: TODO Add rest of list and dict functionality

    def __init__(self,
                 starting_list,
                 dict_key):

        for item in starting_list:
            self.internal_dict[item[dict_key]] = item

    def __iter__(self, key):
        return self.internal_dict[key]

    def get_list(self):
        """
        returns a list of the items.
        """
        return self.internal_dict.items()

    def get_dict(self):
        """
        returns the internal dictionary.
        """
        return self.internal_dict


# ===============================================================================
# general list utilities.
# ===============================================================================


def make_list(in_obj):
    """
    Will take in an object, and if it is not already a list or other iterables, it will convert it to one.

    This is helpfull when you dotn know if someone will pass a single string, or a list of strings (since strings
    are iterable you cant just assume)

    This uses the :py:func:`is_iterable` function from this module.

    :param in_obj: list, string, or other iterable.
    :return: a list object.
    """

    if is_iterable(in_obj):
        return in_obj
    else:
        return [in_obj]


def flatten(l, ltypes=(list, tuple), force=None):
    """
    Will flatten lists and tuples to a single level

    .. note:: from: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html

    :param l: list or tuple to be flattened
    :param ltypes: the types of items allowed to be flattened, default = (list, tuple)
    :param force: forces return to be of this type.
    :return: single level list or tuple (same as what went in)

    Example:
        >>> l = [1, 2, 3, [4, 5, [6, 7]]]
        >>> flatten(l)
        [1, 2, 3, 4, 5, 6, 7]

    """

    if is_string(l):
        if force is None:
            return []
        elif force == list:
            return [l]
        elif force == tuple:
            return tuple(l, )
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


def unpack_class_method(class_object_list, method, ret_type=str, args_list=None, kwargs_dict=None):
    """
    This will iterate through a list of objects and pull a value from each one, even if the items are functions.

    :param class_object_list: A list of objects
    :param method: the method to pull from (string)
    :param return_type: what type of data is expected to be returned. this should be a function/class that will convert
        to the type desired.
        for example, the default is str, but int, float are also options.
    :param args_list: if the method is a function, a list of arguments to pass
    :param kwargs_dict: if the method is a function, a dict of keyword arguments to pass.

    """
    if args_list is None:
        args_list = []
    if kwargs_dict is None:
        kwargs_dict = {}

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

    :param l1: list 1
    :param l2: list 2
    :return: a list of items in both "list 1" and "list 2"
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
    """
    Checks to see if ALL of the items in a list are in the other list

    :param is_this: list of items to check for
    :param in_this: list of items to check against
    :return: booleanTrue if all items in is_this are in in_this.

    .. Warning: currently broken!!!

    """
    #: TODO FIX THIS!!
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
    Counts the unique items a list of items, or counts the unique keys in a list of dicts.

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
        raise TypeError('count_unique requires a list or tuple, not a ' + type(data_in).__name__)

    if dict_key:
        for item in data_in:
            try:
                tmp_list.append(item[dict_key])
            except KeyError:
                if on_key_error == 'raise':
                    raise KeyError('count_unique: dict key "' + dict_key + '" not found')
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

    =====================    ===========================================================================================
    ListPlus.add             allows insert new records past the existing last record
    ListPlus.update          allows updating records or adding them past the existing last record
    ListPlus[key] = value    same as listPlus.update though uses list key notation
    ListPlus.get             allows for setting a default response instead of generating an error if rec does not exist.
    =====================    ===========================================================================================
    """

    def _update_function(self, curr_obj, new_obj):
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
            raise TypeError('ListPlus.get takes at most 2 arguments, ' + str(len(args)) + ' given')

    '''
    def __setitem__(self, i, x):
        if isinstance(i, int):
            self.update(i, x)
        else:
            raise TypeError('ListPlus indices must be integers, not '+type(i).__name__)
    '''



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


    Based on a recipe originally posted to ActiveState Recipes by Raymond Hettiger,
    and released under the MIT license.

    Rob Speer's changes are as follows:

    * changed the content from a doubly-linked list to a regular Python list.
        Seriously, who wants O(1) deletes but O(N) lookups by index?
    * add() returns the index of the added item
    * index() just returns the index of an item
    * added a __getstate__ and __setstate__ so it can be pickled
    * added __getitem__
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




# endregion
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
# region Class utils
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# ===============================================================================
# Simple Argument Handler
# ===============================================================================

def simple_kwarg_handler(parent_obj, kwargs, raise_on_unknown=True):
    """
    This is a simple kwarg handler that will take any kwargs passed and create them on the parent object.

    :param parent_obj:  The object that the parameters will be created on.
    :param raise_on_unknown: if the parameter is not already on the object, this will raise an attribute error.
    :param kwargs: the kwargs to save.
    :return:  None
    """
    for key, value in kwargs.items():
        if not hasattr(parent_obj, key) and raise_on_unknown:
            raise AttributeError("object does not have attribute %s" % key)
        setattr(parent_obj, key, value)


# ===============================================================================
# Simple Data Class
# ===============================================================================

class SimpleDataClass(object):
    def __init__(self, **kwargs):
        simple_kwarg_handler(self, kwargs, raise_on_unknown=False)


# ===============================================================================
# Argument Handler
# ===============================================================================


def args_handler(parent_obj,
                 args=None,
                 attr_list=None,
                 kwargs=None,
                 skip_list=None,
                 skip_startswith='-',
                 overwrite=True,
                 do_not_check_parent_attrs=False):
    """
    Args Handler that will take an args or kwargs list and set contents as attributes.  This also allows some control
    over which values to set.

    This can be used when creating that may need to take different types of arguments as it can intelligently detect
    fields passed as arguments, keyword arguments, or a dictionary of arguments, it can handle required arguments as
    as well as long lists of arguments very simply.

    Parameters:
        parent_obj: the object that gets the attributes
        args: a list from the args parameter
        kwargs: a dict from the kwargs parameter
        attr_list: a list of the attributes to use, required if args are passed

            .. note::
                * if the attribute '_attr_list' exists in the parent object, this will be used.
                * if an attr_list exists for kwargs dicts, only the keys in the args list will be included.
                * if there are more items in the args list than in the attr list, only the ones in the list will be used.
                * if there are more items in the attr list than in the args list, only the ones in the args list will be used.
                * if both args and kwargs are passed, the attr list will ONLY be used for the args
                * if the same attr is in both args and kwargs, kwargs will take precedence.
                * if the attribute name starts with a \*, (star) it will be required and a AttributeError will be raised
                    if it is not found in either the args or kwargs.
                * if a list of tuples can be passed to handle default settings, these should be in the format of:
                    ('attribute name',default_setting)
                    not all items need to be tuples, you can mix and match strings and tuples for fields with no
                    requirement.

        skip_list: a list of attributes to skip

            .. note::
                * if the attribute '_args_skip_list' exists in the parent object, this will be used.

        skip_startswith: skip attributes that start with this string (defaults to '_')

            .. note::
                * if the attribute '_args_skip_startswith' exists in the parent object, this will be used.

        overwrite: overwrite existing attributes, can be set to False if you do not want to update existing attributes

            .. note::
                * if the attribute '_args_overwrite' exists in the parent object, this will be used.

        do_not_check_parent_attrs: will not check parent attributes for skip parameters.  (used when these fields are
            in use in the parent object for something else)

            .. note::
                * this only happens if the parameter is not passed, otherwise the check is skipped.

        Example of use:

            class MyObject(object):

                def __init__(self, *args, **kwargs):
                    args_handler(self, args, ['f_name', 'l_name'], kwargs)
                    # this would apply the first two args as MyObject.f_name and MyObject.l_name, as well as any kwargs


        Examples of options:

            >>> tc = TmpClass()

            test_args = [1, 2, 3, 4]
            test_args_list_1 = ['t1', 't2', 't3', '_t4']
            test_kwargs = {'t5': 5, 't6': 6, 't7': 7, '_t8': 8}
            test_kwargs_ovr = {'t3': 33, '_t4': 44, 't5': 5, 't6': 6, 't7': 7, '_t8': 8}
            test_skip_list = ['t4', 't5']

            test_args_req = [1, 2, 4]
            test_args_list_req = ['t1', '*t2', 't3', '_t4', '*t6']
            test_kwargs_req = {'t5': 5, 't7': 7, '_t8': 8}

            >>> args_handler(tc, test_args, test_args_list_1)
            >>> tc.t2
            2

            >>> args_handler(tc, kwargs=test_kwargs)
            >>> tc.t5
            5

            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs)
            >>> tc.t2
            2
            >>> tc.t5
            5

            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs_ovr)
            >>> tc.t3
            33
            >>> tc.t5
            5
            >>> tc.t2
            2



            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs, skip_list=test_skip_list)
            >>> tc.t2
            2
            >>> tc.t6
            6

            tc.t1 = 11
            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs, skip_list=test_skip_list)
            >>> tc.t1
            1

            >>> tc.t1 = 11
            >>> args_handler(tc, test_args, test_args_list_1, skip_list=test_skip_list, overwrite=False)
            >>> tc.t1
            11


            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs, skip_list=test_skip_list)
            >>> tc.t2
            2
            >>> tc.t6
            6

            >>> tc._args_skip_list = test_skip_list
            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs)
            >>> tc.t2
            2
            >>> tc.t6
            6

            >>> tc._args_skip_list = test_skip_list
            >>> args_handler(tc, kwargs=test_kwargs, do_not_check_parent_attrs=True)
            >>> tc.t5
            5


            >>> test_args = [1, 2, 4]
            >>> test_args_list = [('t1', 11), '*t2', 't3', '_t4', ('t5', 55), ('*t6', 66)]
            >>> test_kwargs = {'t6': 6, 't7': 7, '_t8': 8}
            >>> args_handler(tc, test_args, test_args_list, test_kwargs)

            >>> tc.t1
            1
            >>> tc.t5
            55
            >>> tc.t6
            6

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
                    raise AttributeError('ArgsHandler: Required attribute ' + attr + ' is not found in args or kwargs')

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
    """
    Base object to use for creating meta objects.  This will copy all attrs from the meta object to the parent object.

    This can be used to assign lists or other mutatable objects to Classes as well as to create standard sets of metadata
    for classes that can be reused.

    This uses :py:func:`args_handler` to copy kwargs to the class on init.

    Example:

        >>> class MyObject(object):
        >>>     meta = GenericMeta(name='coolObject', number_list=[1,2,3,4])

        >>> mo = MyObject()
        >>> mo.name
        'coolObject'
        >>> mo.number_list
        [1,2,3,4]

    """

    def __init__(self, *kwargs):
        args_handler(self, kwargs=kwargs)

    def get_meta_attrs(self, parent_obj, skip_list=None, skip_startswith='_', overwrite=True):
        """
        Function to copy the atttrs.

        :param parent_obj: The object to copy the attrs TO
        :param skip_list:  A list of attrs to skip copying.
        :param skip_startswith:  If an attr starts with this (default = '_'), do not copy
        :param overwrite: if False (default = True) will not not overwrite existing attributes if they exist.
        """
        if skip_list is None:
            skip_list = []
        for attr, value in iter(self.__dict__.items()):
            if not attr.startswith(skip_startswith) and attr not in skip_list:
                if not hasattr(parent_obj, attr) or overwrite:
                    setattr(parent_obj, attr, value)


def get_meta_attrs(meta, parent_obj, skip_list=None, skip_startswith='_', overwrite=True):
    """
    Standalone version of the get_meta_attrs from the generic meta object for use in other custom classes.

    :param meta: The object to copy the attrs FROM
    :param parent_obj: The object to copy the attrs TO
    :param skip_list:  A list of attrs to skip copying.
    :param skip_startswith:  If an attr starts with this (default = '_'), do not copy
    :param overwrite: if False (default = True) will not not overwrite existing attributes if they exist.
    """
    if skip_list is None:
        skip_list = []
    for attr, value in iter(meta.__dict__.items()):
        if not attr.startswith(skip_startswith) and attr not in skip_list:
            if not hasattr(parent_obj, attr) or overwrite:
                setattr(parent_obj, attr, value)


# endregion
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
# region String utils
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# ===============================================================================
# text utils
# ===============================================================================


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

        end_pos = instring.find(end_key, start_pos + start_key_len)

        if end_pos == -1:
            break

        if keep_keys:
            suffix = instring[end_pos:end_pos + end_key_len]
            outstring = outstring + instring[curs_pos:start_pos + start_key_len] + replace + suffix
            curs_pos = end_pos + end_key_len

        else:
            outstring = outstring + instring[curs_pos:start_pos] + replace
            curs_pos = end_pos + end_key_len

        found = found + 1

        start_pos = instring.find(start_key, curs_pos)

    return outstring + instring[curs_pos:]


def index_of_count(instring, find, offset_count=1, start=0):
    """
    Returns the string index (offset) for the x iteration of a substring.

    :param instring: the string to search
    :param find: the string to search for
    :param offset_count: return the 'offset_count' iteration of find string
    :param start: start looking at this point in the string
    :return: the offset for the find string
    :rtype int:

    example:
        >>> index_of_count('abcd abcd abcd abcd','abcd',2)
        6

    """
    if instring:
        offset_loc = start
        current_off = 0
        for i in range(offset_count):
            offset_loc = instring.find(find, current_off)
            if offset_loc > -1:
                if i == offset_count - 1:
                    return offset_loc
                current_off = offset_loc + 1
            else:
                return current_off
        return offset_loc
    return -1


def get_before(instring, find, offset_count=1):
    """
    Returns the string that occurs before the find string. If the find string is not in the string,
    this returns the entire string.

    :param instring: the string to search
    :param find: the string to look for
    :param offset_count: find the nth copy of the find string
    :return: the string that immediatly preceeds the find string.


    example:
        >>> get_before('look for the [key] in the lock','[')
        'look for the '

    """
    if find in instring:
        offset_loc = index_of_count(instring, find, offset_count)

        if offset_loc != -1:
            return instring[:offset_loc]
        return instring
    return instring


def get_after(instring, find, offset_count=1):
    """
    Returns the string that occurs after the find string. If the find string is not in the string,
    this returns the entire string.

    :param instring: the string to search
    :param find: the string to look for
    :param offset_count: find the nth copy of the find string
    :return: the string that is immediatly after the find string.


    example:
        >>> get_after('look for the [key] in the lock',']')
        ' in the lock'

    """
    if find in instring:
        offset_len = len(find)
        offset_loc = index_of_count(instring, find, offset_count)

        if offset_loc != -1:
            return_size = offset_loc + offset_len
            return instring[return_size:]
        return instring
    return instring


def get_between(instring, start_key, end_key):
    """
    Returns the string that occurs between the keys
    :param instring: the string to search
    :param start_key: the string to use to start capturing
    :param end_key: the key to use to end capturing
    :return: the string that is between the start_key and the after_key

    example:
        >>> get_betweem('look for the [key] in the lock','[',']')
        'key'

    """
    return get_after(get_before(instring, end_key), start_key)


# ===============================================================================
# Format string
# ===============================================================================

import re
from unicodedata import normalize

def unslugify(text, case='caps', end=''):
    """
    Converts a string to a more clean version.
    :param text:
    :param case: ['caps','upper','lower','title']
    :param end:
    :return:
    """
    tmp_str = ''
    for c in text:
        if c.isupper():
            tmp_str += ' '
        tmp_str += c
    tmp_str = tmp_str.replace('_', ' ').strip()
    if case == 'caps':
        tmp_str = tmp_str.capitalize()
    elif case == 'title':
        tmp_str = tmp_str.title()
    elif case == 'upper':
        tmp_str = tmp_str.upper()
    elif case == 'lower':
        tmp_str = tmp_str.lower()
    tmp_str += end
    return tmp_str


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify2(text, delim=u'-'):
    """Generates a slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    print('sluggify result:', result)
    return str(delim.join(result))


def slugify(text, delim='_', case='lower', allowed=None, punct_replace='', encode=None):
    """
    generates a simpler text string.

    :param text:
    :param delim: a string used to delimit words
    :param case: ['lower'/'upper'/'no_change']
    :param allowed: a string of characters allowed that will not be replaced.  (other than normal alpha-numeric which
        are never replaced.
    :param punct_replace: a string used to replace punctuation characters, if '', the characters will be deleted.
    :param encode: Will encode the result in this format.
    :return:
    """
    punct = '[\t!"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+'
    if allowed is not None:
        for c in allowed:
            punct = punct.replace(c, '')

    result = []

    for word in text.split():
        word = normalize('NFKD', word)
        for c in punct:
            word = word.replace(c, punct_replace)
        result.append(word)

    delim = str(delim)
    # print('sluggify results: ', result)
    text_out = delim.join(result)

    if encode is not None:
        text_out.encode(encode, 'ignore')

    if case == 'lower':
        return text_out.lower()
    elif case == 'upper':
        return text_out.upper()
    else:
        return text_out

# ===============================================================================
# Format number as clean string
# ===============================================================================


def format_as_decimal_string(num, max_decimal_points=6):
    """
    This will format a number as a string including decimals, but will correctly trim the decimal.
    :param num: number to format
    :param max_decimal_points: the max decimals to show
    :return: a string of the number with decimals.

    Examples:
        >>> format_as_decimal_string(1.234)
        '1.234'       # this would normally be '1.234000' when done by the normal format

    """
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
# text / string utils
# ===============================================================================


def is_string(in_obj):
    """ is this a string or not """
    return isinstance(in_obj, str)


def elipse_trim(instr, trim_length, elipse_string='...'):
    """
    Makes sure strings are less than a specified length, and adds an elipse if it needed to trim them.

    :param instr: The String to trim
    :param trim_length: The max length, INCLUDING the elipse
    :param elipse_string: the string used for the elipse.  Default: '...'
    :return: Trimmed string

    Examples:
        >>> elipse_trim('this is a long string',10)
        'this is...'

    """
    instr = str(instr)
    str_len = trim_length - len(elipse_string)
    if len(instr) > trim_length:
        return '{}{}'.format(instr[:str_len], elipse_string)
    else:
        return instr


def concat(*args, separator=' ', trim_items=True):
    """
    Concatenates strings or iterables

    :param args: strings or iterables
    :param separator: the string that will be used between strings.  Default: ' '
    :param trim_items: True/False, trim strings before concatenating.
    :return: string created from contents passed
    """
    # tmp_str = ""

    args = flatten(args)
    tmp_args = []
    for a in args:
        if trim_items:
            tmp_args.append(str(a).strip())
        else:
            tmp_args.append(str(a))
    return separator.join(tmp_args)

    '''
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
    '''


# endregion
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
# region Boolean utils
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************



# ===============================================================================
# return boolean from varied strings
# ===============================================================================

def convert_to_boolean(obj):
    """
    Converts an object to a boolean, mostly for strings, but can also accept objects that will convert correctly.
    :param obj: the object to convert
    :return: a boolean representing the object

    Examples:
        >>> convert_to_boolean('yes')
        True
        >>> convert_to_boolean(0)
        False

    """
    istrue = ('true', 'yes', 'ok', '1', 'on', '+', 'True', 'Yes', 'Ok', 'On', 'TRUE', 'YES', 'OK', 'ON', 1, 1.0)
    isfalse = ('false', 'no', '0', '-', 'off', 'False', 'No', 'Off', 'FALSE', 'NO', 'OFF', 0, 0.0)

    if isinstance(obj, (str, int, float)):
        if obj in istrue:
            return True
        elif obj in isfalse:
            return False
        else:
            raise TypeError('could not convert to boolean')

    elif hasattr(obj, '__bool__'):
        return bool(obj)

    raise TypeError('could not convert to boolean')


# endregion
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
# region Other utils
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


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

    def __init__(self, *args):
        self.stored = args[0]
        self.display = args[1]
        try:
            self.reference = args[2]
        except IndexError:
            pass

    def __str__(self):
        return self.stored


class LookupManager(object):
    def __init__(self, lookup_list):
        """
        This handles a list of tuples where you want to have one string for a lookup, which returns a
        different string, and is called by a third thing.

        This takes a list of tuples and

        :param lookup_list:
                lookup list is a list of tuples (stored_value, display_value [, referenced_name] ):
                    stored value = the value that would be stored in the db
                    representative value = the value that is used for display
                    referenced value is the name used in coding (if not present stored_value is used)
        :param case_sensitive:
                determines if lookups are case sensitive or not.

        .. warning:: still needs work

        """
        #: TODO fix this, needs more thought in how it works
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
            self.lookup_list.append((tmp_l.stored, tmp_l.display ))
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

    def get_by_stored(self, item):
        return self.stored_dict[item]

    def get_by_display(self, item):
        return self.display_dict[item]



# ===============================================================================
# counter Class
# ===============================================================================


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

        if not isinstance(change_by, int):
            if isinstance(change_by, float):
                change_by = int(change_by)
            elif isinstance(change_by, str) and change_by.isnumeric():
                change_by = int(change_by)
            else:
                change_by = len(change_by)

        change_by = change_by * self.step
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
    """
    This object will create and manage a set of counters that can be used to count steps, items, etc...
        *[defaults in brackets]*

    Keyword Arguments:
        initial (int): [0] initial counter number
        step (int): [1] print only on increments of x
        max_value (int): [sys.maxsize] maximum possible counter number, when set echo will return %xx and number stops at max
        min_value (int): [0] minimum possible counter number, when set echo will return %xx and number stops at min
        console_format (format string): ['{counter}']format to use for excoint to console
        format (format string: ['{counter}'] format to use for echo, default = '{name} : {counter}'
        return_every (int): [1] will only echo on multiples of this
        rollover (boolean): [False] Should the counter start back at *min_value* after hitting *max_value*
        rollunder (boolean): [False] Should the counter start back at *max_value* after hitting *min_value*
        autoadd (boolean): [True] will automatically add a counter if it is called.

    Example:
        Clicker can be used in multiple ways,

            >>> c = Clicker()
            >>> c()   # when called, it will increment by :param:step
            1
            >>> c(2)   # an integrer could be passed that would change the step value (for that step)
            3
            >>> c(-1)  # you can also go backwards
            2
            >>> c('my_counter', 1)  # you can pass a counter name and it will track that counter seperatly
            1
            >>> c('my_counter', 3)  # you will have to pass that name each time you call it to get that counter.
            4
            >>> c(5)    # and of couse, the other counter is still running in the background
            7
            >>> c['my_counter', 0] # you can also access the counters this way
            4
            >>> c.my_counter(10)   # or access them this way
            14
            >>> del c['my_counter'] # and delete them this way

        you can use any of the following methods to add / subtrack from a counter:
            * c += 1
            * c(1)
            * c = c + 1
            * c()
            * c += object

        if an object is passed, the following rules will apply:
            * if an int/long is passed, it will be added/subtracted,
            * if a string is passed and is_numeric = True, it will be converted to an int and added/subtracted
            * for all other objects, the len of the object will be added to the counter.
    """

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
        # self.autoadd_name_prefix = kwargs.get('AutoCounter_', True)

        self.add_counter(self.default_name)
        self._default_counter = self._counters[self.default_name]

    def add_counter(self, name, **kwargs):
        """
        adds a new counter

        *if not passed, keyword params will use the base* :class:`Clicker` *settings*

        Parameters:
            name: the name of the counter


        Keyword Arguments:
            initial: [0] initial counter number
            step: [1] print only on increments of x
            max_value: [sys.maxsize] maximum possible counter number, when set echo will return %xx and number stops at max
            min_value: [0] minimum possible counter number, when set echo will return %xx and number stops at min
            console_format: ['{counter}']format to use for excoint to console
            format: ['{counter}'] format to use for echo, default = '{name} : {counter}'
            return_every: [1] will only echo on multiples of this
            rollover: [False] Should the counter start back at *min_value* after hitting *max_value*
            rollunder: [False] Should the counter start back at *max_value* after hitting *min_value*
        """

        self._counters[name] = ClickItem(self, name, **kwargs)

    def del_counter(self, name):
        """
        Will delete a counter by name
        :param name: the name of the counter to delete
        """
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

# endregion


