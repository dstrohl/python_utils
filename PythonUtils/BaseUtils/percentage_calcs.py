#!/usr/bin/env python


__all__ = ['PERC_RET', 'perc_bar', 'format_percentage', 'scaled_perc', 'make_percentage', 'PercCounter',
           'est_finish_timedelta', 'est_finish_time', 'est_total_timedelta']

from enum import Enum
from PythonUtils.BaseUtils.string_utils import spinner_char
from PythonUtils.BaseUtils.date_utils import get_now


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
    AS_STR_DOT_1 = 'str-float-1'
    AS_STR_DOT_2 = 'str-float-2'


def format_percentage(perc, perc_format=PERC_RET.AS_INT):
    """
    Handles converting and formatting of percentages.

    :param perc: is the percentage, normally expected in float form.
    :param perc_format: is a flag enum `py:class:PERC_RET` that tells the function how to format it.
        Can also be a format string for more complex string formatting.
    :return:
    """
    if perc_format is PERC_RET.AS_STR_INT:
        return '{0:.0%}'.format(perc)

    elif perc_format == PERC_RET.AS_STR_DOT_1:
        perc *= 100
        return '{0:.1f}%'.format(perc, precision=2)

    elif perc_format == PERC_RET.AS_STR_DOT_2:
        perc *= 100
        return '{0:.2f}%'.format(perc, precision=2)

    elif perc_format == PERC_RET.AS_INT:
        perc *= 100
        return int(perc)

    elif perc_format == PERC_RET.AS_FLOAT:
        return perc

    elif perc_format == PERC_RET.AS_FLOAT_PERC:
        perc *= 100
        return perc

    elif isinstance(perc_format, str) and '{perc}' in perc_format:
        return perc_format.format(perc=perc)

    else:
        raise AttributeError('Unknown Percentage Format: %r' % perc_format)


# ===============================================================================
# Generate Percentages
# ===============================================================================

def make_percentage(current, total, perc_format=None, min_perc=0, max_perc=None, raise_on_div_zero=True):
    """
    Will make a percentage from a total and current value, with min/max and formatting.

    :param current:  the current number
    :param total: the total number
    :param perc_format: This is based on the above perc_formatting types.  If None (the default), this will return
        a float.
    :param min_perc: if set, no percentage will return below this number.  This should be a float number (i,e, 0.1 for 10%)
    :param max_perc: if set, no percentage will return above this number.  This should be a float number (i,e, 0.1 for 10%)
    :param raise_on_div_zero: if False, a total of zero will return a perc of zero.  if True, a total of zero will
        raise a ZeroDivisionError exception
    :return:

    current / total

    """

    try:
        perc = current / total
    except ZeroDivisionError:
        if raise_on_div_zero:
            raise
        perc = 0.0

    if min_perc is not None and perc < min_perc:
        perc = float(min_perc)

    elif max_perc is not None and perc > max_perc:
        perc = float(max_perc)

    if perc_format:
        return format_percentage(perc, perc_format)
    else:
        return perc


def scaled_perc(perc, scaled_total, as_int=True):
    """
    Returns a number that is scaled based on a perc from the current and total passed.

    This can be used to format a graphical bar for percent done.

    :param perc: current perc done
    :param scaled_total: total number to scale from
    :param as_int: if True (the default) will return an Int
    :return:

    Examples:
        >>> scaled_perc(0.10, 50)
        5

        >>> scaled_perc(0.10, 1024, as_int=False)
        102.4

    """
    tmp_ret = scaled_total * perc

    if as_int:
        return int(tmp_ret)
    else:
        return tmp_ret


