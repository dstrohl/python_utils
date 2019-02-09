__all__ = ['str_to_bool', 'bool_to_yn', 'is_yn', 'datetime_tz_to_str', 'str_to_date', 'str_to_datetime',
           'str_to_datetime_tz', 'str_to_time', 'date_to_str', 'datetime_to_str', 'time_to_str', 'is_datetime_tz']

from datetime import time, date, datetime, tzinfo

YES = 'Yes'
NO = 'No'

TRUE_FALSE = {
    'true': True,
    'True': True,
    'false': False,
    'False': False,
    YES: True,
    'yes': True,
    NO: False,
    'no': False
}

YES_NO_TO_BOOL = {
    YES: True,
    NO: False,
    'yes': True,
    'YES': True,
    'no': False,
    'NO': False
}

BOOL_TO_YN = {
    True: YES,
    False: NO
}

DEFAULT_TIME_FORMAT = '%H:%M:%S.%f'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATETIME_FORMAT = DEFAULT_DATE_FORMAT+'T'+DEFAULT_TIME_FORMAT
DEFAULT_DATETIME_TZ_FORMAT = DEFAULT_DATETIME_FORMAT + '%z'


def str_to_bool(in_str):
    try:
        return TRUE_FALSE[in_str]
    except KeyError:
        raise ValueError('%s cannot be converted to bool' % in_str)


def bool_to_yn(in_bool):
    try:
        return BOOL_TO_YN[in_bool]
    except KeyError:
        raise ValueError('%r cannot be converted to yes/no' % in_bool)


def is_yn(in_yn):
    return isinstance(in_yn, str) and in_yn in YES_NO_TO_BOOL


def date_to_str(date_in):
    return date_in.strftime(DEFAULT_DATE_FORMAT)


def str_to_date(str_in):
    return datetime.strptime(str_in, DEFAULT_DATE_FORMAT).date()


def time_to_str(time_in):
    return time_in.strftime(DEFAULT_TIME_FORMAT)


def str_to_time(str_in):
    tmp_dt = datetime.strptime(str_in, DEFAULT_TIME_FORMAT)
    return tmp_dt.time()


def datetime_to_str(dt_in):
    return dt_in.strftime(DEFAULT_DATETIME_FORMAT)


def str_to_datetime(str_in):
    return datetime.strptime(str_in, DEFAULT_DATETIME_FORMAT)


def datetime_tz_to_str(dt_in):
    return dt_in.strftime(DEFAULT_DATETIME_TZ_FORMAT)


def str_to_datetime_tz(str_in):
    return datetime.strptime(str_in, DEFAULT_DATETIME_TZ_FORMAT)


def is_datetime_tz(dt_in):
    if isinstance(dt_in, datetime):
        return dt_in.tzinfo is not None
    else:
        return False

