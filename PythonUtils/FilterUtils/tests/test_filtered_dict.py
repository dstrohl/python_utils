__author__ = 'dstrohl'

import unittest
import copy
import sys
this_function_name = sys._getframe().f_code.co_name

from PythonUtils import Filter
from PythonUtils.FilterUtils.filtered_dict import ip

filter = Filter()


class MyTmpTestClass(object):
    a1 = 'one'
    a2 = 'two'


class MyTmpTestClass2(object):
    a1 = 'one_one'
    a2 = 'two_two'


test_dic = {'d1': 'one', 'd2': 'two'}
test_dic2 = {'d1': 'one_one', 'd2': 'two_two'}


class FilteredList(unittest.TestCase):

    def setUp(self):
        self.tc = MyTmpTestClass()
        self.tc2 = MyTmpTestClass2()
        d1 = copy.copy(test_dic)
        d2 = copy.copy(test_dic2)
        self.flt_list = [1, 2, 3, 4, 'test', 'test']
        self.dict_list = [d1, d2, d1, d2]
        self.class_list = [self.tc2, self.tc, self.tc2, self.tc]

    def test_filter_list(self):
        ycheck = list(filter(self.flt_list, 'test'))
        self.assertEqual(ycheck, ['test', 'test'])

    def test_filter_dict(self):
        ycheck = list(filter(self.dict_list, ('one', '__d1__')))
        self.assertEqual(ycheck, [test_dic, test_dic])

    def test_filter_attr(self):
        ycheck = list(filter(self.class_list, ('two', '__a2__')))
        self.assertEqual(ycheck, [self.tc, self.tc])

    def test_complex_filter(self):
        cd1 = {'c1': self.tc, 'c2': self.tc2}
        cd2 = {'c1': self.tc2, 'c2': self.tc}

        l1 = [cd1, cd2, cd1, cd2]

        check_me = list(filter(l1, ('__c1__.__a1__', 'eq', 'one'), filter_field_type='dict_key.attribute'), )
        self.assertEqual(check_me, [cd1, cd1])


class Filters(unittest.TestCase):

    def test_filter_2_set_and(self):
        test_filter = [('yes', 'eq', 'yes'),
                       ('y', 'in', 'yes')]

        yes = filter.filter_set_engine(test_filter)
        self.assertEqual(yes, True)

    def test_filter_2_set_or(self):
        test_filter = [('yes', 'eq', 'yes'),
                       ('y', 'nin', 'yes')]

        yes = filter.filter_set_engine(test_filter, filter_with='or')
        self.assertEqual(yes, True)

    def test_filter_2_set_and_fail(self):
        test_filter = [('yes', 'eq', 'yes'),
                       ('y', 'eq', 'yes')]

        yes = filter.filter_set_engine(test_filter)
        self.assertEqual(yes, False)

    def test_filter_2_set_or_fail(self):
        test_filter = [('yes', 'ne', 'yes'),
                       ('y', 'nin', 'yes')]

        yes = filter.filter_set_engine(test_filter, filter_with='or')
        self.assertEqual(yes, False)


    def test_filter_3_strings(self):
        yes = filter.filter_engine('y', 'eq', 'y')
        self.assertEqual(yes, True)

    def test_filter_ne(self):
        yes = filter.filter_engine('y', 'ne', 'M')
        self.assertEqual(yes, True)

    def test_filter_lt(self):
        yes = filter.filter_engine(5, 'lt', 10)
        self.assertEqual(yes, True)

    def test_filter_in(self):
        yes = filter.filter_engine('y', 'in', 'yes')
        self.assertEqual(yes, True)

    def test_filter_gt(self):
        yes = filter.filter_engine(10, 'gt', 4)
        self.assertEqual(yes, True)

    def test_filter_gte(self):
        yes = filter.filter_engine(10, 'gte', 10)
        self.assertEqual(yes, True)

    def test_filter_lte(self):
        yes = filter.filter_engine(10, 'lte', 10)
        self.assertEqual(yes, True)

    def test_filter_not(self):
        yes = filter.filter_engine(None, 'not', None)
        self.assertEqual(yes, True)

    def test_filter_is(self):
        yes = filter.filter_engine(1, 'is', None)
        self.assertEqual(yes, True)

    def test_filter_instance_of(self):
        yes = filter.filter_engine('y', 'instance_of', str)
        self.assertEqual(yes, True)
        
    # tests for false
    def test_filter_ne_fail(self):
        yes = filter.filter_engine('y', 'ne', 'y')
        self.assertEqual(yes, False)

    def test_filter_lt_fail(self):
        yes = filter.filter_engine(53, 'lt', 10)
        self.assertEqual(yes, False)

    def test_filter_in_fail(self):
        yes = filter.filter_engine('y3', 'in', 'yes')
        self.assertEqual(yes, False)

    def test_filter_gt_fail(self):
        yes = filter.filter_engine(10, 'gt', 46)
        self.assertEqual(yes, False)

    def test_filter_gte_fail(self):
        yes = filter.filter_engine(10, 'gte', 102)
        self.assertEqual(yes, False)

    def test_filter_lte_fail(self):
        yes = filter.filter_engine(102, 'lte', 10)
        self.assertEqual(yes, False)

    def test_filter_not_fail(self):
        yes = filter.filter_engine(True, 'not', None)
        self.assertEqual(yes, False)

    def test_filter_is_fail(self):
        yes = filter.filter_engine(0, 'is', None)
        self.assertEqual(yes, False)

    def test_filter_instance_of_fail(self):
        yes = filter.filter_engine('y', 'instance_of', int)
        self.assertEqual(yes, False)


if __name__ == '__main__':
    unittest.main()
