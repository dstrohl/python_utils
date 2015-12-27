import unittest
from CompIntel.Core.mongo.fields.fields import *
from CompIntel.Core.mongo.fields.exceptions import *
from CompIntel.Core.mongo.fields.base_helpers import *

class DummyDoc(object):

    def __init__(self, data=None):
        if data is None:
            self._data_ = {}
        else:
            if isinstance(data, dict):
                self._data_ = data
            else:
                self._list = data
                self._data_ = KeyedList(self._list)
        self._dirty = False

dummy_doc = DummyDoc()


class TestTagging(unittest.TestCase):

    def setUp(self):
        self.base_string_dict = dict(
            name='TestString',
            data_key='test_str',
            data_obj=dummy_doc._data_,
            parent=dummy_doc,
            help_text='Test help text',
        )

    def test_single_tag(self):
        tmp_field = ShortStringField(**self.base_string_dict)

        self.assertTrue(tmp_field.match_tags('basic'))
        self.assertTrue(tmp_field.match_tags('basic', 'leaf'))
        self.assertTrue(tmp_field.match_tags('basic', '-branch'))
        self.assertTrue(tmp_field.match_tags('leaf'))

        self.assertFalse(tmp_field.match_tags('foo'))
        self.assertFalse(tmp_field.match_tags('-basic'))
        self.assertFalse(tmp_field.match_tags('leaf', '-basic'))


class TestBaseSetGetField(unittest.TestCase):

    '''
    def setUp(self):

        self.dummy_doc = DummyDoc()

        self.base_string_dict = dict(
            name='TestString',
            key='test_str',
            parent=self.dummy_doc,
            help_text='Test help text',
        )
    '''

    def build_field(self, data=None, list_key=None, **kwargs):
        self.dummy_doc = DummyDoc(data)
        self.base_string_dict = dict(
            name='TestString',
            parent=self.dummy_doc,
            data_obj=self.dummy_doc._data_,
            data_key=list_key or 'test_str',
            help_text='Test help text',
        )

        self.base_string_dict.update(**kwargs)
        return ShortStringField(**self.base_string_dict)


    def test_field_get_set(self):
        tmp_field = self.build_field({'test_str': 'test'})
        self.assertFalse(self.dummy_doc._dirty)

        self.assertEqual(tmp_field.get(), 'test')
        tmp_field.set('new test')
        self.assertEqual(tmp_field.get(), 'new test')
        self.assertEqual(self.dummy_doc._data_['test_str'], 'new test')
        self.assertTrue(self.dummy_doc._dirty)

    def test_get_set_no_object(self):
        tmp_field = self.build_field()
        self.assertFalse(self.dummy_doc._dirty)
        self.assertEqual(tmp_field.get(), None)

        tmp_field.set('new test')
        self.assertEqual(tmp_field.get(), 'new test')
        self.assertEqual(self.dummy_doc._data_['test_str'], 'new test')
        self.assertTrue(self.dummy_doc._dirty)

    def test_set_no_change(self):
        tmp_field = self.build_field({'test_str': 'test'})
        self.assertFalse(self.dummy_doc._dirty)

        self.assertEqual(tmp_field.get(), 'test')
        tmp_field.set('test')
        self.assertEqual(tmp_field.get(), 'test')
        self.assertEqual(self.dummy_doc._data_['test_str'], 'test')
        self.assertFalse(self.dummy_doc._dirty)

    '''
    def test_set_get_from_list(self):
        tmp_field = self.build_field(['t1', 't2', 't3'], list_key=1)
        self.assertFalse(self.dummy_doc._dirty)

        self.assertEqual(tmp_field.get(), 't2')
        tmp_field.set('new test')
        self.assertEqual(tmp_field.get(), 'new test')
        self.assertEqual(self.dummy_doc._data_[1], 'new test')
        self.assertTrue(self.dummy_doc._dirty)
    '''


