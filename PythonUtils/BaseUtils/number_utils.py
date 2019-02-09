#!/usr/bin/env python

__all__ = ['is_number', 'make_number', 'quartiles', 'MathList', 'MATHLIST_OUTLIERS', 'RollingInt', 'rollover_calc',
           'looping_iterator']

from decimal import Decimal, InvalidOperation
import statistics
from enum import Enum
from PythonUtils.BaseUtils.class_utils import simple_kwarg_handler
from PythonUtils.BaseUtils.list_utils import make_list
from PythonUtils.BaseUtils.percentage_calcs import PERC_RET, format_percentage
from math import fsum
import sys
import collections

# ===============================================================================
# is_number
#  ===============================================================================


def is_number(value):
    if isinstance(value, (int, float, Decimal)):
        return True
    elif isinstance(value, str):
        return value.isnumeric()
    else:
        return False


def make_number(value, default=None, float_as_decimal=False):
    if isinstance(value, (int, float, Decimal)):
        if float_as_decimal and isinstance(value, float):
            return Decimal(value)
        else:
            return value

    try:
        return int(value)
    except ValueError:
        try:
            if float_as_decimal:
                return Decimal(value)
            else:
                return float(value)
        except (ValueError, InvalidOperation):
            if default is None:
                raise
            else:
                return default


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
        tmp_upper = tmp_data[tmp_split + 1:]
        tmp_lower = tmp_data[:tmp_split]

    q1 = statistics.median(tmp_lower)
    q3 = statistics.median(tmp_upper)
    return q1, tmp_median, q3


# ===============================================================================
# MathList
# ===============================================================================

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
                if x <= self._cache_['inner_fence_low'] or x >= self._cache_['inner_fence_high']:
                    tmp_ret.append(i)

        elif filter_outliers == MATHLIST_OUTLIERS.MAJOR_OUTLIERS:
            for i, x in enumerate(self._data):
                if x <= self._cache_['outer_fence_low'] or x >= self._cache_['outer_fence_high']:
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
                        elif row_value < self._cache_['inner_fence_low'] or row_value > self._cache_[
                            'inner_fence_high']:
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
# Rolling Int
# ===============================================================================


class RollingInt(object):
    """
    This object allows setting a min, max, and initial value.  it then can be added to or subtratracted from
    and will operate as an integer, however, upon reaching the min or max value, it will roll over to start again.

    This can be used to generate looping over an iterator if needed though care should be taken to not end up
    in an endless loop.

    """

    def __init__(self, max, min=0, value=None):
        """
        :param max: an integer for the max value.
            if a non-integer is passed, the length of that object will be used.
        :param min: the minimum value to be used when rolling under.  (defaults to 0)
        :param value: the current value of the object, defaults to the minimum value.
        """
        self.min = min
        if isinstance(max, int):
            self.max = max
        else:
            self.max = len(max) -1
        if value is None:
            value = min
        if self.min >= self.max:
            raise AttributeError('Min value must be less than max value')
        self.distance = self.max - self.min
        self(value)

        self.rollover_counter = 0
        self.rollunder_counter = 0

    @property
    def roll_counter(self):
        return self.rollover_counter - self.rollunder_counter


    def _add_value(self, value):
        if value < 0:
            return self._sub_value(value * -1)
        # print('adding %s to %r' % (value, self))
        if value == 0:
            return self.value
        new_val = self.value + value
        # print(' - interim value = ', new_val)
        if new_val > self.max:
            while new_val > self.max:
                self.rollover_counter += 1
                new_val -= self.distance
                # print('%r is rolling over from %s' % (self, new_val))
                # print(' - rolling over to = ', new_val)
                new_val -= 1
            #print(' - rolling over to = ', new_val)
        return new_val

    def _sub_value(self, value):
        if value < 0:
            return self._add_value(value * -1)
        # print('subtracting %s from %r' % (value, self))
        if value == 0:
            return self.value
        new_val = self.value - value
        # print(' - interim value = ', new_val)
        if new_val < self.min:
            while new_val < self.min:
                self.rollunder_counter += 1
                new_val += self.distance
                # if new_val < 0:
                #     new_val = self.max - new_val
                # else:
                #     new_val = self.max + new_val
                # print(' - rolling under to = ', new_val)
                new_val += 1
            # print(' - rolling under to = ', new_val)
        return new_val

    def _new_ri(self, value):
        return self.__class__(max=self.max, min=self.min, value=value)

    def __call__(self, value=None):
        self.rollunder_counter = 0
        self.rollover_counter = 0
        if value is None:
            self.value = self.min
        else:
            if not self.min <= value <= self.max:
                raise AttributeError('Invalid value: %s is not between %s and %s' % (value, self.min, self.max))
            self.value = int(value)
        return self

    def __add__(self, x: int):
        return self._new_ri(self._add_value(x))

    def __sub__(self, x: int):
        return self._new_ri(self._sub_value(x))

    def __radd__(self, x: int):
        return self._new_ri(self._add_value(x))

    def __rsub__(self, x: int):
        return self._new_ri(self._sub_value(x))

    def __isub__(self, x: int):
        self.value = self._sub_value(x)
        return self

    def __iadd__(self, x: int):
        self.value = self._add_value(x)
        return self

    def __eq__(self, x: object) -> bool:
        return self.value == x

    def __ne__(self, x: object) -> bool:
        return self.value != x

    def __lt__(self, x: int) -> bool:
        return self.value < x

    def __le__(self, x: int) -> bool:
        return self.value <= x

    def __gt__(self, x: int) -> bool:
        return self.value > x

    def __ge__(self, x: int) -> bool:
        return self.value >= x

    def __str__(self) -> str:
        return str(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __int__(self) -> int:
        return self.value

    def __abs__(self) -> int:
        return abs(self.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)

    def __repr__(self) -> str:
        return 'RollingInt(%s < %s < %s)' % (self.min, self.value, self.max)

    def __format__(self, format_spec: str) -> str:
        return format(self.value, format_spec=format_spec)


def rollover_calc(max, add_value, current=0, min=0):
    """
    Wrapper function for RollingInt for when you simply need to do one calculation
    :param current: Current Value
    :param add_value: Added value (or pass a negative number for subtraction)
    :param min: the minimum value,
    :param max: the maximum value,
    :return:
    """
    tmp_ro = RollingInt(max, min, current)
    return int(tmp_ro + add_value)


def looping_iterator(obj_in, current_index=0, max_iteration=10000, step=1):
    index = RollingInt(obj_in, value=current_index)
    current_iter = 1
    while True:
        if max_iteration is not None and current_iter > max_iteration:
            break
        yield obj_in[int(index)]

        index += step
        current_iter += 1

