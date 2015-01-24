__author__ = 'strohl'

from TextUtils.find_and_replace import replace_between, get_after, get_before, get_between
from TextUtils.trim_and_fix import elipse_trim
from TextUtils.detection import is_string, make_list
from TextUtils.lists import get_different, get_not_in, get_same
from TextUtils.records import Record, RecordAddFieldDisallowed, RecordReorderFieldsException
from TextUtils.csv_wrapper import CSVData