class TestStringField(unittest.TestCase):

    def setUp(self):
        self.base_string_dict = dict(
            name='TestString',
            data_key='test_str',
            data_obj=dummy_doc._data_,
            parent=dummy_doc,
            help_text='Test help text',
        )

    def test_string_field_basic(self):
        tmp_field = ShortStringField(**self.base_string_dict)

        self.assertEqual(tmp_field.name, 'TestString')
        self.assertEqual(tmp_field.verbose_name, 'Test string')
        self.assertEqual(tmp_field.verbose_plural_name, 'Test strings')
        self.assertEqual(tmp_field.help_text, 'Test help text')

        self.assertEqual(tmp_field.conversions.to_user('test'), 'test')
        self.assertEqual(tmp_field.conversions.from_user('test'), 'test')

    def test_string_regex_validation(self):
        tmp_dict = self.base_string_dict
        tmp_dict['regex'] = r'hello.*you'

        tmp_field = ShortStringField(**tmp_dict)

        tmp_field.validate('hello how are you')

        with self.assertRaises(FieldValidationException):
            tmp_field.validate('hell this should fail')

    def test_string_min_len_validation(self):
        tmp_dict = self.base_string_dict
        tmp_dict['min_length'] = 5

        tmp_field = ShortStringField(**tmp_dict)

        tmp_field.validate('hello there')

        with self.assertRaises(FieldValidationException):
            tmp_field.validate('hell')

    def test_string_max_len_validation(self):
        tmp_dict = self.base_string_dict
        tmp_dict['max_length'] = 5

        tmp_field = ShortStringField(**tmp_dict)

        tmp_field.validate('hell')

        with self.assertRaises(FieldValidationException):
            tmp_field.validate('hello there')

    def test_string_required_validation(self):
        tmp_dict = self.base_string_dict
        tmp_dict['required'] = True

        tmp_field = ShortStringField(**tmp_dict)

        tmp_field.validate('hell')

        with self.assertRaises(FieldValidationException):
            tmp_field.validate('')

        with self.assertRaises(FieldValidationException):
            tmp_field.validate(None)


    def test_string_default(self):
        tmp_dict = self.base_string_dict
        tmp_dict['default'] = 'good_test'

        tmp_field = ShortStringField(**tmp_dict)

        self.assertEqual(tmp_field.conversions.from_user(''), 'good_test')

    def test_string_choices_suggest(self):
        tmp_dict = self.base_string_dict
        tmp_dict['suggest'] = 'good_test'

        tmp_field = ShortStringField(**tmp_dict)

        self.assertEqual(tmp_field.conversions.to_user(None), 'good_test')

    def test_string_choices_list(self):
        tmp_dict = self.base_string_dict
        tmp_dict['choices'] = ['test_1', 'test_2']

        tmp_field = ShortStringField(**tmp_dict)

        self.assertEqual(tmp_field.get_choices, [('test_1', 'Test 1'), ('test_2', 'Test 2')])

    def test_string_choices_validation(self):
        tmp_dict = self.base_string_dict
        tmp_dict['choices'] = ['test_1', 'test_2']

        tmp_field = ShortStringField(**tmp_dict)

        tmp_field.validate('test_1')

        with self.assertRaises(FieldValidationException):
            tmp_field.validate('foo')

    def test_string_choices_desc(self):
        tmp_dict = self.base_string_dict
        tmp_dict['choices'] = ['test_1', 'test_2']

        tmp_field = ShortStringField(**tmp_dict)

        self.assertEqual(tmp_field._choice_user_string('test_1'), 'Test 1')

    def test_string_choices_edited(self):
        tmp_dict = self.base_string_dict
        tmp_dict['choices'] = ['test_1', 'test_2']
        tmp_dict['choice_allow_edit'] = True

        tmp_field = ShortStringField(**tmp_dict)

        tmp_field.conversions.from_user('hell')

    def test_string_compare(self):
        tmp_dict = self.base_string_dict
        tmp_field = ShortStringField(**tmp_dict)

        self.assertTrue(tmp_field.compare('test', 'test'))
        self.assertFalse(tmp_field.compare('test', 'test2'))

    def test_string_get_compare(self):
        tmp_dict = self.base_string_dict
        tmp_field = ShortStringField(**tmp_dict)
        self.assertEqual(tmp_field.get_compare('test', 'test2'), 'Old value: test\nNew Value: test2')

    def test_string_check_datatype(self):
        tmp_dict = self.base_string_dict
        tmp_field = ShortStringField(**tmp_dict)

        self.assertTrue(tmp_field.check_datatype('test'))
        self.assertFalse(tmp_field.check_datatype(1))
        self.assertTrue(tmp_field.check_datatype(1, try_coercing=True))


