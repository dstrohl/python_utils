#!/usr/bin/env python

"""
Test quarter calculation functions
"""

__author__ = "Dan Strohl"
__copyright__ = "Copyright 2019, Dan Strohl"

from unittest import TestCase
from PythonUtils.BaseUtils.base_utils import add_month, date_add_month, FiscalDate, FiscalDateCalc, short_month_name, full_month_name
import csv
from datetime import date, datetime

quarters = {
    1: 1, 2: 1, 3: 1,
    4: 2, 5: 2, 6: 2,
    7: 3, 8: 3, 9: 3,
    10: 4, 11: 4, 12: 4,
}

class TestMonthHelpers(TestCase):

    def test_add_month(self):
        tests = [
            (2019, 1, 1, 2019, 2),
            (2019, 10, 3, 2020, 1),
            (2019, 1, -1, 2018, 12),
            (2019, 1, 0, 2019, 1),
            (2019, 1, 26, 2021, 3),
            (2019, 1, 1, 2019, 2),
        ]
        for cy, cm, am, ry, rm in tests:
            self.assertEqual((ry, rm), add_month(cy, cm, am))


    def test_add_month_date(self):
        tests = [
            (2019, 1, 1, 1, 2019, 2, 1),
            (2019, 10, 1, 3, 2020, 1, 1),
            (2019, 1, 1, -1, 2018, 12, 1),
            (2019, 1, 31, 1, 2019, 2, 28),
            (2019, 1, 15, 26, 2021, 3, 15),
            (2019, 1, 15, 1, 2019, 2, 15),
        ]
        for cy, cm, cd, am, ry, rm, rd in tests:
            test_name = '%s/%s/%s + %s = %s/%s/%s' % (cy, cm, cd, am, ry, rm, rd)
            with self.subTest(test_name):
                exp_date = date(ry, rm, rd)
                start_date = date(cy, cm, cd)
                ret_date = date_add_month(start_date, am)
                self.assertEqual(exp_date, ret_date)
                self.assertIsInstance(ret_date, date)

    def test_add_month_datetime(self):
        tests = [
            (2019, 1, 1, 1, 2019, 2, 1),
            (2019, 10, 1, 3, 2020, 1, 1),
            (2019, 1, 1, -1, 2018, 12, 1),
            (2019, 1, 31, 1, 2019, 2, 28),
            (2019, 1, 15, 26, 2021, 3, 15),
            (2019, 1, 15, 1, 2019, 2, 15),
        ]
        for cy, cm, cd, am, ry, rm, rd in tests:
            test_name = '%s/%s/%s + %s = %s/%s/%s' % (cy, cm, cd, am, ry, rm, rd)
            with self.subTest(test_name):
                exp_date = datetime(ry, rm, rd)
                start_date = datetime(cy, cm, cd)
                ret_date = date_add_month(start_date, am)
                self.assertEqual(exp_date, ret_date)
                self.assertIsInstance(ret_date, datetime)

    def test_get_short_month(self):
        tests = [
            (1, 'Jan'),
            (2, 'Feb'),
            (3, 'Mar'),
            (4, 'Apr'),
            (5, 'May'),
            (6, 'Jun'),
            (7, 'Jul'),
            (8, 'Aug'),
            (9, 'Sep'),
            (10, 'Oct'),
            (11, 'Nov'),
            (12, 'Dec'),
        ]

        for test_mon, test_name in tests:
            tmp_ret = short_month_name(test_mon)
            self.assertEqual(test_name, tmp_ret)

    def test_get_full_month(self):
        tests = [
            (1, 'January'),
            (2, 'February'),
            (3, 'March'),
            (4, 'April'),
            (5, 'May'),
            (6, 'June'),
            (7, 'July'),
            (8, 'August'),
            (9, 'September'),
            (10, 'October'),
            (11, 'November'),
            (12, 'December'),
        ]

        for test_mon, test_name in tests:
            tmp_ret = full_month_name(test_mon)
            self.assertEqual(test_name, tmp_ret)


