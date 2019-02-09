#!/usr/bin/env python

__all__ = ['get_now', 'add_month', 'date_add_month', 'FiscalDateCalc', 'FiscalDate', 'last_day_of_month',
           'full_month_name', 'short_month_name']

from datetime import datetime, timedelta, date, time
import calendar

# Imported in function below to avoid recursive imports
# from PythonUtils.BaseUtils.number_utils import RollingInt

def get_rolling_int(*args, **kwargs):
    from PythonUtils.BaseUtils.number_utils import RollingInt
    return RollingInt(*args, **kwargs)

# ===============================================================================
# get_now
#  ===============================================================================


def get_now(time_now=None, tz=None):
    """
    returns a datetime object with an optional timezone.

    :param time_now: a datetime or time object to return
    :param tz: if None, will return the time_now object or a niaeve datetime object.
        if a datetime or time object with a tz object, it will return the time_now object based on that timezone, or
        generate a new datetime object baed on datetime.now(tz=tz from that object)
        if any other object is passed, it will assume that is a tzone object and try to use that.
    :return:
    """
    if isinstance(tz, (datetime, time)):
        if hasattr(tz, 'tz'):
            tz = tz.tz
        else:
            tz = None

    if time_now is not None:
        if tz is None:
            return time_now
        else:
            return time_now.astimezone(tz=tz)
    else:
        return datetime.now(tz=tz)


# ===============================================================================
# Month calculations
# ===============================================================================


def add_month(curr_year, curr_month, add_months):
    """
    A function to add or subtract months to a date and year
    :param curr_year: The initial year
    :param curr_month:  The initial month
    :param add_months: the number of months to add (can be a negative number
    :return: (year, month)
    """
    if add_months == 0:
        return curr_year, curr_month

    month_calc = get_rolling_int(12, min=1, value=curr_month)

    month_calc += add_months

    new_month = int(month_calc)
    year_diff = month_calc.roll_counter

    new_year = curr_year + year_diff

    return new_year, new_month


def date_add_month(date_obj, add_months, new_day=None):
    """
    A wrapper for add_month that will add or subtract months from a date/datetime object.  This can also adjust for forcing the
        "day" property to a specific day of the resulting month.
    :param date_obj: a date or datetime object
    :param add_months: the number of months to add (can be a negative number to subtract months)
    :param new_day: can be any of the following:
        an int: will be used for the new date object
        None: the current day will be used (if the current day is higher than the end of the new month, the last day in the month will be returned
        'end': the last day of the month will be returned.
    :return: a matching object to the date_obj with the dates adjusted.
    """
    if add_months == 0:
        return date_obj
    current_month = date_obj.month
    current_year = date_obj.year
    new_year, new_month = add_month(current_year, current_month, add_months)


    if new_day is None:
        current_day = date_obj.day
    elif isinstance(new_day, str):
        if new_day == 'end':
            current_day = 99
        else:
            raise AttributeError("Invalid new day parameter: %s" % new_day)
    else:
        current_day = new_day

    new_eom = calendar.monthrange(new_year, new_month)[1]

    if new_eom < current_day:
        current_day = new_eom

    date_obj = date_obj.replace(year=new_year, month=new_month, day=current_day)
    return date_obj


def last_day_of_month(year, month, date_obj=None):
    """
    returns a date object for the last day of a given month.
    :param year: the year
    :param month: the month
    :param date_obj: defaults to a date object, but allows passing any other object to use.
    :return:
    """
    date_obj = date_obj or date
    new_eom = calendar.monthrange(year, month)[1]
    return date_obj(year, month, new_eom)


month_starts = {
    1: date(2019, 1, 1),
    2: date(2019, 2, 1),
    3: date(2019, 3, 1),
    4: date(2019, 4, 1),
    5: date(2019, 5, 1),
    6: date(2019, 6, 1),
    7: date(2019, 7, 1),
    8: date(2019, 8, 1),
    9: date(2019, 9, 1),
    10: date(2019, 10, 1),
    11: date(2019, 11, 1),
    12: date(2019, 12, 1),
}


def short_month_name(month):
    """
    returns the local's short month name from a given date object or month integer
    :param month: a date/datetime object or month integer
    """
    if isinstance(month, (date, datetime)):
        month = month.month
    tmp_date = month_starts[month]
    return tmp_date.strftime('%b')


def full_month_name(month):
    """
    returns the local's full month name from a given date object or month integer
    :param month: a date/datetime object or month integer
    """
    if isinstance(month, (date, datetime)):
        month = month.month
    tmp_date = month_starts[month]
    return tmp_date.strftime('%B')

# ===============================================================================
# Fiscal Calculations
# ===============================================================================