class TestIntField(unittest.TestCase):

    def setUp(self):
        self.base_int_dict = dict(
            name='TestInt',
            data_key='test_int',
            data_obj=dummy_doc._data_,
            parent=dummy_doc,
            help_text='Test help text',
        )


    def test_int_field_basic(self):
        tmp_field = IntegerField(**self.base_int_dict)

        self.assertEqual(tmp_field.name, 'TestInt')

        self.assertEqual(tmp_field.conversions.to_user(3), 3)
        self.assertEqual(tmp_field.conversions.from_user(4), 4)

    def test_int_regex_validation(self):
        tmp_dict = self.base_int_dict
        tmp_dict['regex'] = r'12.*12'

        tmp_field = IntegerField(**tmp_dict)

        tmp_field.validate(123456789012)

        with self.assertRaises(FieldValidationException):
            tmp_field.validate(123456)


    def test_int_min_validation(self):
        tmp_dict = self.base_int_dict
        tmp_dict['min'] = 5

        tmp_field = IntegerField(**tmp_dict)

        tmp_field.validate(19)

        with self.assertRaises(FieldValidationException):
            tmp_field.validate(1)

    def test_int_max_validation(self):
        tmp_dict = self.base_int_dict
        tmp_dict['max'] = 5

        tmp_field = IntegerField(**tmp_dict)

        tmp_field.validate(3)

        with self.assertRaises(FieldValidationException):
            tmp_field.validate(19)

    def test_int_required_validation(self):
        tmp_dict = self.base_int_dict
        tmp_dict['required'] = True

        tmp_field = IntegerField(**tmp_dict)

        tmp_field.validate(2)

        with self.assertRaises(FieldValidationException):
            tmp_field.validate(None)


    def test_int_default(self):
        tmp_dict = self.base_int_dict
        tmp_dict['default'] = 10

        tmp_field = IntegerField(**tmp_dict)

        self.assertEqual(tmp_field.conversions.from_user(None), 10)

    def test_int_suggest(self):
        tmp_dict = self.base_int_dict
        tmp_dict['suggest'] = 100

        tmp_field = IntegerField(**tmp_dict)

        self.assertEqual(tmp_field.conversions.to_user(None), 100)

    def test_int_choices_list(self):
        tmp_dict = self.base_int_dict
        tmp_dict['choices'] = [(1, 'One'), (2, 'Two')]

        tmp_field = IntegerField(**tmp_dict)

        self.assertEqual(tmp_field.get_choices, [(1, 'One'), (2, 'Two')])

    def test_int_choices_validation(self):
        tmp_dict = self.base_int_dict
        tmp_dict['choices'] = [1, 2]

        tmp_field = IntegerField(**tmp_dict)

        tmp_field.validate(1)

        with self.assertRaises(FieldValidationException):
            tmp_field.validate(3)


    def test_int_choices_desc(self):
        tmp_dict = self.base_int_dict
        tmp_dict['choices'] = [(1, 'One'), (2, 'Two')]

        tmp_field = IntegerField(**tmp_dict)

        self.assertEqual(tmp_field._choice_user_string(1), 'One')

    def test_int_choices_edited(self):
        tmp_dict = self.base_int_dict
        tmp_dict['choices'] = [(1, 'One'), (2, 'Two')]
        tmp_dict['choice_allow_edit'] = True

        tmp_field = IntegerField(**tmp_dict)

        tmp_field.conversions.from_user(10)

    def test_int_compare(self):
        tmp_dict = self.base_int_dict
        tmp_field = IntegerField(**tmp_dict)

        self.assertTrue(tmp_field.compare(1, 1))
        self.assertFalse(tmp_field.compare(2, 1))

    def test_int_get_compare(self):
        tmp_dict = self.base_int_dict
        tmp_field = IntegerField(**tmp_dict)
        self.assertEqual(tmp_field.get_compare(1, 2), 'Old value: 1\nNew Value: 2')

    def test_int_check_datatype(self):
        tmp_dict = self.base_int_dict
        tmp_field = IntegerField(**tmp_dict)

        self.assertTrue(tmp_field.check_datatype(1))
        self.assertFalse(tmp_field.check_datatype('test'))
        self.assertTrue(tmp_field.check_datatype('1', try_coercing=True))
        self.assertFalse(tmp_field.check_datatype('test', try_coercing=True))


