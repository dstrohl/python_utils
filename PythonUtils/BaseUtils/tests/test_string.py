#!/usr/bin/env python

from unittest import TestCase

from PythonUtils.BaseUtils import convert_to_boolean, spinner_char, index_of_count, get_before, get_after, get_between, \
    replace_between, ellipse_trim, indent_str, format_key_value, StringList
from PythonUtils.BaseUtils.string_utils import NumberFormatHelper, FORMAT_RETURN_STYLE
from decimal import Decimal
from textwrap import dedent, indent
from enum import Flag, auto


class CFB_Test(object):
    def __bool__(self):
        return True


class CFB_No_Bool_Test(object):
    pass


class ConvertToBooleanTests(TestCase):

    def test_from_string(self):
        self.assertEqual(convert_to_boolean('true'), True)
        self.assertEqual(convert_to_boolean('True'), True)
        self.assertEqual(convert_to_boolean('Yes'), True)
        self.assertEqual(convert_to_boolean('No'), False)
        self.assertEqual(convert_to_boolean('+'), True)
        self.assertEqual(convert_to_boolean('-'), False)
        self.assertEqual(convert_to_boolean('OK'), True)

    def test_fail_from_string(self):
        with self.assertRaises(TypeError):
            convert_to_boolean('test')

    def test_from_boolean(self):
        self.assertEqual(convert_to_boolean(False), False)
        self.assertEqual(convert_to_boolean(True), True)

    def test_from_obj(self):
        bo = CFB_Test()
        self.assertEqual(convert_to_boolean(bo), True)

    def test_fail_from_obj(self):
        nbo = CFB_No_Bool_Test()
        with self.assertRaises(TypeError):
            convert_to_boolean(nbo)

    def test_from_int(self):
        self.assertEqual(convert_to_boolean(0), False)
        self.assertEqual(convert_to_boolean(1), True)

        with self.assertRaises(TypeError):
            convert_to_boolean(12)

    def test_from_float(self):
        self.assertEqual(convert_to_boolean(0.0), False)
        self.assertEqual(convert_to_boolean(1.0), True)

        with self.assertRaises(TypeError):
            convert_to_boolean(1.1)


class TestSpinner(TestCase):
    def test_spinner_normal(self):
        self.assertEqual('|', spinner_char(0))
        self.assertEqual('/', spinner_char(1))
        self.assertEqual('-', spinner_char(2))
        self.assertEqual('\\', spinner_char(3))
        self.assertEqual('|', spinner_char(4))
        self.assertEqual('/', spinner_char(5))
        self.assertEqual('-', spinner_char(6))
        self.assertEqual('\\', spinner_char(7))
        self.assertEqual('|', spinner_char(8))

    def test_states(self):
        self.assertEqual(' ', spinner_char(0, not_started_state=1, finished_state=6))
        self.assertEqual(' ', spinner_char(1, not_started_state=1, finished_state=6))
        self.assertEqual('-', spinner_char(2, not_started_state=1, finished_state=6))
        self.assertEqual('\\', spinner_char(3, not_started_state=1, finished_state=6))
        self.assertEqual('|', spinner_char(4, not_started_state=1, finished_state=6))
        self.assertEqual('/', spinner_char(5, not_started_state=1, finished_state=6))
        self.assertEqual('x', spinner_char(6, not_started_state=1, finished_state=6))
        self.assertEqual('x', spinner_char(7, not_started_state=1, finished_state=6))
        self.assertEqual('x', spinner_char(8, not_started_state=1, finished_state=6))


