import unittest
from CompIntel.Core.mongo.fields.fields import BaseListField, BaseDictField
from CompIntel.Core.mongo.fields.base_helpers import DictRecord, ListRecord
from CompIntel.Core.mongo.fields.exceptions import *

dummy_doc = 'foo'

required_int = {'name': 'test_int', 'field_type': 'integer', 'required': False}

default_string = {'name': 'test_def_str', 'field_type': 'short_string',
                  'default': 'default text', 'build_if_missing': True}

basic_string = {'name': 'test_str', 'field_type': 'short_string'}

basic_bool = {'name': 'test_bool', 'field_type': 'boolean'}


class TestDictRecord(unittest.TestCase):

    def setUp(self):
        self.basic_record = [
            basic_string,
            required_int,
            default_string
        ]

        self.data_dict = dict(
            test_str='test1',
            test_int=1,
        )
        self.dr = DictRecord(*self.basic_record, data_in=self.data_dict)

    def test_initial_load(self):
        dr = DictRecord(*self.basic_record, data_in=self.data_dict)

        self.assertEqual(dr['test_str'], 'test1')        
        self.assertEqual(dr['test_int'], 1) 
        self.assertEqual(dr['test_def_str'], 'default text')
    
    def test_update_field(self):
        dr = DictRecord(*self.basic_record, data_in=self.data_dict)

        dr['test_str'] = 'new_test'
        dr['test_int'] = 10
        dr['test_def_str'] = 'new_default_test'
        
        self.assertEqual(dr['test_str'], 'new_test')        
        self.assertEqual(dr['test_int'], 10) 
        self.assertEqual(dr['test_def_str'], 'new_default_test')

    def test_add_field(self):
        dr = DictRecord(*self.basic_record, data_in=self.data_dict)        
        
        dr.add_field(**basic_bool)
        
        dr['test_bool'] = False
        dr['test_new_field'] = 'new_field'
                
        self.assertEqual(dr['test_bool'], False)
        self.assertEqual(dr['test_new_field'], 'new_field') 

    def test_locked(self):
        dr = DictRecord(*self.basic_record, data_in=self.data_dict, locked=True)        
        
        with self.assertRaises(AddFieldDisallowedException):        
            dr.add_field(**basic_bool)
        
        with self.assertRaises(UnknownFieldException):        
            dr['test_new_field'] = 'new_field'
        
    def test_external_dict(self):
        dr = DictRecord(*self.basic_record, data_in=self.data_dict)        
        
        dr.add_field(**basic_bool)
        # self.assertEqual(self.data_dict['test_bool'], None)
        
        dr['test_bool'] = False
        dr['test_new_field'] = 'new_field'
        dr['test_str'] = 'new_test'
        dr['test_int'] = 10
        dr['test_def_str'] = 'new_default_test'
        
        self.assertEqual(self.data_dict['test_str'], 'new_test')        
        self.assertEqual(self.data_dict['test_int'], 10) 
        self.assertEqual(self.data_dict['test_def_str'], 'new_default_test')
                
        self.assertEqual(self.data_dict['test_bool'], False)        
        self.assertEqual(self.data_dict['test_new_field'], 'new_field') 

    def test_update(self):
        dr = DictRecord(*self.basic_record, data_in=self.data_dict)        
        dr.add_field(**basic_bool)
        
        update_test = dict(
            test_bool=False,
            test_new_field='new_field',
            test_str='new_test',
            test_int=10,
            test_def_str='new_default_test',
        )
        
        dr.update(update_test)
        
        self.assertEqual(self.data_dict['test_str'], 'new_test')        
        self.assertEqual(self.data_dict['test_int'], 10) 
        self.assertEqual(self.data_dict['test_def_str'], 'new_default_test')
                
        self.assertEqual(self.data_dict['test_bool'], False)        
        self.assertEqual(self.data_dict['test_new_field'], 'new_field') 

    def test_del_field(self):
        dr = DictRecord(*self.basic_record, data_in=self.data_dict)        
        
        update_test = dict(
            test_str='new_test',
            test_int=10,
            test_def_str='new_default_test',
        )
        
        dr.update(update_test)
        
        self.assertEqual(self.data_dict['test_str'], 'new_test')        
        self.assertEqual(self.data_dict['test_int'], 10) 
        self.assertEqual(self.data_dict['test_def_str'], 'new_default_test')
                
        del dr['test_int']

        with self.assertRaises(UnknownFieldException):        
            test = dr['test_int']

        #self.assertEqual(self.data_dict['test_int'], None)

    def test_pop(self):
        self.dr.add_field(**basic_bool)

        update_test = dict(
            test_bool=False,
            test_new_field='new_field',
            test_str='new_test',
            test_int=10,
            test_def_str='new_default_test',
        )

        self.dr.update(update_test)

        tmp_int = self.dr.pop('test_int')
        self.assertEqual(tmp_int, 10)

        with self.assertRaises(KeyError):
            tmp = self.data_dict['test_int']

        tmp_str = self.dr.pop('test_def_str', keep_default=True)
        self.assertEqual(self.data_dict['test_def_str'], 'default text')

    def test_len(self):
        self.assertEqual(3, len(self.dr))

    def test_in(self):
        self.assertIn('test_int', self.dr)
        self.assertNotIn('foo', self.dr)

    def test_iter_keys(self):
        self.assertListEqual(self.dr.keys(), ['test_str', 'test_int', 'test_def_str'])

    def test_clear(self):
        self.dr.clear()
        self.assertDictEqual(self.data_dict, {'test_def_str': 'default text'})

    def test_get(self):
        self.assertEqual(self.dr.get('test_str'), 'test1')
        self.assertEqual(self.dr.get('test_def_str'), 'default text')

    def test_iter(self):
        tmp_list = []
        for f in self.dr:
            tmp_list.append(f)
        self.assertListEqual(tmp_list, ['test_str', 'test_int', 'test_def_str'])

    def test_copy(self):
        tmp_dict = self.dr.copy()

        self.assertDictEqual(tmp_dict, self.data_dict)

    def test_iter_items(self):
        tmp_resp_list = [
            ('test_str', 'test1'),
            ('test_int', 1),
            ('test_def_str', 'default text')
        ]
        self.assertListEqual(self.dr.items(), tmp_resp_list)

    def test_iter_values(self):
        self.assertListEqual(self.dr.values(), ['test1', 1, 'default text'])


