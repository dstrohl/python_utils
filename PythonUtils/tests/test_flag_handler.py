__author__ = 'dstrohl'

from unittest import TestCase
from PythonUtils.IndentedPrint.flag_manager import Flagger


class TestFlagger(TestCase):

    def setUp(self):
        self.fl = Flagger()

    def test_inc_mt(self):
        check = self.fl('f1')
        self.assertEqual(check, True)

    def test_cur_in_inc(self):
        self.fl(include='f2')
        self.fl('f2')
        self.assertEqual(self.fl(), True)

    def test_cur_nin_inc(self):
        self.fl(include='f2')
        self.fl('f1')
        self.assertEqual(self.fl(), False)

    def test_cur_in_exc(self):
        self.fl(exclude='f2')
        self.fl('f2')
        check = self.fl()
        self.assertEqual(check, False)

    def test_cur_nin_exc(self):
        self.fl(exclude='f2')
        check = self.fl('f1')
        self.assertEqual(check, True)

    def test_cur_in_inc_and_exc(self):
        self.fl(include='f2')
        self.fl(exclude='f2')
        check = self.fl('f2')
        self.assertEqual(check, False)

    def test_mt_cur_inc(self):
        self.fl(include='f2')
        check = self.fl()
        self.assertEqual(check, False)

    def test_add_with_plus(self):
        self.fl(include='f2')
        check = self.fl('+f2')
        self.assertEqual(check, True)

    def test_rem_with_minus(self):
        self.fl(exclude='f2, f3, f4')
        self.fl(exclude='-f2, -f3')
        check = self.fl('f1')
        self.assertEqual(check, True)

        self.assertEqual(len(self.fl.exc), 1)