class TestTextUtils(TestCase):

    def test_index_of_count(self):
        test_string = 'This {is} a test {is} string'
        test_response = index_of_count(test_string, '{')
        self.assertEqual(5, test_response)

        test_response = index_of_count(test_string, '}', offset_count=2)
        self.assertEqual(20, test_response)

    def test_get_before(self):
        test_string = 'This** is** a test string'
        test_response = get_before(test_string, '**')
        self.assertEqual('This', test_response)

        test_string = 'This** is** a This test string'
        test_response = get_before(test_string, '**', 2)
        self.assertEqual('This** is', test_response)

    def test_get_after(self):
        test_string = 'This {is} a test (string This is a test string This is a test) string'
        test_response = get_after(test_string, ')')

        self.assertEqual(' string', test_response)

        test_response = get_after(test_string, ' test', 3)

        self.assertEqual(') string', test_response)

        test_response = get_after(test_string, 'a')

        self.assertEqual(' test (string This is a test string This is a test) string', test_response)

    def test_get_between(self):
        test_string = 'This {is} a test {string This is a test string This is a test} string'
        test_response = get_between(test_string, '{', '}')
        self.assertEqual('is', test_response)

    def test_replace_between_01(self):
        test_string = '...|{..}|....|'
        resp_string = replace_between(test_string, '{', '}', '++++')
        self.assertEqual('...|++++|....|', resp_string)

    def test_replace_between_02(self):
        test_string = '...|{..}|....|....|{..}|....|'
        resp_string = replace_between(test_string, '{', '}', '++++')
        self.assertEqual('...|++++|....|....|++++|....|', resp_string)

    def test_replace_between_03(self):
        test_string = '...|{...|....|'
        resp_string = replace_between(test_string, '{', '}', '++++')
        self.assertEqual('...|{...|....|', resp_string)

    def test_replace_between_04(self):
        test_string = '...|}..{|....|'
        resp_string = replace_between(test_string, '{', '}', '++++')
        self.assertEqual('...|}..{|....|', resp_string)

    def test_replace_between_05(self):
        test_string = '...|{..}|....|....|{..}|....|'
        resp_string = replace_between(test_string, '{', '}', '++++', count=1)
        self.assertEqual('...|++++|....|....|{..}|....|', resp_string)

    def test_replace_between_06(self):
        test_string = '...|{..}|....|....|{..}|....|....|{..}|....|'
        resp_string = replace_between(test_string, '{', '}', '++++', count=1, offset_count=2)
        self.assertEqual('...|{..}|....|....|++++|....|....|{..}|....|', resp_string)

    def test_replace_between_07(self):
        test_string = '...|{..}|....|....|{..}|....|'
        resp_string = replace_between(test_string, '{', '}', '++++', count=1, keep_keys=True)
        self.assertEqual('...|{++++}|....|....|{..}|....|', resp_string)


class TrimTests(TestCase):
    def test_elipse_trim_basic(self):
        instr = '1234567890'
        outstr = ellipse_trim(instr, 8)
        self.assertEqual('12345...', outstr)

    def test_elipse_trim_in_between_trim(self):
        instr = '1234567890'
        outstr = ellipse_trim(instr, 9)
        self.assertEqual('123456...', outstr)

    def test_elipse_trim_exact(self):
        instr = '1234567890'
        outstr = ellipse_trim(instr, 10)
        self.assertEqual('1234567890', outstr)

    def test_elipse_trim_too_long(self):
        instr = '1234567890'
        outstr = ellipse_trim(instr, 20)
        self.assertEqual('1234567890', outstr)


class TestIndentStr(TestCase):
    def test_indent_str(self):
        test_in = 'this is a test'
        test_ret = indent_str(test_in)
        exp_ret = '    this is a test'
        self.assertEqual(exp_ret, test_ret)

    def test_indent_str_first_line(self):
        test_in = 'this\nis\na\ntest'
        test_ret = indent_str(test_in, first_line=0)
        exp_ret = 'this\n    is\n    a\n    test'
        self.assertEqual(exp_ret, test_ret)


