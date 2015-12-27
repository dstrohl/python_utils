__author__ = 'dstrohl'

import copy
from unittest import TestCase
from PythonUtils.FilterEngine.filter_engine2 import FilterItem


class MyTmpTestClass(object):
    a1 = 'one'
    a2 = 'two'

    def b1(self):
        return 'b-one'

    def b2(self):
        return 'b-two'


class MyTmpTestClass2(object):
    a1 = 'one_one'
    a2 = 'two_two'

    def b1(self):
        return 'b-one_one'

    def b2(self):
        return 'b-two_two'


test_dic = {'d1': 'one', 'd2': 'two'}
test_dic2 = {'d1': 'one_one', 'd2': 'two_two'}
test_dic3 = {'d1': 'four', 'd2': 'five'}

test_list = ['one', 'two']
test_list2 = ['one_one', 'two_two']

test_dic_int = {'d1': 10, 'd2': 20}
test_dic2_int  = {'d1': 15, 'd2': 25}

test_list_tf = [True, False]
test_list_ft = [False, True]

class Filters(TestCase):

    def test_filter_eq(self):
        tf = FilterItem(('d1', 'eq', 'one'))

        self.assertTrue(tf(test_dic))
        self.assertFalse(tf(test_dic2))

    def test_filter_nefilter(self):
        tf = FilterItem(('d1', 'ne', 'one_one'))

        self.assertTrue(tf(test_dic))
        self.assertFalse(tf(test_dic2))

    def test_filter_gtfilter(self):
        tf = FilterItem(('d1', 'gt', 13))

        self.assertTrue(tf(test_dic2_int))
        self.assertFalse(tf(test_dic_int))

    def test_filter_gtefilter(self):
        tf = FilterItem(('d1', 'gte', 15))

        self.assertTrue(tf(test_dic2_int))
        self.assertFalse(tf(test_dic_int))

    def test_filter_ltfilter(self):
        tf = FilterItem(('d2', 'lt', 23))

        self.assertTrue(tf(test_dic_int))
        self.assertFalse(tf(test_dic2_int))

    def test_filter_ltefilter(self):
        tf = FilterItem(('d2', 'lte', 20))

        self.assertTrue(tf(test_dic_int))
        self.assertFalse(tf(test_dic2_int))

    def test_filter_infilter(self):
        tf = FilterItem(('d1', 'in', ['one', 'four', 'five']))

        self.assertTrue(tf(test_dic))
        self.assertFalse(tf(test_dic2))

    def test_filter_notfilter(self):
        tf = FilterItem((0, 'not', None))

        self.assertTrue(tf(test_list_ft))
        self.assertFalse(tf(test_list_tf))

    def test_filter_isfilter(self):
        tf = FilterItem((1, 'is'))

        self.assertTrue(tf(test_list_ft))
        self.assertFalse(tf(test_list_tf))

    def test_filter_instancefilter(self):
        tf = FilterItem((0, 'instance', str))

        self.assertTrue(tf(test_list))
        self.assertFalse(tf(test_list_ft))

    def test_filter_startswith(self):
        tf = FilterItem(('d1', 'startswith', 'on'))

        self.assertTrue(tf(test_dic))
        self.assertFalse(tf(test_dic3))

    def test_filter_endsswith(self):
        tf = FilterItem(('d1', 'endswith', 'ne'))

        self.assertTrue(tf(test_dic))
        self.assertFalse(tf(test_dic3))

    def test_complex_filter1(self):
        tf = FilterItem(('d1', 'startswith', 'one'),
                        ('d1', 'not eq', 'one_one'))

        self.assertTrue(tf(test_dic))
        self.assertFalse(tf(test_dic2))

    def test_complex_filter_or(self):
        tf = FilterItem(('d1', 'startswith', 'one'),
                        ('d1', 'startswith', 'two'), filter_by='or')

        self.assertTrue(tf(test_dic))
        self.assertTrue(tf(test_dic2))
        self.assertFalse(tf(test_dic3))
