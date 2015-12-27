import unittest
from PythonUtils.FieldObjects.field_bases import StringField, IntegerField, _UNSET
from PythonUtils.FieldObjects.field_exceptions import *
from PythonUtils.ChoicesHelper import ChoicesHelper, Choice

class DummyObject(object):
    def __str__(self):
        raise TypeError

dummy_object = DummyObject()


class TestStringField(unittest.TestCase):
    def test_init(self):
        sf = StringField('test', default='bar')

        self.assertEqual('foo', sf.to_db('foo'))
        self.assertEqual('foo', sf.from_db('foo'))
        self.assertEqual('foo', sf.to_user('foo'))
        self.assertEqual('foo', sf.from_user('foo'))

    def test_base_default_init(self):
        sf = StringField('test', default='bar')

        self.assertEqual(_UNSET, sf.to_db(_UNSET))
        self.assertEqual(_UNSET, sf.from_db(_UNSET))
        self.assertEqual('bar', sf.to_user(_UNSET))
        self.assertEqual(_UNSET, sf.from_user('bar'))

    def test_default_save_default(self):
        sf = StringField('test', default='bar', save_default=True)

        self.assertEqual('bar', sf.to_db(_UNSET))
        self.assertEqual(_UNSET, sf.from_db(_UNSET))
        self.assertEqual('bar', sf.to_user(_UNSET))
        self.assertEqual(_UNSET, sf.from_user('bar'))

    def test_read_only(self):
        sf = StringField(read_only=True)
        self.assertEqual('foo', sf.to_db('foo'))
        self.assertEqual('foo', sf.from_db('foo'))
        self.assertEqual('foo', sf.to_user('foo'))
        self.assertEqual('foo', sf.from_user('foo', raw=True))

        with self.assertRaises(FieldReadOnlyException):
            self.assertNotEqual('foo', sf.from_user('foo'))

    def test_suggest(self):
        sf = StringField(suggest='foo')
        self.assertEqual('foo', sf.suggested_value)
        
        sf = StringField()
        self.assertEqual(_UNSET, sf.suggested_value)

    def test_compare(self):
        sf = StringField('test')
        
        self.assertTrue(sf.compare('test', 'test'))
        self.assertFalse(sf.compare('test2', 'test'))

        sf.comparable = False
        self.assertTrue(sf.compare('test', 'test', on_error=True))
        self.assertTrue(sf.compare('test', 'test2', on_error=True))
        self.assertTrue(sf.compare('test', 1, on_error=True))

        self.assertFalse(sf.compare('test', 'test', on_error=False))
        self.assertFalse(sf.compare('test', 'test2', on_error=False))
        self.assertFalse(sf.compare('test', 1, on_error=False))

        with self.assertRaises(UncomparableFieldsException):
            test = sf.compare(1, 'test2')

        with self.assertRaises(UncomparableFieldsException):
            test = sf.compare('test', 'test2')

        with self.assertRaises(UncomparableFieldsException):
            test = sf.compare('test', 'test')

    def test_valid_type(self):
        
        sf = StringField()
        self.assertTrue(sf.valid_object_type('test'))         
        self.assertTrue(sf.valid_coerceable_type(1))
        
        self.assertFalse(sf.valid_object_type(1))         
        self.assertFalse(sf.valid_coerceable_type(dummy_object))
        
    def test_type_validation(self):
        sf = StringField()

        self.assertEqual('one', sf.from_user('one'))
        self.assertEqual(1, sf.from_user(1, raw=True))
        self.assertEqual(1, sf.from_user(1, validate=False))
        with self.assertRaises(FieldValidationException):
            sf.from_user(1)


