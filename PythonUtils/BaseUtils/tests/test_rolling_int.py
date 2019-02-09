import unittest
from PythonUtils.BaseUtils.base_utils import RollingInt, rollover_calc, looping_iterator


class TestRollingInt(unittest.TestCase):
    
    def verify_result(self, ri, value, rollover, rollunder, roll):
        self.assertEqual(value, ri)
        self.assertEqual(rollover, ri.rollover_counter)
        self.assertEqual(rollunder, ri.rollunder_counter)
        self.assertEqual(roll, ri.roll_counter)

        
    def test_rolling_int(self):
        ri = RollingInt(10, value=5)
        self.verify_result(ri, 5, 0, 0, 0)
        ri += 1
        self.verify_result(ri, 6, 0, 0, 0)
        ri += 4
        self.verify_result(ri, 10, 0, 0, 0)
        ri += 1
        self.verify_result(ri, 0, 1, 0, 1)
        ri += 20
        self.verify_result(ri, 9, 2, 0, 2)
        ri += -5
        self.verify_result(ri, 4, 2, 0, 2)
        ri += -5
        self.verify_result(ri, 10, 2, 1, 1)
        ri += -1
        self.verify_result(ri, 9, 2, 1, 1)
        ri = ri - 5
        self.verify_result(ri, 4, 0, 0, 0)
        ri -= 1
        self.verify_result(ri, 3, 0, 0, 0)
        ri += 10
        self.verify_result(ri, 2, 1, 0, 1)

    def test_rolling_int_2(self):
        ri = RollingInt(10, 2, 5)
        self.verify_result(ri, 5, 0, 0, 0)
        ri += 1
        self.verify_result(ri, 6, 0, 0, 0)
        ri += 4
        self.verify_result(ri, 10, 0, 0, 0)
        ri += 1
        self.verify_result(ri, 2, 1, 0, 1)
        ri += 20
        self.verify_result(ri, 4, 3, 0, 3)
        ri += -5
        self.verify_result(ri, 8, 3, 1, 2)
        ri += -5
        self.verify_result(ri, 3, 3, 1, 2)
        ri += -1
        self.verify_result(ri, 2, 3, 1, 2)
        ri = ri - 5
        self.verify_result(ri, 6, 0, 0, 0)
        ri -= 1
        self.verify_result(ri, 5, 0, 0, 0)
        ri += 10
        self.verify_result(ri, 6, 1, 0, 1)

    def test_rolling_int_3(self):
        ri = RollingInt(10, -10, 5)
        self.verify_result(ri, 5, 0, 0, 0)
        ri += 1
        self.verify_result(ri, 6, 0, 0, 0)
        ri += 4
        self.verify_result(ri, 10, 0, 0, 0)
        ri += 1
        self.verify_result(ri, -10, 1, 0, 1)
        ri += 20
        self.verify_result(ri, 10, 1, 0, 1)
        ri += -5
        self.verify_result(ri, 5, 1, 0, 1)
        ri += -5
        self.verify_result(ri, 0, 1, 0, 1)
        ri += -1
        self.verify_result(ri, -1, 1, 0, 1)
        ri = ri - 5
        self.verify_result(ri, -6, 0, 0, 0)
        ri -= 1
        self.verify_result(ri, -7, 0, 0, 0)
        ri += 10
        self.verify_result(ri, 3, 0, 0, 0)

    def test_rolling_int_4(self):
        ri = RollingInt(-1, -10, -5)
        self.verify_result(ri, -5, 0, 0, 0)
        ri += 1
        self.verify_result(ri, -4, 0, 0, 0)
        ri += 4
        self.verify_result(ri, -10, 1, 0, 1)
        ri += 1
        self.verify_result(ri, -9, 1, 0, 1)
        ri += 20
        self.verify_result(ri, -9, 3, 0, 3)
        ri += -5
        self.verify_result(ri, -4, 3, 1, 2)
        ri += -5
        self.verify_result(ri, -9, 3, 1, 2)
        ri += -1
        self.verify_result(ri, -10, 3, 1, 2)
        ri = ri - 5
        self.verify_result(ri, -5, 0, 0, 0)
        ri -= 1
        self.verify_result(ri, -6, 0, 0, 0)
        ri += 10
        self.verify_result(ri, -6, 1, 0, 1)

    def test_rolling_int_other(self):
        ri = RollingInt(10)
        ri(5)
        self.assertEqual('5', str(ri))
        self.assertEqual(5, int(ri))
        self.assertEqual(5.0, float(ri))

    def test_rolling_max_from_other(self):

        ri = RollingInt('test')
        self.assertEqual(3, ri.max)

        ri = RollingInt([1, 2, 3, 4, 5, 6])
        self.assertEqual(5, ri.max)

    def test_exceptions(self):
        with self.assertRaises(AttributeError):
            ri = RollingInt(-1, -10, 5)

        with self.assertRaises(AttributeError):
            ri = RollingInt(5, 10, -1)

    def test_rollover_calc(self):
        tmp_ret = rollover_calc(10, 15)
        self.assertEqual(4, tmp_ret)

    def test_looping_iter(self):
        test_data = [1, 2, 3]
        tmp_ret = list(looping_iterator(test_data, max_iteration=10))

        self.assertEqual([1, 2, 3, 1, 2, 3 ,1, 2, 3, 1], tmp_ret)

    def test_looping_iter_2(self):
        test_data = [1, 2, 3]
        tmp_ret = list(looping_iterator(test_data, current_index=2, max_iteration=10))

        self.assertEqual([3, 1, 2, 3 ,1, 2, 3, 1, 2, 3], tmp_ret)


    def test_looping_iter_3(self):
        test_data = [1, 2, 3]
        tmp_ret = list(looping_iterator(test_data, max_iteration=10, step=2))

        self.assertEqual([1, 3, 2, 1, 3, 2, 1, 3, 2, 1], tmp_ret)