def perc_bar(perc,
             filled_char='#',
             empty_char='.',
             length=60,
             bar_format="{left_bar}",
             spin_state=None,
             spinner_kwargs=None,
             **format_kwargs,
             ):
    """
    Returns a string that is a percentage complete bar.

    :param perc: the percent completed
    :param filled_char: the char used to represent perc done
    :param empty_char: the char used to represent remaining space
    :param length: the total length of the bar
    :param_bar_format: the bar format style
        This uses the normal string format option with the following variables available:
            {perc} : shows the percentage.  To show int, use {perc:.0%}
            {left_bar}: "###########...."
            {right_bar}:"....###########"
            {center_bar}: ......#........"
            {spinner}: a spinner character available if spin_state is also passed.

            for example, a 25% format string of "[{spinner}] {left_bar} {perc!.0%} finished"  would return
                "[/] ##........ 25% finished"

        NOTE: updating the spinner adds extra processing time.
    :param spin_state: an integer that is used to increment the spinner.  this is normally just a counter that is
        incremented for each call, the spinner is incremented for each changed number.  If this is incremented in units
        other than 1, the spinner may not operate as expected.
    :param spinner_kwargs: a dict of kwargs that is passed to the spinner function.
    :return:

    Note the result is always rounded down.

    example:
        >>> perc_bar(0.10, length=20)
        "##.................."

        >>> perc_bar(0.1, length=20)
        "...................."

        >>> perc_bar(0.4, length=20)
        "...................."

        >>> perc_bar(0.5, length=20)
        "#..................."

    """

    spinner_kwargs = spinner_kwargs or {}

    if perc > 1:
        set_perc = 1
    elif perc < 0:
        set_perc = 0
    else:
        set_perc = perc

    tmp_filled_count = scaled_perc(scaled_total=length, perc=set_perc, as_int=True)

    if '{left_bar}' in bar_format:
        tmp_bar = filled_char * tmp_filled_count
        tmp_bar += (empty_char * (length - tmp_filled_count))
        format_kwargs['left_bar'] = tmp_bar

    elif "{right_bar}" in bar_format:
        tmp_bar = (empty_char * (length - tmp_filled_count))
        tmp_bar += filled_char * tmp_filled_count
        format_kwargs['right_bar'] = tmp_bar

    elif "{center_bar}" in bar_format:
        tmp_bar = empty_char * (tmp_filled_count - 1)
        tmp_bar += filled_char
        tmp_bar += (empty_char * (length - tmp_filled_count))
        format_kwargs['center_bar'] = tmp_bar

    if spin_state is None:
        format_kwargs['spinner'] = ''
    else:
        format_kwargs['spinner'] = spinner_char(spin_state, **spinner_kwargs)

    return bar_format.format(
        perc=perc,
        **format_kwargs
    )


def est_total_timedelta(perc, start_time, time_now=None):
    """
    Returns a timedelta object with the total estimated time it will take for a process to finish based on a given perc done.

    :param perc: the percentage done taht the task is.
    :param start_time: the time that the task started
    :param time_now: the current time (if not passed, assumes now.
    :return:

    Example:
        >>> start_time = now() - timedelta(seconds=10)
        >>> est_total_timedelta(perc=0.25, start_time=start_time)
        timedelta(seconds=40)

    """
    if perc > 1:
        perc = 1
    if perc < 0:
        perc = 0

    if time_now is None:
        time_now = get_now()

    current_td = time_now - start_time

    return current_td / perc


def est_finish_timedelta(perc, start_time, time_now=None):
    """
    returns a timedelta object with the estimated remaining time to finish a job from now based on a percentage done and start time.
    :param perc: the percentage complete
    :param start_time: the tiem the task was started
    :param time_now: the current time, if None, assumes Now
    :return:

    Example:
        >>> start_time = now() - timedelta(seconds=10)
        >>> est_finish_timedelta(perc=0.25, start_time=start_time)
        timedelta(seconds=30)

    """
    if perc > 1:
        perc = 1
    if perc < 0:
        perc = 0

    if time_now is None:
        time_now = get_now(time_now=time_now)

    total_td = est_total_timedelta(time_now=time_now, start_time=start_time, perc=perc)
    current_td = time_now - start_time
    return total_td - current_td


