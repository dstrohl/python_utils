#!/usr/bin/env python


from unittest import TestCase
from PythonUtils.BaseUtils import flatten_dict, MultiLevelDictManager, AdvDict


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