class TestQuarterCalculator(TestCase):


    def test_quarter_calc(self):
        with open('quarter_tests4.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            """
            'Current', 'Offset', 'Year Offset', 'Quarter-BE', 'Quarter_Loc', 'FY', 'Start Quarter Date', 'End Quarter Date', 'Start FY Date', 'End FY Date'
            """

            TEST_CURRENT = None
            TEST_OFFSET = None
            TEST_FORMAT = None
            # TEST_CURRENT = 1
            # TEST_OFFSET = 2
            # TEST_FORMAT = 'FY_MON_SE'
            if TEST_CURRENT is not None or TEST_OFFSET is not None:
                with self.subTest('Not Finished'):
                    self.fail('filtered tests')

            for test in reader:
                # print(test)
                current = int(test['current'])
                offset = int(test['offset'])
                fq = int(test['fq'])
                fy = int(test['fy'])

                current_date = date(2019, current, 15)
                current_datetime = datetime(2019, current, 15)

                fq_start_datetime = datetime.strptime(test['fq_start'], '%m/%d/%Y')
                fq_end_datetime = datetime.strptime(test['fq_end'], '%m/%d/%Y')
                fy_start_datetime = datetime.strptime(test['fy_start'], '%m/%d/%Y')
                fy_end_datetime = datetime.strptime(test['fy_end'], '%m/%d/%Y')

                fq_start_date = fq_start_datetime.date()
                fq_end_date = fq_end_datetime.date()
                fy_start_date = fy_start_datetime.date()
                fy_end_date = fy_end_datetime.date()

                fy2 = fy-2000

                cq = quarters[current]

                fy_s_mon_num = fy_start_date.month
                fy_e_mon_num = fy_end_date.month
                fy_s_mon_name = short_month_name(fy_s_mon_num)
                fy_e_mon_name = short_month_name(fy_e_mon_num)

                fq_s_mon_num = fq_start_date.month
                fq_e_mon_num = fq_end_date.month
                fq_s_mon_name = full_month_name(fq_s_mon_num)
                fq_e_mon_name = full_month_name(fq_e_mon_num)

                format_checks = [
                    ('FQ_FY2', '%02d/15/2019 FQ%s-%02d' % (current, fq, fy2), '%m/%d/%Y FQ%(fq)-%(fy!2)'),
                    ('CQ_FY2', '%02d/15/2019 CQ%s-%02d' % (current, cq, fy2), '%m/%d/%Y CQ%(cq)-%(fy!2)'),
                    ('FQ_FY4', '%02d/15/2019 FQ%s-%s' % (current, fq, fy), '%m/%d/%Y FQ%(fq)-%(fy)'),
                    ('CQ_FY4', '%02d/15/2019 CQ%s-%s' % (current, cq, fy), '%m/%d/%Y CQ%(cq)-%(fy)'),

                    ('FQ2_FY2', '%02d/15/2019 FQ%02d-%s' % (current, fq, fy2), '%m/%d/%Y FQ%(fq!2)-%(fy!2)'),
                    ('CQ2_FY2', '%02d/15/2019 CQ%02d-%s' % (current, cq, fy2), '%m/%d/%Y CQ%(cq!2)-%(fy!2)'),

                    ('FY_MON_SE', 'FY %s [%s -> %s]' %(fy, fy_s_mon_name, fy_e_mon_name), 'FY %(fy) [%(fy_start!%b) -> %(fy_end!%b)]'),
                    ('FQ_MON_SE_LONG', 'FQ %s [%s (%02d) -> %s (%02d)]' % (fq, fq_s_mon_name, fq_s_mon_num, fq_e_mon_name, fq_e_mon_num), 'FQ %(fq) [%(fq_start!%B (%m)) -> %(fq_end!%B (%m))]'),

                ]

                if TEST_CURRENT is not None and TEST_CURRENT != current:
                    continue
                if TEST_OFFSET is not None and TEST_OFFSET != offset:
                    continue

                msg = [
                    'EXPECTED:',
                    '---------'
                    '    current month: %s' % current,
                    '    current: %s' % current_date,
                    '    offset:  %s' % offset,
                    '    FY: %s:  %s (%s/%s) -> %s (%s/%s)' % (fy, fy_start_date, fy_s_mon_name, fy_s_mon_num, fy_end_date, fy_e_mon_name, fy_e_mon_num),
                    '    FQ: %s:  %s (%s/%s) -> %s (%s/%s)' % (fq, fq_start_date, fq_s_mon_name, fq_s_mon_num, fq_end_date, fq_e_mon_name, fq_e_mon_num),
                    '    CQ: %s' % cq,
                    '    Formsts:',
                ]
                for f in format_checks:
                    msg.append('         %s' % repr(f))
                msg.append('')
                msg = '\n'.join(msg)

                test_name = 'C%s:O%s' % (current, offset)
                with self.subTest(test_name):
                    fiscal_date_obj = FiscalDate(current_date, fiscal_offset=offset)
                    fiscal_datetime_obj = FiscalDate(current_datetime, fiscal_offset=offset)

                    fiscal_calculator = FiscalDateCalc(fiscal_offset=offset)

                    do_msg = msg + fiscal_date_obj.dump()
                    dto_msg = msg + fiscal_datetime_obj.dump()
                    calc_msg = msg + fiscal_calculator.dump(current_date)

                    sub_test_name = 'fy' + ' | ' + test_name
                    with self.subTest(sub_test_name):
                        with self.subTest('calc-' + sub_test_name):
                            self.assertEqual(fy, fiscal_calculator.fy(current_date))
                        with self.subTest('dto-' + sub_test_name):
                            self.assertEqual(fy, fiscal_datetime_obj.fy)
                        with self.subTest('do-' + sub_test_name):
                            self.assertEqual(fy, fiscal_date_obj.fy)

                    sub_test_name = 'fq' + ' | ' + test_name
                    with self.subTest(sub_test_name):
                        with self.subTest('calc-' + sub_test_name):
                            self.assertEqual(fq, fiscal_calculator.fq(current_date))
                        with self.subTest('dto-' + sub_test_name):
                            self.assertEqual(fq, fiscal_datetime_obj.fq)
                        with self.subTest('do-' + sub_test_name):
                            self.assertEqual(fq, fiscal_date_obj.fq)

                    sub_test_name = 'cq' + ' | ' + test_name
                    with self.subTest(sub_test_name):
                        with self.subTest('calc-' + sub_test_name):
                            self.assertEqual(cq, fiscal_calculator.cq(current_date))
                        with self.subTest('dto-' + sub_test_name):
                            self.assertEqual(cq, fiscal_datetime_obj.cq)
                        with self.subTest('do-' + sub_test_name):
                            self.assertEqual(cq, fiscal_date_obj.cq)

                    sub_test_name = 'fy_start' + ' | ' + test_name
                    with self.subTest(sub_test_name):
                        with self.subTest('calc-' + sub_test_name):
                            self.assertEqual(fy_start_date, fiscal_calculator.fy_start(current_date), calc_msg)
                        with self.subTest('dto-' + sub_test_name):
                            self.assertEqual(fy_start_datetime, fiscal_datetime_obj.fy_start, dto_msg)
                        with self.subTest('do-' + sub_test_name):
                            self.assertEqual(fy_start_date, fiscal_date_obj.fy_start, do_msg)

                    sub_test_name = 'fy_end' + ' | ' + test_name
                    with self.subTest(sub_test_name):
                        with self.subTest('calc-' + sub_test_name):
                            self.assertEqual(fy_end_date, fiscal_calculator.fy_end(current_date), calc_msg)
                        with self.subTest('dto-' + sub_test_name):
                            self.assertEqual(fy_end_datetime, fiscal_datetime_obj.fy_end, dto_msg)
                        with self.subTest('do-' + sub_test_name):
                            self.assertEqual(fy_end_date, fiscal_date_obj.fy_end, do_msg)

                    sub_test_name = 'fq_start' + ' | ' + test_name
                    with self.subTest(sub_test_name):
                        with self.subTest('calc-' + sub_test_name):
                            self.assertEqual(fq_start_date, fiscal_calculator.fq_start(current_date), calc_msg)
                        with self.subTest('dto-' + sub_test_name):
                            self.assertEqual(fq_start_datetime, fiscal_datetime_obj.fq_start, dto_msg)
                        with self.subTest('do-' + sub_test_name):
                            self.assertEqual(fq_start_date, fiscal_date_obj.fq_start, do_msg)

                    sub_test_name = 'fq_end' + ' | ' + test_name
                    with self.subTest(sub_test_name):
                        with self.subTest('calc-' + sub_test_name):
                            self.assertEqual(fq_end_date, fiscal_calculator.fq_end(current_date), calc_msg)
                        with self.subTest('dto-' + sub_test_name):
                            self.assertEqual(fq_end_datetime, fiscal_datetime_obj.fq_end, dto_msg)
                        with self.subTest('do-' + sub_test_name):
                            self.assertEqual(fq_end_date, fiscal_date_obj.fq_end, do_msg)

                    for f_name, f_exp, f_string in format_checks:
                        if TEST_FORMAT is None or TEST_FORMAT == f_name:
                            sub_test_name = 'format_' + f_name + ' | ' + test_name
                            with self.subTest(sub_test_name):
                                with self.subTest('calc-' + sub_test_name):
                                    self.assertEqual(f_exp, fiscal_calculator.format(current_date, f_string), calc_msg)
                                with self.subTest('dto-' + sub_test_name):
                                    self.assertEqual(f_exp, fiscal_datetime_obj.format(f_string), dto_msg)
                                with self.subTest('do-' + sub_test_name):
                                    self.assertEqual(f_exp, fiscal_date_obj.format(f_string), do_msg)