class TestListRecord(unittest.TestCase):

    def setUp(self):

        self.data_list = ['test1', 'test2']
        self.lr = ListRecord(basic_string, data_in=self.data_list)

    def test_initial_load(self):
        self.assertEqual(len(self.lr), 2)

    def test_index(self):
        self.assertEqual(self.lr.index(0), 'test1')

    def test_iterate_fields(self):
        for i in self.lr.fields():
            self.assertEqual(i.name, 'test_str')

    def test_iterate_data(self):
        for index, i in enumerate(self.lr):
            self.assertEqual(i, self.data_list[index])

    def test_append(self):
        self.lr.append('test3')
        self.assertEqual(3, self.lr.count())
        self.assertEqual(3, len(self.data_list))

    def test_extend(self):
        self.lr.extend(['test3', 'test4'])
        self.lr.push()
        self.assertListEqual(self.data_list, ['test1', 'test2', 'test3', 'test4'])

    def test_pop(self):
        self.lr.pop()
        self.assertEqual(1, len(self.lr))
        self.lr.pop()
        self.assertEqual(0, len(self.lr))
        self.assertEqual(0, len(self.data_list))

        with self.assertRaises(IndexError):
            self.lr.pop()

    def test_remove(self):
        self.lr.remove(0)
        self.assertEqual(1, len(self.lr))
        self.assertEqual('test2', self.lr[0])

    '''
    def test_insert_diff_type(self):
        self.lr.insert(1, 200)
        self.assertEqual(2, len(self.lr))
        self.assertEqual(200, self.lr[2])

        with self.assertRaises(TypeError):
            self.sort()
    '''

    def test_insert(self):

        self.data_list = ['test1', 'test2']
        self.lr = ListRecord(basic_string, data_in=self.data_list)

        self.lr.insert(1, 'test4')
        self.assertEqual(3, len(self.lr))
        self.assertEqual('test2', self.lr[2])

        self.lr.sort()
        self.assertEqual('test1', self.lr[0])
        self.assertEqual('test2', self.lr[1])
        self.assertEqual('test4', self.lr[2])

    def test_reverse(self):
        self.lr.reverse()
        self.assertEqual('test2', self.lr[0])
        self.assertEqual('test1', self.lr[1])

    def test_add_locked_type(self):
        self.lr = ListRecord(basic_string, data_in=self.data_list)

        with self.assertRaises(FieldValidationException):
            self.lr.insert(1, 200)

    def test_update_with_index(self):
        self.lr[1] = 'test3'
        self.assertEqual('test1', self.lr[0])
        self.assertEqual('test3', self.lr[1])

        self.assertEqual('test1', self.data_list[0])
        self.assertEqual('test3', self.data_list[1])

    def test_rem_item(self):
        del self.lr[0]
        self.assertEqual(1, len(self.lr))
        self.assertEqual('test2', self.lr[0])

    def test_slice(self):
        self.lr.extend(['test3', 'test4'])

        tmp_list = self.lr[0:1]
        self.assertListEqual(self.data_list, ['test1', 'test2', 'test3', 'test4'])
        self.assertListEqual(tmp_list, ['test1'])

        tmp_list = self.lr[2:]
        self.assertListEqual(self.data_list, ['test1', 'test2', 'test3', 'test4'])
        self.assertListEqual(tmp_list, ['test3', 'test4'])

        tmp_list = self.lr[:1]
        self.assertListEqual(self.data_list, ['test1', 'test2', 'test3', 'test4'])
        self.assertListEqual(tmp_list, ['test1'])

    def test_in(self):
        self.assertIn('test1', self.lr)
        self.assertNotIn('test5', self.lr)

