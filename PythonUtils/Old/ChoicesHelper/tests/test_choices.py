import unittest

from PythonUtils.Old.ChoicesHelper.choices_helper import ChoicesHelper, ChoiceDuplicateParameterError, \
    ChoiceInvalidChoiceError, ChoiceInvalidPropertyNameError, Choice

__author__ = 'dstrohl'


class dummy_obj(object):
    choices = None
    default = None

    def get_four(self):
        return 'four'

    get_five = 'five'

    def test_passing(self, choices=None, default=None):
        self.choices = choices
        self.default = default

dummy_inst = dummy_obj()


class ChoiceHelperTests(unittest.TestCase):

    def test_load_strings(self):
        test_list = ['test1', 'test2', 'test3']
        ch = ChoicesHelper(*test_list)

        res_list = []
        for c in ch:
            res_list.append(c)

        check_list = [('test1', 'Test1'), ('test2', 'Test2'), ('test3', 'Test3')]

        self.assertListEqual(check_list, res_list)

    def test_load_2_tuples(self):
        ch = ChoicesHelper(
            ('stored1', 'display1'),
            ('stored2', 'display2'),
            ('stored3', 'display3'),
        )

        res_list = []

        for c in ch:
            res_list.append(c)

        check_list = [('stored1', 'display1'), ('stored2', 'display2'), ('stored3', 'display3')]

        self.assertListEqual(check_list, res_list)

        '''
        self.assertEqual(ch[0], 'display1')
        self.assertEqual(ch[1], 'display2')
        self.assertEqual(ch[2], 'display3')
        '''

    def test_load_3_tuples(self):
        ch = ChoicesHelper(
            ('stored1', 'display1', 'property1'),
            ('stored2', 'display2', 'property2'),
            ('stored3', 'display3', 'property3'),
        )

        self.assertEqual(ch.property1.display_text, 'display1')

    def test_load_choice_class(self):
        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1'),
            Choice('stored2', 'display2', 'property2'),
            Choice('stored3', 'display3', 'property3'),
        )

        self.assertEqual(ch.property1.stored, 'stored1')

    def test_get_data(self):
        ch = ChoicesHelper(
            Choice('Stored 1', 'display1', td1='data1.1', td2='data1.2'),
            Choice('Stored 2', 'display2', td1='data2.1', td2='data2.2'),
            Choice('Stored 3', 'display3', td1='data3.1', td2='data3.2'),
        )

        self.assertEqual(ch.stored_1['td1'], 'data1.1')
        self.assertEqual(ch['Stored 3']['td2'], 'data3.2')
        self.assertEqual(ch['Stored 1']['stored'], 'Stored 1')

    def test_run_property(self):
        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1', td1='data1.1', td2='data1.2', call=dummy_obj.get_five),
            Choice('stored2', 'display2', 'property2', td1='data2.1', td2='data2.2', call=dummy_obj.get_five),
            Choice('stored3', 'display3', 'property3', td1='data3.1', td2='data3.2', call=dummy_obj.get_five),
        )

        self.assertEqual(ch['stored3'](), 'five')

    def test_run_method(self):
        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1', td1='data1.1', td2='data1.2', call=dummy_inst.get_four),
            Choice('stored2', 'display2', 'property2', td1='data2.1', td2='data2.2', call=dummy_inst.get_four),
            Choice('stored3', 'display3', 'property3', td1='data3.1', td2='data3.2', call=dummy_inst.get_four),
        )

        self.assertEqual(ch['stored3'](), 'four')

    def test_synonyms(self):
        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1', stored_synonyms=['st1', 'stor1', 'store1']),
            Choice('stored2', 'display2', 'property2'),
            Choice('stored3', 'display3', 'property3', stored_synonyms=['st3', 'stor3', 'store3']),
        )

        self.assertEqual(ch['st3'].display_text, 'display3')
        self.assertEqual(ch['store1'].display_text, 'display1')
        self.assertEqual(ch['stored1'].display_text, 'display1')
        self.assertEqual(ch['stored2'].display_text, 'display2')

    def test_invalid_parameter(self):
        with self.assertRaises(ChoiceInvalidPropertyNameError):
            ch = ChoicesHelper(
                Choice('stored1', 'display1', 'get_display'),
                Choice('stored2', 'display2', 'if'),
                Choice('stored3', 'display3', 'while'),
            )

        with self.assertRaises(ChoiceInvalidPropertyNameError):
            ch = ChoicesHelper(
                Choice('stored1', 'display1', dummy_obj),
                Choice('stored2', 'display2', 'if2'),
                Choice('stored3', 'display3', 'while2'),
            )

    def test_catch_duplicate_property(self):
        with self.assertRaises(ChoiceDuplicateParameterError):
            ch = ChoicesHelper(
                Choice('stored1', 'display1', 'property1'),
                Choice('stored2', 'display2', 'property1'),
                Choice('stored3', 'display3', 'property1'),
            )

    def test_catch_duplicate_storable(self):
        with self.assertRaises(ChoiceDuplicateParameterError):
            ch = ChoicesHelper(
                Choice('stored1', 'display1', 'property1'),
                Choice('stored1', 'display2', 'property2'),
                Choice('stored1', 'display3', 'property3'),
                duplicate_stored_check=True,
            )

        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1'),
            Choice('stored2', 'display2', 'property2'),
            Choice('stored3', 'display3', 'property3'),
            duplicate_stored_check=True,
        )

        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1'),
            Choice('stored1', 'display2', 'property2'),
            Choice('stored1', 'display3', 'property3'),
        )

    def test_catch_duplicate_display(self):
        with self.assertRaises(ChoiceDuplicateParameterError):
            ch = ChoicesHelper(
                Choice('stored1', 'display1', 'property1'),
                Choice('stored2', 'display1', 'property2'),
                Choice('stored3', 'display1', 'property3'),
                duplicate_display_check=True,
            )

        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1'),
            Choice('stored2', 'display2', 'property2'),
            Choice('stored3', 'display3', 'property3'),
            duplicate_display_check=True,
        )

        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1'),
            Choice('stored2', 'display1', 'property2'),
            Choice('stored3', 'display1', 'property3'),
        )

    def test_default(self):
        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1'),
            Choice('stored2', 'display2', 'property2'),
            Choice('stored3', 'display3', 'property3'),
            no_default=False,
        )

        self.assertEqual(ch.default, 'stored1')

        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1'),
            Choice('stored2', 'display2', 'property2', default=True),
            Choice('stored3', 'display3', 'property3'),
            no_default=False,
        )

        self.assertEqual(ch.default, 'stored2')

        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1'),
            Choice('stored2', 'display2', 'property2', default=True),
            Choice('stored3', 'display3', 'property3'),
            no_default=True,
        )

        self.assertEqual(ch.default, None)

    def test_invalid_choice(self):
        test_list = ['test1', 'test2', 'test3']
        ch = ChoicesHelper(*test_list)

        with self.assertRaises(ChoiceInvalidChoiceError):
            ch.validate('foo')


    '''
    def test_pass_via_star_star(self):
        ch = ChoicesHelper(
            Choice('stored1', 'display1', 'property1'),
            Choice('stored2', 'display2', 'property2'),
            Choice('stored3', 'display3', 'property3', default=True),
            no_default=False,
        )

        dummy_inst.test_passing(**ch())
        check_list = [('stored1', 'display1'), ('stored2', 'display2'), ('stored3', 'display3')]

        self.assertEqual(dummy_inst.choices, check_list)
        self.assertEqual(dummy_inst.default, 'stored3')

    '''