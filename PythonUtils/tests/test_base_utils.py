__author__ = 'dstrohl'

import copy
import sys
import string
from datetime import datetime, timedelta

from unittest import TestCase
from PythonUtils.BaseUtils.base_utils import *
import statistics
from decimal import Decimal
from math import fsum
# from common.utils import generatePercentages
# from PythonUtils.ClassUtils.args_kwargs_handlers import args_handler

class TestFlattenDict(TestCase):
    def test_flatten_dict_1(self):
        tmp_in = {'l1': [1, 2, 3, 4]}
        exp_out = [1, 2, 3, 4]
        tmp_ret = flatten_dict(tmp_in, flatten_single=True)
        self.assertEqual(exp_out, tmp_ret)

    def test_flatten_dict_2(self):
        tmp_in = {'l1': [1, 2, 3, 4], 'l1.2': 'foobar'}
        exp_out = {'l1': [1, 2, 3, 4], 'l1.2': 'foobar'}
        tmp_ret = flatten_dict(tmp_in)
        self.assertEqual(exp_out, tmp_ret)

    def test_flatten_dict_3(self):
        tmp_in = {'l1.1': {'l2.1': {}}, 'l1.2': 'foobar'}
        exp_out = 'foobar'
        tmp_ret = flatten_dict(tmp_in, flatten_single=True)
        self.assertEqual(exp_out, tmp_ret)

    def test_flatten_dict_3b(self):
        tmp_in = {'l1.1': {'l2.1': {}}, 'l1.2': 'foobar'}
        exp_out = {'l1.2': 'foobar'}
        tmp_ret = flatten_dict(tmp_in)
        self.assertEqual(exp_out, tmp_ret)

    def test_flatten_dict_4(self):
        tmp_in = {'l1.1': {'l2.1': {}, 'l2.2': [1, 2, 3, 4]}, 'l1.2': 'foobar'}
        exp_out = {'l1.1': [1, 2, 3, 4], 'l1.2': 'foobar'}
        tmp_ret = flatten_dict(tmp_in, flatten_single=True)
        self.assertEqual(exp_out, tmp_ret)



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


class TestUnset(TestCase):
    def test_unset(self):
        t = _UNSET

        self.assertEqual(_UNSET, t)
        self.assertFalse(t)
        self.assertIs(t, _UNSET)

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


def path_validate_func(path_in):
    if 'p3' not in path_in:
        raise ValueError