class FiscalDateCalc(object):
    """
    This is a calculator object that will calculate fiscal dates based on a given month offset for the initial FQ.
    """
    rolling_months = get_rolling_int(12, 1, 1)
    one_day = timedelta(days=1)
    base_quarters = {
        1: 1, 2: 1, 3: 1,
        4: 2, 5: 2, 6: 2,
        7: 3, 8: 3, 9: 3,
        10: 4, 11: 4, 12: 4,
    }
    date_class = date

    def __init__(self, fiscal_offset=0, date_class=None):
        """
        :param fiscal_offset: the number of months offset from Jan that the fiscal year begins.
            for example, if FY2019 begins on 10/1/2018, then fiscal_offset=-3
            if FY2019 begins on 2/1/2019, then fiscal_offset=1.
        :param date_class: this defaults to 'date', but any other date/datetime like object can be passed.  this is used
        for methods that return a date (or datetime) object.
        """

        self.date_class = date_class or self.date_class

        if not -12 < fiscal_offset < 12:
            raise AttributeError('Quarter offset must be between -11 and 11')
        self.fiscal_offset = fiscal_offset
        self.years = {}
        self.q_mbe = {}
        self.offset_quarters = {}
        month = self.rolling_months(1)
        month += self.fiscal_offset
        for q in range(1, 5):
            tmp_begin = int(month)
            self.offset_quarters[int(month)] = q
            month += 1
            self.offset_quarters[int(month)] = q
            month += 1
            self.offset_quarters[int(month)] = q
            tmp_end = int(month)
            month += 1
            self.q_mbe[q] = (tmp_begin, tmp_end)

    def dump(self, date_in=None):
        """
        This dumps diagnostic information about the internal tables and stats, used for troubleshooting.

        :param date_in:
        :return:

        Internals:
            offset_quarters
            quarter_start/end months

            years:
                2019:
                    start / end: xxx
                    quarters:
                        1
                        2
                        3
                        4

        Date Values:
            date_in:
            fiscal year :
                start / end:
            fiscal quarter:
                start / end
        """
        tmp_ret = ['Fiscal Calculator:  (offset: %s)' % self.fiscal_offset]
        a = tmp_ret.append
        a('')
        if date_in is not None:

            try:
                a('DATE CALCULATIONS:')
                a('------------------')
                a('    Date In        : %s' % date_in)
                a('    Fiscal Year    : %s  (%s -> %s' % (self.fy(date_in), self.fy_start(date_in), self.fy_end(date_in)))
                a('    Fiscal Quarter : %s  (%s -> %s' % (self.fq(date_in), self.fq_start(date_in), self.fq_end(date_in)))
            except Exception as err:
                a('  *** EXCEPTION: %r' % err)
            a('')
        a('INTERNALS:')
        a('----------')
        a('    Offset Quarters : %r' % self.offset_quarters)
        a('    Quarter Months  : %r' % self.q_mbe)
        a('    Years: %s' % len(self.years))
        for y, values in self.years.items():
            a('        %s:  %s -> %s' % (y, values['start'], values['end']))
            for q, qt_values in values['quarters'].items():
                a('            Q- %s: %s -> %s' % (q, qt_values['start'], qt_values['end']))

        a('')
        return '\n'.join(tmp_ret)

    def _get_fy_info(self, year):
        if year not in self.years:
            self.years[year] = {}
            new_year, new_month = add_month(year, 1, self.fiscal_offset)
            tmp_start = self.date_class(year=new_year, month=new_month, day=1)
            self.years[year]['start'] = tmp_start
            tmp_end = date_add_month(tmp_start, 11, new_day=99)
            self.years[year]['end'] = tmp_end
            self.years[year]['quarters'] = {}
            quarters = self.years[year]['quarters']
            q_start = tmp_start
            for q in range(1, 5):
                quarters[q] = {
                    'start': q_start,
                    'end': date_add_month(q_start, 2, new_day=99)
                }
                q_start = date_add_month(q_start, 3)

        return self.years[year]

    def fy(self, date_in):
        """
        returns the fiscal year for a given date/datetime object.
        :param date_in: a date/datetime object
        :return: an integer of the fiscal year.
        """
        tmp_year = date_in.year
        tmp_start = self._get_fy_info(tmp_year)['start']
        tmp_end = self._get_fy_info(tmp_year)['end']
        if tmp_start <= date_in <= tmp_end:
            return tmp_year
        elif tmp_start > date_in:
            return tmp_year - 1
        else:
            return tmp_year + 1

    def fq(self, date_in):
        """
        returns the fiscal quarter of a date / datetime object.
        :param date_in: a date/datetime object
        :return: an integer of the fiscal quarter.
        """
        if isinstance(date_in, (date, datetime)):
            date_in = date_in.month
        try:
            return self.offset_quarters[date_in]
        except KeyError:
            raise KeyError('key %s not found in %r' % (date_in, self.offset_quarters))

    def cq(self, date_in):
        """
        returns the calendar quarter for a given date/datetime object.
        :param date_in: a date/datetime object
        :return: an integer of the calendar quarter
        """
        return self.base_quarters[date_in.month]

    def fq_start(self, date_in):
        """
        returns a date/datetime object with the first day of the fiscal quarter based on the passed date/datetime object
        :param date_in: a date/datetime object
        :return:
        """
        if isinstance(date_in, int):
            return self.q_mbe[date_in][0]

        if isinstance(date_in, (date, datetime)):
            pass

        elif isinstance(date_in, (list, tuple)):
            date_in = date(year=date_in[0], month=date_in[1], day=1)

        else:
            raise AttributeError('Invalid date passed: %r' % date_in)

        tmp_fy = self._get_fy_info(self.fy(date_in))
        tmp_q = self.fq(date_in)
        return tmp_fy['quarters'][tmp_q]['start']

    def fq_end(self, date_in):
        """
        returns a date/datetime object with the last day of the fiscal quarter based on the passed date/datetime object

        :param date_in: a date/datetime object
        :return:
        """
        if isinstance(date_in, int):
            return self.q_mbe[date_in][0]

        if isinstance(date_in, (date, datetime)):
            pass

        elif isinstance(date_in, (list, tuple)):
            date_in = date(year=date_in[0], month=date_in[1], day=1)

        else:
            raise AttributeError('Invalid date passed: %r' % date_in)

        tmp_fy = self._get_fy_info(self.fy(date_in))
        tmp_q = self.fq(date_in)
        return tmp_fy['quarters'][tmp_q]['end']

    def fy_start(self, date_in):
        """
        returns a date/datetime object with the first day of the fiscal year based on the passed date/datetime object

        :param date_in: a date/datetime object
        :return:
        """
        if isinstance(date_in, (datetime, date)):
            tmp_year = self.fy(date_in)
        else:
            tmp_year = int(date_in)
        return self._get_fy_info(tmp_year)['start']

    def fy_end(self, date_in):
        """
        returns a date/datetime object with the last day of the fiscal year based on the passed date/datetime object

        :param date_in: a date/datetime object
        :return:
        """
        if isinstance(date_in, (datetime, date)):
            tmp_year = self.fy(date_in)
        else:
            tmp_year = int(date_in)
        return self._get_fy_info(tmp_year)['end']

    def in_fy(self, date_in, year):
        """
        returns a true if the date/datetime object passed in in the fiscal year passed.
        :param date_in: a date/datetime object to check
        :param year: an integer of the year to check if the date is in.
        :return: True if the date/datetime is in the fiscal quarter
        """
        return self.fy(date_in) == year

    def in_fq(self, date_in, quarter, year=None):
        """
        returns a true if the date/datetime object passed in in the fiscal quarter passed (and year if passed.)
        :param date_in: a date/datetime object to check
        :param quarter: an integer of the quarter to check if the date is in.
        :param year: an integer of the year to check if the date is in, or None if the year does not matter.
        :return: True if the date/datetime is in the fiscal quarter and year.
        """
        if year is not None:
            if self.fy(date_in) != year:
                return False
        return self.fq(date_in) == quarter

    def format(self, date_in, format_str):
        """
        This will return a string from a date or datetime object.  any existing date / datetime formatting options are
            passed through, and new ones are added for quarter and fiscal year.

            %(cq[!2)               : The Calendar Quarter
            %(fq[!2])               : The Fiscal Quarter
            %(fy[!2])     : The Fiscal Year in 4 digits (i.e. 2018)
            %(fy_start[!<date_format_code>])   : the fiscal year start date
            %(fy_end[!<date_format_code>])     : The fiscal year end date
            %(fq_start[!<date_format_code>])   : The fiscal quarter start date
            %(fq_end[!<date_format_code>])     : The fiscal quarter end date

            NOTES:
                for fq/cq values, you can pass a !2 to force padding to 2 digits (i.e. 01 or 04 instead of 1 or 4)

                for fy values, you can pass a !2 to force shortening to a 2 digit year (i.e. 18 instead of 2018)

                for *_start/end dates, this will pass the date into the string using the "%x" format (default locals
                    short date.

                    if a "!" is included, the text afterwards (until the close ")" will be passed to the string formatter
                        for that date object.  for example, passing a %(fq_end!%b) would return fq_start.strftime("%b"),
                        or the short form of the month name.

        :param date_in: A date or date time object
        :param format_str: a format string to use to format the datetime object.
        :return:
        """
        def format_wrapped(initial_code, sub_format_str, date_obj):
            tmp_format_str, init_tmp_date_str = sub_format_str.split(initial_code, maxsplit=1)

            tmp_date_str = init_tmp_date_str
            if tmp_date_str[0] == ')':
                tmp_end_str = tmp_date_str[1:]
                tmp_date_str = '%x'
                end_index = -1
            elif tmp_date_str[0] == '!':
                tmp_date_str = tmp_date_str[1:]

                param_counter = 1
                end_index = -1
                for x, c in enumerate(tmp_date_str):
                    if c == '(':
                        param_counter += 1
                    elif c == ')':
                        param_counter -= 1
                        if param_counter == 0:
                            end_index = x
                            break
                if end_index == -1:
                    raise ValueError('Missing closing paran in format string: %s' % format_str)

                tmp_date_format = tmp_date_str[:end_index]
                tmp_end_str = tmp_date_str[end_index+1:]

            else:
                raise ValueError('Invalid format string: %s' % sub_format_str)

            try:
                tmp_date_ret = date_obj.strftime(tmp_date_format)
            except ValueError as err:
                msg = '%s: format_str: %r  (ei: %s, full: %r)' % (
                    err,
                    tmp_date_format,
                    end_index,
                    init_tmp_date_str,
                )
                raise ValueError(msg)

            return tmp_format_str + tmp_date_ret + tmp_end_str

        init_format_str = format_str
        found = True

        while found:
            found = False
            if '%(cq)' in format_str:
                found = True
                format_str = format_str.replace('%(cq)', str(self.cq(date_in)))
            if '%(cq!2)' in format_str:
                found = True
                format_str = format_str.replace('%(cq!2)', '0' + str(self.cq(date_in)))
            if '%(fq)' in format_str:
                found = True
                format_str = format_str.replace('%(fq)', str(self.fq(date_in)))
            if '%(fq!2)' in format_str:
                found = True
                format_str = format_str.replace('%(fq!2)', '0' + str(self.fq(date_in)))
            if '%(fy!2)' in format_str:
                found = True
                tmp_yr = str(self.fy(date_in))[-2:]
                format_str = format_str.replace('%(fy!2)', tmp_yr)
            if '%(fy)' in format_str:
                found = True
                format_str = format_str.replace('%(fy)', str(self.fy(date_in)))
            if '%(fy_start' in format_str:
                found = True
                format_str = format_wrapped('%(fy_start', format_str, self.fy_start(date_in))
            if '%(fy_end' in format_str:
                found = True
                format_str = format_wrapped('%(fy_end', format_str, self.fy_end(date_in))
            if '%(fq_start' in format_str:
                found = True
                format_str = format_wrapped('%(fq_start', format_str, self.fq_start(date_in))
            if '%(fq_end' in format_str:
                found = True
                format_str = format_wrapped('%(fq_end', format_str, self.fq_end(date_in))

        try:
            return date_in.strftime(format_str)
        except ValueError as err:
            raise TypeError('%s: format_str = %s' % (err, format_str))

    def __repr__(self):
        return 'FiscalDateCalc(offset=%s) [%s -> %s]' % (self.fiscal_offset,
                                                         short_month_name(self.q_mbe[1][0]),
                                                         short_month_name(self.q_mbe[4][1]))


