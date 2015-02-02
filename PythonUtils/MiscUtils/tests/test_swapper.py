__author__ = 'dstrohl'

import unittest
from PythonUtils.MiscUtils.swapper import swap


class MyTestCase(unittest.TestCase):
    def test_swap(self):
        self.assertEqual(swap(True), False)

    def test_swap_rev(self):
        self.assertEqual(swap(False), True)

    def test_swap_str(self):
        self.assertEqual(swap('yes', 'yes', 'no'), 'no')

    def test_swap_err(self):
        with self.assertRaises(AttributeError):
            swap('yes')

if __name__ == '__main__':
    unittest.main()