class TestBoolField(unittest.TestCase):

    def setUp(self):
        self.base_bool_dict = dict(
            name='TestBool',
            data_key='test_bool',
            data_obj=dummy_doc._data_,
            parent=dummy_doc,
            help_text='Test help text',
        )


    def test_bool_field_basic(self):
        tmp_field = BooleanField(**self.base_bool_dict)

        self.assertEqual(tmp_field.conversions.to_user(True, raw=True), True)
        self.assertEqual(tmp_field.conversions.from_user(False), False)


    def test_bool_required_validation(self):
        tmp_dict = self.base_bool_dict
        tmp_dict['required'] = True

        tmp_field = BooleanField(**tmp_dict)

        tmp_field.validate(True)

        with self.assertRaises(FieldValidationException):
            tmp_field.validate(None)


    def test_bool_default(self):
        tmp_dict = self.base_bool_dict
        tmp_dict['default'] = True

        tmp_field = BooleanField(**tmp_dict)

        self.assertEqual(tmp_field.conversions.from_user(None), True)

    def test_bool_suggest(self):
        tmp_dict = self.base_bool_dict
        tmp_dict['suggest'] = True

        tmp_field = BooleanField(**tmp_dict)

        self.assertEqual(tmp_field.conversions.to_user(None), True)

    def test_bool_choices_list(self):
        tmp_dict = self.base_bool_dict

        tmp_field = BooleanField(**tmp_dict)

        self.assertEqual(tmp_field.get_choices, [(True, 'Yes'), (False, 'No')])


    def test_bool_choices_desc(self):
        tmp_dict = self.base_bool_dict

        tmp_field = BooleanField(**tmp_dict)

        self.assertEqual(tmp_field._choice_user_string(True), 'Yes')


    def test_bool_compare(self):
        tmp_dict = self.base_bool_dict
        tmp_field = BooleanField(**tmp_dict)

        self.assertTrue(tmp_field.compare(True, True))
        self.assertFalse(tmp_field.compare(False, True))

    def test_bool_get_compare(self):
        tmp_dict = self.base_bool_dict
        tmp_field = BooleanField(**tmp_dict)
        self.assertEqual(tmp_field.get_compare(True, False), 'Old value: Yes\nNew Value: No')

    def test_bool_check_datatype(self):
        tmp_dict = self.base_bool_dict
        tmp_field = BooleanField(**tmp_dict)

        self.assertTrue(tmp_field.check_datatype(True))
        self.assertFalse(tmp_field.check_datatype('test'))
        self.assertTrue(tmp_field.check_datatype('Yes', try_coercing=True))
        self.assertFalse(tmp_field.check_datatype('glah', try_coercing=True))

