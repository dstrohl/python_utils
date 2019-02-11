#!/usr/bin/env python

from unittest import TestCase
from PythonUtils.TestHelpers.test_mapping import TestHashMappingProtocol, TestMappingProtocol, \
    NxtNum, NxtAlpha, NxtSet

NxN = NxtNum()
NxA = NxtAlpha()
NxS = NxtSet()

class TestNextItems(TestCase):

    def setUp(self):
        NxN.clear()
        NxA.clear()
        NxS.clear()

    def test_next_num(self):
        self.assertEqual(1, NxN.g)
        self.assertEqual(2, NxN.n)
        self.assertEqual(3, NxN.n)

    def test_next_num_2(self):
        NxN.set(5)
        self.assertEqual(5, NxN.g)
        self.assertEqual(6, NxN.n)
        self.assertEqual(7, NxN.n)

    def test_next_alpha(self):
        self.assertEqual('a', NxA.g)
        self.assertEqual('b', NxA.n)
        self.assertEqual('c', NxA.n)

    def test_next_set(self):
        self.assertEqual({1, 2, 3}, NxS.n)
        self.assertEqual({4, 5, 6}, NxS.n)
        self.assertEqual({7, 8, 9}, NxS.n)

"""
class TestDataGenerator(TestCase):
    def test_get_aa_data_list(self):
        self.assertEqual({'a': 'a', 'b': 'b'}, AA(2))

    def test_get_nn_data_list(self):
        self.assertEqual({1: 1, 2: 2}, NN(2))

    def test_get_nn_data_list_no_num(self):
        self.assertEqual({'a': 1, 'b': 2}, AN(2, 'nn'))

    def test_get_an_data_list(self):
        self.assertEqual({'a': 1, 'b': 2}, AN(2))

    def test_get_asn_data_list(self):
        self.assertEqual({'a': {0, 1, 2}, 'b': {0, 1, 2}}, ASN(2))

    def test_get_all_data_list(self):
        self.assertEqual({'a': 'a', 1: 1}, TDG(2, 'aa', 'nn'))

    def test_get_keys(self):
        self.assertEqual({'a': 'a', 'b': 'b'}, AA(2))
        self.assertEqual(['a', 'b'], list(AN.keys()))

    def test_get_values(self):
        self.assertEqual({'a': 1, 'b': 2}, AN(2))
        self.assertEqual([1, 2], list(AN.values()))

    def test_get_items(self):
        self.assertEqual({'a': 1, 'b': 2}, AN(2))
        self.assertEqual([('a', 1), ('b', 2)], list(AN.items()))

    def test_getitem(self):
        self.assertEqual({'a': 1, 'b': 2}, AN(2))
        self.assertEqual(1, AN['a'])

    def test_setitem(self):
        self.assertEqual({'a': 1, 'b': 2}, AN(2))
        self.assertEqual(1, AN['a'])
        AN['a'] = 'foobar'
        self.assertEqual('foobar', AN['a'])

    def test_get_invalid_key(self):
        self.assertEqual({'a': 1, 'b': 2}, AN(2))
        self.assertNotIn(AN.invalid_key(), ['a', 'b'])
"""

class TestHashingTest(TestHashMappingProtocol, TestCase):
    type2test = dict

class TestMappingTest(TestMappingProtocol, TestCase):
    type2test = dict
