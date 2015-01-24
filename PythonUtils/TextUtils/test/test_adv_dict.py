from unittest import TestCase
import pprint

p=pprint.PrettyPrinter()

from HelperUtils.helper_utils.string_helpers import AdvDict
__author__ = 'strohl'


class TestAdvDict(TestCase):


    def test_adv_dict_get(self):
        tmp_dict = AdvDict()

        tmp_dict['t1'] = 'test1'
        tmp_dict['t2'] = 'test2'
        tmp_dict['t3'] = 'test3'
        tmp_dict['t4'] = 'test4'

        self.assertEqual( tmp_dict.k.t1, 'test1')
        self.assertEqual( tmp_dict.k.t2, 'test2')
        self.assertEqual( tmp_dict.k.t3, 'test3')

        with self.assertRaises(KeyError):
            test = tmp_dict.k.bace


    def test_adv_dict_set(self):
        tmp_dict = AdvDict()

        tmp_dict.k.t1 = 'test1'
        tmp_dict.k.t2 = 'test2'
        tmp_dict.k.t3 = 'test3'
        tmp_dict.k.t4 = 'test4'

        self.assertEqual( tmp_dict['t1'], 'test1')
        self.assertEqual( tmp_dict['t2'], 'test2')
        self.assertEqual( tmp_dict['t3'], 'test3')


