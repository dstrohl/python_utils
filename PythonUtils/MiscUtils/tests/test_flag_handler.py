__author__ = 'dstrohl'

from PythonUtils import Flagger

import unittest



class TestFlagger(unittest.TestCase):

    fl = Flagger()

    def test_inc_mt(self):
        check = self.fl('f1')
        self.assertEqual(check, True)


if __name__ == '__main__':
    unittest.main()
