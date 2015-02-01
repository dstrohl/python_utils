__author__ = 'dstrohl'

import unittest
from PythonUtils import Clicker


class ClickerTestCases(unittest.TestCase):

    def test_basic_operation(self):
        c = Clicker()

        self.assertEqual(c(), 1)
        self.assertEqual(c(1), 2)
        self.assertEqual(c(1), 3)
        self.assertEqual(c(-1), 2)
        self.assertEqual(c('test', 1), 1)
        self.assertEqual(c('test', 1), 2)
        self.assertEqual(c(5), 7)



if __name__ == '__main__':
    unittest.main()