class TestNoneOptions(unittest.TestCase):

    def test_allow_none_required(self):
        sf = StringField('test', required=True, allow_none=True)
        self.assertEqual(None, sf.from_user(None))

    def test_allow_none_not_required(self):
        sf = StringField('test', required=False, allow_none=True)
        self.assertEqual(None, sf.from_user(None))

    def test_disallow_none_required(self):
        sf = StringField('test', required=True, allow_none=False)
        with self.assertRaises(FieldValidationException):
            self.assertNotEqual(None, sf.from_user(None))

    def test_disallow_none_not_required(self):
        sf = StringField('test', required=False, allow_none=False)
        self.assertEqual(_UNSET, sf.from_user(None))

    def test_allow_none_from_db(self):
        sf = StringField('test', required=True, allow_none=True)
        self.assertEqual(None, sf.from_db(None))

    def test_disallow_none_from_db(self):
        sf = StringField('test', required=True, allow_none=False)
        self.assertEqual(_UNSET, sf.from_db(None))


class TestConversions(unittest.TestCase):
    def test_db_conversions(self):
        sf = IntegerField(db_system='sys_str')

        self.assertEqual('1', sf.to_db(1))
        self.assertEqual(2, sf.from_db('2'))
        self.assertEqual(3, sf.to_user(3))
        self.assertEqual(4, sf.from_user(4))

    def test_user_conversions(self):
        sf = IntegerField(user_system='sys_str')

        self.assertEqual(1, sf.to_db(1))
        self.assertEqual(2, sf.from_db(2))
        self.assertEqual('3', sf.to_user(3))
        self.assertEqual(4, sf.from_user('4'))

    def test_both_conversions(self):
        sf = IntegerField(user_system='sys_str', db_system='sys_str')

        self.assertEqual('1', sf.to_db(1))
        self.assertEqual(2, sf.from_db('2'))
        self.assertEqual('3', sf.to_user(3))
        self.assertEqual(4, sf.from_user('4'))


class TestChoiceMixins(unittest.TestCase):

    option_1_place_tuple = ['sto_and_disp_1', 'sto_and_disp_1', 'sto_and_disp_1']

    option_2_place_tuple = [('stored_1', 'display_1'),
                            ('stored_2', 'display_2'),
                            ('stored_3', 'display_3')]

    option_3_place_tuple = [('stored_1', 'display_1', 'meth_1'),
                            ('stored_2', 'display_2', 'meth_2'),
                            ('stored_3', 'display_3', 'meth_3')]

    option_choices = [Choice('stored_1', 'display_1'),
                      Choice('stored_2', 'display_2'),
                      Choice('stored_3', 'display_3')]
    
    option_helper = ChoicesHelper(*option_choices)

    def test_init_choice_helper(self):
        sf = StringField(choices=self.option_helper)

        self.assertEqual('foo', sf.to_db('foo'))
        self.assertEqual('foo', sf.from_db('foo'))
        self.assertEqual('display_1', sf.to_user('stored_1'))
        self.assertEqual('stored_1', sf.from_user('display_1'))

        self.assertEqual('foo', sf.from_user('foo', raw=True))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual('foo', sf.from_user('foo'))

    def test_init_list_1_place_tuples(self):
        sf = StringField(choices=self.option_1_place_tuple)

        self.assertEqual('foo', sf.to_db('foo'))
        self.assertEqual('foo', sf.from_db('foo'))
        self.assertEqual('sto_and_disp_1', sf.to_user('sto_and_disp_1'))
        self.assertEqual('sto_and_disp_2', sf.from_user('sto_and_disp_2'))

        self.assertEqual('foo', sf.from_user('foo', raw=True))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual('foo', sf.from_user('foo'))

    def test_init_list_choices(self):
        sf = StringField(choices=self.option_choices)

        self.assertEqual('foo', sf.to_db('foo'))
        self.assertEqual('foo', sf.from_db('foo'))
        self.assertEqual('display_1', sf.to_user('stored_1'))
        self.assertEqual('stored_1', sf.from_user('display_1'))

        self.assertEqual('foo', sf.from_user('foo', raw=True))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual('foo', sf.from_user('foo'))

    def test_init_list_2_place_tuples(self):
        sf = StringField(choices=self.option_2_place_tuple)

        self.assertEqual('foo', sf.to_db('foo'))
        self.assertEqual('foo', sf.from_db('foo'))
        self.assertEqual('display_1', sf.to_user('stored_1'))
        self.assertEqual('stored_2', sf.from_user('display_1'))

        self.assertEqual('foo', sf.from_user('foo', raw=True))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual('foo', sf.from_user('foo'))

    def test_init_list_3_place_tuples(self):
        sf = StringField(choices=self.option_3_place_tuple)

        self.assertEqual('foo', sf.to_db('foo'))
        self.assertEqual('foo', sf.from_db('foo'))
        self.assertEqual('display_1', sf.to_user('stored_1'))
        self.assertEqual('stored_1', sf.from_user('display_1'))

        self.assertEqual('foo', sf.from_user('foo', raw=True))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual('foo', sf.from_user('foo'))

    def test_get_user_string(self):
        sf = StringField(choices=self.option_helper)

        self.assertEqual('display_3', sf.get_user_string('stored_3'))
        self.assertEqual('bar', sf.get_user_string('foo', default='bar'))

    def test_allow_user_edit(self):
        sf = StringField(choices=self.option_helper, require_choice=False)

        self.assertEqual('display_3', sf.to_user('stored_3'))
        self.assertEqual('foo', sf.to_user('foo'))

        self.assertEqual('stored_3', sf.from_user('display_3'))
        self.assertEqual('foo', sf.from_user('foo'))

    def test_get_choices(self):
        sf = StringField(choices=self.option_helper, require_choice=False)
        self.assertEqual(['display_1', 'display_2', 'display_3'], sf.get_choices())
        self.assertEqual([('', 'display_1'), ('display_2', 'display_2'), ('', 'display_3')], sf.get_choices(value='display_2'))
        self.assertEqual([('foo', 'foo'), ('', 'display_1'), ('', 'display_2'), ('', 'display_3')], sf.get_choices(value='foo'))