'''
class TestBaseListField(unittest.TestCase):

    def setUp(self):
        self.base_list_dict = dict(
            name='TestBaseList',
            parent='foo',
            help_text='Test help text',
        )


    def test_list_field_basic(self):
        tmp_field = BaseListField(**self.base_list_dict)

        self.assertEqual(tmp_field.fieldname, 'TestBaseList')
        self.assertEqual(tmp_field.plural_name, 'TestBaseLists')
        self.assertEqual(tmp_field.help_text, 'Test help text')

        self.assertEqual(tmp_field.to_mongodb(['test1', 'test2']), ['test1', 'test2'])
        self.assertEqual(tmp_field.from_mongodb(['test1', 'test2']), ['test1', 'test2'])
        self.assertEqual(tmp_field.to_user(['test1', 'test2']), ['test1', 'test2'])
        self.assertEqual(tmp_field.from_user(['test1', 'test2']), ['test1', 'test2'])


    def test_list_min_len_validation(self):
        tmp_dict = self.base_list_dict
        tmp_dict['min_length'] = 2

        tmp_field = BaseListField(**tmp_dict)

        tmp_field.from_user(['test1', 'test2', 'test3'])

        with self.assertRaises(FieldValidationException):
            tmp_field.from_user(['test1',])

    def test_list_max_len_validation(self):
        tmp_dict = self.base_list_dict
        tmp_dict['max_length'] = 2

        tmp_field = BaseListField(**tmp_dict)

        tmp_field.from_user(['test1', 'test2'])

        with self.assertRaises(FieldValidationException):
            tmp_field.from_user(['test1', 'test2', 'test3'])

    def test_list_required_validation(self):
        tmp_dict = self.base_list_dict
        tmp_dict['required'] = True

        tmp_field = BaseListField(**tmp_dict)

        tmp_field.from_user(['hell', ])

        with self.assertRaises(FieldValidationException):
            tmp_field.from_user([])

        with self.assertRaises(FieldValidationException):
            tmp_field.from_user(None)

    def test_list_default(self):
        tmp_dict = self.base_list_dict
        tmp_dict['default'] = ['test1']

        tmp_field = BaseListField(**tmp_dict)

        self.assertEqual(tmp_field.from_user(None), ['test1'])

    def test_list_compare(self):
        tmp_dict = self.base_list_dict
        tmp_field = BaseListField(**tmp_dict)

        self.assertTrue(tmp_field.compare(['test1', 'test2', 'test3'],['test1', 'test2', 'test3']))
        self.assertFalse(tmp_field.compare(['test1', 'test2', 'test3'], ['test1', 'test2', 'test']))

    def test_list_get_compare(self):
        tmp_dict = self.base_list_dict
        tmp_field = BaseListField(**tmp_dict)
        self.assertEqual(tmp_field.get_compare(['test1', 'test2', 'test3'],['test1', 'test22', 'test']), '')

    def test_list_check_datatype(self):
        tmp_dict = self.base_list_dict
        tmp_field = BaseListField(**tmp_dict)

        self.assertTrue(tmp_field.check_datatype([]))
        self.assertFalse(tmp_field.check_datatype('test'))


class TestBaseDictField(unittest.TestCase):

    def setUp(self):
        self.base_dict_dict = dict(
            name='TestBaseDict',
            parent='foo',
            help_text='Test help text',
        )

        self.test_dict1 = dict(
            test1="Test 1",
            test2="Test 2",
            test3="Test 3",
        )

        self.test_dict2 = dict(
            test10="Test 10",
            test11="Test 11",
            test12="Test 12",
            test13="Test 13",
            test14="Test 14",
        )


    def test_dict_field_basic(self):
        tmp_field = BaseDictField(**self.base_dict_dict)

        self.assertEqual(tmp_field.fieldname, 'TestBaseDict')
        self.assertEqual(tmp_field.plural_name, 'TestBaseDicts')
        self.assertEqual(tmp_field.help_text, 'Test help text')

        self.assertEqual(tmp_field.to_mongodb(self.test_dict1), self.test_dict1)
        self.assertEqual(tmp_field.from_mongodb(self.test_dict1), self.test_dict1)
        self.assertEqual(tmp_field.to_user(self.test_dict1), self.test_dict1)
        self.assertEqual(tmp_field.from_user(self.test_dict1), self.test_dict1)


    def test_dict_min_len_validation(self):
        tmp_dict = self.base_dict_dict
        tmp_dict['min_length'] = 5

        tmp_field = BaseDictField(**tmp_dict)

        tmp_field.from_user(self.test_dict2)

        with self.assertRaises(FieldValidationException):
            tmp_field.from_user(self.test_dict1)

    def test_dict_max_len_validation(self):
        tmp_dict = self.base_dict_dict
        tmp_dict['max_length'] = 3

        tmp_field = BaseDictField(**tmp_dict)

        tmp_field.from_user(self.test_dict1)

        with self.assertRaises(FieldValidationException):
            tmp_field.from_user(self.test_dict2)

    def test_dict_required_validation(self):
        tmp_dict = self.base_dict_dict
        tmp_dict['required'] = True

        tmp_field = BaseDictField(**tmp_dict)

        tmp_field.from_user(self.test_dict1)

        with self.assertRaises(FieldValidationException):
            tmp_field.from_user({})

        with self.assertRaises(FieldValidationException):
            tmp_field.from_user(None)

    def test_dict_default(self):
        tmp_dict = self.base_dict_dict
        tmp_dict['default'] = self.test_dict1

        tmp_field = BaseDictField(**tmp_dict)

        self.assertEqual(tmp_field.from_user(None), self.test_dict1)

    def test_dict_compare(self):
        tmp_dict = self.base_dict_dict
        tmp_field = BaseDictField(**tmp_dict)

        self.assertTrue(tmp_field.compare(self.test_dict1, self.test_dict1))
        self.assertFalse(tmp_field.compare(self.test_dict1, self.test_dict2))

    def test_dict_get_compare(self):
        tmp_dict = self.base_dict_dict
        tmp_field = BaseDictField(**tmp_dict)
        self.assertEqual(tmp_field.get_compare(self.test_dict1, self.test_dict2), '')

    def test_dict_check_datatype(self):
        tmp_dict = self.base_dict_dict
        tmp_field = BaseDictField(**tmp_dict)

        self.assertTrue(tmp_field.check_datatype({}))
        self.assertFalse(tmp_field.check_datatype('test'))
'''