def est_finish_time(perc, start_time, time_now=None, tz=None, format_str=None):
    """
    Returns the estimated finish time for a task based on a percentage and start time.

    :param perc: the percentage that the task is done
    :param start_time: the time that the task was started
    :param time_now: the current time (if not passed, assumes Now
    :param tz: the timezone to return the time in. (if not passed, will check the start time for a TZ, if none,
        a naieve datetime object will be returned.)
    :param format_str: if passed, this will format the returning datetime as a string using this format string, if None
        we will return a datetime object.
    :return:

    Examples:
        >>> now = datetime.now()
        >>> start_time = now - timedelta(seconds=10)
        >>> ends_at = est_finish_time(perc=0.25, start_time=start_time)
        >>> ends_at == now + timedelta(seconds=30)
        True
    """
    if perc > 1:
        perc = 1
    if perc < 0:
        perc = 0

    if tz is None:
        tz = start_time

    if time_now is None:
        time_now = get_now(tz=tz)

    tmp_finish_td = est_total_timedelta(time_now=time_now, start_time=start_time, perc=perc)

    tmp_ret = time_now + tmp_finish_td

    if format_str is not None:
        tmp_ret = tmp_ret.strftime(format_str)

    return tmp_ret


class PercCounter(object):
    """

    This is a counter object that tracks percentage complete.  it can be used to generate percentages as indicators
    change.

    In addition to the listed methods, some common interactions with this are:

    >>> pc = PercCounter(total=500)
    PercCounter() total=100

    >>> pc += 50
    10

    >>> pc(250)
    40

    >>> pc -= 200
    10





    """

    def __init__(self,
                 total=None,
                 current=0,
                 offset=0,
                 perc_format=PERC_RET.AS_INT,
                 def_string_format='{perc:.0%}',
                 time_start=None,
                 perc_bar_filled_char='#',
                 perc_bar_empty_char='.',
                 perc_bar_length=60,
                 scaled_total=100,
                 min_perc=0,
                 max_perc=None,
                 tz=None,
                 auto_start=True,
                 ):
        """
        :param total:
        :param current:
        :param offset: offset allows setting a different start point for perc calculation.  for example, if your set
            starts at 10 with a total of 110, but you want to calculat the percentage based on 10-110 instead of 0-110,
            you can set the offset to 10.
        :param perc_format: this is the default format that is returned when using "percentage", or "__call__"
        :param def_string_format: defines the default format for str(PercCounter) as well as if you call .format()
            with no format string.
            available variables include:
                {perc]:  the current percentage, can use standard formatting options like {perc:.0%} to get an integer.
                {current}: returns the current value
                {total}: returns the total value
                {spinner}: returns a spinner object
                {bar_left}:
                {bar_right}:
                {bar_center}:
                {start_time}:
                {time_now}:
                {est_remaining_time}:
                {est_total_time}:
                {est_time_done):
                {offset}:

        :param time_start:  what time the counter started, if not set, will autoset to the current time when the first
            value is set.  (if auto_start is enabled)
        :param auto_start:  Automatically set the start time if not set upon the first value.  if not set, you have to
            manually set the start time.
        :param perc_bar_filled_char: see perc bar
        :param perc_bar_empty_char: see perc bar
        :param perc_bar_length: see perc bar
        :param scaled_total: allows setting the default scaled total (see scaled method)
        :param min_perc: if set, this is the minimum that will return  (set using float numbers)
        :param max_perc:if set, this is the maximum that will return  (set using float numbers)
        :param tz: the timezone (only needed for est_finish_time, and onl if there is not a timezone in the start time.
        """
        self.tz = tz
        self.current = current
        self.offset = offset
        self.perc_format = perc_format
        self.def_string_format = def_string_format
        self.time_start = time_start
        self.auto_start = auto_start
        self.perc_bar_filled_char = perc_bar_filled_char
        self.perc_bar_empty_char = perc_bar_empty_char
        self.perc_bar_length = perc_bar_length
        self.scaled_total = scaled_total
        self.min_perc = min_perc
        self.max_perc = max_perc
        self.set_total(total)

    def set_total(self, total):
        """
        Allows resetting the total possible value
        :param total:
        :return:
        """
        if total == 0:
            raise ZeroDivisionError()
        self.total = total

    def clear(self):
        """
        Will clear the starting points
        :return:
        """
        self.current = 0
        self.time_start = None

    def set_start_time(self, time_start=None, tz=None):
        """
        allows setting the start time and time zone.
        :param time_start:
        :param tz:
        :return:
        """
        if tz is not None:
            self.tz = tz
        self.time_start = get_now(time_now=time_start, tz=self.tz)
        if self.tz is None and hasattr(self.time_start, 'tz'):
            self.tz = self.time_start.tz

    def percentage(self, current=None, delta=None, perc_format=None):
        """
        Allows getting the percentage and setting the current state.
        (this is called if the object is called without a method).

        :param current: if passed, overwrites the current setting
        :param delta: if oassed, will add to the current setting
        :param perc_format: if passed modifies what this returns.
        :return:
        """
        if self.time_start is None and self.auto_start:
            self.set_start_time()

        if current is not None:
            self.current = current

        if delta is not None:
            self.current += delta

        current = self.current
        total = self.total

        if self.offset:
            current -= self.offset
            total -= self.offset

        if perc_format is None:
            perc_format = self.perc_format

        return make_percentage(current=current, total=total, perc_format=perc_format, min_perc=self.min_perc,
                               max_perc=self.max_perc)

    def scaled(self, scaled_total, current=None, delta=None, as_int=True):
        """
        returns a scaled number based on the current percentage.  for example, if the current percentage os 50%,
        and a scaled total of 50 is passed, it would return 25.

        :param scaled_total: if passed, is used for the calc, if not, the default s used from the init.
        :param current: if passed updates the current counter
        :param delta: if passed, adds to the current counter
        :param as_int: if passed, will return an int.
        :return:
        """
        perc = self.percentage(current=current, perc_format=PERC_RET.AS_FLOAT, delta=delta)
        return scaled_perc(perc, scaled_total=scaled_total, as_int=as_int)

    def perc_bar(self, current=None, delta=None, bar_format='{left_bar}', **bar_kwargs):
        """
        returns a string percentage bar, see "perc_bar" for more info
        :param current: if passed updates the current counter
        :param delta: if passed, adds to the current counter
        :param bar_format: these args are passed to the perc_bar function.
        :param bar_kwargs: These additional kwargs are passed to the end format function.
        :return:
        """
        perc = self.percentage(current=current, perc_format=PERC_RET.AS_FLOAT, delta=delta)
        return perc_bar(perc=perc, filled_char=self.perc_bar_filled_char, empty_char=self.perc_bar_empty_char,
                        length=self.perc_bar_length, bar_format=bar_format, spin_state=self.current,
                        current=self.current, **bar_kwargs)

    def est_finish_time(self, time_now=None, current=None, delta=None, format_str=None):
        """
        Returns the estimated finish time as a datetime object or string.
        this is based on a simple caclulation based on the perc done and assums a constant rate of perc change.
        :param time_now: if not passed, assumes datetime.now()
        :param current: if passed updates the current counter
        :param delta: if passed, adds to the current counter
        :param format_str: if passed, this will return a string based on this format code.
        :return:
        """
        if self.time_start is None:
            raise AttributeError('Start Time is not set, cannot compute est finish time')
        perc = self.percentage(current=current, perc_format=PERC_RET.AS_FLOAT, delta=delta)
        return est_finish_time(perc=perc, start_time=self.time_start, time_now=time_now, tz=self.tz,
                               format_str=format_str)

    def est_finish_timedelta(self, time_now=None, current=None, delta=None):
        """
        Returns a timedelta object based on the time required to finish the processing.
        this is based on a simple caclulation based on the perc done and assums a constant rate of perc change.
        :param time_now: if not passed, assumes datetime.now()
        :param current: if passed updates the current counter
        :param delta: if passed, adds to the current counter

        :return:
        """
        if self.time_start is None:
            raise AttributeError('Start Time is not set, cannot compute est finish timedelta')
        perc = self.percentage(current=current, perc_format=PERC_RET.AS_FLOAT, delta=delta)
        return est_finish_timedelta(perc=perc, start_time=self.time_start, time_now=time_now)

    def est_total_timedelta(self, time_now=None, current=None, delta=None):
        """
        Returns a timedelta object based on the total time required to do the task, including the time already done.

        This is based on a simple caclulation based on the perc done and assums a constant rate of perc change.
        :param time_now: if not passed, assumes datetime.now()
        :param current: if passed updates the current counter
        :param delta: if passed, adds to the current counter
        :return:
        """
        if self.time_start is None:
            raise AttributeError('Start Time is not set, cannot compute total time delta')
        perc = self.percentage(current=current, perc_format=PERC_RET.AS_FLOAT, delta=delta)
        return est_total_timedelta(perc=perc, start_time=self.time_start, time_now=time_now)

    def current_timedelta(self, time_now=None):
        """
        Returns a timedelta object based on the time elapsed since the project began.
        :param time_now: if not passed, assumes datetime.now()
        :return:
        """
        if self.time_start is None:
            raise AttributeError('Start Time is not set, cannot compute timedelta')
        time_now = get_now(time_now)
        return time_now - self.time_start

    def format(self, format_str=None, **kwargs):
        """
        returns a formatted string based on a format_str with a number of possible variables.

        :param format_str: defines the format to return using str.format()
            available variables include:
                {perc]:  the current percentage, can use standard formatting options like {perc:.0%} to get an integer.
                {current}: returns the current value
                {total}: returns the total value
                {spinner}: returns a spinner object
                {bar_left}:
                {bar_right}:
                {bar_center}:
                {start_time}:
                {time_now}:
                {est_remaining_time}:
                {est_total_time}:
                {est_time_done):
                {offset}:
        """
        if format_str is None:
            format_str = self.def_string_format
        if '{time_now}' in format_str:
            kwargs['time_now'] = get_now(tz=self.tz)
        if '{start_time}' in format_str and self.time_start is not None:
            kwargs['start_time'] = self.time_start
        if 'est_finish_timedelta' in format_str:
            kwargs['est_finish_timedelta'] = self.est_finish_timedelta()
        if 'est_total_timedelta' in format_str:
            kwargs['est_total_timedelta'] = self.est_total_timedelta()
        if 'est_finish_time' in format_str:
            kwargs['est_finish_time'] = self.est_finish_time()

        return self.perc_bar(
            bar_format=format_str,
            total=self.total,
            offset=self.offset,
            **kwargs
        )

    def __call__(self, current=None, delta=None):
        return self.percentage(current=current, delta=delta)

    def __str__(self):
        return self.format()

    def __repr__(self):
        if self.time_start is None:
            return self.format('PercCounter: Perc: {perc:.2%} Current: {current} / Total: {total}')
        else:
            return self.format(
                'PercCounter: Perc: {perc:.2%} Current: {current} / Total: {total} Started: {start_time} Est_Fininh In: {est_finish_timedelta}')

    def __iadd__(self, other):
        self.percentage(delta=other)
        return self

    def __isub__(self, other):
        self.percentage(delta=(other * -1))
        return self

    def __int__(self):
        return self.percentage(perc_format=PERC_RET.AS_INT)

    def __float__(self):
        return self.percentage(perc_format=PERC_RET.AS_FLOAT)