class TestOtherMixins(unittest.TestCase):
    def test_regex_mixin(self):
        sf = StringField(match_regex='^foo.*')
        self.assertEqual('foobar', sf.from_user('foobar'))
        self.assertEqual('foobar2', sf.from_user('foobar2'))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual('fodbar', sf.from_user('fodbar'))

    def test_max_len_mixin(self):
        sf = StringField(max_len=5)
        self.assertEqual('foo', sf.from_user('foo'))
        self.assertEqual('bar', sf.from_user('bar'))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual('fodbar', sf.from_user('fodbar'))

    def test_min_len_mixin(self):
        sf = StringField(min_len=3)
        self.assertEqual('foo', sf.from_user('foo'))
        self.assertEqual('foobar', sf.from_user('foobar'))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual('f', sf.from_user('f'))

    def test_min_max_len_mixin(self):
        sf = StringField(max_len=5, min_len=3)
        self.assertEqual('foo', sf.from_user('foo'))
        self.assertEqual('bar', sf.from_user('bar'))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual('fodbar', sf.from_user('fodbar'))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual('f', sf.from_user('f'))

    def test_max_value_mixin(self):
        sf = IntegerField(min=50)
        self.assertEqual(55, sf.from_user(55))
        self.assertEqual(100, sf.from_user(100))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual(25, sf.from_user(25))

    def test_min_value_mixin(self):
        sf = IntegerField(max=100)
        self.assertEqual(55, sf.from_user(55))
        self.assertEqual(100, sf.from_user(100))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual(125, sf.from_user(125))

    def test_min_max_value_mixin(self):
        sf = IntegerField(min=50, max=100)
        self.assertEqual(55, sf.from_user(55))
        self.assertEqual(100, sf.from_user(100))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual(25, sf.from_user(25))

        with self.assertRaises(FieldValidationException):
            self.assertNotEqual(125, sf.from_user(25))
