#!/usr/bin/env python

"""
Tests for merger.py
"""

__author__ = "Dan Strohl"
__copyright__ = "Copyrigth 2019, Dan Strohl"

from unittest import TestCase
from PythonUtils.BaseUtils.merger import merge_object, BaseMergeHandler, MERGE_ACTION, merge_handler


class MergeHandlerFixture(BaseMergeHandler):
    name = 'test_fixture'
    action = MERGE_ACTION.KEEP
    path = 't1.1.t2.1.t3.*'

merge_handler.add_handler(MergeHandlerFixture)

class TestMergerManager(TestCase):

    def test_merge_object_dict(self):
        items_in = [
            {'t1': 1, 't2': 2},
            {'t2': 3, 't4': 4},
        ]
        exp_ret = {'t1': 1, 't2': 3, 't4': 4}

        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)

    def test_merge_object_list(self):
        items_in = [
            [1, 2, 3, 4],
            [5, 6, 7, 8, 9]
        ]
        exp_ret = [5, 6, 7, 8, 9]
        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)

    def test_merge_object_list_2(self):
        items_in = [
            [1, 2, 3, 4, 5],
            [5, 6, 7, 8]
        ]
        exp_ret = [5, 6, 7, 8, 5]
        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)

    def test_merge_object_str(self):
        items_in = ['foobar', 'snafu']
        exp_ret = 'snafu'
        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)

    def test_merge_object_list_in_dict(self):
        items_in = [
            {'t1': 1, 't2': 2, 'tl': [1, 2, 3, 4, 5]},
            {'t2': 3, 't4': 4, 'tl': [5, 6, 7, 8]},
        ]
        exp_ret = {'t1': 1, 't2': 3, 't4': 4, 'tl': [5, 6, 7, 8, 5]}

        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)

    def test_merge_object_dict_in_list(self):
        items_in = [
            [ {'t1': 1, 't2': 2}, 2, 3, 4, 5],
            [{'t2': 3, 't4': 4}, 5, 6, 7, 8],
        ]
        exp_ret = [{'t1': 1, 't2': 3, 't4': 4}, 5, 6, 7, 8]

        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)

    def test_merge_object_dict_in_dict(self):
        items_in = [
            {'t1': 1, 't2': {'t5.1': 51, 't5.2': 52}},
            {'t2':  {'t5.2': 55, 't5.3': 53}, 't4': 4},
        ]
        exp_ret = {'t1': 1, 't2': {'t5.1': 51, 't5.2': 55, 't5.3': 53}, 't4': 4}

        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)

    def test_merge_object_list_in_list(self):
        items_in = [
            [[10, 11, 12], 2, 3, 4, 5],
            [[13, 14, 15], 5, 6, 7, 8],
        ]
        exp_ret = [[13, 14, 15], 5, 6, 7, 8]

        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)

    def test_merge_object_list_in_list_mismatch(self):
        items_in = [
            [{'t5.2': 55, 't5.3': 53}, 2, 3, 4, 5],
            [[13, 14, 15], 5, 6, 7, 8],
        ]
        exp_ret = [[13, 14, 15], 5, 6, 7, 8]

        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)

    def test_merge_object_dict_3_level(self):
        items_in = [
            {'t1': 1, 't2': {'t5.1': 51, 't5.2': {'t6.1': 61, 't6.2': 62}}},
            {'t2': {'t5.2': {'t6.2': 72, 't6.3': 63}, 't5.3': 53}, 't4': 4},
        ]
        exp_ret = {'t1': 1, 't2': {'t5.1': 51, 't5.2': {'t6.1': 61, 't6.3': 63, 't6.2': 72}, 't5.3': 53}, 't4': 4}

        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)

    def test_merge_object_dict_3_level_w_path(self):
        items_in = [
            {'t1.1':
                 {'t2.1':
                      {'t3.1': 31,
                       't3.2': 32},
                  't2.2': 22},
             't1.2':
                 {'t2.1': 51,
                  't2.2':
                      {'t3.1': 61,
                       't3.2': 62
                       }
                  }
             },
            {'t1.1':
                 {'t2.1':
                      {'t3.1': 310,
                       't3.2': 320},
                  't2.2': 220},
             't1.2':
                 {'t2.2':
                      {'t3.2': 72,
                       't3.3': 63},
                  't2.3': 53},
             't1.3': 4}
        ]

        exp_ret = {
            't1.1':
                {'t2.1':
                     {'t3.1': 31,
                      't3.2': 32},
                 't2.2': 220},
            't1.2':
                {'t2.1': 51,
                 't2.2':
                     {'t3.1': 61,
                      't3.3': 63,
                      't3.2': 72},
                 't2.3': 53},
            't1.3': 4}

        tmp_ret = merge_object(*items_in)
        self.assertEqual(exp_ret, tmp_ret)


