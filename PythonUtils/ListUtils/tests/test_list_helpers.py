__author__ = 'dstrohl'

import unittest
from PythonUtils.ListUtils import count_unique, remove_dupes, get_not_in, get_same, unpack_class_method, flatten, make_list

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


class TestListHelpersCase(unittest.TestCase):

    def test_count_unique(self):
        tmp = ['1','2','3','4','1','2','3','4']
        self.assertEqual(count_unique(tmp), 4)

    def test_count_unique_dict(self):
        tmp = [
            {'k':'1','j':'a','i':'aa'},
            {'k':'2','j':'b','i':'aa'},
            {'k':'3','j':'c','i':'aa'},
            {'k':'4','j':'d'},
            {'k':'1','j':'e'},
            {'k':'2','j':'f','i':'bb'},
            {'k':'3','j':'g'},
            {'k':'4','j':'h','i':'bb'}]
        self.assertEqual(count_unique(tmp,dict_key='k'), 4)
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
        tmp_ret = unpack_class_method(tmp, 'kwargs_demo', kwargs_dict={'n1':3, 'n2':4})
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

