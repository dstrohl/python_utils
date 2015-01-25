__author__ = 'strohl'

import unittest
from PythonUtils.TextUtils import elipse_trim


class TrimTests(unittest.TestCase):
    def test_elipse_trim_basic(self):
        instr = '1234567890'
        outstr = elipse_trim(instr, 8)
        self.assertEqual('12345...', outstr)

    def test_elipse_trim_in_between_trim(self):
        instr = '1234567890'
        outstr = elipse_trim(instr, 9)
        self.assertEqual('123456...', outstr)

    def test_elipse_trim_exact(self):
        instr = '1234567890'
        outstr = elipse_trim(instr, 10)
        self.assertEqual('1234567890', outstr)

    def test_elipse_trim_too_long(self):
        instr = '1234567890'
        outstr = elipse_trim(instr, 20)
        self.assertEqual('1234567890', outstr)