class TestNumberFormatHelper(TestCase):

    def test_nfh(self):
        tests = [
            # (val, dp, has_n, int_len, int_val, dec_len, dec_val,
            #   (get_max_int, get_max_dec, with_neg, ret_val)
            # )
            (10, 0, False, 2, '10', 0, '',
              [(4, 0, False, '  10'),
               (4, 3, False, '  10.000'),
               (1, 2, False, '10.00'),]
             ),

            (-121, 2, True, 4, '-121', 2, '00',
             [(4, 2, True, '-121.00'),
              (6, 3, True, '  -121.000'),
              (1, 2, True, '-121.00'), ]
             ),

            (121, -2, False, 3, '121', 0, '',
             [(4, 0, False, ' 121'),
              (6, 3, True, '   121.000'),
              (1, 2, False, '121.00'), ]
             ),

            (1210.1020123, 4, False, 5, '1,210', 4, '1020',
             [(4, 4, True, '1,210.1020'),
              (6, 0, True, ' 1,210'),
              (1, 6, False, '1,210.102000'), ]
             ),
            (-121.1, -2, True, 4, '-121', 1, '1',
             [(4, 0, False, '-121'),
              (6, 3, True, '  -121.100'),
              (1, 2, False, '-121.10'), ]
             ),
            (-121.1, 0, True, 4, '-121', 0, '',
             [(4, 0, False, '-121'),
              (6, 3, True, '  -121.000'),
              (1, 2, False, '-121.00'), ]
             ),

            (Decimal(1210.1020123), 4, False, 5, '1,210', 4, '1020',
             [(4, 4, True, '1,210.1020'),
              (6, 0, True, ' 1,210'),
              (1, 4, False, '1,210.1020'), ]
             ),
            (Decimal(-121.1), -2, True, 4, '-121', 1, '1',
             [(4, 0, False, '-121'),
              (6, 3, True, '  -121.100'),
              (1, 2, False, '-121.10'), ]
             ),
            (Decimal(-121.1), 0, True, 4, '-121', 0, '',
             [(4, 0, False, '-121'),
              (6, 3, True, '  -121.000'),
              (1, 2, False, '-121.00'), ]
             ),

        ]
        l1 = 0
        l2 = 0
        for value, decimal_places, has_neg, int_len, int_val, dec_len, dec_val, get_vals in tests:
            l1 += 1
            l2 = 0
            for max_int, max_dec, max_neg, exp_output in get_vals:
                l2 += 1
                with self.subTest('%s:%s' % (l1, l2)):
                    nh = NumberFormatHelper(value, decimal_places=decimal_places)
                    self.assertEqual(has_neg, nh.has_neg)
                    self.assertEqual(int_val, nh.int_value)
                    self.assertEqual(int_len, nh.my_int_len)
                    self.assertEqual(dec_val, nh.dec_value)
                    self.assertEqual(dec_len, nh.my_dec_len)
                    self.assertEqual(exp_output, nh.get(max_dec=max_dec, max_int=max_int))


class FixFormatTest(object):
    def __repr__(self):
        return 'FixFormatTest'

    def __float__(self):
        return 123.1

    def __int__(self):
        return 321


class FixFormatTestNoFloat(object):
    def __repr__(self):
        return 'FixFormatTest'

    def __int__(self):
        return 12


