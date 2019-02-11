#!/usr/bin/env python

from unittest import TestCase
from PythonUtils.BaseUtils import args_handler


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

