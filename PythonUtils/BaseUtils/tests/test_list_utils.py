#!/usr/bin/env python

"""
"""

__author__ = ""
__copyright__ = ""
__credits__ = []
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = ""


from datetime import datetime, timedelta

from unittest import TestCase
from PythonUtils.BaseUtils.base_utils import *
import statistics
from decimal import Decimal

class SwapTest(TestCase):
    def test_swap(self):
        self.assertEqual(swap(True), False)

    def test_swap_rev(self):
        self.assertEqual(swap(False), True)

    def test_swap_str(self):
        self.assertEqual(swap('yes', 'yes', 'no'), 'no')

    def test_swap_err(self):
        with self.assertRaises(AttributeError):
            swap('yes')

class TestMaxLen(TestCase):
    def test_max_len_item(self):
        test_ret = max_len('1', '22', '333')
        self.assertEqual(3, test_ret)

    def test_max_len_list(self):
        test_ret = max_len(['1', '22', '333'], ['1'], ('1', '22', '333', '4444'))
        self.assertEqual(4, test_ret)

    def test_max_len_dict(self):
        d1 = {'t1': ('1', '22', '333', '4444')}
        d2 = {'t1': ('1', '22')}
        d3 = {'t1': ('1', '22', '333')}

        test_ret = max_len(d1, d2, d3, field_key='t1')
        self.assertEqual(4, test_ret)



class NextTest(TestCase):
    def test_next(self):
        tn = NextItem([10, 20, 30, 40])

        self.assertEqual(10, tn())
        self.assertEqual(20, tn(2))
        self.assertEqual(40, tn())
        self.assertEqual(10, tn())
        self.assertEqual(20, tn(-1))
        self.assertEqual(10, tn(0))
        self.assertEqual(10, tn(-10))
        self.assertEqual(30, tn(0))


class MergeListTest(TestCase):
    def test_merge_list_1(self):
        tmp_ret = merge_list([1, 2, 3, 4], [1, 2, 3, 4])
        self.assertEqual([1, 2, 3, 4], tmp_ret)

    def test_merge_list_2(self):
        tmp_ret = merge_list([1, 2, 3, 4], [2, 3, 4, 5])
        self.assertListEqual([1, 2, 3, 4, 5], tmp_ret)

    def test_merge_list_3(self):
        tmp_ret = merge_list([1, 2, 3, 4], [1, 2, 3])
        self.assertListEqual([1, 2, 3, 4, 1, 2, 3], tmp_ret)

    def test_merge_list_4(self):
        tmp_ret = merge_list([1, 2, 3, 4], [5, 6, 7, 8])
        self.assertListEqual([1, 2, 3, 4, 5, 6, 7, 8], tmp_ret)

    def test_merge_list_5(self):
        tmp_ret = merge_list([1, 2, 3, 4], [1, 3, 4, 5])
        self.assertListEqual([1, 2, 3, 4, 1, 3, 4, 5], tmp_ret)

    def test_merge_list_6(self):
        tmp_ret = merge_list([1, 2, 3, 4], [1, 2, 3, 4, 5])
        self.assertListEqual([1, 2, 3, 4, 5], tmp_ret)

    def test_merge_list_7(self):
        tmp_ret = merge_list([1, 2, 3, 4], [2, 3])
        self.assertListEqual([1, 2, 3, 4, 2, 3], tmp_ret)

    def test_merge_list_8(self):
        tmp_ret = merge_list([1, 2, 3], [3, 4])
        self.assertListEqual([1, 2, 3, 4], tmp_ret)



class MakeListTests(TestCase):
    def test_string(self):
        self.assertEqual(make_list('test'), ['test'])

    def test_list(self):
        self.assertEqual(make_list(['test', 'test']), ['test', 'test'])

    def test_set(self):
        self.assertEqual(make_list({'test', 'test2'}), {'test', 'test2'})

    def test_tuple(self):
        self.assertEqual(make_list(('test', 'test')), ('test', 'test'))

    def test_others(self):
        self.assertEqual(make_list(1), [1, ])