class TestFormatKeyValue(TestCase):
    def setUp(self):
        self.dec_data = Decimal(3456.3)
        self.test_data = {
            'foobar_str': 'this is a string',
            'foo_long_str': 'this is a long str\nwith\nmultiple lines',
            'f_dict': {'snafu': 1, 'rofl': 'value_test', 't_list': [1, 2, 3]},
            'foobar_list': ['a', 'b', 'c'],
            'foob_int': 123,
            'foob_float': 123456.12,
            'foob_dec': self.dec_data,
            'foob_fix': FixFormatTest(),
            'foob_fix_nf': FixFormatTestNoFloat(),
        }
        self.dec_str = str(self.dec_data)
        self.dec_repr = repr(self.dec_data)
        self.foo_long_str = 'this is a long str\nwith\nmultiple lines'

    def test_key_value_base(self):
        act_ret = format_key_value(self.test_data)
        exp_ret = '''
        foobar_str   : this is a string
        foo_long_str : this is a long str
                       with
                       multiple lines
        f_dict       : {
                           "snafu": 1,
                           "rofl": "value_test",
                           "t_list": [
                               1,
                               2,
                               3
                           ]
                       }
        foobar_list  : [
                           "a",
                           "b",
                           "c"
                       ]
        foob_int     :     123.00
        foob_float   : 123,456.12
        foob_dec     :   3,456.30
        foob_fix     : FixFormatTest
        foob_fix_nf  : FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_iter_input(self):
        tmp_test = list(self.test_data.items())
        act_ret = format_key_value(tmp_test)
        exp_ret = '''
        foobar_str   : this is a string
        foo_long_str : this is a long str
                       with
                       multiple lines
        f_dict       : {
                           "snafu": 1,
                           "rofl": "value_test",
                           "t_list": [
                               1,
                               2,
                               3
                           ]
                       }
        foobar_list  : [
                           "a",
                           "b",
                           "c"
                       ]
        foob_int     :     123.00
        foob_float   : 123,456.12
        foob_dec     :   3,456.30
        foob_fix     : FixFormatTest
        foob_fix_nf  : FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_left_trimmed(self):
        act_ret = format_key_value(self.test_data, key_format='left_trimmed')
        exp_ret = '''
        foobar_str : this is a string
        foo_long_str : this is a long str
                       with
                       multiple lines
        f_dict : {
                     "snafu": 1,
                     "rofl": "value_test",
                     "t_list": [
                         1,
                         2,
                         3
                     ]
                 }
        foobar_list : [
                          "a",
                          "b",
                          "c"
                      ]
        foob_int : 123.00
        foob_float : 123,456.12
        foob_dec : 3,456.30
        foob_fix : FixFormatTest
        foob_fix_nf : FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_right(self):
        act_ret = format_key_value(self.test_data, key_format='right')
        exp_ret = '''
          foobar_str : this is a string
        foo_long_str : this is a long str
                       with
                       multiple lines
              f_dict : {
                           "snafu": 1,
                           "rofl": "value_test",
                           "t_list": [
                               1,
                               2,
                               3
                           ]
                       }
         foobar_list : [
                           "a",
                           "b",
                           "c"
                       ]
            foob_int :     123.00
          foob_float : 123,456.12
            foob_dec :   3,456.30
            foob_fix : FixFormatTest
         foob_fix_nf : FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_dp_neg_3(self):
        act_ret = format_key_value(self.test_data, decimal_places=-3)
        exp_ret = '''
        foobar_str   : this is a string
        foo_long_str : this is a long str
                       with
                       multiple lines
        f_dict       : {
                           "snafu": 1,
                           "rofl": "value_test",
                           "t_list": [
                               1,
                               2,
                               3
                           ]
                       }
        foobar_list  : [
                           "a",
                           "b",
                           "c"
                       ]
        foob_int     :     123.00
        foob_float   : 123,456.12
        foob_dec     :   3,456.30
        foob_fix     : FixFormatTest
        foob_fix_nf  : FixFormatTest
       '''
        exp_ret = dedent(exp_ret)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_dp_pos_4(self):
        act_ret = format_key_value(self.test_data, decimal_places=4)
        exp_ret = '''
        foobar_str   : this is a string
        foo_long_str : this is a long str
                       with
                       multiple lines
        f_dict       : {
                           "snafu": 1,
                           "rofl": "value_test",
                           "t_list": [
                               1,
                               2,
                               3
                           ]
                       }
        foobar_list  : [
                           "a",
                           "b",
                           "c"
                       ]
        foob_int     :     123.0000
        foob_float   : 123,456.1200
        foob_dec     :   3,456.3000
        foob_fix     : FixFormatTest
        foob_fix_nf  : FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_dp_zero(self):
        act_ret = format_key_value(self.test_data, decimal_places=0)
        exp_ret = '''
        foobar_str   : this is a string
        foo_long_str : this is a long str
                       with
                       multiple lines
        f_dict       : {
                           "snafu": 1,
                           "rofl": "value_test",
                           "t_list": [
                               1,
                               2,
                               3
                           ]
                       }
        foobar_list  : [
                           "a",
                           "b",
                           "c"
                       ]
        foob_int     :     123
        foob_float   : 123,456
        foob_dec     :   3,456
        foob_fix     : FixFormatTest
        foob_fix_nf  : FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_repr(self):
        act_ret = format_key_value(self.test_data, value_format='repr')
        exp_ret = '''
        foobar_str   : 'this is a string'
        foo_long_str : %r
        f_dict       : {'snafu': 1, 'rofl': 'value_test', 't_list': [1, 2, 3]}
        foobar_list  : ['a', 'b', 'c']
        foob_int     : 123
        foob_float   : 123456.12
        foob_dec     : %s
        foob_fix     : FixFormatTest
        foob_fix_nf  : FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        exp_ret = exp_ret % (self.foo_long_str, self.dec_repr)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_vk_kf_pp(self):
        act_ret = format_key_value(self.test_data, value_format='pprint')
        exp_ret = '''
        foobar_str   : 'this is a string'
        foo_long_str : %r
        f_dict       : {'rofl': 'value_test', 'snafu': 1, 't_list': [1, 2, 3]}
        foobar_list  : ['a', 'b', 'c']
        foob_int     : 123
        foob_float   : 123456.12
        foob_dec     : %s
        foob_fix     : FixFormatTest
        foob_fix_nf  : FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        exp_ret = exp_ret % (self.foo_long_str, self.dec_repr)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_json(self):
        tmp_data = self.test_data.copy()
        del tmp_data['foob_dec']
        del tmp_data['foob_fix']
        del tmp_data['foob_fix_nf']
        act_ret = format_key_value(tmp_data, value_format='json')
        exp_ret = '''
        foobar_str   : "this is a string"
        foo_long_str : %r
        f_dict       : {
                           "snafu": 1,
                           "rofl": "value_test",
                           "t_list": [
                               1,
                               2,
                               3
                           ]
                       }
        foobar_list  : [
                           "a",
                           "b",
                           "c"
                       ]
        foob_int     : 123
        foob_float   : 123456.12
        '''
        exp_ret = dedent(exp_ret)
        act_ret = '\n' + act_ret + '\n'
        exp_ret = exp_ret % self.foo_long_str
        exp_ret = exp_ret.replace("'", '"')
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_str(self):
        tmp_data = self.test_data.copy()
        del tmp_data['f_dict']
        act_ret = format_key_value(tmp_data, value_format='str')
        exp_ret = '''
        foobar_str   : this is a string
        foo_long_str : this is a long str
                       with
                       multiple lines
        foobar_list  : ['a', 'b', 'c']
        foob_int     : 123
        foob_float   : 123456.12
        foob_dec     : %s
        foob_fix     : FixFormatTest
        foob_fix_nf  : FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        exp_ret = exp_ret % self.dec_str
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_number(self):
        tmp_data = self.test_data.copy()
        del tmp_data['foobar_str']
        del tmp_data['foo_long_str']
        del tmp_data['f_dict']
        del tmp_data['foobar_list']
        act_ret = format_key_value(tmp_data, value_format='number')
        exp_ret = '''
        foob_int    :     123.00
        foob_float  : 123,456.12
        foob_dec    :   3,456.30
        foob_fix    :     123.10
        foob_fix_nf :      12.00
        '''
        exp_ret = dedent(exp_ret)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_indent(self):
        act_ret = format_key_value(self.test_data, indent=4)
        exp_ret = '''
        foobar_str   : this is a string
        foo_long_str : this is a long str
                       with
                       multiple lines
        f_dict       : {
                           "snafu": 1,
                           "rofl": "value_test",
                           "t_list": [
                               1,
                               2,
                               3
                           ]
                       }
        foobar_list  : [
                           "a",
                           "b",
                           "c"
                       ]
        foob_int     :     123.00
        foob_float   : 123,456.12
        foob_dec     :   3,456.30
        foob_fix     : FixFormatTest
        foob_fix_nf  : FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        exp_ret = indent(exp_ret, '    ')
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_repr_as_list(self):
        act_ret = format_key_value(self.test_data, value_format='repr', return_style=FORMAT_RETURN_STYLE.LIST)
        exp_ret = [
            "foobar_str   : 'this is a string'",
            'foo_long_str : %r' % self.foo_long_str,
            "f_dict       : {'snafu': 1, 'rofl': 'value_test', 't_list': [1, 2, 3]}",
            "foobar_list  : ['a', 'b', 'c']",
            'foob_int     : 123',
            'foob_float   : 123456.12',
            "foob_dec     : %s" % self.dec_repr,
            'foob_fix     : FixFormatTest',
            'foob_fix_nf  : FixFormatTest',
        ]
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_repr_as_tuple(self):
        act_ret = format_key_value(self.test_data, value_format='repr', return_style=FORMAT_RETURN_STYLE.TUPLES)
        exp_ret = [
            ("foobar_str  ", "'this is a string'"),
            ("foo_long_str", repr(self.foo_long_str)),
            ("f_dict      ", "{'snafu': 1, 'rofl': 'value_test', 't_list': [1, 2, 3]}"),
            ("foobar_list ", "['a', 'b', 'c']"),
            ("foob_int    ", "123"),
            ("foob_float  ", "123456.12"),
            ("foob_dec    ", self.dec_repr),
            ("foob_fix    ", "FixFormatTest"),
            ("foob_fix_nf ", "FixFormatTest"),
        ]
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_repr_as_dict(self):
        act_ret = format_key_value(self.test_data, value_format='repr', return_style=FORMAT_RETURN_STYLE.DICT)
        exp_ret = {
            "foobar_str  ": "'this is a string'",
            'foo_long_str' : repr(self.foo_long_str),
            "f_dict      ": "{'snafu': 1, 'rofl': 'value_test', 't_list': [1, 2, 3]}",
            "foobar_list ": "['a', 'b', 'c']",
            'foob_int    ': '123',
            'foob_float  ': '123456.12',
            'foob_dec    ': self.dec_repr,
            'foob_fix    ': 'FixFormatTest',
            'foob_fix_nf ': 'FixFormatTest',
        }
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_none_as_dict(self):
        act_ret = format_key_value(self.test_data, value_format='none', return_style=FORMAT_RETURN_STYLE.DICT)
        exp_ret = {
            'foobar_str  ': 'this is a string',
            'foo_long_str': 'this is a long str\nwith\nmultiple lines',
            'f_dict      ': {'snafu': 1, 'rofl': 'value_test', 't_list': [1, 2, 3]},
            'foobar_list ': ['a', 'b', 'c'],
            'foob_int    ': 123,
            'foob_float  ': 123456.12,
            'foob_dec    ': self.dec_data,
            'foob_fix    ': self.test_data['foob_fix'],
            'foob_fix_nf ': self.test_data['foob_fix_nf'],
        }
        self.assertEqual(exp_ret, act_ret)

    def test_raise_on_skip_in_dict(self):
        with self.assertRaises(AttributeError):
            act_ret = format_key_value(self.test_data, value_format='skip', return_style=FORMAT_RETURN_STYLE.DICT)
        with self.assertRaises(AttributeError):
            act_ret = format_key_value(self.test_data, key_format='skip', return_style=FORMAT_RETURN_STYLE.DICT)

    def test_kv_kf_repr_as_list_skip_value(self):
        act_ret = format_key_value(self.test_data, value_format='skip', return_style=FORMAT_RETURN_STYLE.LIST)
        exp_ret = [
            "foobar_str  ",
            'foo_long_str',
            "f_dict      ",
            "foobar_list ",
            'foob_int    ',
            'foob_float  ',
            "foob_dec    ",
            "foob_fix    ",
            'foob_fix_nf ',
        ]
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_repr_as_tuple_slip_value(self):
        act_ret = format_key_value(self.test_data, value_format='skip', return_style=FORMAT_RETURN_STYLE.TUPLES)
        exp_ret = [
            ("foobar_str  ", ),
            ("foo_long_str", ),
            ("f_dict      ", ),
            ("foobar_list ", ),
            ("foob_int    ", ),
            ("foob_float  ", ),
            ("foob_dec    ", ),
            ("foob_fix    ", ),
            ("foob_fix_nf ", ),
        ]
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_repr_skip_value(self):
        act_ret = format_key_value(self.test_data, value_format='skip')
        exp_ret = '''
        foobar_str  
        foo_long_str
        f_dict      
        foobar_list 
        foob_int    
        foob_float  
        foob_dec    
        foob_fix    
        foob_fix_nf 
        '''
        exp_ret = dedent(exp_ret)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_repr_as_list_skip_key(self):
        act_ret = format_key_value(self.test_data, value_format='repr', key_format='skip', return_style=FORMAT_RETURN_STYLE.LIST)
        exp_ret = [
            "'this is a string'",
            '%r' % self.foo_long_str,
            "{'snafu': 1, 'rofl': 'value_test', 't_list': [1, 2, 3]}",
            "['a', 'b', 'c']",
            '123',
            '123456.12',
            "%s" % self.dec_repr,
            'FixFormatTest',
            'FixFormatTest',
        ]
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_repr_as_tuple_slip_key(self):
        act_ret = format_key_value(self.test_data, value_format='repr', key_format='skip', return_style=FORMAT_RETURN_STYLE.TUPLES)
        exp_ret = [
            ("'this is a string'",),
            (repr(self.foo_long_str),),
            ("{'snafu': 1, 'rofl': 'value_test', 't_list': [1, 2, 3]}",),
            ("['a', 'b', 'c']",),
            ("123",),
            ("123456.12",),
            (self.dec_repr,),
            ("FixFormatTest",),
            ("FixFormatTest",),
        ]
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_repr_skip_key(self):
        act_ret = format_key_value(self.test_data, value_format='repr', key_format='skip')
        exp_ret = '''
        'this is a string'
        %r
        {'snafu': 1, 'rofl': 'value_test', 't_list': [1, 2, 3]}
        ['a', 'b', 'c']
        123
        123456.12
        %s
        FixFormatTest
        FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        exp_ret = exp_ret % (self.foo_long_str, self.dec_repr)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))

    def test_kv_kf_repr_skip_key_diff_join(self):
        act_ret = format_key_value(self.test_data, value_format='repr', key_format='skip', join_str=',')
        exp_ret = '''
        'this is a string',%r,{'snafu': 1, 'rofl': 'value_test', 't_list': [1, 2, 3]},['a', 'b', 'c'],123,123456.12,%s,FixFormatTest,FixFormatTest
        '''
        exp_ret = dedent(exp_ret)
        exp_ret = exp_ret % (self.foo_long_str, self.dec_repr)
        act_ret = '\n' + act_ret + '\n'
        self.assertEqual(exp_ret, act_ret, repr(act_ret))


class TestStringList(TestCase):

    def test_init(self):
        sl = StringList()
        sl.extend(['test', 'foobar'])
        self.assertEqual('test|foobar', str(sl))

    def test_get_item(self):
        s1 = StringList(['1', '2', '3'])
        s1.extend(['4', '5'])
        self.assertEqual('1|2|3|4|5', s1)
        self.assertEqual('1|2|3', s1[:3])

    def test_add(self):
        s1 = StringList(['1', '2', '3'])
        s2 = s1 + ['4', '4']
        self.assertEqual('1|2|3|4|4', s2)

    def test_radd(self):
        s1 = StringList(['1', '2', '3'])
        s1 += '4'
        self.assertEqual('1|2|3|4', s1)

    def test_mul(self):
        s1 = StringList(['1', '2', '3'])
        s1 *= 2
        self.assertEqual('1|2|3|1|2|3', s1)

    def test_sub(self):
        s1 = StringList(['1', '2', '3'])
        s2 = s1 - '4'
        self.assertEqual('1|2|4', s2)

    def test_rsub(self):
        s1 = StringList(['1', '2', '3'])
        s1 -= '4'
        self.assertEqual('1|2|4', s1)

    def test_ne(self):
        s1 = StringList(['1', '2', '3'])
        self.assertNotEqual(['1', '2', '2'], s1)

    def test_eq(self):
        s1 = StringList(['1', '2', '3'])
        s2 = StringList(['1', '2', '3'])
        self.assertEqual(s2, s1)
        self.assertEqual(['1', '2', '3'], s1)
        self.assertEqual('1|2|3', s1)

