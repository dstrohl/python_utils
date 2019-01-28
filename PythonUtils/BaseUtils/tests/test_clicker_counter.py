__author__ = 'dstrohl'

from unittest import TestCase
from PythonUtils.Clicker.clicker_counter import Clicker


class ClickerTestCases(TestCase):

    def test_basic_operation(self):
        c = Clicker()

        self.assertEqual(c(), 1)
        self.assertEqual(c(1), 2)
        self.assertEqual(c(1), 3)
        self.assertEqual(c(-1), 2)
        self.assertEqual(c('test', 1), 1)
        self.assertEqual(c('test', 1), 2)
        self.assertEqual(c(5), 7)