class TestListHelpersCase(TestCase):

    def test_count_unique(self):
        tmp = ['1', '2', '3', '4', '1', '2', '3', '4']
        self.assertEqual(count_unique(tmp), 4)

    def test_count_unique_dict(self):
        tmp = [
            {'k': '1', 'j': 'a', 'i': 'aa'},
            {'k': '2', 'j': 'b', 'i': 'aa'},
            {'k': '3', 'j': 'c', 'i': 'aa'},
            {'k': '4', 'j': 'd'},
            {'k': '1', 'j': 'e'},
            {'k': '2', 'j': 'f', 'i': 'bb'},
            {'k': '3', 'j': 'g'},
            {'k': '4', 'j': 'h', 'i': 'bb'}]
        self.assertEqual(count_unique(tmp, dict_key='k'), 4)
        self.assertEqual(count_unique(tmp, dict_key='i', on_key_error='skip'), 2)
        self.assertEqual(count_unique(tmp, dict_key='i', on_key_error='count'), 3)
        with self.assertRaises(KeyError):
            tmp = count_unique(tmp, dict_key='i')


    def test_remove_dupes(self):
        tmp = ['1', '2', '3', '4', '1', '2', '3', '4']
        self.assertEqual(len(remove_dupes(tmp)), 4)

    def test_get_not_in(self):
        tmp1 = ['1', '2', '3', '4']
        tmp2 = ['3', '4', '5', '6']
        self.assertEqual(len(get_not_in(tmp1, tmp2)), 2)

    def test_get_same(self):
        tmp1 = ['1', '2', '3', '4']
        tmp2 = ['3', '4', '5', '6']
        self.assertEqual(len(get_same(tmp1, tmp2)), 2)

    def test_unpack_class_method_prop(self):
        tmp = [
            UnpackDemo(),
            UnpackDemo(),
            UnpackDemo2(),
        ]
        tmp_ret = unpack_class_method(tmp, 't1')
        self.assertEqual(len(tmp_ret), 3)
        self.assertIn('1', tmp_ret)
        self.assertIn('2', tmp_ret)



    def test_unpack_class_method_args(self):
        tmp = [
            UnpackDemo(),
            UnpackDemo(),
            UnpackDemo2(),
        ]
        tmp_ret = unpack_class_method(tmp, 'args_demo', args_list=[2, 4])
        self.assertEqual(len(tmp_ret), 3)
        self.assertIn('6', tmp_ret)
        self.assertIn('8', tmp_ret)


    def test_unpack_class_method_kwargs(self):
        tmp = [
            UnpackDemo(),
            UnpackDemo(),
            UnpackDemo2(),
        ]
        tmp_ret = unpack_class_method(tmp, 'kwargs_demo', kwargs_dict={'n1': 3, 'n2': 4})
        self.assertEqual(len(tmp_ret), 3)
        self.assertIn('7', tmp_ret)
        self.assertIn('12', tmp_ret)


    def test_flatten(self):
        tmp1 = ['11', '22', '33', '44']
        tmp2 = [tmp1, '55', '66']
        tmp3 = [tmp2, '77', '88']

        tmp_ret = ['11', '22', '33', '44', '55', '66', '77', '88']
        self.assertListEqual(flatten(tmp3), tmp_ret)

    def test_make_list(self):
        tmp1 = ['1', '2', '3', '4']
        self.assertListEqual(make_list(tmp1), tmp1)
        self.assertListEqual(make_list('test'), ['test'])


class TestListPlus(TestCase):

    def test_list_2_basic_list(self):
        l = ListPlus()
        l.append('test')
        self.assertEqual(l, ['test'])

    def test_list_2_add(self):
        l = ListPlus()
        l.append('test')

        l.add(1, 'test_2')
        self.assertEqual(l, ['test', 'test_2'])

        l.add(1, 'test_3')
        self.assertEqual(l, ['test', 'test_3', 'test_2'])

        l.add(4, 'test_4')
        self.assertEqual(l, ['test', 'test_3', 'test_2', None, 'test_4'])

        l.add(6, 'test_5', new_item_default='test_new')
        self.assertEqual(l, ['test', 'test_3', 'test_2', None, 'test_4', 'test_new', 'test_5'])

    def test_ListPlus_update(self):
        l = ListPlus()
        l.append('test')

        l.update(1, 'test_2')
        self.assertEqual(l, ['test', 'test_2'])

        l.update(1, 'test_3')
        self.assertEqual(l, ['test', 'test_3'])

        l.update(4, 'test_4')
        self.assertEqual(l, ['test', 'test_3', None, None, 'test_4'])

        l.update(6, 'test_5', new_item_default='test_new')
        self.assertEqual(l, ['test', 'test_3', None, None, 'test_4', 'test_new', 'test_5'])

    def test_ListPlus_get(self):
        l = ListPlus()
        l.append('test')
        l.add(1, 'test_2')

        tmp_ret = l.get(1)
        self.assertEqual(tmp_ret, 'test_2')

        with self.assertRaises(IndexError):
            tmp_ret = l.get(4)

        tmp_ret = l.get(4, 'test_3')
        self.assertEqual(tmp_ret, 'test_3')

    '''
    def test_ListPlus_index_set(self): 
        l = ListPlus()
        l.append('test')
        l.add(1, 'test_2')

        l[1] = 'test_3'
        self.assertEqual(l[1], 'test_3')

        with self.assertRaises(TypeError): 
            l['4'] = 'test'

        l[4] = 'test_4'
        self.assertEqual(l[3: 4], [None, 'test_4'])

        l.set_new_item_default('empty')
        l[6] = 'test_5'
        self.assertEqual(l[5: 6], ['empty', 'test_5'])
    '''

    def test_ListPlus_update_override_internal_funct(self):
        l = list3()

        l.append(5)
        l.add(0, 5)
        self.assertEqual(l, [5, 5])

        l.update(0, 2)
        self.assertEqual(l, [3, 5])

        # l[0] = 4
        # self.assertEqual(l, [-1, 5])

    '''
    def test_ListPlus_update_external_cl_pass_funct(self): 
        l = ListPlus()

        l.append(1)
        l.add(0, 1)
        self.assertEqual(l, [1, 1])

        l.update(0, 2)
        self.assertEqual(l, [2, 1])

        # l[0] = 3
        # self.assertEqual(l, [3, 1])

        l.update(0, 2, funct = test_list_update)
        self.assertEqual(l, [4, 1])
    '''


def test_list_update(old, new):
    return old + new


class list3(ListPlus):
    def _update_function(self, old, new):
        # print(old, '-', new, '=', old - new)
        return old - new

