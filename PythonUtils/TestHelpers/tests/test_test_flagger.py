import unittest
from PythonUtils.TestHelpers.test_flagger import *


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