class PathTests(TestCase):

    def test_new_create(self):
        p = Path('p1/p2', key_sep='/')
        self.assertEqual(['p1', 'p2'], list(p))

    def test_create_from_path(self):
        p = Path('p1/p2', key_sep='/')
        q = Path(p)
        self.assertEqual(list(q), ['p1', 'p2'])

    def test_cd(self):
        p = Path('p1/p2', key_sep='/')
        self.assertEqual('/p1', str(p.cd('//')))
        self.assertEqual(p[-1], 'p1')

        self.assertEqual('/p3', str(p.cd('//p3')))
        self.assertEqual(p[-1], 'p3', p)

        self.assertEqual('/p3/p4', str(p.cd('p4')))
        self.assertEqual('/p3/p4/p4/p5', str(p.cd('p4/p5')))
        self.assertEqual('/', str(p.cd('/')))
        self.assertEqual('/p1/p2/p3/p4', str(p.cd('p1/p2/p3/p4')))
        self.assertEqual('/p5/p6', str(p.cd('/p5/p6')))

    def test_cd_up_2(self):
        p = Path('p1.p2.p3.p4.')
        self.assertEqual(p.cd('...')._path, ['p1', 'p2'])
        self.assertEqual(p[-1], 'p2')

    def test_cd_to_root(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(p.cd('.')._path, [])

    def test_addition_1(self):
        print('--- making p1 ----')
        p1 = Path('p1/p2', key_sep='/')
        print('--- making p2 ----')
        p2 = Path('p3.p4')
        print('--- making p ----')
        p = p1 + p2

        self.assertEqual('p1/p2', p1)
        self.assertEqual('p3.p4', p2)

        self.assertEqual('/p1/p2/p3/p4', p)

    def test_addition_2(self):
        p1 = Path('p1.p2')
        p = p1 + 'p3.p4'

        self.assertEqual('.p1.p2.p3.p4', p)
        self.assertEqual('p1.p2', p1)

    def test_addition_3(self):
        p1 = Path('p1.p2')
        p1 += 'p3.p4'

        self.assertEqual('p1.p2.p3.p4', p1)

    def test_merge_1(self):
        p1 = Path('p1.p2')
        p2 = Path('p3.p4')
        p1 &= p2

        self.assertEqual('p1.p2.p3.p4', p1)
        self.assertEqual('p3.p4', p2)

    def test_merge_2(self):
        p1 = Path('p1.p2.p3')
        p2 = Path('p3.p4')
        p = p1 & p2

        self.assertEqual('p1.p2.p3', p1)
        self.assertEqual('p3.p4', p2)
        self.assertEqual('p1.p2.p3.p4', p)

    def test_merge_3(self):
        p1 = Path('p1.p2.p3')
        p2 = Path('p2.p3.p4')
        p = p1 & p2

        self.assertEqual('p1.p2.p3', p1)
        self.assertEqual('p2.p3.p4', p2)
        self.assertEqual('p1.p2.p3.p4', p)

    def test_merge_4(self):
        p1 = Path('p1.p2.p3')
        p2 = Path('p1.p3.p4')
        p = p1 & p2

        self.assertEqual('p1.p2.p3', p1)
        self.assertEqual('p1.p3.p4', p2)
        self.assertEqual('p1.p2.p3.p1.p3.p4', p)

    def test_str(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(str(p), '.p1.p2.p3.p4')

    def test_str_2(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual('/p1/p2/p3/p4', p.to_string('/'))

    def test_str_3(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(p.to_string('/', leading=False), 'p1/p2/p3/p4')

    def test_str_4(self):
        p = Path('p1.p2.p3.p4', key_xform=str.upper)
        self.assertEqual(p.to_string('/', trailing=True), '/P1/P2/P3/P4/')

    def test_index(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(p[2], 'p3')

    def test_index_2(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(p[2:], 'p3.p4')

    def test_index_3(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(len(p), 4)
        p2 = p[:2]
        self.assertEqual(p2, '.p1.p2')
        self.assertEqual(len(p2), 2)
        self.assertEqual(len(p), 4)

    def test_len(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(len(p), 4)

    def test_find(self):
        p = Path('p1.p2.p3.p4', key_xform=str.upper)
        self.assertEqual(p.find('p2'), 1)
        self.assertEqual(p.find('P2'), 1)

    def test_no_find(self):
        p = Path('p1.p2.p3.p4')
        with self.assertRaises(ValueError):
            p.find('p6')

    def test_in(self):
        p = Path('p1.p2.p3.p4')
        self.assertTrue('p2' in p)

    def test_not_in(self):
        p = Path('p1.p2.p3.p4')
        self.assertFalse('p6' in p)

    def test_from(self):
        p = Path('p1.p2.p3.p4')
        p2 = p.path_from('p2')
        self.assertEqual(p2, 'p2.p3.p4')
        self.assertEqual(len(p2), 3)
        self.assertEqual(len(p), 4)

    def test_to(self):
        p = Path('p1.p2.p3.p4')
        p2 = p.path_to('p3')
        self.assertEqual('p1.p2.p3', p2)
        self.assertEqual(len(p2), 3)
        self.assertEqual(len(p), 4)

    def test_no_from(self):
        p = Path('p1.p2.p3.p4')
        with self.assertRaises(ValueError):
            p2 = p.path_from('p6')

    def test_no_to(self):
        p = Path('p1.p2.p3.p4')
        with self.assertRaises(ValueError):
            p2 = p.path_to('p6')

    def test_compare(self):
        test_items = [

            ('lt_1', ('<', '<=', '!='), 5),
            ('lt_2', ('<', '<=', '!='), 'p1.p2.p3.p4'),
            ('lt_4', ('<', '<=', '!='), Path('p1.p2.p3.p4', key_sep='/')),
            ('lt_5', ('<', '<=', '!='), ['p1', 'p2', 'p3', 'p4']),

            ('eq_1', ('==', '<=', '>='), 3),
            ('eq_2', ('==', '<=', '>='), 'p1.p2.p3'),
            ('eq_3', ('==', '<=', '>='), Path('p1.p2.p3')),
            ('eq_4', ('==', '<=', '>='), ['p1', 'p2', 'p3']),

            ('gt_1', ('>', '>=', '!='), 1),
            ('gt_2', ('>', '>=', '!='), 'p1.p2'),
            ('gt_3', ('>', '>=', '!='), Path('p1.p2', key_sep='/')),
            ('gt_4', ('>', '>=', '!='), ['p1', 'p2']),

            ('ne_3', ('!=',), 'p6.p2.p3'),
            ('ne_4', ('!=',), Path('p6.p2.p3')),
            ('ne_5', ('!=',), ['p6', 'p2', 'p3']),
        ]

        all_test_types = (
            ('==', self.assertEqual),
            ('>', self.assertGreater),
            ('<', self.assertLess),
            ('<=', self.assertLessEqual),
            ('>=', self.assertGreaterEqual),
            ('!=', self.assertNotEqual)
        )
        base_item = Path('p1.p2.p3')

        TEST_ITEM_CODE = None
        TEST_TYPE = None
        # TEST_ITEM_CODE = 'lt_2'
        # TEST_TYPE = '<'

        for name, test_types, test_value in test_items:
            for cur_test_type, cur_test_assert in all_test_types:
                if TEST_ITEM_CODE is None or TEST_ITEM_CODE == name:
                    if TEST_TYPE is None or TEST_TYPE == cur_test_type:
                        if cur_test_type in test_types:
                            with self.subTest(f'{name} {cur_test_type} (good)'):
                                cur_test_assert(base_item, test_value)
                        else:
                            with self.subTest(f'{name} {cur_test_type} (bad)'):
                                with self.assertRaises(AssertionError):
                                    cur_test_assert(base_item, test_value)

    def test_bool(self):
        p = Path('p1.p2.p3.p4')
        self.assertTrue(p)

    def test_not_bool(self):
        p = Path('p1.p2.p3.p4')
        p.cd('.')
        self.assertEqual(p, '')
        self.assertFalse(p)

    def test_validate_ok(self):
        p = Path('p1.p2.p3.p4', validate_func=path_validate_func)
        self.assertEqual(p, 'p1.p2.p3.p4')

    def test_validate_ok_2(self):
        p = Path('p1.p2.p3.p4', validate_func=path_validate_func)
        p.cd('..')
        self.assertEqual(p, 'p1.p2.p3')

    def test_validate_bad(self):
        with self.assertRaises(ValueError):
            p = Path('p1.p2.p4', validate_func=path_validate_func)
            self.assertEqual(p, 'p1.p2.p3.p4')

    def test_validate_bad_2(self):
        p = Path('p1.p2.p3.p4', validate_func=path_validate_func)
        p.cd('..')
        self.assertEqual(p, 'p1.p2.p3')
        with self.assertRaises(ValueError):
            p.cd('..')

        self.assertEqual(p, 'p1.p2.p3')
        with self.assertRaises(ValueError):
            p.cd('.')

        self.assertEqual(p, 'p1.p2.p3')

class MLDictManagerTests(TestCase):

    test_dict = {
        'level': '1',
        'l2a': {
            'level': '2a',
            'l3aa': {
                'level': '3aa',
                'l4aaa': {'level': '4aaa'},
                'l4aab': {'level': '4aab'}},
            'l3ab': {
                'level': '3ab',
                'l4aba': {'level': '4aba'},
                'l4abb': {'level': '4abb'}}},
        'l2b': {
            'level': '2b',
            'l3ba': {
                'level': '3ba',
                'l4baa': {'level': '4baa'},
                'l4bab': {'level': '4bab'}},
            'l3bb': {
                'level': '3bb',
                'l4bba': {'level': '4bba'},
                'l4bbb': {'level': '4bbb'}}}
    }

    mldm = MultiLevelDictManager(test_dict)

    def test_simple_lookup(self):
        self.mldm.cd('.')
        self.assertEqual(self.mldm['level'], '1')

    def test_2_level_lookup(self):
        self.assertEqual(self.mldm['.l2a.level'], '2a')

    def test_2_level_from_cur_level(self):
        self.mldm('.l2a.')
        self.assertEqual(self.mldm.get('level'), '2a')

    def test_3_level_down_1(self):
        self.mldm.cd('.l2b.l3bb')
        self.assertEqual(self.mldm['..level'], '2b')

    def test_4_level_down_2(self):
        self.mldm.cd('.l2b.l3bb.l4bbb')
        self.assertEqual(self.mldm['....level'], '1')

    def test_4_level_down_5(self):
        self.mldm.cd('.l2b.l3bb.14bbb')
        self.assertEqual(self.mldm['......level'], '1')

    def test_get_default(self):
        self.mldm.cd('.l2b.l3bb.l4bbb')
        self.assertEqual(self.mldm.get('......leddvel', 'noanswer'), 'noanswer')

    def test_pwd(self):
        self.mldm.cd('.l2b.l3bb.l4bbb')
        self.assertEqual(self.mldm.pwd, 'l2b.l3bb.l4bbb')

    def test_get_cwd(self):
        self.mldm.cd('.')
        self.assertEqual(self.mldm.get('l2b.l3bb.l4bbb.level', cwd=True), '4bbb')
        self.assertEqual(self.mldm.get('..level', cwd=True), '3bb')



    '''
    def test_2_level_from_cur_level(self):
        tmp_ret = ml_dict(self.l2_level, 'l2', current_path='l1')
        self.assertEqual(tmp_ret, 'level2')

    def test_2_level_key_from_root(self):
        tmp_ret = ml_dict(self.l2_level, '.l1.l2', current_path='l1')
        self.assertEqual(tmp_ret, 'level2')


    def test_3_level_key_down_1(self):
        tmp_ret = ml_dict(self.l3_level, '..l1b.l2b.l3b', current_path='l1')
        self.assertEqual(tmp_ret, 'level3b')


    def test_4_level_key_down_2(self):
        tmp_ret = ml_dict(self.l4_level, '...l2c', current_path='l1.l2.l3')
        self.assertEqual(tmp_ret, 'level2c')


    def test_4_level_key_down_5(self):
        tmp_ret = ml_dict(self.l4_level, '......l1b.l2b.l3b.l4b', current_path='l1.l2.l3')
        self.assertEqual(tmp_ret, 'level4b')




    def test_default_response(self):
        tmp_ret = ml_dict(self.l1_level, 'not_valid', default_response='no level')
        self.assertEqual(tmp_ret, 'no level')
    '''

'''
class ML_DictTests(TestCase):
    """
    def ml_dict(dict_map,
                key,
                key_sep='.',
                fixed_depth=0,
                default_path=None,
                default_response=_UNSET
                ):
    """

    l1_level = {'l1': 'level1'}
    l2_level = {'l1': {'l2': 'level2'},'l1b': {'l2b': 'level2b'}}

    l3_level = {'l1': {'l2': {'l3': 'level3'}},
                'l1b': {'l2b': {'l3b': 'level3b'}}}

    l4_level = {'l1': {'l2': {'l3': {'l4': 'level4'}},
                       'l2c': 'level2c'},
                'l1b': {'l2b': {'l3b': {'l4b': 'level4b'}}}}

    l1_path = 'l1'
    l2_path = 'l1.l2'
    l3_path = 'l1.l2.l3'

    l3_short_path = 'l3'
    l3_med_path = 'l2.l3'
    l3_default_path = 'l1.l2'

    def test_simple_lookup(self):
        tmp_ret = ml_dict(self.l1_level, self.l1_path)
        self.assertEqual(tmp_ret, 'level1')

    def test_2_level_lookup(self):
        tmp_ret = ml_dict(self.l2_level, self.l2_path)
        self.assertEqual(tmp_ret, 'level2')

    def test_2_level_from_cur_level(self):
        tmp_ret = ml_dict(self.l2_level, 'l2', current_path='l1')
        self.assertEqual(tmp_ret, 'level2')

    def test_2_level_key_from_root(self):
        tmp_ret = ml_dict(self.l2_level, '.l1.l2', current_path='l1')
        self.assertEqual(tmp_ret, 'level2')


    def test_3_level_key_down_1(self):
        tmp_ret = ml_dict(self.l3_level, '..l1b.l2b.l3b', current_path='l1')
        self.assertEqual(tmp_ret, 'level3b')


    def test_4_level_key_down_2(self):
        tmp_ret = ml_dict(self.l4_level, '...l2c', current_path='l1.l2.l3')
        self.assertEqual(tmp_ret, 'level2c')


    def test_4_level_key_down_5(self):
        tmp_ret = ml_dict(self.l4_level, '......l1b.l2b.l3b.l4b', current_path='l1.l2.l3')
        self.assertEqual(tmp_ret, 'level4b')

    """
    def test_fixed_depth_3_level_fix_1_level(self):
        tmp_ret = ml_dict(self.l3_level, self.l3_med_path, fixed_depth=3, default_path=self.l3_default_path)
        self.assertEqual(tmp_ret, 'level3')

    def test_fixed_depth_3_level_fix_2_level(self):
        tmp_ret = ml_dict(self.l3_level, self.l3_short_path, fixed_depth=3, default_path=self.l3_default_path)
        self.assertEqual(tmp_ret, 'level3')

    def test_fixed_depth_3_level_no_fixing(self):
        tmp_ret = ml_dict(self.l3_level, self.l3_path, fixed_depth=3, default_path=self.l3_default_path)
        self.assertEqual(tmp_ret, 'level3')
    """

    def test_default_response(self):
        tmp_ret = ml_dict(self.l1_level, 'not_valid', default_response='no level')
        self.assertEqual(tmp_ret, 'no level')
'''


class CFB_Test(object):
    def __bool__(self):
        return True


class CFB_No_Bool_Test(object):
    pass

class ConvertToBooleanTests(TestCase):

    def test_from_string(self):
        self.assertEqual(convert_to_boolean('true'), True)
        self.assertEqual(convert_to_boolean('True'), True)
        self.assertEqual(convert_to_boolean('Yes'), True)
        self.assertEqual(convert_to_boolean('No'), False)
        self.assertEqual(convert_to_boolean('+'), True)
        self.assertEqual(convert_to_boolean('-'), False)
        self.assertEqual(convert_to_boolean('OK'), True)

    def test_fail_from_string(self):
        with self.assertRaises(TypeError):
            convert_to_boolean('test')

    def test_from_boolean(self):
        self.assertEqual(convert_to_boolean(False), False)
        self.assertEqual(convert_to_boolean(True), True)

    def test_from_obj(self):
        bo = CFB_Test()
        self.assertEqual(convert_to_boolean(bo), True)

    def test_fail_from_obj(self):
        nbo = CFB_No_Bool_Test()
        with self.assertRaises(TypeError):
            convert_to_boolean(nbo)

    def test_from_int(self):
        self.assertEqual(convert_to_boolean(0), False)
        self.assertEqual(convert_to_boolean(1), True)

        with self.assertRaises(TypeError):
            convert_to_boolean(12)

    def test_from_float(self):
        self.assertEqual(convert_to_boolean(0.0), False)
        self.assertEqual(convert_to_boolean(1.0), True)

        with self.assertRaises(TypeError):
            convert_to_boolean(1.1)

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

class TestQuartileCalc(TestCase):

    def test_qu_calc(self):
        test_list = [71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69]
        q1, q2, q3 = quartiles(test_list)
        self.assertEqual(q1, 70)
        self.assertEqual(q2, 70.5)
        self.assertEqual(q3, 71.5)

    def test_qu_calc_2(self):
        test_list = [2, 5, 6, 9, 12]
        q1, q2, q3 = quartiles(test_list)
        self.assertEqual(q1, 3.5)
        self.assertEqual(q2, 6)
        self.assertEqual(q3, 10.5)

    def test_qu_calc_3(self):
        test_list = [3, 10, 14, 22, 19, 29, 70, 49, 36, 32]
        q1, q2, q3 = quartiles(test_list)
        self.assertEqual(q1, 14)
        self.assertEqual(q2, 25.5)
        self.assertEqual(q3, 36)

class TestSpinner(TestCase):
    def test_spinner_normal(self):
        self.assertEqual('|', spinner_char(0))
        self.assertEqual('/', spinner_char(1))
        self.assertEqual('-', spinner_char(2))
        self.assertEqual('\\', spinner_char(3))
        self.assertEqual('|', spinner_char(4))
        self.assertEqual('/', spinner_char(5))
        self.assertEqual('-', spinner_char(6))
        self.assertEqual('\\', spinner_char(7))
        self.assertEqual('|', spinner_char(8))

    def test_states(self):
        self.assertEqual(' ', spinner_char(0, not_started_state=1, finished_state=6))
        self.assertEqual(' ', spinner_char(1, not_started_state=1, finished_state=6))
        self.assertEqual('-', spinner_char(2, not_started_state=1, finished_state=6))
        self.assertEqual('\\', spinner_char(3, not_started_state=1, finished_state=6))
        self.assertEqual('|', spinner_char(4, not_started_state=1, finished_state=6))
        self.assertEqual('/', spinner_char(5, not_started_state=1, finished_state=6))
        self.assertEqual('x', spinner_char(6, not_started_state=1, finished_state=6))
        self.assertEqual('x', spinner_char(7, not_started_state=1, finished_state=6))
        self.assertEqual('x', spinner_char(8, not_started_state=1, finished_state=6))


class TestPercCalcs(TestCase):
    def test_basic_function(self):
        pc = PercCounter(total=10)
        self.assertEqual(0, pc())
        self.assertEqual(10, pc(1))
        self.assertEqual(20, pc(2))
        self.assertEqual(30, pc(delta=1))
        self.assertEqual(110, pc(11))

    def test_iadd_isub_function(self):
        pc = PercCounter(total=10)
        self.assertEqual(0, pc())
        pc += 1
        self.assertEqual('10%', str(pc))
        pc += 1
        self.assertEqual(0.2, float(pc))
        pc -= 1
        self.assertEqual(10, int(pc))


    def test_format_perc_float(self):
        pc = PercCounter(total=10, perc_format=PERC_RET.AS_FLOAT)
        self.assertEqual(0.0, pc())
        self.assertEqual(0.1, pc(1))
        self.assertEqual(0.2, pc(2))
        self.assertEqual(0.3, pc(delta=1))
        self.assertEqual(1.1, pc(11))

    def test_format_str(self):
        pc = PercCounter(total=10, perc_format=PERC_RET.AS_STR_INT)
        self.assertEqual('0%', pc())
        self.assertEqual('10%', pc(1))
        self.assertEqual('20%', pc(2))
        self.assertEqual('30%', pc(delta=1))
        self.assertEqual('110%', pc(11))

    def test_make_perc_min_max(self):
        pc = PercCounter(total=10, min_perc=0.2, max_perc=0.75)
        self.assertEqual(20, pc())
        self.assertEqual(20, pc(1))
        self.assertEqual(20, pc(2))
        self.assertEqual(30, pc(delta=1))
        self.assertEqual(75, pc(11))

    def test_make_perc_raise(self):
        with self.assertRaises(ZeroDivisionError):
            pc = PercCounter(total=0)

    def test_scaled_perc(self):
        pc = PercCounter(total=100, current=10)
        self.assertEqual(5, pc.scaled(50, as_int=True))
        self.assertEqual(5.5, pc.scaled(55, as_int=False))

    def test_perc_bar_left(self):
        pc = PercCounter(total=50, current=5, perc_bar_length=20)
        tmp_ret = pc.perc_bar()
        exp_ret = '##..................'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_right(self):
        pc = PercCounter(total=50, current=5, perc_bar_length=20)
        tmp_ret = pc.perc_bar(bar_format='{right_bar}')
        exp_ret = '..................##'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_center(self):
        pc = PercCounter(total=50, current=22, perc_bar_length=20)
        tmp_ret = pc.perc_bar(bar_format='{center_bar}')
        exp_ret = '.......#............'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_with_perc(self):
        pc = PercCounter(total=50, perc_bar_length=20)
        tmp_ret = pc.perc_bar(5, bar_format='{left_bar} {perc:.0%}')
        exp_ret = '##.................. 10%'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_with_spinner(self):
        pc = PercCounter(total=50, perc_bar_length=20)
        tmp_ret = pc.perc_bar(5, bar_format='[{spinner}] {left_bar}')
        exp_ret = '[/] ##..................'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_complex(self):
        pc = PercCounter(total=50, current=40, perc_bar_length=20)
        tmp_ret = pc.perc_bar(5, bar_format='{perc} {foobar} snafu', foobar='FOOBAR')
        exp_ret = '0.1 FOOBAR snafu'
        self.assertEqual(exp_ret, tmp_ret)

    def test_est_total_timedelta(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        pc = PercCounter(total=100, time_start=start_time)

        exp_time = timedelta(seconds=40)

        tmp_ret = pc.est_total_timedelta(current=25, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)

    def test_est_finish_timedelta(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        exp_time = timedelta(seconds=30)

        pc = PercCounter(total=100, time_start=start_time)

        tmp_ret = pc.est_finish_timedelta(current=25, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)

    def test_est_finish_time(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        exp_time = time_now + timedelta(seconds=40)

        pc = PercCounter(total=100, time_start=start_time)

        tmp_ret = pc.est_finish_time(current=25, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)


    def test_format(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)

        pc = PercCounter(total=100, current=25, time_start=start_time)

        tmp_ret = repr(pc)
        tmp_exp = 'PercCounter: Perc: 25.00% Current: 25 / Total: 100 Started: {start_time} Est_Fininh In: 0:00:30'.format(start_time=start_time)

        self.assertEqual(tmp_exp, tmp_ret)


class TestPercCounter(TestCase):
    def test_format_perc(self):
        self.assertEqual(0.1234, format_percentage(0.1234, perc_format=PERC_RET.AS_FLOAT))
        self.assertEqual(12, format_percentage(0.1234, perc_format=PERC_RET.AS_INT))
        self.assertEqual('12%', format_percentage(0.1234, perc_format=PERC_RET.AS_STR_INT))
        self.assertEqual('12.34%', format_percentage(0.1234, perc_format=PERC_RET.AS_STR_DOT_2))
        self.assertEqual('12.3%', format_percentage(0.1234, perc_format=PERC_RET.AS_STR_DOT_1))
        self.assertEqual(12.34, format_percentage(0.1234, perc_format=PERC_RET.AS_FLOAT_PERC))
        self.assertEqual('perc=0.1234', format_percentage(0.1234, perc_format='perc={perc}'))

    def test_make_perc(self):
        self.assertEqual(0.10, make_percentage(10, 100))

    def test_make_perc_format(self):
        self.assertEqual(10, make_percentage(10, 100, perc_format=PERC_RET.AS_INT))

    def test_make_perc_min_max(self):
        self.assertEqual(0.1, make_percentage(9, 100, min_perc=0.1, max_perc=1))
        self.assertEqual(1.0, make_percentage(110, 100, min_perc=0.1, max_perc=1))
        self.assertEqual(0.2, make_percentage(20, 100, min_perc=0.1, max_perc=1))

    def test_make_perc_raise_good(self):
        with self.assertRaises(ZeroDivisionError):
            make_percentage(10, 0, raise_on_div_zero=True)

    def test_make_perc_raise_bad(self):
        self.assertEqual(0, make_percentage(110, 0, raise_on_div_zero=False))

    def test_scaled_perc(self):
        self.assertEqual(5, scaled_perc(0.1, 50, as_int=True))
        self.assertEqual(5.25, scaled_perc(0.105, 50, as_int=False))

    def test_perc_bar_left(self):
        tmp_ret = perc_bar(0.1, length=20)
        exp_ret = '##..................'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_right(self):
        tmp_ret = perc_bar(0.1, length=20, bar_format='{right_bar}')
        exp_ret = '..................##'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_center(self):
        tmp_ret = perc_bar(0.22, length=20, bar_format='{center_bar}')
        exp_ret = '...#................'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_with_perc(self):
        tmp_ret = perc_bar(0.1, length=20, bar_format='{left_bar} {perc:.0%}')
        exp_ret = '##.................. 10%'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_with_spinner(self):
        tmp_ret = perc_bar(0.1, length=20, bar_format='[{spinner}] {left_bar}', spin_state=0)
        exp_ret = '[|] ##..................'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_complex(self):
        tmp_ret = perc_bar(0.1, length=20, bar_format='{perc} {foobar} snafu', foobar='FOOBAR')
        exp_ret = '0.1 FOOBAR snafu'
        self.assertEqual(exp_ret, tmp_ret)

    def test_est_total_timedelta(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        exp_time = timedelta(seconds=40)

        tmp_ret = est_total_timedelta(perc=0.25, start_time=start_time, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)

    def test_est_finish_timedelta(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        exp_time = timedelta(seconds=30)

        tmp_ret = est_finish_timedelta(perc=0.25, start_time=start_time, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)

    def test_est_finish_time(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        exp_time = time_now + timedelta(seconds=40)

        tmp_ret = est_finish_time(perc=0.25, start_time=start_time, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)


def math_list_test_func(value, **kwargs):
    return value * 2


class TestMathList(TestCase):

    def test_list_like_behaivior(self):

        ml = MathList()
        self.assertFalse(ml)
        self.assertEqual(len(ml), 0)
        ml.append(1)
        self.assertTrue(ml == [1])
        ml.extend([2, 3, 4])
        self.assertTrue([1, 2, 3, 4] == ml)
        self.assertTrue(3 == ml[2])
        ml[2] = 5
        self.assertTrue([1, 2, 5, 4] == ml)
        ml.reverse()
        self.assertFalse([1, 2, 5, 4] == ml)
        self.assertTrue([4, 5, 2, 1] == ml)

    def test_item_in_list(self):

        ml = MathList([1, 2, 3, 4])
        self.assertTrue(1 in ml)

    def test_sum(self):
        ml = MathList([1, 2, 3, 4])
        self.assertEqual(ml.sum, 10)
        self.assertFalse(ml.has_float)
        self.assertTrue(ml.has_int)
        self.assertFalse(ml.has_dec)

    def test_fsum(self):
        td = [1, 1e100, 1, -1e100] * 10000
        # print(sum(td))
        # print(fsum(td))
        ml = MathList(td)
        self.assertTrue(ml.has_float)
        self.assertTrue(ml.has_int)
        self.assertFalse(ml.has_dec)
        self.assertEqual(ml.sum, 20000.0)

    def test_min(self):
        ml = MathList([1, 2, 3, 4])
        self.assertEqual(ml.min, 1)

    def test_max(self):
        ml = MathList([1, 2, 3, 4])
        self.assertEqual(ml.max, 4)

    def test_mean(self):
        ml = MathList([1, 2, 3, 4])
        self.assertEqual(ml.mean, 2.5)

    def test_harmonic_mean(self):
        ml = MathList([2.5, 3, 10])
        self.assertEqual(ml.harmonic_mean, 3.6)

    def test_median(self):
        ml = MathList([1, 3, 5])
        self.assertEqual(ml.median, 3)
        ml.append(7)
        self.assertEqual(ml._cache_, {})
        self.assertEqual(ml.median, 4.0)

    def test_median_low(self):
        ml = MathList([1, 3, 5])
        self.assertEqual(ml.median_low, 3)
        ml.append(7)
        self.assertEqual(ml._cache_, {})
        self.assertEqual(ml.median_low, 3)

    def test_median_high(self):
        ml = MathList([1, 3, 5])
        self.assertEqual(ml.median_high, 3)
        ml.append(7)
        self.assertEqual(ml._cache_, {})
        self.assertEqual(ml.median_high, 5)

    def test_median_grouped(self):
        ml = MathList([52, 52, 53, 54])
        self.assertEqual(ml.median_grouped(), 52.5)

        ml = MathList([1, 2, 2, 3, 4, 4, 4, 4, 4, 5])
        self.assertEqual(ml.median_grouped(), 3.7)

        ml = MathList([1, 3, 3, 5, 7])
        self.assertEqual(ml.median_grouped(interval=1), 3.25)

        ml = MathList([1, 3, 3, 5, 7])
        self.assertEqual(ml.median_grouped(interval=2), 3.5)

    def test_mode(self):
        ml = MathList([1, 1, 2, 3, 3, 3, 3, 4])
        self.assertEqual(ml.mode, 3)

        ml = MathList([1, 2, 3, 4, 5])
        with self.assertRaises(statistics.StatisticsError):
            x = ml.mode

    def test_pstdev(self):
        ml = MathList([1.5, 2.5, 2.5, 2.75, 3.25, 4.75])
        self.assertEqual(ml.pstdev, 0.986893273527251)
        self.assertTrue(ml.has_float)
        self.assertFalse(ml.has_int)
        self.assertFalse(ml.has_dec)

    def test_pvariance(self):
        ml = MathList([0.0, 0.25, 0.25, 1.25, 1.5, 1.75, 2.75, 3.25])
        self.assertEqual(ml.pvariance, 1.25)

        ml = MathList([Decimal("27.5"), Decimal("30.25"), Decimal("30.25"), Decimal("34.5"), Decimal("41.75")])
        self.assertEqual(ml.pvariance, Decimal('24.815'))
        self.assertFalse(ml.has_float)
        self.assertFalse(ml.has_int)
        self.assertTrue(ml.has_dec)

    def test_stdev(self):
        ml = MathList([1.5, 2.5, 2.5, 2.75, 3.25, 4.75])
        self.assertEqual(ml.stdev, 1.0810874155219827)

    def test_variance(self):
        ml = MathList([2.75, 1.75, 1.25, 0.25, 0.5, 1.25, 3.5])
        self.assertEqual(ml.variance, 1.3720238095238095)

    def test_find_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61])
        self.assertEqual([300, 1, 78, 61], ml.list_outliers(include_outliers=ml.OUTLIERS.ALL_OUTLIERS))
        self.assertEqual([78, 61], ml.list_outliers(include_outliers=ml.OUTLIERS.MINOR_OUTLIERS))
        self.assertEqual([300, 1], ml.list_outliers(include_outliers=ml.OUTLIERS.MAJOR_OUTLIERS))
        self.assertEqual([], ml.list_outliers(include_outliers=ml.OUTLIERS.NO_OUTLIERS))
        self.assertEqual(ml.list_outliers(), [])
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=ml.OUTLIERS.ALL_OUTLIERS)
        self.assertEqual(ml.list_outliers(), [300, 1, 78, 61])

    def test_filter_all_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.ALL_OUTLIERS)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.sum, 776)
        self.assertEqual(len(ml), 11)
        self.assertEqual(ml.list_outliers(), [300, 1, 78, 61])

    def test_filter_no_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.NO_OUTLIERS)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.sum, 1216)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.list_outliers(), [])

    def test_filter_major_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.MAJOR_OUTLIERS)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.sum, 915)
        self.assertEqual(len(ml), 13)
        self.assertEqual(ml.list_outliers(), [300, 1])

        self.assertEqual(ml.list_outliers(include_outliers=ml.OUTLIERS.MINOR_OUTLIERS), [78, 61])
        self.assertEqual(ml.list_outliers(include_outliers=ml.OUTLIERS.MAJOR_OUTLIERS), [300, 1])
        self.assertEqual(ml.list_outliers(include_outliers=ml.OUTLIERS.ALL_OUTLIERS), [300, 1, 78, 61])
        self.assertEqual(ml.list_outliers(include_outliers=ml.OUTLIERS.NO_OUTLIERS), [])

        self.assertEqual(ml.sum, 915)
        self.assertEqual(len(ml), 13)
        self.assertEqual(ml.list_outliers(), [300, 1])

    def test_filter_minor_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.MINOR_OUTLIERS)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.sum, 776)
        self.assertEqual(len(ml), 11)
        self.assertEqual(ml.list_outliers(), [300, 1, 78, 61])

    def test_remove_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.ALL_OUTLIERS)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.list_outliers(), [300, 1, 78, 61])
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.sum, 776)
        self.assertEqual(len(ml), 11)
        self.assertEqual(len(ml._data), 15)
        ml.rem_outliers()
        self.assertEqual(len(ml), 11)
        self.assertEqual(len(ml._data), 11)
        self.assertEqual(ml.list_outliers(), [73])
        self.assertEqual(ml.sum, 703)
        self.assertEqual(len(ml), 10)
        self.assertEqual(len(ml._data), 11)


    def test_calc_list_basic(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.ALL_OUTLIERS)
        tmp_list = ml.calc_list()
        exp_list = [71, 70, 73, 70, 70, 69, 70, 72, 71, 71, 69]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_return_as_list(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(return_row_as='list')
        exp_list = [[1], [2], [3], [4]]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_return_as_list_auto(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['row_num', 'value'], return_row_as='list')
        exp_list = [[0, 1], [1, 2], [2, 3], [3, 4]]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_return_as_dict(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['row_num', 'value'], return_row_as='dict')
        exp_list = [{'row_num': 0, 'value': 1},
                    {'row_num': 1, 'value': 2},
                    {'row_num': 2, 'value': 3},
                    {'row_num': 3, 'value': 4}]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_return_as_object(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['row_num', 'value'], return_row_as=SimpleDataClass)
        self.assertEqual(0, tmp_list[0].row_num)
        self.assertEqual(1, tmp_list[0].value)

        self.assertEqual(1, tmp_list[1].row_num)
        self.assertEqual(2, tmp_list[1].value)

        self.assertEqual(2, tmp_list[2].row_num)
        self.assertEqual(3, tmp_list[2].value)

        self.assertEqual(3, tmp_list[3].row_num)
        self.assertEqual(4, tmp_list[3].value)

    def test_calc_list_return_as_named(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['row_num', 'value'], return_row_as='named')
        self.assertEqual(0, tmp_list[0].row_num)
        self.assertEqual(1, tmp_list[0].value)

        self.assertEqual(1, tmp_list[1].row_num)
        self.assertEqual(2, tmp_list[1].value)

        self.assertEqual(2, tmp_list[2].row_num)
        self.assertEqual(3, tmp_list[2].value)

        self.assertEqual(3, tmp_list[3].row_num)
        self.assertEqual(4, tmp_list[3].value)

    def test_calc_list_format_dict(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_sum'], format_dict={'running_sum': '{}'})
        exp_list = ['1', '3', '6', '10']
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_func_dict(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_sum'], format_dict={'running_sum': '{}'}, func_dict={'running_sum': math_list_test_func})
        exp_list = ['2', '6', '12', '20']
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_row_offset(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['row_num', 'value'], row_num_offset=1)
        exp_list = [[1, 1], [2, 2], [3, 3], [4, 4]]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_start_end(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_sum'], start_at=1, end_at=3)
        exp_list = [3, 6]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_force_total(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], force_total=20)
        exp_list = [5, 15, 30, 50]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_int(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'])
        exp_list = [10, 30, 60, 100]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_float(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], perc_return=PERC_RET.AS_FLOAT)
        exp_list = [0.1, 0.3, 0.6, 1.0]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_float_perc(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], perc_return=PERC_RET.AS_FLOAT_PERC)
        exp_list = [10.0, 30.0, 60.0, 100.0]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_str(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], perc_return=PERC_RET.AS_STR_INT)
        exp_list = ['10%', '30%', '60%', '100%']
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_str_2(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], perc_return=PERC_RET.AS_STR_DOT_2)
        exp_list = ['10.00%', '30.00%', '60.00%', '100.00%']
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_format(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], perc_return={'running_perc_value_done':'perc: {0:.1f}'})
        exp_list = ['perc: 0.1','perc: 0.3','perc: 0.6','perc: 1.0']
        self.assertListEqual(exp_list, tmp_list)

    def test_running_perc_rows_done_headers(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['value', 'perc_rows_done', 'running_perc_value_done'], perc_return={'running_perc_value_done':'perc: {0:.1f}'}, inc_header=True)
        exp_list = [['value', 'perc_rows_done', 'running_perc_value_done'],[1, 25, 'perc: 0.1'],[2, 50, 'perc: 0.3'],[3, 75, 'perc: 0.6'],[4, 100, 'perc: 1.0']]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_perc_rows_done(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list('perc_rows_done')
        exp_list = [25, 50, 75, 100]
        self.assertListEqual(exp_list, tmp_list)

    def test_perc_of_total(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['perc_of_total'])
        exp_list = [10, 20, 30, 40]
        self.assertListEqual(exp_list, tmp_list)

    def test_difference_from_mean(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['difference_from_mean'])
        exp_list = [-1.5, -0.5, .5, 1.5]
        self.assertListEqual(exp_list, tmp_list)

    def test_difference_from_median(self):
        ml = MathList([1, 2, 5, 3, 4])
        tmp_list = ml.calc_list(['difference_from_median'])
        exp_list = [-2, -1, 2, 0, 1]
        self.assertListEqual(exp_list, tmp_list)

    def test_outlier_flag(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.NO_OUTLIERS)
        tmp_list = ml.calc_list(['outlier_flag'])
        exp_list = ['', '', '', '', '', '', '', '', '', 'major', '', '', 'major', 'minor', 'minor']
        self.assertListEqual(exp_list, tmp_list)

    def test_running_mean(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_mean'])
        exp_list = [1.0, 1.5, 2, 2.5]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_median(self):
        ml = MathList([1, 2, 3, 4, 5])
        tmp_list = ml.calc_list(['running_median'])
        exp_list = [1.0, 1.5, 2.0, 2.5, 3]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_max(self):
        ml = MathList([1, 3, 2, 4])
        tmp_list = ml.calc_list(['running_max'])
        exp_list = [1, 3, 3, 4]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_min(self):
        ml = MathList([3, 2, 4, 1])
        tmp_list = ml.calc_list(['running_min'])
        exp_list = [3, 2, 2, 1]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_change(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_change'])
        exp_list = [1, 1, 1, 1]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_perc_change(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_change'])
        exp_list = [100, 100, 50, 33]
        self.assertListEqual(exp_list, tmp_list)

    def test_interval(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61])
        tmp_list = ml.calc_list(interval=4)
        exp_list = [70, 72, 69]
        self.assertListEqual(exp_list, tmp_list)

'''
THIRTY_THREE = 1 / 3
THIRTY_THREE_PERC = THIRTY_THREE * 100
THREE_ONES = [1, 1, 1]

class MathListRecordsTest(TestCase):


    def run_records_tests(self):

        if self.load_on_init:
            mlr = MathListRecords(self.data_array, value_fields=self.value_fields, group_fields=self.group_fields, **self.mlr_kwargs)

        else:
            mlr = MathListRecords(value_fields=self.value_fields, group_fields=self.group_fields, **self.mlr_kwargs)

            with self.subTest('pre_test_len'):
                self.assertEqual(0, len(mlr))

            with self.subTest('pre_test_bool'):
                self.assertFalse(mlr)

            if self.add_recs_as_list:
                mlr.add_rec_list(self.data_array)
            else:
                for rec in self.data_array:
                    mlr.add_rec(rec)

        with self.subTest('test_len'):
            self.assertEqual(self.exp_len, len(mlr))

        with self.subTest('test_bool'):
            self.assertTrue(mlr)

        for test in self.my_tests:
            with self.subTest(test['name']):

                if test['command'] == '__getitem__':
                    if test['raises'] is not None:
                        with self.assertRaises(test['raises']):
                            tmp_ret = mlr[test['args'][0]]
                    else:
                        tmp_ret = mlr[test['args'][0]]
                        self.assertEqual(test['expected'], tmp_ret)

                else:
                    test_command = getattr(mlr, test['command'])
                    if test['raises'] is not None:
                        with self.assertRaises(test['raises']):
                            test_command(*test['args'], **test['kwargs'])
                    else:
                        tmp_ret = test_command(*test['args'], **test['kwargs'])
                        self.assertEqual(test['expected'], tmp_ret)



    def setUp(self):
        self.data_array = []
        self.value_fields = None
        self.group_fields = None
        self.mlr_kwargs = {}
        self.exp_len = None
        self.load_on_init = True
        self.add_recs_as_list = False
        """
                      
 
        get_record_list_as_list = {
            'name': 'get_record_list_as_list',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'list'},
             'args': [],
             'raises': None,
             'expected': {},
             },

        get_record_list_as_dict = {
            'name': 'get_record_list_as_dict',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'dict'},
             'args': [],
             'raises': None,
             'expected': {},
             },

        get_record_list_as_flat_list = {
            'name': 'get_record_list_as_flat_list',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'list', 'flat': True},
             'args': [],
             'raises': None,
             'expected': {},
             },

        get_calc_list = {
            'name': 'get_calc_list',
             'command': 'get_calc_list',
             'kwargs': {},
             'args': [],
             'raises': None,
             'expected': {},
             },
            
        get_calc_list_flat = {
            'name': 'get_calc_list_flat',
             'command': 'get_calc_list',
             'kwargs': {'flat': True},
             'args': [],
             'raises': None,
             'expected': {},
             },

        get_aggregate = {
            'name': 'get_aggregate',
             'command': 'get_aggregate',
             'kwargs': {},
             'args': [],
             'raises': None,
             'expected': {},
             },

        get_item = (
            'name': '__getitem__',
             'command': '__getitem__',
             'kwargs': {},
             'args': [],
             'raises': None,
             'expected': {},
             },

        
        
        self.my_tests = [
            get_calc_list,
            get_calc_list_flat,
            get_record_list_as_list,
            get_record_list_as_dict,
            get_record_list_as_flat_list,
            get_aggregate,
            get_item,
        ]

        """
        self.my_tests = []

    def test_records_no_fields(self):

        # output_items = '0__running_sum'

        self.data_array = [
            (1, 60, 40),
            (2, 70, 50),
            (3, 80, 60),
            (4, 90, 70),
        ]

        self.value_fields = None
        self.group_fields = None
        self.mlr_kwargs = {}
        self.exp_len = 4
        self.load_on_init = False
        self.add_recs_as_list = False

        get_record_list_as_list = {
            'name': 'get_record_list_as_list',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'list'},
             'args': [],
             'raises': None,
             'expected': [1, 3, 6, 10],
             },

        get_record_list_as_dict = {
            'name': 'get_record_list_as_dict',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'dict'},
             'args': [],
             'raises': None,
             'expected': {0: [1, 3, 6, 10]},
             },

        get_record_list_as_flat_list = {
            'name': 'get_record_list_as_flat_list',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'list', 'flat': True},
             'args': [],
             'raises': None,
             'expected': [1, 3, 6, 10],
             },

        get_calc_list = {
            'name': 'get_calc_list',
             'command': 'get_calc_list',
             'kwargs': {},
             'args': [],
             'raises': None,
             'expected': [1, 3, 6, 10],
             },

        get_calc_list_flat = {
            'name': 'get_calc_list_flat',
             'command': 'get_calc_list',
             'kwargs': {'flat': True},
             'args': [],
             'raises': None,
             'expected': [1, 3, 6, 10],
             },

        get_aggregate = {
            'name': 'get_aggregate',
             'command': 'get_aggregate',
             'kwargs': {},
             'args': [],
             'raises': None,
             'expected': 10,
             },

        get_item = {
            'name': '__getitem__',
             'command': '__getitem__',
             'kwargs': {},
             'args': [0],
             'raises': None,
             'expected': 1,
             },

        self.my_tests = [
            get_calc_list,
            get_calc_list_flat,
            get_record_list_as_list,
            get_record_list_as_dict,
            get_record_list_as_flat_list,
            get_aggregate,
            get_item,
        ]


    def dummy_test_method(self):
        self.data_array = [
            (1, 60, 40),
            (2, 70, 50),
            (3, 80, 60),
            (4, 90, 70),
        ]

        self.value_fields = None
        self.group_fields = None
        self.mlr_kwargs = {}
        self.exp_len = 4
        self.load_on_init = True
        self.add_recs_as_list = False

        output_items = [
            '0__running_sum',
            ]

        get_record_list_as_list = {
            'name': 'get_record_list_as_list',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'list'},
             'args': [output_items],
             'raises': None,
             'expected': {},
             },

        get_record_list_as_dict = {
            'name': 'get_record_list_as_dict',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'dict'},
             'args': [output_items],
             'raises': None,
             'expected': {},
             },

        get_record_list_as_flat_list = {
            'name': 'get_record_list_as_flat_list',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'list', 'flat': True},
             'args': [output_items],
             'raises': None,
             'expected': {},
             },

        get_calc_list = {
            'name': 'get_calc_list',
             'command': 'get_calc_list',
             'kwargs': {},
             'args': [output_items],
             'raises': None,
             'expected': {},
             },

        get_calc_list_flat = {
            'name': 'get_calc_list_flat',
             'command': 'get_calc_list',
             'kwargs': {'flat': True},
             'args': [output_items],
             'raises': None,
             'expected': {},
             },


        get_aggregate = {
            'name': 'get_aggregate',
             'command': 'get_aggregate',
             'kwargs': {},
             'args': [],
             'raises': None,
             'expected': {},
             },

        get_item = {
            'name': '__getitem__',
             'command': '__getitem__',
             'kwargs': {},
             'args': [],
             'raises': None,
             'expected': {},
             },

        self.my_tests = [
            get_record_list_as_list,
            get_record_list_as_dict,
            get_record_list_as_flat_list,
            get_calc_list,
            get_calc_list_flat,
            get_aggregate,
            get_item,
        ]


    def test_records_index_fields(self):
        self.data_array = [
            (1, 6, 4),
            (2, 7, 5),
            (3, 8, 6),
            (4, 9, 7),
        ]

        output_items = [
            '0__running_sum',
            '1__running_sum',
            '2__perc_ot_total',
            '0__perc_of_total',
        ]

        self.value_fields = [0, 1, 2]
        self.group_fields = None
        self.mlr_kwargs = {}
        self.exp_len = 4
        self.load_on_init = False
        self.add_recs_as_list = True

        get_record_list_as_list = {
            'name': 'get_record_list_as_list',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'list'},
             'args': [output_items],
             'raises': None,
             'expected': [
                (1, 6, 0, 10),
                (3, 13, 0, 30),
                (6, 21, 0, 60),
                (10, 30, 0, 100)],
             },

        get_record_list_as_dict = {
            'name': 'get_record_list_as_dict',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'dict'},
             'args': [output_items],
             'raises': None,
             'expected': {
                 0: (1, 6, 0, 10),
                 1: (3, 13, 0, 30),
                 2: (6, 21, 0, 60),
                 3: (10, 30, 0, 100)},
             },

        get_record_list_as_flat_list = {
            'name': 'get_record_list_as_flat_list',
             'command': 'get_record_list',
             'kwargs': {'ret_as': 'list', 'flat': True},
             'args': ['0__running_sum'],
             'raises': None,
             'expected': None
             },

        get_calc_list = {
            'name': 'get_calc_list',
             'command': 'get_calc_list',
             'kwargs': {},
             'args': [output_items],
             'raises': None,
             'expected': {
                 '0__running_sum': [1, 2, 6, 10],
                 '1__running_sum': [6, 13, 21, 30],
                 '2__perc_of_total': [0, 0, 0, 0],
                 '0__perc_of_total': [10, 30, 60, 100],
             },
             },

        get_calc_list_flat = {
            'name': 'get_calc_list_flat',
             'command': 'get_calc_list',
             'kwargs': {'flat': True},
             'args': [output_items],
             'raises': None,
             'expected': {},
             },


        get_aggregate = {
            'name': 'get_aggregate',
             'command': 'get_aggregate',
             'kwargs': {},
             'args': [],
             'raises': None,
             'expected': {},
             },

        get_item = {
            'name': '__getitem__',
             'command': '__getitem__',
             'kwargs': {},
             'args': [],
             'raises': None,
             'expected': {},
             },

        self.my_tests = [
            get_record_list_as_list,
            get_record_list_as_dict,
            get_record_list_as_flat_list,
            get_calc_list,
            get_calc_list_flat,
            get_aggregate,
            get_item,
        ]





    def test_records_no_groups_muly_value(self):
        data_array = [
            {'v1': 1, 'v2': 6, 'v3': 4},
            {'v1': 2, 'v2': 7, 'v3': 5},
            {'v1': 3, 'v2': 8, 'v3': 6},
            {'v1': 4, 'v2': 9, 'v3': 7},
        ]

        mlr = MathListRecords(data_array, value_fields=['v1', 'v2', 'v3'])

        output_items = [
            'v1__value',
            'v1__running_sum',
            'v3__running_sum',
            'v3__perc_ot_total',
            'v1__perc_of_total',
        ]

        exp_ret_rec_list = [
            (1, 1, 6, 0, 10),
            (2, 3, 13, 0, 30),
            (3, 6, 21, 0, 60),
            (4, 10, 30, 0, 100),
        ]

        with self.subTest('exp_ret_rec_list'):
            tmp_act = mlr.get_record_list(output_items)
            self.assertListEqual(exp_ret_rec_list, tmp_act)

        exp_ret_rec_dict = [
            {'v1__value': 1, 'v1__running_sum': 1, 'v2__running_sum': 6, 'v3__perc_of_total': 0, 'v1__perc_of_total': 10},
            {'v1__value': 2, 'v1__running_sum': 3, 'v2__running_sum': 13, 'v3__perc_of_total': 0, 'v1__perc_of_total': 30},
            {'v1__value': 3, 'v1__running_sum': 6, 'v2__running_sum': 21, 'v3__perc_of_total': 0, 'v1__perc_of_total': 60},
            {'v1__value': 4, 'v1__running_sum': 10, 'v2__running_sum': 30, 'v3__perc_of_total': 0, 'v1__perc_of_total': 100},
        ]

        with self.subTest('exp_ret_rec_dict'):
            tmp_act = mlr.get_record_list(output_items, ret_as='dict')
            self.assertListEqual(exp_ret_rec_dict, tmp_act)

        exp_ret_list = {
            'v1__value': [1, 2, 3, 4],
            'v1__running_sum': [1, 3, 6, 10],
            'v2__running_sum': [6, 13, 21, 30],
            'v3__perc_of_total': [0, 0, 0, 0],
            'v1__perc_of_total': [10, 30, 60, 100],
        }

        with self.subTest('exp_ret_list'):
            tmp_act = mlr.get_calc_list(output_items)
            self.assertListEqual(exp_ret_list, tmp_act)


    def test_records_no_groups_single_values(self):
        data_array = [
            {'v1': 1, 'v2': 6, 'v3': 4},
            {'v1': 2, 'v2': 7, 'v3': 5},
            {'v1': 3, 'v2': 8, 'v3': 6},
            {'v1': 4, 'v2': 9, 'v3': 7},
        ]
        mlr = MathListRecords(data_array, value_fields=['v1', 'v2', 'v3'])

        output_items = 'v1__running_sum'

        exp_ret_rec_list_flat = [1, 3, 6, 10]

        with self.subTest('exp_ret_rec_list_flat'):
            tmp_act = mlr.get_record_list(output_items, flat=True)
            self.assertListEqual(exp_ret_rec_list_flat, tmp_act)

        exp_ret_rec_list = [[1], [3], [6], [10]]

        with self.subTest('exp_ret_rec_list'):
            tmp_act = mlr.get_record_list(output_items)
            self.assertListEqual(exp_ret_rec_list, tmp_act)

        exp_ret_rec_dict = [
            {'v1__running_sum': 1},
            {'v1__running_sum': 3},
            {'v1__running_sum': 6},
            {'v1__running_sum': 10}
        ]
        
        with self.subTest('exp_ret_rec_dict'):
            tmp_act = mlr.get_record_list(output_items, ret_as='dict')
            self.assertListEqual(exp_ret_rec_dict, tmp_act)

        exp_ret_list = {
            'v1__running_sum': [1, 2, 6, 10],
        }

        with self.subTest('exp_ret_list'):
            tmp_act = mlr.get_calc_list(output_items)
            self.assertListEqual(exp_ret_list, tmp_act)

    def test_records_one_group(self):
        data_array = [
            {'group_val_1': 'one', 'v1': 1, 'v2': 6, 'v3': 4},
            {'group_val_1': 'one', 'v1': 2, 'v2': 7, 'v3': 5},
            {'group_val_1': 'one', 'v1': 3, 'v2': 8, 'v3': 6},
            {'group_val_1': 'one', 'v1': 4, 'v2': 9, 'v3': 7},

            {'group_val_1': 'two', 'v1': 1, 'v2': 6, 'v3': 4},
            {'group_val_1': 'two', 'v1': 2, 'v2': 7, 'v3': 5},
            {'group_val_1': 'two', 'v1': 3, 'v2': 8, 'v3': 6},
            {'group_val_1': 'two', 'v1': 4, 'v2': 9, 'v3': 7},

            {'group_val_1': 'three', 'v1': 1, 'v2': 6, 'v3': 4},
            {'group_val_1': 'three', 'v1': 2, 'v2': 7, 'v3': 5},
            {'group_val_1': 'three', 'v1': 3, 'v2': 8, 'v3': 6},
            {'group_val_1': 'three', 'v1': 4, 'v2': 9, 'v3': 7},
        ]

        mlr = MathListRecords(data_array, value_fields=['v1', 'v2', 'v3'], group_fields='group_val_1')

        output_items = [
            'v1__value',
            'v1__running_sum',
            'v3__running_sum',
            'v3__perc_ot_total',
            'v1__perc_of_total',
        ]

        with self.assertRaises(AttributeError):        
            tmp_act = mlr.get_record_list(output_items, ret_as='list')

        exp_ret_rec_dict = [
            {'group_val_1': 'one', 'v1__value': 1, 'v1__running_sum': 1, 'v2__running_sum': 6, 'v3__perc_of_total': 0, 'v1__perc_of_total': 10},
            {'group_val_1': 'one', 'v1__value': 2, 'v1__running_sum': 3, 'v2__running_sum': 13, 'v3__perc_of_total': 0, 'v1__perc_of_total': 30},
            {'group_val_1': 'one', 'v1__value': 3, 'v1__running_sum': 6, 'v2__running_sum': 21, 'v3__perc_of_total': 0, 'v1__perc_of_total': 60},
            {'group_val_1': 'one', 'v1__value': 4, 'v1__running_sum': 10, 'v2__running_sum': 30, 'v3__perc_of_total': 0, 'v1__perc_of_total': 100},

            {'group_val_1': 'two', 'v1__value': 1, 'v1__running_sum': 1, 'v2__running_sum': 6, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 10},
            {'group_val_1': 'two', 'v1__value': 2, 'v1__running_sum': 3, 'v2__running_sum': 13, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 30},
            {'group_val_1': 'two', 'v1__value': 3, 'v1__running_sum': 6, 'v2__running_sum': 21, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 60},
            {'group_val_1': 'two', 'v1__value': 4, 'v1__running_sum': 10, 'v2__running_sum': 30, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 100},

            {'group_val_1': 'three', 'v1__value': 1, 'v1__running_sum': 1, 'v2__running_sum': 6, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 10},
            {'group_val_1': 'three', 'v1__value': 2, 'v1__running_sum': 3, 'v2__running_sum': 13, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 30},
            {'group_val_1': 'three', 'v1__value': 3, 'v1__running_sum': 6, 'v2__running_sum': 21, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 60},
            {'group_val_1': 'three', 'v1__value': 4, 'v1__running_sum': 10, 'v2__running_sum': 30, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 100},
        ]

        with self.subTest('exp_ret_rec_dict'):
            tmp_act = mlr.get_record_list(output_items, ret_as='dict')
            self.assertListEqual(exp_ret_rec_dict, tmp_act)

        exp_ret_list = {
            'v1__value': {'one': [1, 2, 3, 4], 'two': [1, 2, 3, 4], 'three': [1, 2, 3, 4]},
            'v1__running_sum': {'one': [1, 3, 6, 10], 'two': [1, 3, 6, 10], 'three': [1, 3, 6, 10]},
            'v2__running_sum': {'one': [6, 13, 21, 30], 'two': [6, 13, 21, 30], 'three': [6, 13, 21, 30]},
            'v3__perc_of_total': {'one': [0, 0, 0, 0], 'two': [0, 0, 0, 0], 'three': [0, 0, 0, 0]},
            'v1__perc_of_total': {'one': [10, 30, 60, 100], 'two': [10, 30, 60, 100], 'three': [10, 30, 60, 100]},
        }

        with self.subTest('exp_ret_list'):
            tmp_act = mlr.get_calc_list(output_items)
            self.assertEqual(exp_ret_list, tmp_act)

        with self.assertRaises(AssertionError):
            tmp_act = mlr.get_calc_list(output_items, flat=True)


    def test_records_mult_gorups(self):
        data_array = [
            {'group_val_1': 'one', 'group_val_2': '1', 'v1': 1, 'v2': 6, 'v3': 4},
            {'group_val_1': 'one', 'group_val_2': '1', 'v1': 2, 'v2': 7, 'v3': 5},
            {'group_val_1': 'one', 'group_val_2': '1', 'v1': 3, 'v2': 8, 'v3': 6},
            {'group_val_1': 'one', 'group_val_2': '1', 'v1': 4, 'v2': 9, 'v3': 7},

            {'group_val_1': 'two', 'group_val_2': '1', 'v1': 1, 'v2': 6, 'v3': 4},
            {'group_val_1': 'two', 'group_val_2': '1', 'v1': 2, 'v2': 7, 'v3': 5},
            {'group_val_1': 'two', 'group_val_2': '1', 'v1': 3, 'v2': 8, 'v3': 6},
            {'group_val_1': 'two', 'group_val_2': '1', 'v1': 4, 'v2': 9, 'v3': 7},

            {'group_val_1': 'three', 'group_val_2': '1', 'v1': 1, 'v2': 6, 'v3': 4},
            {'group_val_1': 'three', 'group_val_2': '1', 'v1': 2, 'v2': 7, 'v3': 5},
            {'group_val_1': 'three', 'group_val_2': '1', 'v1': 3, 'v2': 8, 'v3': 6},
            {'group_val_1': 'three', 'group_val_2': '1', 'v1': 4, 'v2': 9, 'v3': 7},


            {'group_val_1': 'one', 'group_val_2': '2', 'v1': 1, 'v2': 6, 'v3': 4},
            {'group_val_1': 'one', 'group_val_2': '2', 'v1': 2, 'v2': 7, 'v3': 5},
            {'group_val_1': 'one', 'group_val_2': '2', 'v1': 3, 'v2': 8, 'v3': 6},
            {'group_val_1': 'one', 'group_val_2': '2', 'v1': 4, 'v2': 9, 'v3': 7},

            {'group_val_1': 'two', 'group_val_2': '2', 'v1': 1, 'v2': 6, 'v3': 4},
            {'group_val_1': 'two', 'group_val_2': '2', 'v1': 2, 'v2': 7, 'v3': 5},
            {'group_val_1': 'two', 'group_val_2': '2', 'v1': 3, 'v2': 8, 'v3': 6},
            {'group_val_1': 'two', 'group_val_2': '2', 'v1': 4, 'v2': 9, 'v3': 7},

            {'group_val_1': 'three', 'group_val_2': '2', 'v1': 1, 'v2': 6, 'v3': 4},
            {'group_val_1': 'three', 'group_val_2': '2', 'v1': 2, 'v2': 6, 'v3': 5},
            {'group_val_1': 'three', 'group_val_2': '2', 'v1': 3, 'v2': 7, 'v3': 6},
            {'group_val_1': 'three', 'group_val_2': '2', 'v1': 4, 'v2': 8, 'v3': 7},

        ]

        mlr = MathListRecords(data_array, value_fields=['v1', 'v2', 'v3'], group_fields=['group_val_2', 'group_val_1'])

        output_items = [
            'v1__value',
            'v1__running_sum',
            'v3__running_sum',
            'v3__perc_ot_total',
            'v1__perc_of_total',
        ]

        with self.assertRaises(AttributeError):        
            tmp_act = mlr.get_record_list(output_items, ret_as='list')

        exp_ret_rec_dict = [
            {'group_val_2': '1', 'group_val_1': 'one', 'v1__value': 1, 'v1__running_sum': 1, 'v2__running_sum': 6, 'v3__perc_of_total': 0, 'v1__perc_of_total': 10},
            {'group_val_2': '1', 'group_val_1': 'one', 'v1__value': 2, 'v1__running_sum': 3, 'v2__running_sum': 13, 'v3__perc_of_total': 0, 'v1__perc_of_total': 30},
            {'group_val_2': '1', 'group_val_1': 'one', 'v1__value': 3, 'v1__running_sum': 6, 'v2__running_sum': 21, 'v3__perc_of_total': 0, 'v1__perc_of_total': 60},
            {'group_val_2': '1', 'group_val_1': 'one', 'v1__value': 4, 'v1__running_sum': 10, 'v2__running_sum': 30, 'v3__perc_of_total': 0, 'v1__perc_of_total': 100},

            {'group_val_2': '1', 'group_val_1': 'two', 'v1__value': 1, 'v1__running_sum': 1, 'v2__running_sum': 6, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 10},
            {'group_val_2': '1', 'group_val_1': 'two', 'v1__value': 2, 'v1__running_sum': 3, 'v2__running_sum': 13, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 30},
            {'group_val_2': '1', 'group_val_1': 'two', 'v1__value': 3, 'v1__running_sum': 6, 'v2__running_sum': 21, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 60},
            {'group_val_2': '1', 'group_val_1': 'two', 'v1__value': 4, 'v1__running_sum': 10, 'v2__running_sum': 30, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 100},

            {'group_val_2': '1', 'group_val_1': 'three', 'v1__value': 1, 'v1__running_sum': 1, 'v2__running_sum': 6, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 10},
            {'group_val_2': '1', 'group_val_1': 'three', 'v1__value': 2, 'v1__running_sum': 3, 'v2__running_sum': 13, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 30},
            {'group_val_2': '1', 'group_val_1': 'three', 'v1__value': 3, 'v1__running_sum': 6, 'v2__running_sum': 21, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 60},
            {'group_val_2': '1', 'group_val_1': 'three', 'v1__value': 4, 'v1__running_sum': 10, 'v2__running_sum': 30, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 100},

            {'group_val_2': '2', 'group_val_1': 'one', 'v1__value': 1, 'v1__running_sum': 1, 'v2__running_sum': 6, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 10},
            {'group_val_2': '2', 'group_val_1': 'one', 'v1__value': 2, 'v1__running_sum': 3, 'v2__running_sum': 13, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 30},
            {'group_val_2': '2', 'group_val_1': 'one', 'v1__value': 3, 'v1__running_sum': 6, 'v2__running_sum': 21, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 60},
            {'group_val_2': '2', 'group_val_1': 'one', 'v1__value': 4, 'v1__running_sum': 10, 'v2__running_sum': 30, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 100},

            {'group_val_2': '2', 'group_val_1': 'two', 'v1__value': 1, 'v1__running_sum': 1, 'v2__running_sum': 6, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 10},
            {'group_val_2': '2', 'group_val_1': 'two', 'v1__value': 2, 'v1__running_sum': 3, 'v2__running_sum': 13, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 30},
            {'group_val_2': '2', 'group_val_1': 'two', 'v1__value': 3, 'v1__running_sum': 6, 'v2__running_sum': 21, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 60},
            {'group_val_2': '2', 'group_val_1': 'two', 'v1__value': 4, 'v1__running_sum': 10, 'v2__running_sum': 30, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 100},

            {'group_val_2': '2', 'group_val_1': 'three', 'v1__value': 1, 'v1__running_sum': 1, 'v2__running_sum': 6, 'v3__perc_of_total': 0,
             'v1__perc_of_total': 10},
            {'group_val_2': '2', 'group_val_1': 'three', 'v1__value': 2, 'v1__running_sum': 3, 'v2__running_sum': 13,
             'v3__perc_of_total': 0,
             'v1__perc_of_total': 30},
            {'group_val_2': '2', 'group_val_1': 'three', 'v1__value': 3, 'v1__running_sum': 6, 'v2__running_sum': 21,
             'v3__perc_of_total': 0,
             'v1__perc_of_total': 60},
            {'group_val_2': '2', 'group_val_1': 'three', 'v1__value': 4, 'v1__running_sum': 10, 'v2__running_sum': 30,
             'v3__perc_of_total': 0,
             'v1__perc_of_total': 100},

        ]

        with self.subTest('exp_ret_rec_dict'):
            tmp_act = mlr.get_record_list(output_items, ret_as='dict')
            self.assertListEqual(exp_ret_rec_dict, tmp_act)

        exp_ret_list = {
            'v1__value': {
                'one': [1, 2, 3, 4], 'two': [1, 2, 3, 4], 'three': [1, 2, 3, 4]},
            'v1__running_sum': {
                'one': [1, 3, 6, 10], 'two': [1, 3, 6, 10], 'three': [1, 3, 6, 10]},
            'v2__running_sum': {
                'one': [6, 13, 21, 30], 'two': [6, 13, 21, 30], 'three': [6, 13, 21, 30]},
            'v3__perc_of_total': {
                'one': [0, 0, 0, 0], 'two': [0, 0, 0, 0], 'three': [0, 0, 0, 0]},
            'v1__perc_of_total': {
                'one': [10, 30, 60, 100], 'two': [10, 30, 60, 100], 'three': [10, 30, 60, 100]},
        }

        with self.subTest('exp_ret_list'):
            tmp_act = mlr.get_calc_list(output_items)
            self.assertListEqual(exp_ret_list, tmp_act)

        with self.assertRaises(AssertionError):
            tmp_act = mlr.get_calc_list(output_items, flat=True)
'''
'''
class GeneratePercTests(TestCase):
    def test_list_perc(self):
        data_array_1 = [1, 1, 1, 2, 1, 3, 1]
        test_res = generate_list_perc(data_array_1)
        self.assertListEqual(test_res, [10, 10, 10, 20, 10, 30, 10])

    def test_list_perc_2(self):
        test_res = generate_list_perc(THREE_ONES, ret_as=int, precision=2)
        self.assertListEqual(test_res, [33, 33, 33])

    def test_list_perc_float(self):
        test_res = generate_list_perc(THREE_ONES, ret_as=float, precision=2)
        self.assertListEqual(test_res, [THIRTY_THREE_PERC, THIRTY_THREE_PERC, THIRTY_THREE_PERC])

    def test_list_perc_float_perc(self):
        test_res = generate_list_perc(THREE_ONES, ret_as=float, precision=2, ret_perc=False)
        self.assertListEqual(test_res, [THIRTY_THREE, THIRTY_THREE, THIRTY_THREE])

    def test_list_perc_str_perc(self):
        test_res = generate_list_perc(THREE_ONES, ret_as=str, precision=2)
        self.assertListEqual(test_res, ['33.33%', '33.33%', '33.33%'])

    def test_list_perc_str_no_perc(self):
        test_res = generate_list_perc(THREE_ONES, ret_as=str, precision=2, ret_perc=False)
        self.assertListEqual(test_res, ['33.33', '33.33', '33.33'])

    def test_list_perc_str_no_perc_with_total(self):
        test_res = generate_list_perc(THREE_ONES, total=4, ret_as=str, precision=2, ret_perc=False)
        self.assertListEqual(test_res, ['25.00', '25.00', '25.00'])

    def test_generate_percentages_1(self):

        data_array = [
            [
                {'quarter': 1, 'measure': 1},
                {'quarter': 2, 'measure': 4},
                {'quarter': 3, 'measure': 500},
                {'quarter': 4, 'measure': 5.2234},
                {'quarter': 5, 'measure': 400},
                {'quarter': 6, 'measure': 0},
            ],
            [
                {'quarter': 1, 'measure': 4},
                {'quarter': 2, 'measure': 4},
                {'quarter': 3, 'measure': 5000},
                {'quarter': 4, 'measure': 5.0345},
                {'quarter': 5, 'measure': 401},
                {'quarter': 6, 'measure': 0}
            ],
           [
                {'quarter': 1, 'measure': 45},
                {'quarter': 2, 'measure': 4},
                {'quarter': 3, 'measure': 50000},
                {'quarter': 4, 'measure': 0},
                {'quarter': 5, 'measure': 402},
                {'quarter': 6, 'measure': 0},
           ],
           [
                {'quarter': 1, 'measure': 50},
                {'quarter': 2, 'measure': 4},
                {'quarter': 3, 'measure': 50000.0001},
                {'quarter': 4, 'measure': 10},
                {'quarter': 5, 'measure': 403},
                {'quarter': 6, 'measure': 0},
           ]

        ]

        result_array = [
            [
                {'quarter': 1, 'measure': 1, 'perc': 1.00},
                {'quarter': 2, 'measure': 4, 'perc': 25.00},
                {'quarter': 3, 'measure': 500, 'perc': 1.00},
                {'quarter': 4, 'measure': 5.2234, 'perc': 1.00},
                {'quarter': 5, 'measure': 400, 'perc': 25.00},
                {'quarter': 6, 'measure': 0, 'perc': 0.00},
            ],
            [
                {'quarter': 1, 'measure': 4, 'perc': 4.00},
                {'quarter': 2, 'measure': 4, 'perc': 25.00},
                {'quarter': 3, 'measure': 5000, 'perc': 1.00},
                {'quarter': 4, 'measure': 5.0345, 'perc': 1.00},
                {'quarter': 5, 'measure': 401, 'perc': 25.00},
                {'quarter': 6, 'measure': 0, 'perc': 0.00}
            ],
           [
                {'quarter': 1, 'measure': 45, 'perc': 45.00},
                {'quarter': 2, 'measure': 4, 'perc': 25.00},
                {'quarter': 3, 'measure': 50000, 'perc': 1.00},
                {'quarter': 4, 'measure': 0, 'perc': 1.00},
                {'quarter': 5, 'measure': 402, 'perc': 25.00},
                {'quarter': 6, 'measure': 0, 'perc': 0.00},
           ],
           [
                {'quarter': 1, 'measure': 50, 'perc': 50.00},
                {'quarter': 2, 'measure': 4, 'perc': 25.00},
                {'quarter': 3, 'measure': 50000.0001, 'perc': 1.00},
                {'quarter': 4, 'measure': 10, 'perc': 1.00},
                {'quarter': 5, 'measure': 403, 'perc': 25.00},
                {'quarter': 6, 'measure': 1, 'perc': 100.00},
           ]

        ]

        tmp_ret = generate_percentages(data_array,
                                       value_fieldname='measure',
                                       perc_fieldname='perc')

        for set_index, exp_set in enumerate(result_array):
            for index, expected in enumerate(exp_set):
                with self.subTest(f'{set_index}:{index}'):
                    test_item = tmp_ret[set_index][index]
                    exp_item = expected['perc']
                    self.assertEqual(exp_item, test_item)


    def test_generate_percentages_2(self):
        data_array = [{'key': 'A10',
                       'values': [{'quarter': 1, 'measure': 1}, 
                                  {'quarter': 2, 'measure': 4}, 
                                  {'quarter': 3, 'measure': 500}, 
                                  {'quarter': 4, 'measure': 5.2234}, 
                                  {'quarter': 5, 'measure': 400}, 
                                  {'quarter': 6, 'measure': 0}, ]}, 
                      {'key': 'Radware', 
                       'values': [{'quarter': 1, 'measure': 4}, 
                                  {'quarter': 2, 'measure': 4}, 
                                  {'quarter': 3, 'measure': 5000}, 
                                  {'quarter': 4, 'measure': 5.0345}, 
                                  {'quarter': 5, 'measure': 401}, 
                                  {'quarter': 6, 'measure': 0}, ]}, 
                      {'key': 'Citrix', 
                       'values': [{'quarter': 1, 'measure': 45}, 
                                  {'quarter': 2, 'measure': 4}, 
                                  {'quarter': 3, 'measure': 50000}, 
                                  {'quarter': 5, 'measure': 402},
                                  {'quarter': 6, 'measure': 0}, ]}, 
                      {'key': 'Brocade', 
                       'values': [{'quarter': 1, 'measure': 50}, 
                                  {'quarter': 2, 'measure': 4}, 
                                  {'quarter': 3, 'measure': 50000.0001}, 
                                  {'quarter': 4, 'measure': 10}, 
                                  {'quarter': 5, 'measure': 403}, 
                                  {'quarter': 6, 'measure': 0}, ]}, 

                      ]
        self.fail()

    def test_generate_percentages_3(self):

        data_array = [{'key': 'A10',
                       'values': [[1, 1], 
                                  [2, 4], 
                                  [3, 500], 
                                  [4, 5.2234], 
                                  [5, 400], 
                                  [6, 0], ]}, 
                      {'key': 'Radware', 
                       'values': [[1, 4], 
                                  [2, 4], 
                                  [3, 5000], 
                                  [4, 5.0345], 
                                  [5, 401], 
                                  [6, 0], ]}, 
                      {'key': 'Citrix', 
                       'values': [[1, 45], 
                                  [2, 4], 
                                  [3, 50000], 
                                  [4, 0], 
                                  [5, 402], 
                                  [6, 0], ]}, 
                      {'key': 'Brocade', 
                       'values': [[1, 50], 
                                  [2, 4], 
                                  [3, 50000.0001], 
                                  [4, 10], 
                                  [5, 403], 
                                  [6, 0], ]}, 

                      ]
        self.fail()

'''

class TmpClass(object):
    t1 = 1
    t9 = 9


class ArgsHandlerTestCase(TestCase): 
    def setUp(self): 

        self.tc = TmpClass()

        self.test_args = [1, 2, 3, 4]
        self.test_args_list_1 = ['t1', 't2', 't3', '_t4']
        self.test_kwargs = {'t5': 5, 't6': 6, 't7': 7, '_t8': 8}
        self.test_kwargs_ovr = {'t3': 33, '_t4': 44, 't5': 5, 't6': 6, 't7': 7, '_t8': 8}
        self.test_skip_list = ['t4', 't5']

        self.test_args_req = [1, 2, 4]
        self.test_args_list_req = ['t1', '*t2', 't3', '_t4', '*t6']
        self.test_kwargs_req = {'t5': 5, 't7': 7, '_t8': 8}




    def test_args_default(self): 
        args_handler(self.tc, self.test_args, self.test_args_list_1)
        self.assertEqual(self.tc.t2, 2)

    def test_kwargs_default(self): 
        args_handler(self.tc, kwargs=self.test_kwargs)
        self.assertEqual(self.tc.t5, 5)

    def test_both_default(self): 
        args_handler(self.tc, self.test_args, self.test_args_list_1, self.test_kwargs)
        self.assertEqual(self.tc.t2, 2)
        self.assertEqual(self.tc.t5, 5)

    def test_both_with_overlap(self): 
        args_handler(self.tc, self.test_args, self.test_args_list_1, self.test_kwargs_ovr)
        self.assertEqual(self.tc.t3, 33)
        self.assertEqual(self.tc.t5, 5)
        self.assertEqual(self.tc.t2, 2)

    def test_args_no_list_exception(self): 
        with self.assertRaises(AttributeError): 
            args_handler(self.tc, self.test_args)

    def test_both_skiplist(self): 
        args_handler(self.tc, self.test_args, self.test_args_list_1, self.test_kwargs, skip_list=self.test_skip_list)
        self.assertEqual(self.tc.t2, 2)
        self.assertEqual(self.tc.t6, 6)
        with self.assertRaises(AttributeError): 
            test = self.tc.t5

    def test_both_overwrite_default(self): 
        self.tc.t1 = 11
        args_handler(self.tc, self.test_args, self.test_args_list_1, self.test_kwargs, skip_list=self.test_skip_list)
        self.assertEqual(self.tc.t1, 1)

    def test_args_overwrite_false(self): 
        self.tc.t1 = 11
        args_handler(self.tc, self.test_args, self.test_args_list_1, skip_list=self.test_skip_list, overwrite=False)
        self.assertEqual(self.tc.t1, 11)


    def test_both_skip_startswith(self): 
        args_handler(self.tc, self.test_args, self.test_args_list_1, self.test_kwargs, skip_list=self.test_skip_list)
        self.assertEqual(self.tc.t2, 2)
        self.assertEqual(self.tc.t6, 6)
        with self.assertRaises(AttributeError): 
            test = self.tc.t4

    def test_both_class_attr_control(self): 
        self.tc._args_skip_list = self.test_skip_list
        args_handler(self.tc, self.test_args, self.test_args_list_1, self.test_kwargs)
        self.assertEqual(self.tc.t2, 2)
        self.assertEqual(self.tc.t6, 6)
        with self.assertRaises(AttributeError): 
            test = self.tc.t5

    def test_kwargs_class_attr_control_skip(self): 
        self.tc._args_skip_list = self.test_skip_list
        args_handler(self.tc, kwargs=self.test_kwargs, do_not_check_parent_attrs=True)
        self.assertEqual(self.tc.t5, 5)

    def test_both_required_raise(self): 
        with self.assertRaises(AttributeError): 
            args_handler(self.tc, self.test_args_req, self.test_args_list_req, self.test_kwargs_req)

    def test_both_with_default_args(self): 
        test_args = [1, 2, 4]
        test_args_list = [('t1', 11), '*t2', 't3', '_t4', ('t5', 55), ('*t6', 66)]
        test_kwargs = {'t6': 6, 't7': 7, '_t8': 8}

        args_handler(self.tc, test_args, test_args_list, test_kwargs)

        self.assertEqual(self.tc.t1, 1)
        self.assertEqual(self.tc.t5, 55)
        self.assertEqual(self.tc.t6, 6)


class TestAdvDict(TestCase): 

    def test_adv_dict_get(self): 
        tmp_dict = AdvDict()

        tmp_dict['t1'] = 'test1'
        tmp_dict['t2'] = 'test2'
        tmp_dict['t3'] = 'test3'
        tmp_dict['t4'] = 'test4'

        self.assertEqual(tmp_dict.key.t1, 'test1')
        self.assertEqual(tmp_dict.key.t2, 'test2')
        self.assertEqual(tmp_dict.key.t3, 'test3')

        with self.assertRaises(KeyError): 
            test = tmp_dict.key.bace

    def test_adv_dict_set(self): 
        tmp_dict = AdvDict(property_name='k')

        tmp_dict.k.t1 = 'test1'
        tmp_dict.k.t2 = 'test2'
        tmp_dict.k.t3 = 'test3'
        tmp_dict.k.t4 = 'test4'

        self.assertEqual(tmp_dict['t1'], 'test1')
        self.assertEqual(tmp_dict['t2'], 'test2')
        self.assertEqual(tmp_dict['t3'], 'test3')


class UnpackDemo(object): 
    t1 = '1'

    def args_demo(self, num1, num2): 
        return num1+num2

    def kwargs_demo(self, **kwargs): 
        n1 = kwargs['n1']
        n2 = kwargs['n2']
        return n1+n2


class UnpackDemo2(object): 
    t1 = '2'

    def args_demo(self, num1, num2): 
        return num1*num2

    def kwargs_demo(self, **kwargs): 
        n1 = kwargs['n1']
        n2 = kwargs['n2']
        return n1*n2


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



class TestTextUtils(TestCase): 

    def test_index_of_count(self): 
        test_string = 'This {is} a test {is} string'
        test_response = index_of_count(test_string, '{')
        self.assertEqual(5, test_response)

        test_response = index_of_count(test_string, '}', offset_count=2)
        self.assertEqual(20, test_response)


    def test_get_before(self): 
        test_string = 'This** is** a test string'
        test_response = get_before(test_string, '**')
        self.assertEqual('This', test_response)

        test_string = 'This** is** a This test string'
        test_response = get_before(test_string, '**', 2)
        self.assertEqual('This** is', test_response)


    def test_get_after(self): 
        test_string = 'This {is} a test (string This is a test string This is a test) string'
        test_response = get_after(test_string, ')')

        self.assertEqual(' string', test_response)

        test_response = get_after(test_string, ' test', 3)

        self.assertEqual(') string', test_response)

        test_response = get_after(test_string, 'a')

        self.assertEqual(' test (string This is a test string This is a test) string', test_response)

    def test_get_between(self): 
        test_string = 'This {is} a test {string This is a test string This is a test} string'
        test_response = get_between(test_string, '{', '}')
        self.assertEqual('is', test_response)

    def test_replace_between_01(self): 
        test_string = '...|{..}|....|'
        resp_string = replace_between(test_string, '{', '}', '++++')
        self.assertEqual('...|++++|....|', resp_string)

    def test_replace_between_02(self): 
        test_string = '...|{..}|....|....|{..}|....|'
        resp_string = replace_between(test_string, '{', '}', '++++')
        self.assertEqual('...|++++|....|....|++++|....|', resp_string)

    def test_replace_between_03(self): 
        test_string = '...|{...|....|'
        resp_string = replace_between(test_string, '{', '}', '++++')
        self.assertEqual('...|{...|....|', resp_string)

    def test_replace_between_04(self): 
        test_string = '...|}..{|....|'
        resp_string = replace_between(test_string, '{', '}', '++++')
        self.assertEqual('...|}..{|....|', resp_string)

    def test_replace_between_05(self): 
        test_string = '...|{..}|....|....|{..}|....|'
        resp_string = replace_between(test_string, '{', '}', '++++', count=1)
        self.assertEqual('...|++++|....|....|{..}|....|', resp_string)

    def test_replace_between_06(self): 
        test_string = '...|{..}|....|....|{..}|....|....|{..}|....|'
        resp_string = replace_between(test_string, '{', '}', '++++', count=1, offset_count=2)
        self.assertEqual('...|{..}|....|....|++++|....|....|{..}|....|', resp_string)

    def test_replace_between_07(self): 
        test_string = '...|{..}|....|....|{..}|....|'
        resp_string = replace_between(test_string, '{', '}', '++++', count=1, keep_keys=True)
        self.assertEqual('...|{++++}|....|....|{..}|....|', resp_string)



class TrimTests(TestCase): 
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


TEST_TREE_1 = [
               {'key': 'one', 
                'parent': '', 
                'children': [], 
                'name': 'name-one', 
                'lname': 'lanem-one', 
                'sal': 'sal-one'}, 


                 {'key': 'two', 
                'parent': '', 
                'children': [], 
                'name': 'name-two', 
                'lname': 'lanem-two', 
                'sal': 'sal-two'}, 

               {'key': 'three', 
                'parent': 'one', 
                'children': [], 
                'name': 'name-three', 
                'lname': 'lanem-three', 
                'sal': 'sal-three'}, 

                 {'key': 'four', 
                'parent': 'two', 
                'children': [], 
                'name': 'name-four', 
                'lname': 'lanem-four', 
                'sal': 'sal-four'}, 


                 {'key': 'five', 
                'parent': 'three', 
                'children': [], 
                'name': 'name-five', 
                'lname': 'lanem-five', 
                'sal': 'sal-five'}, 

               ]

def setup_tree(width, depth): 

    parent_string = ''
    tmp_tree = []

    for i in range(width): 
        tmp_node = {'key': str(i), 
                    'parent' : '', 
                    'children' : [], 
                    'other1' : 'test other item {}'.format(i)
                    }
        tmp_tree.append(tmp_node)
    return tmp_tree