class FiscalDate(object):
    """
    This is a wrapper for FiscalDateCalc that allows passing a date/datetime object during initialization.

    All methods then operate the same as FiscalDateCalc except that they operate on the previously passed object. (The
        exception is that any methods that only take the date object are not properties.)

    This can be used to when the same date object will be used to calculate multiple types of values.
    """
    def __init__(self, date_in, fiscal_offset=0):
        self.date_in = date_in
        self.date_class = date_in.__class__
        self.fiscal_offset = fiscal_offset
        self.calculator = FiscalDateCalc(fiscal_offset, self.date_class)

    def dump(self):
        return self.calculator.dump(self.date_in)

    @property
    def fy(self):
        return self.calculator.fy(self.date_in)

    @property
    def fq(self):
        return self.calculator.fq(self.date_in)

    @property
    def cq(self):
        return self.calculator.cq(self.date_in)

    @property
    def fq_start(self):
        return self.calculator.fq_start(self.date_in)

    @property
    def fq_end(self):
        return self.calculator.fq_end(self.date_in)

    @property
    def fy_start(self):
        return self.calculator.fy_start(self.date_in)

    @property
    def fy_end(self):
        return self.calculator.fy_end(self.date_in)

    def in_fy(self, year):
        return self.calculator.in_fy(self.date_in, year)

    def in_fq(self, quarter, year=None):
        return self.calculator.in_fq(self.date_in, quarter, year)

    def format(self, format_str):
        return self.calculator.format(self.date_in, format_str)

    def __repr__(self):
        return 'FiscalDate(%r) offset: %s FY:%s, FQ:%s' % (self.date_in, self.fiscal_offset, self.fy, self.fq)
