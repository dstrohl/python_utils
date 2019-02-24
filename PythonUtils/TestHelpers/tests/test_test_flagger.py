import unittest
from PythonUtils.TestHelpers.test_flagger import *
import os
import sys
import platform
import re


class TestRegex(unittest.TestCase):

    def test_re_match(self):

        re_in = r'skip_if_(?P<is_not>is|not)_os_(?P<os_name>.+)'
        # re_in = r'skip_if_(?P<is_not>is|not)_os_.*'
        tests = [
            # (str_in, Match_TF, Match_dict),
            ('skip_if_not_os_nt', True, {'os_name': 'nt', 'is_not': 'not'})
        ]

        for str_in, match_tf, match_dict in tests:
            with self.subTest(str_in):
                rex = re.compile(re_in)
                tmp_match = rex.fullmatch(str_in)
                if match_tf:
                    self.assertTrue(tmp_match)
                    self.assertEqual(match_dict, tmp_match.groupdict())
                else:
                    self.assertFalse(rex.fullmatch(str_in))



class FlaggerFixture(object):
    pass

flagger_fixture = FlaggerFixture()


class TestTestFlaggerIDItem(unittest.TestCase):

    def test_base(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('test_name', tmp_obj.name)

    def test_eq(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name*', 'test_desc')
        self.assertEqual('test_name', tmp_obj)
        self.assertEqual('test_name_is_me', tmp_obj)
        self.assertNotEqual('foobar test_name', tmp_obj)
        self.assertEqual('test_name*', tmp_obj)

    def test_str(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('test_name', str(tmp_obj))

    def test_match_one_metric(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc', )
        tmp_obj.referenced_obj.append('foobar')
        tmp_obj.referenced_obj.append('snafu')
        self.assertEqual('test_name', str(tmp_obj))
        self.assertTrue(tmp_obj.match('any_test_count'))
        self.assertFalse(tmp_obj.match('any_not_found'))

    def test_match_inc_ref_item(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_obj.referenced_obj.append('foobar')
        tmp_obj.referenced_obj.append('snafu')
        self.assertTrue(tmp_obj.match(inc_tests=['foobar', 'snafu']))
        self.assertTrue(tmp_obj.match(inc_tests='foobar'))
        self.assertFalse(tmp_obj.match(inc_tests='not there'))

    def test_stats_dict(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_obj.referenced_obj.append('foobar')
        tmp_obj.referenced_obj.append('snafu')
        exp_ret = {'Matched Tests': 2, 'Not Found IDs': 0}
        self.assertEqual(exp_ret, tmp_obj.stats_dict())

        exp_ret = {'Matched Tests': 2}
        self.assertEqual(exp_ret, tmp_obj.stats_dict(inc_empty=False))

        exp_ret = {'Not Found IDs': 0}
        self.assertEqual(exp_ret, tmp_obj.stats_dict(inc_stats='not_found'))

        exp_ret = {'Matched Tests': 2}
        self.assertEqual(exp_ret, tmp_obj.stats_dict(exc_stat='not_found'))

    def test_stats_empty(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        exp_ret = {'Matched Tests': 0, 'Not Found IDs': 1}
        self.assertEqual(exp_ret, tmp_obj.stats_dict())

    def test_summary_data(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('[Not Matched] (test_desc)', tmp_obj.summary_data())
        self.assertEqual('[Not Matched]', tmp_obj.summary_data(inc_desc=False))

    def test_short_name(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('test_name', tmp_obj.short_name())

    def test_long_name(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('test_name [Not Matched] (test_desc)', tmp_obj.long_name())
        self.assertEqual('test_name [Not Matched]', tmp_obj.long_name(inc_desc=False))

    def test_dump_w_summary(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'test_desc')
        tmp_sub_2 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)
        exp_ret = 'test_name_2 : [Not Matched]\n' \
                  'test_name_3 : [Not Matched]'

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_w_summary_empty(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')

        exp_ret = ''

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_no_summary(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_obj.dump_inc_summary = False
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_dest_2')
        tmp_sub_2 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name_2\n' \
                  'test_name_3'

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_no_summary_empty(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_obj.dump_inc_summary = False

        exp_ret = ''

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_analysis(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_dest_2')
        tmp_sub_2 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)
        exp_ret = 'All Matched Tests'
        self.assertEqual(exp_ret, tmp_obj._analysis())

    def test_analysis_empty(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        exp_ret = 'All Not Found IDs'
        self.assertEqual(exp_ret, tmp_obj._analysis())

    def test_details(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name [Matched 2 times] (test_desc)'

        self.assertEqual(exp_ret, tmp_obj.details())

    def test_details_w_dump(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Matched 2 times\n' \
                  '  Analysis      : All Matched Tests\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0\n' \
                  '  Tests         : test_name_2 : [Not Matched]\n' \
                  '                  test_name_3 : [Not Matched]'

        self.assertEqual(exp_ret, tmp_obj.details(dump=True))

    def test_details_no_status(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)'

        self.assertEqual(exp_ret, tmp_obj.details(inc_status=False))

    def test_details_w_analysis(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Analysis      : All Matched Tests\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(inc_analysis=True, inc_stats=True))

    def test_details_w_stats(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(inc_stats=True, inc_status=False))

    def test_details_indent(self):
        tmp_obj = TestFlaggerSkipIDObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = '  test_name (test_desc)\n' \
                  '    Analysis      : All Matched Tests\n' \
                  '    Matched Tests : 2\n' \
                  '    Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(indent=2, inc_analysis=True, inc_stats=True))


class TestFlaggerIDList(unittest.TestCase):

    def test_base(self):
        fl = TestFlaggerSkipIDList(flagger_fixture)
        self.assertFalse(fl)

    def test_base_load_list(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        self.assertTrue(fl)
        self.assertEqual(3, len(fl))

    def test_base_load_dict(self):
        load_items = {'test_1':'td1', 'test_2': 'td2', 'test_3': 'td3'}
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        self.assertTrue(fl)
        self.assertEqual(3, len(fl))

    def test_clear(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        self.assertEqual(1, fl.get_stat('test_count'))

        fl.clear()

        exp_ret = 'Matched Tests : 0\n' \
                  'Not Found IDs : 3\n' \
                  'Total IDs     : 3'

        self.assertEqual(exp_ret, fl.summary())

    def test_add(self):
        fl = TestFlaggerSkipIDList(flagger_fixture)
        fl.add('t1', 'td1')
        fl.add('t2', 'td2')
        self.assertEqual(2, len(fl))

    def test_add_raise(self):
        fl = TestFlaggerSkipIDList(flagger_fixture)
        fl.add('t1', 'td1')
        fl.add('t2', 'td2')
        self.assertEqual(2, len(fl))
        with self.assertRaises(AttributeError):
            fl.add('t2')

    def test__iter__(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        for i in fl:
            print(i.name)
            load_items.remove(i.name)
        self.assertEqual([], load_items)

    def test_get_item(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)

        self.assertEqual('test_1', fl['test_1'].name)

    def test_iter(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        load_expect = ['test_2', 'test_3']

        for i in fl.iter('test_2', 'test_3'):
            self.assertIn(i.name, load_expect)
            load_expect.remove(i.name)
        self.assertEqual([], load_expect)

    def test_contains(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        self.assertIn('test_2', fl)
        self.assertNotIn('test_4', fl)

    def test_summary(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        exp_ret = 'Matched Tests : 1\n' \
                  'Not Found IDs : 2\n' \
                  'Total IDs     : 3'

        self.assertEqual(exp_ret, fl.summary())

    def test_name_list(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)

        exp_ret = 'test_1 [Not Matched]\n' \
                  'test_2 [Not Matched]\n' \
                  'test_3 [Not Matched]'

        self.assertEqual(exp_ret, fl.name_list())

    def test_details(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        exp_ret = 'Summary:\n' \
                  '  Matched Tests : 1\n' \
                  '  Not Found IDs : 2\n' \
                  '  Total IDs     : 3\n' \
                  'Details:\n' \
                  '  test_1 : Matched 1 time\n' \
                  '  test_2 : Not Matched\n' \
                  '  test_3 : Not Matched' \

        self.assertEqual(exp_ret, fl.details())

    def test_details_w_dump(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        exp_ret = 'Summary:\n' \
                  '  Matched Tests : 1\n' \
                  '  Not Found IDs : 2\n' \
                  '  Total IDs     : 3\n' \
                  'Details:\n' \
                  '  test_1 : Analysis      : All Matched Tests\n' \
                  '           Matched Tests : 1\n' \
                  '           Not Found IDs : 0\n' \
                  '  test_2 : Analysis      : All Not Found IDs\n' \
                  '           Matched Tests : 0\n' \
                  '           Not Found IDs : 1\n' \
                  '  test_3 : Analysis      : All Not Found IDs\n' \
                  '           Matched Tests : 0\n' \
                  '           Not Found IDs : 1'

        self.assertEqual(exp_ret, fl.details(dump=True))

    def test_details_no_summary(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        exp_ret = 'test_1 : Matched 1 time\n' \
                  'test_2 : Not Matched\n' \
                  'test_3 : Not Matched' \

        self.assertEqual(exp_ret, fl.details(inc_summary=False))

    def test_details_filtered(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        exp_ret = 'Summary:\n' \
                  '  Matched Tests : 1\n' \
                  '  Not Found IDs : 1\n' \
                  '  Total IDs     : 2\n' \
                  'Details:\n' \
                  '  test_1 : Matched 1 time\n' \
                  '  test_2 : Not Matched' \

        self.assertEqual(exp_ret, fl.details('test_1', 'test_2'))

class FixtureTestCase(object):
    """test_desc"""
    def id(self):
        return 'test_module.test_case.test_name'    
ftc = FixtureTestCase()

class TestTestFlaggerTestObj(unittest.TestCase):
    
    def test_base_obj(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, ftc, passed=True, run=True)
        self.assertEqual('name', tmp_obj.name)
        self.assertEqual('test_desc', tmp_obj.desc)
        self.assertTrue(tmp_obj.passed)
        self.assertFalse(tmp_obj.skipped)

    def test_base_test_start(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'test_name', 'test_desc', passed=True, run=True)
        self.assertEqual('name', tmp_obj.name)
        self.assertTrue(tmp_obj.passed)
        self.assertFalse(tmp_obj.skipped)

    def test_base_test__start(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'testof_name', 'test_desc', passed=True, run=True)
        self.assertEqual('of_name', tmp_obj.name)
        self.assertTrue(tmp_obj.passed)
        self.assertFalse(tmp_obj.skipped)

    def test_base_no_test_start(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'of_test_name', 'test_desc', passed=True, run=True)
        self.assertEqual('of_test_name', tmp_obj.name)
        self.assertTrue(tmp_obj.passed)
        self.assertFalse(tmp_obj.skipped)

    def test_eq(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        self.assertEqual('my_test_name', tmp_obj)
        self.assertNotEqual('test_name_is_me', tmp_obj)
        self.assertNotEqual('foobar test_name', tmp_obj)

    def test_str(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        self.assertEqual('my_test_name', str(tmp_obj))

    def test_match_set_result(self):
        tests = [
            ('passed', dict(passed=True, failed=False, raised=False, run=True, skipped=False)),
            ('failed', dict(passed=False, failed=True, raised=False, run=True, skipped=False)),
            ('raised', dict(passed=False, failed=True, raised=False, run=True, skipped=False)),
            ('run', dict(passed=None, failed=None, raised=None, run=True, skipped=False)),
            ('skipped', dict(passed=None, failed=None, raised=None, run=False, skipped=True)),
        ]
        for test_set, test_result in tests:
            with self.subTest(**test_set):
                tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
                tmp_obj.set_result(state=test_set)
                self.assertEqual(test_result, tmp_obj.stats_dict(full_field_names=False))


    def test_match_any_metric(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_obj.set_result(passed=True)
        self.assertTrue(tmp_obj.match('all_passed'))
        self.assertTrue(tmp_obj.match('all_run'))
        self.assertFalse(tmp_obj.match('all_failed'))
        self.assertTrue(tmp_obj.match('any_passed'))
        self.assertTrue(tmp_obj.match('any_run'))
        self.assertFalse(tmp_obj.match('any_failed'))
        self.assertFalse(tmp_obj.match('no_passed'))
        self.assertFalse(tmp_obj.match('no_run'))
        self.assertTrue(tmp_obj.match('no_failed'))

    def test_match_inc_ref_item(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_obj.referenced_obj.append('foobar3')
        tmp_obj.referenced_obj.append('snafu3')
        self.assertTrue(tmp_obj.match(inc_tests=['foobar3', 'snafu3']))
        self.assertTrue(tmp_obj.match(inc_tests='foobar3'))
        self.assertFalse(tmp_obj.match(inc_tests='not there'))

    def test_set_result_failed(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc', run=True)
        tmp_sub_obj = TestFlaggerFlagObj(flagger_fixture, 'test_flag')
        tmp_obj.flags.append(tmp_sub_obj)
        self.assertTrue(tmp_obj.run)
        self.assertIsNone(tmp_obj.passed)
        tmp_obj.set_result(AssertionError('foobar'))

        self.assertTrue(tmp_obj.failed)
        self.assertFalse(tmp_obj.passed)
        self.assertFalse(tmp_obj.raised)
        self.assertEqual(0, tmp_sub_obj.passed)
        self.assertEqual(1, tmp_sub_obj.failed)
        self.assertEqual(0, tmp_sub_obj.raised)
        self.assertEqual(1, len(tmp_obj.fail_reasons))

    def test_set_result_passed(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc', run=True)
        tmp_sub_obj = TestFlaggerFlagObj(flagger_fixture, 'test_flag')
        tmp_obj.flags.append(tmp_sub_obj)
        self.assertTrue(tmp_obj.run)
        self.assertIsNone(tmp_obj.passed)
        tmp_obj.set_result()

        self.assertTrue(tmp_obj.passed)
        self.assertFalse(tmp_obj.failed)
        self.assertFalse(tmp_obj.raised)
        self.assertEqual(0, tmp_sub_obj.passed)
        self.assertEqual(0, tmp_sub_obj.failed)
        self.assertEqual(1, tmp_sub_obj.raised)
        self.assertEqual(1, len(tmp_obj.fail_reasons))

    def test_set_result_raised(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc', run=True)
        tmp_sub_obj = TestFlaggerFlagObj(flagger_fixture, 'test_flag')
        tmp_obj.flags.append(tmp_sub_obj)
        self.assertTrue(tmp_obj.run)
        self.assertIsNone(tmp_obj.passed)
        tmp_obj.set_result(AttributeError('foobar'))

        self.assertTrue(tmp_obj.raised)
        self.assertFalse(tmp_obj.passed)
        self.assertFalse(tmp_obj.failed)
        self.assertEqual(1, tmp_sub_obj.passed)
        self.assertEqual(0, tmp_sub_obj.failed)
        self.assertEqual(0, tmp_sub_obj.raised)
        self.assertEqual(0, len(tmp_obj.fail_reasons))

    def test_summary_data(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        self.assertEqual('[Included] (test_desc)', tmp_obj.summary_data())
        self.assertEqual('[Included]', tmp_obj.summary_data(inc_desc=False))

    def test_short_name_prefix(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        self.assertEqual('[I] test_name', tmp_obj.short_name())

    def test_short_name_no_prefix(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        self.assertEqual('my_test_name', tmp_obj.short_name(inc_status_prefix=False))

    def test_long_name(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc', _should_skip=True)
        self.assertEqual('test_name [Skipped] (test_desc)', tmp_obj.long_name())
        self.assertEqual('test_name [Skipped]', tmp_obj.long_name(inc_desc=False))
        self.assertEqual('[S] test_name [Skipped]', tmp_obj.long_name(inc_desc=False, inc_status_prefix=True))

    def test_dump_w_summary(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc', passed=1, failed=2, raised=0, run=1, skipped=1)
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'test_desc')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)
        exp_ret = 'test_name_2 : [Not Matched]\n' \
                  'test_name_3 : [Not Matched]'

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_w_summary_empty(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')

        exp_ret = ''

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_no_summary(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_obj.dump_inc_summary = False
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_dest_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name_2\n' \
                  'test_name_3'

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_no_summary_empty(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_obj.dump_inc_summary = False

        exp_ret = ''

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_analysis(self):
        tests = [
            (dict(passed=None, failed=None, raised=None, run=False, skipped=False), 'Not Tried'),
            (dict(passed=None, failed=None, raised=None, run=True, skipped=False), 'Run'),
            (dict(passed=None, failed=None, raised=None, run=False, skipped=True), 'Skipped'),
            (dict(passed=True, failed=False, raised=False, run=True, skipped=False), 'Passed'),
            (dict(passed=False, failed=True, raised=False, run=True, skipped=False), 'Failed'),
            (dict(passed=False, failed=False, raised=True, run=True, skipped=False), 'Raised'),
        ]
        for test_args, analysis in tests:
            with self.subTest(analysis):    
                tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc', **test_args)
                self.assertEqual(analysis, tmp_obj.status())

    def test_details(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name [Matched 2 times] (test_desc)'

        self.assertEqual(exp_ret, tmp_obj.details())

    def test_details_w_dump(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Matched 2 times\n' \
                  '  Analysis      : All Matched Tests\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0\n' \
                  '  Tests         : test_name_2 : [Not Matched]\n' \
                  '                  test_name_3 : [Not Matched]'

        self.assertEqual(exp_ret, tmp_obj.details(dump=True))

    def test_details_no_status(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)'

        self.assertEqual(exp_ret, tmp_obj.details(inc_status=False))

    def test_details_w_analysis(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Analysis      : All Matched Tests\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(inc_analysis=True, inc_stats=True))

    def test_details_w_stats(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(inc_stats=True, inc_status=False))

    def test_details_indent(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = '  test_name (test_desc)\n' \
                  '    Analysis      : All Matched Tests\n' \
                  '    Matched Tests : 2\n' \
                  '    Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(indent=2, inc_analysis=True, inc_stats=True))

class TestTestFlaggerFlagObj(unittest.TestCase):

    def test_base(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=2)
        self.assertEqual('test_name', tmp_obj.name)
        self.assertEqual(2, tmp_obj.passed)

    def test_eq(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('test_name', tmp_obj)
        self.assertNotEqual('test_name_is_me', tmp_obj)
        self.assertNotEqual('foobar test_name', tmp_obj)

    def test_str(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('test_name', str(tmp_obj))

    def test_match_any_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=2, run=2, found=3)

        self.assertTrue(tmp_obj.match('any_passed'))
        self.assertTrue(tmp_obj.match('inc_passed'))
        self.assertFalse(tmp_obj.match('any_failed'))

    def test_match_all_pfr_yes_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=0, raised=0, run=1,
                                     skipped=1)

        self.assertTrue(tmp_obj.match('all_passed'))
        self.assertFalse(tmp_obj.match('all_failed'))

    def test_match_all_pfr_no_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=0,
                                     skipped=0)

        self.assertFalse(tmp_obj.match('all_passed'))
        self.assertFalse(tmp_obj.match('all_failed'))

    def test_match_all_rs_yes_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=0, raised=0, run=0,
                                     skipped=1)

        self.assertTrue(tmp_obj.match('all_skipped'))
        self.assertFalse(tmp_obj.match('all_run'))

    def test_match_all_rs_no_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=0,
                                     skipped=0)

        self.assertFalse(tmp_obj.match('all_skipped'))
        self.assertFalse(tmp_obj.match('all_run'))

    def test_match_all_rs_no_metric_2(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=1,
                                     skipped=1)

        self.assertFalse(tmp_obj.match('all_skipped'))
        self.assertFalse(tmp_obj.match('all_run'))

    def test_match_no_good_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=1,
                                     skipped=1)

        self.assertTrue(tmp_obj.match('no_raised'))
        self.assertFalse(tmp_obj.match('no_run'))
        self.assertFalse(tmp_obj.match('no_passed'))
        self.assertFalse(tmp_obj.match('no_skipped'))

    def test_match_inc_ref_item(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_obj.referenced_obj.append('foobar2')
        tmp_obj.referenced_obj.append('snafu2')
        self.assertTrue(tmp_obj.match(inc_tests=['foobar2', 'snafu2']))
        self.assertTrue(tmp_obj.match(inc_tests='foobar2'))
        self.assertFalse(tmp_obj.match(inc_tests='not there'))

    def test_set_result(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=1,
                                     skipped=1)
        self.assertEqual(2, tmp_obj.failed)
        tmp_obj.set_result(failed=True, exc_reason='foobar')
        self.assertEqual(3, tmp_obj.failed)
        self.assertEqual(1, len(tmp_obj.fail_reasons))
        tmp_obj.set_result(failed=True, exc_reason='foobar')
        self.assertEqual(4, tmp_obj.failed)
        self.assertEqual(1, len(tmp_obj.fail_reasons))

    def test_stats_dict(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=1,
                                     skipped=1)
        exp_ret = {'Run': 1,
                   'Passed': 1,
                   'Failed': 2,
                   'Raised': 0,
                   'Skipped': 1,
                   'Skipped(self)': 0,
                   'Skipped(other)': 0
                   }
        self.assertEqual(exp_ret, tmp_obj.stats_dict())

        exp_ret = {'run': 1,
                   'passed': 1,
                   'failed': 2,
                   'raised': 0,
                   'skipped': 1,
                   'self_skipped': 0,
                   'other_skipped': 0
                   }
        self.assertEqual(exp_ret, tmp_obj.stats_dict(full_field_names=False))

    def test_summary_data(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('[Included] (test_desc)', tmp_obj.summary_data())
        self.assertEqual('[Included]', tmp_obj.summary_data(inc_desc=False))

    def test_short_name_prefix(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('[I] test_name', tmp_obj.short_name())

    def test_short_name_no_prefix(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('test_name', tmp_obj.short_name(inc_status_prefix=False))

    def test_long_name(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', _should_skip=True)
        self.assertEqual('test_name [Skipped] (test_desc)', tmp_obj.long_name())
        self.assertEqual('test_name [Skipped]', tmp_obj.long_name(inc_desc=False))
        self.assertEqual('[S] test_name [Skipped]', tmp_obj.long_name(inc_desc=False, inc_status_prefix=True))

    def test_dump_w_summary(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=1,
                                     skipped=1)
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'test_desc')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)
        exp_ret = 'test_name_2 : [Not Matched]\n' \
                  'test_name_3 : [Not Matched]'

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_w_summary_empty(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')

        exp_ret = ''

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_no_summary(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_obj.dump_inc_summary = False
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_dest_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name_2\n' \
                  'test_name_3'

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_no_summary_empty(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_obj.dump_inc_summary = False

        exp_ret = ''

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_analysis(self):
        tests = [
            (dict(passed=0, failed=0, raised=0, run=0, skipped=0, found=0), 'Not Found'),

            (dict(passed=0, failed=0, raised=0, run=2, skipped=2, found=4), 'Some Skipped, No PF Info'),
            (dict(passed=0, failed=0, raised=0, run=2, skipped=0, found=2), 'All Run, No PF Info'),
            (dict(passed=0, failed=0, raised=0, run=0, skipped=2, found=2), 'All Skipped, No PF Info'),

            (dict(passed=1, failed=0, raised=0, run=2, skipped=2, found=4), 'Some Skipped, All Passed'),
            (dict(passed=1, failed=0, raised=0, run=2, skipped=0, found=2), 'All Run, All Passed'),
            (dict(passed=1, failed=0, raised=0, run=0, skipped=2, found=2), 'All Skipped, All Passed'),

            (dict(passed=0, failed=1, raised=0, run=2, skipped=2, found=4), 'Some Skipped, All Failed'),
            (dict(passed=0, failed=1, raised=0, run=2, skipped=0, found=2), 'All Run, All Failed'),
            (dict(passed=0, failed=1, raised=0, run=0, skipped=2, found=2), 'All Skipped, All Failed'),

            (dict(passed=0, failed=0, raised=1, run=2, skipped=2, found=4), 'Some Skipped, All Raised'),
            (dict(passed=0, failed=0, raised=1, run=2, skipped=0, found=2), 'All Run, All Raised'),
            (dict(passed=0, failed=0, raised=1, run=0, skipped=2, found=2), 'All Skipped, All Raised'),

            (dict(passed=0, failed=1, raised=1, run=2, skipped=2, found=4), 'Some Skipped, All Failed or Raised'),
            (dict(passed=0, failed=1, raised=1, run=2, skipped=0, found=2), 'All Run, All Failed or Raised'),
            (dict(passed=0, failed=1, raised=1, run=0, skipped=2, found=2), 'All Skipped, All Failed or Raised'),

            (dict(passed=1, failed=0, raised=1, run=2, skipped=2, found=4), 'Some Skipped, All Passed or Raised'),
            (dict(passed=1, failed=0, raised=1, run=2, skipped=0, found=2), 'All Run, All Passed or Raised'),
            (dict(passed=1, failed=0, raised=1, run=0, skipped=2, found=2), 'All Skipped, All Passed or Raised'),

            (dict(passed=1, failed=1, raised=0, run=2, skipped=2, found=4), 'Some Skipped, All Passed or Failed'),
            (dict(passed=1, failed=1, raised=0, run=2, skipped=0, found=2), 'All Run, All Passed or Failed'),
            (dict(passed=1, failed=1, raised=0, run=0, skipped=2, found=2), 'All Skipped, All Passed or Failed'),

            (dict(passed=1, failed=1, raised=1, run=2, skipped=2, found=4),
             'Some Skipped, All Passed, Failed, or Raised'),
            (dict(passed=1, failed=1, raised=1, run=2, skipped=0, found=2), 'All Run, All Passed, Failed, or Raised'),
            (dict(passed=1, failed=1, raised=1, run=0, skipped=2, found=2),
             'All Skipped, All Passed, Failed, or Raised'),
        ]
        for test_args, analysis in tests:
            with self.subTest(analysis):
                tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', **test_args)
                self.assertEqual(analysis, tmp_obj._analysis())

    def test_details(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name [Matched 2 times] (test_desc)'

        self.assertEqual(exp_ret, tmp_obj.details())

    def test_details_w_dump(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Matched 2 times\n' \
                  '  Analysis      : All Matched Tests\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0\n' \
                  '  Tests         : test_name_2 : [Not Matched]\n' \
                  '                  test_name_3 : [Not Matched]'

        self.assertEqual(exp_ret, tmp_obj.details(dump=True))

    def test_details_no_status(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)'

        self.assertEqual(exp_ret, tmp_obj.details(inc_status=False))

    def test_details_w_analysis(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Analysis      : All Matched Tests\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(inc_analysis=True, inc_stats=True))

    def test_details_w_stats(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(inc_stats=True, inc_status=False))

    def test_details_indent(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = '  test_name (test_desc)\n' \
                  '    Analysis      : All Matched Tests\n' \
                  '    Matched Tests : 2\n' \
                  '    Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(indent=2, inc_analysis=True, inc_stats=True))


s_os = TestFlaggerTestSkipOS
s_mod = TestFlaggerTestSkipModule
s_py = TestFlaggerTestSkipPyVer
s_tst = TestFlaggerTestSkipTestRun
s_flg = TestFlaggerTestSkipFlag
s_pla = TestFlaggerTestSkipPlatform
s_env = TestFlaggerTestSkipEnvironBase


class TestFlaggerSkipActiveObjects(unittest.TestCase):

    def test_common_skips(self):

        os_name = os.name
        pyv = platform.python_version()

        platform_ = platform.platform()
        platform_terse = platform.platform(terse=True)
        platform_aliased = platform.platform(aliased=True)
        processor = platform.processor()
        machine = platform.machine()
        node = platform.node()
        python_compiler = platform.python_compiler()
        python_implementation = platform.python_implementation()
        python_branch = platform.python_branch()
        release = platform.release()
        version = platform.version()
        env_var = 'windir'
        env_value = os.environ[env_var]

        print(repr(os_name))
        print(repr(platform_))
        print(repr(platform_terse))
        print(repr(platform_aliased))
        print(repr(processor))
        print(repr(machine))
        print(repr(node))
        print(repr(python_compiler))
        print(repr(python_implementation))
        print(repr(python_branch))
        print(repr(release))
        print(repr(version))

        tests = [
            {'obj': s_os,
             'is': {True: [(os_name, 'Skip this test if the OS is {is_not}' + os_name)],
                    False: [('foobar', 'Skip this test if the OS is {is_not}foobar')]},
             },
            {'obj': s_mod,
             'is': {True: [('unittest', 'Skip this test if the module unittest was {is_not}loaded')],
                    False: [('foobar', 'Skip this test if the module foobar was {is_not}loaded')]},
             },
            {'obj': s_env,
             'is': {True: [(env_var + '_' + env_value, 'Skip this test if the environment var %s is %s' % (env_var, env_value))],
                    False: [(env_var + '_foobar', 'Skip this test if the environment var %s is foobar' % env_var)]},
             },
            {'obj': s_py,
             'is': {True: [
                        (pyv, 'Skip this test if the Python Version does {is_not}==' + pyv),
                        (pyv + '+', 'Skip this test if the Python Version does {is_not}>=' + pyv),
                        (pyv + '-', 'Skip this test if the Python Version does {is_not}<=' + pyv),
                        ('1.0+', 'Skip this test if the Python Version does {is_not}>= 1.0'),
                        ('10-', 'Skip this test if the Python Version does {is_not}<= 10'),
                    ],
                    False: [
                        ('foobar', 'Skip this test if the Python Version does {is_not}== foobar'),
                        ('10.0', 'Skip this test if the Python Version does {is_not}== 10.0'),
                        ('1.0', 'Skip this test if the Python Version does {is_not}== 1.0'),
                        ('1.0-', 'Skip this test if the Python Version does {is_not}<= 1.0'),
                        ('10+', 'Skip this test if the Python Version does {is_not}>= 10'),
                    ],
             }},
            {'obj': s_pla,
             'is': {True: [
                        ('platform_' + platform_, 'Skip this test if the platform.%s() is {is_not}%s' % ('platform', platform)),
                        ('platform_terse_' + platform_terse, 'Skip this test if the platform.%s() is {is_not}%s' % ('platform_terse', platform_terse)),
                        ('platform_aliased_' + platform_aliased, 'Skip this test if the platform.%s() is {is_not}%s' % ('platform_aliased', platform_aliased)),
                        ('processor_' + processor, 'Skip this test if the platform.%s() is {is_not}%s' % ('processor', processor)),
                        ('machine_' + machine, 'Skip this test if the platform.%s() is {is_not}%s' % ('machine', machine)),
                        ('node_' + node, 'Skip this test if the platform.%s() is {is_not}%s' % ('node', node)),
                        ('python_compiler_' + python_compiler, 'Skip this test if the platform.%s() is {is_not}%s' % ('python_compiler', python_compiler)),
                        ('python_implementation_' + python_implementation, 'Skip this test if the platform.%s() is {is_not}%s' % ('python_implementation', python_implementation)),
                        ('python_branch_' + python_branch, 'Skip this test if the platform.%s() is {is_not}%s' % ('python_branch', python_branch)),
                        ('version_' + version, 'Skip this test if the platform.%s() is {is_not}%s' % ('version', version)),
                        ('release_' + release, 'Skip this test if the platform.%s() is {is_not}%s' % ('release', release)),
             ],
                    False: [
                        ('platform_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('platform', 'foobar')),
                        ('platform_terse_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('platform_terse', 'foobar')),
                        ('platform_aliased_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('platform_aliased', 'foobar')),
                        ('processor_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('processor', 'foobar')),
                        ('machine_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('machine', 'foobar')),
                        ('node_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('node', 'foobar')),
                        ('python_compiler_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('python_compiler', 'foobar')),
                        ('python_implementation_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('python_implementation', 'foobar')),
                        ('python_branch_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('python_branch', 'foobar')),
                        ('version_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('version', 'foobar')),
                        ('release_foobar', 'Skip this test if the platform.%s() is {is_not}%s' % ('release', 'foobar')),
                    ]
             },
             },

        ]


        def test_item(obj_in, local_is_not, tf, tf_list):
            for rem_str, desc in tf_list:
                match_str = 'skip_if_%s_%s_%s' % (local_is_not, obj_in.skip_name, rem_str)
                with self.subTest(match_str):
                    tmp_obj = obj_in(flagger_fixture, match_str)
                    if tf:
                        self.assertTrue(tmp_obj.should_skip())
                    else:
                        self.assertFalse(tmp_obj.should_skip())
                    self.assertEqual(desc, tmp_obj.desc)
                    with self.assertRaises(AttributeError):
                        tmp_obj = obj_in(flagger_fixture, 'foobar')

        for test_obj_set in tests:
            test_obj = test_obj_set['obj']
            test_is = test_obj_set['is']
            if 'not' in test_obj_set:
                test_not = test_obj_set['not']
            else:
                test_not = {
                    True: test_is[False],
                    False: test_is[True]
                }
            test_item(test_obj, 'is', True, test_is[True])
            test_item(test_obj, 'is', False, test_is[False])

            test_item(test_obj, 'not', True, test_not[True])
            test_item(test_obj, 'not', False, test_not[False])


