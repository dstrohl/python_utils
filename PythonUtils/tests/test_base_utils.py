__author__ = 'dstrohl'

import copy
import sys

from unittest import TestCase
from PythonUtils.BaseUtils.base_utils import *

# from common.utils import generatePercentages
# from PythonUtils.ClassUtils.args_kwargs_handlers import args_handler


class UtilityTests(TestCase): 
    def test_generatePercentages(self): 

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
                                  {'quarter': 4, 'measure': 0}, 
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

        data_array_2 = [{'key': 'A10', 
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


        # generatePercentages(data_array, 'values', 'measure' , 'newfield')
        generate_percentages(data_array_2, 'values', 1)




        # self.assertEqual(str(tmpQuery), str(expected))


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


class MyTestCase(TestCase): 
    def test_swap(self): 
        self.assertEqual(swap(True), False)

    def test_swap_rev(self): 
        self.assertEqual(swap(False), True)

    def test_swap_str(self): 
        self.assertEqual(swap('yes', 'yes', 'no'), 'no')

    def test_swap_err(self): 
        with self.assertRaises(AttributeError): 
            swap('yes')


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



class TestFieldHandler(TestCase): 

    ff = None
    fields = []
    field_instrings = []

    default_dict = {
                    'max_length': None, 
                    'min_length': 10, 
                    'do_not_show_length': 4, 
                    'pad_to_max': False, 
                    'justification': 'left', 
                    'end_string': '', 
                    'padding_string': ' ', 
                    'trim_string': '+', 
                    'trim_priority': 1, }


    def load_data(self, 
                       counter = 0, 
                       init_size = 40, 
                       format_string = None, 
                       field_def = {}, 
                      ): 



        name = 'name_{}'.format(counter)
        if not format_string: 
            format_string = '{' + name + '}'
        in_string = 'name_'.ljust(init_size, '*')
        # print('in_string: ', in_string)
        # print('in_size: ', init_size)

        self.ff = FormatField(
                         name, 
                         format_string, 
                         field_def, 
                         initial_string = in_string
                        )


    def test_formatfield_full(self): 
        self.load_data(1)

        self.assertEqual(self.ff.length_ok, True)
        self.assertEqual(self.ff.curr_length, 40)


    def test_formatfield_20(self): 
        self.load_data(1)
        self.ff.max_length(20)
        self.assertEqual(self.ff.length_ok, False)

    def test_formatfield_mt(self): 
        self.load_data(1)
        self.ff._trim_me()
        self.assertEqual(self.ff.length_ok, True)
        self.assertEqual(self.ff.curr_length, 40)


    def test_formatfield_15(self): 
        self.load_data(1)
        self.ff._trim_me(15)
        self.assertEqual(self.ff.curr_length, 15)


    def test_formatfield_7(self): 
        self.load_data(1)
        self.ff._trim_me(7, True)
        self.assertEqual(self.ff.curr_length, 7)

    def test_formatfield_2(self): 
        self.load_data(1)
        self.ff._trim_me(2)
        self.assertEqual(self.ff.curr_length, 10)

    def test_formatfield_2_ignore_min(self): 
        self.load_data(1)
        self.ff._trim_me(2 , True)
        self.assertEqual(self.ff.curr_length, 0)


    def test_formatfield_pad_none(self): 
        self.load_data(1, 12)
        self.ff._pad_me()
        self.assertEqual(self.ff.curr_length, 12)

    def test_formatfield_pad_to_max_no_max(self): 
        self.load_data(1, 12)
        self.ff.pad_to_max = True
        self.ff._pad_me()
        self.assertEqual(self.ff.curr_length, 12)

    def test_formatfield_pad_to_max_max_40(self): 
        self.load_data(1, 12)
        self.ff.pad_to_max = True
        self.ff.max_length(40)
        self.ff.padding_string = '.'
        self.ff._pad_me()
        # print(self.ff)
        self.assertEqual(self.ff.curr_length, 40)
        self.assertEqual(self.ff.current_string, 'name_******* ...........................')

    def test_formatfield_pad_to_max_left(self): 
        self.load_data(1, 12)
        self.ff.pad_to_max = True
        self.ff.max_length(40)
        self.ff.padding_string = '.'
        self.ff.justification = 'left'
        self.ff._pad_me()
        # print(self.ff)
        self.assertEqual(self.ff.curr_length, 40)
        self.assertEqual(self.ff.current_string, 'name_******* ...........................')

    def test_formatfield_pad_to_max_right(self): 
        self.load_data(1, 12)
        self.ff.pad_to_max = True
        self.ff.max_length(40)
        self.ff.padding_string = '.'
        self.ff.justification = 'right'
        self.ff._pad_me()
        # print(self.ff)
        self.assertEqual(self.ff.curr_length, 40)
        self.assertEqual(self.ff.current_string, '........................... name_*******')

    def test_formatfield_pad_to_max_center(self): 
        self.load_data(1, 12)
        self.ff.pad_to_max = True
        self.ff.max_length(40)
        self.ff.padding_string = '.'
        self.ff.justification = 'center'
        self.ff._pad_me()
        # print(self.ff)
        self.assertEqual(self.ff.curr_length, 40)
        self.assertEqual(self.ff.current_string, '............. name_******* .............')



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





