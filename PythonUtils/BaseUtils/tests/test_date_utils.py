#!/usr/bin/env python

from unittest import TestCase
from PythonUtils.BaseUtils import timedelta_to_string, TIMEDELTA_PERIOD_ACTION
from datetime import timedelta

MINUTE_SECS = 60
HOUR_SECS = MINUTE_SECS * 60
DAY_SECS = HOUR_SECS * 24
WEEK_SECS = DAY_SECS * 7
MONTH_SECS = DAY_SECS * 30
YEAR_SECS = DAY_SECS * 365
DECADE_SECS = YEAR_SECS * 10

print(YEAR_SECS)

PERIOD_SECONDS = dict(
    decade=DECADE_SECS,
    year=YEAR_SECS,
    month=MONTH_SECS,
    week=WEEK_SECS,
    day=DAY_SECS,
    hour=HOUR_SECS,
    minute=MINUTE_SECS,
    second=1,
)


class TestTD2String(TestCase):

    def calc_secs(self, **kwargs):
        tmp_ret = 0
        for key, item in kwargs.items():
            tmp_ret += PERIOD_SECONDS[key] * item
        return tmp_ret

    def test_td_to_string_default_1(self):
        tot_sec = self.calc_secs(day=1, hour=23, second=20)
        exp_text = 'In 1 Day, 23 Hours, 20 Seconds'
        tmp_ret = timedelta_to_string(tot_sec)
        self.assertEqual(exp_text, tmp_ret)

    def test_td_to_string_default_2(self):
        tot_sec = self.calc_secs(week=40, day=84, hour=23, minute=50, second=600)
        exp_text = 'In 1 Year'
        tmp_ret = timedelta_to_string(tot_sec)
        self.assertEqual(exp_text, tmp_ret)

    def test_td_to_string_some_always(self):
        tot_sec = self.calc_secs(day=1, hour=23, second=20)
        exp_text = 'In 1 Day, 23 Hours, 0 Minutes, 20 Seconds'
        tmp_ret = timedelta_to_string(tot_sec, minute=TIMEDELTA_PERIOD_ACTION.ALWAYS)
        self.assertEqual(exp_text, tmp_ret)

    def test_td_to_string_some_always_td_obj(self):
        tot_sec = self.calc_secs(day=1, hour=23, second=20)
        tot_sec = timedelta(seconds=tot_sec)
        exp_text = 'In 1 Day, 23 Hours, 0 Minutes, 20 Seconds'
        tmp_ret = timedelta_to_string(tot_sec, minute=TIMEDELTA_PERIOD_ACTION.ALWAYS)
        self.assertEqual(exp_text, tmp_ret)

    def test_td_to_string_some_never_td_obj(self):
        tot_sec = self.calc_secs(day=1, hour=23, second=20)
        tot_sec = timedelta(seconds=tot_sec)
        exp_text = 'In 1 Day, 1380 Minutes, 20 Seconds'
        tmp_ret = timedelta_to_string(tot_sec, hour=TIMEDELTA_PERIOD_ACTION.NEVER, minute=TIMEDELTA_PERIOD_ACTION.ALWAYS)
        self.assertEqual(exp_text, tmp_ret)

    def test_td_to_string_some_lower_case(self):
        tot_sec = self.calc_secs(day=1, hour=23, second=20)
        exp_text = 'in 1 day, 23 hours, 0 minutes, 20 seconds'
        tmp_ret = timedelta_to_string(tot_sec, minute=TIMEDELTA_PERIOD_ACTION.ALWAYS, case=str.lower)
        self.assertEqual(exp_text, tmp_ret)

    def test_td_to_string_some_always_td_obj_ms(self):
        tot_sec = self.calc_secs(day=1, hour=23, second=20)
        tot_sec = timedelta(seconds=tot_sec, microseconds=1234)
        exp_text = 'In 1 Day, 23 Hours, 0 Minutes, 20 Seconds'
        tmp_ret = timedelta_to_string(tot_sec, minute=TIMEDELTA_PERIOD_ACTION.ALWAYS)
        self.assertEqual(exp_text, tmp_ret)

    def test_td_to_string_some_always_td_obj_ms_2(self):
        tot_sec = self.calc_secs(day=1, hour=23, second=20)
        tot_sec = timedelta(seconds=tot_sec, microseconds=1234)
        exp_text = 'In 1 Day, 23 Hours, 0 Minutes, 20 Seconds, 1233 Microseconds'
        tmp_ret = timedelta_to_string(tot_sec,
                                      minute=TIMEDELTA_PERIOD_ACTION.ALWAYS,
                                      microsecond=TIMEDELTA_PERIOD_ACTION.DEFAULT)
        self.assertEqual(exp_text, tmp_ret)

    def test_td_to_string_some_always_td_obj_mi_2(self):
        tot_sec = self.calc_secs(day=1, hour=23, second=20)
        tot_sec = timedelta(seconds=tot_sec, microseconds=1234, milliseconds=134)
        exp_text = 'In 1 Day, 23 Hours, 0 Minutes, 20 Seconds, 135 Milliseconds, 233 Microseconds'
        tmp_ret = timedelta_to_string(tot_sec,
                                      minute=TIMEDELTA_PERIOD_ACTION.ALWAYS,
                                      microsecond=TIMEDELTA_PERIOD_ACTION.DEFAULT,
                                      millisecond=TIMEDELTA_PERIOD_ACTION.DEFAULT)
        self.assertEqual(exp_text, tmp_ret)

    def test_td_to_string_less_than(self):
        tot_sec = self.calc_secs(day=1, hour=23, second=20)
        more_secs = self.calc_secs(day=1)
        less_secs = 60
        tot_sec = timedelta(seconds=tot_sec)
        exp_text = 'In More Than 1 Day'
        tmp_ret = timedelta_to_string(tot_sec, less_than_at=less_secs, more_than_at=more_secs)
        self.assertEqual(exp_text, tmp_ret)

    def test_td_to_string_more_than(self):
        tot_sec = self.calc_secs(second=20)
        more_secs = self.calc_secs(day=1)
        less_secs = 60
        tot_sec = timedelta(seconds=tot_sec)
        exp_text = 'In Less Than 1 Minute'
        tmp_ret = timedelta_to_string(tot_sec, less_than_at=less_secs, more_than_at=more_secs)
        self.assertEqual(exp_text, tmp_ret)
