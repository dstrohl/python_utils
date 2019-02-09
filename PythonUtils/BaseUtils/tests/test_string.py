#!/usr/bin/env python

from unittest import TestCase
from PythonUtils.BaseUtils import convert_to_boolean, spinner_char, index_of_count, get_before, get_after, get_between, \
    replace_between, ellipse_trim


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
