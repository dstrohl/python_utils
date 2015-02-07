__author__ = 'dstrohl'

from unittest import TestCase
from PythonUtils.IntelligentFormatter.intel_format import IntelligentFormat, find_enclosed


class TestIntelFormat(TestCase):

    limits_dict = {
                   '__full_str__': {'max_length': 50, 'pax_to_max': True},
                   'f1': {'max_length': 38},
                   'f2': {'min_length': 10,
                         'trim_priority': 2},
                   'f3': {'max_length': 10,
                         'trim_priority': 0},
                   'f4': {'min_length': 3},
                   }

    data_dict = {
                 'f1': 'This is a test of the max length field*********',
                 'f2': 'This is 10*******',
                 'f3': 12345,
                 'f4': 'Hi!************',
                 'f5': 'More Text',
                 'f6': 'and still more text that is not in the template'
                 }

    format_str = '{f1}<--->{f2}<->{f3}{f4}'


    intel_format = None

    def test_find_enclosed(self):

        test_list = [
                     {'args': ('[this] is a test', '[', ']'),
                      'kwargs': {},
                      'return': ['this']
                      },
                     {'args': ('this [is] a test', '[', ']'),
                      'kwargs': {},
                      'return': ['is']
                      },

                     {'args': ('[this] is [a] test', '[', ']'),
                      'kwargs': {},
                      'return': ['this', 'a']
                      },

                     {'args': ('this [is] a [test]', '[', ']'),
                      'kwargs': {},
                      'return': ['is', 'test']
                      },

                     {'args': ('this is [a test', '[', ']'),
                      'kwargs': {},
                      'return': []
                      },

                     {'args': ('this is a] test', '[', ']'),
                      'kwargs': {},
                      'return': []
                      },

                     {'args': ('this [is] [a] [test]', '[', ']'),
                      'kwargs': {'include_all': False},
                      'return': 'is'
                      },

                     {'args': ('this is a] test', '[', ']'),
                      'kwargs': {'include_all': False},
                      'return': ''
                      },

                     {'args': ('this is a] test', '[', ']'),
                      'kwargs': {'default': 'rat bastard'},
                      'return': ['rat bastard']
                      },

                     {'args': ('this is a] test', '[', ']'),
                      'kwargs': {'default': 'junk', 'include_all': False},
                      'return': 'junk'
                      },
                     {'args': ('this is [a |test]', '[', ']'),
                      'kwargs': {'ignore_after': '|'},
                      'return': ['a ']
                      },
                     ]

    def run_find_enclosed_test(self, test_def):

        test_ret = find_enclosed(*test_def['args'], **test_def['kwargs'])
        self.assertEqual(test_ret, test_def['return'])

    def setup_intel_format(self):


        self.intel_format = IntelligentFormat(self.limits_dict, self.format_str)


    '''
    def test_verify_fields(self):
        self.setup_intel_format()

        self.assertEqual(self.intel_format.full_fields_list ,
                         ['f1', 'f2', 'f3', 'f4'])

        self.assertEqual(len(self.intel_format.fields_def_dict) , 4)


        self.assertEqual(self.intel_format.priority_list  ,
                         [['f3'], ['f1', 'f4'], ['f2']])

        self.assertEqual(self.intel_format.template_overhead , 8)



    def test_check_formatted(self):
        self.setup_intel_format()
        self.intel_format.fields_dict = self.data_dict

        tmp_ret = self.intel_format._check_formatted()

        self.assertTrue(tmp_ret)
        self.assertEqual(self.intel_format.formatted_str, 'This is a test of the max length field*********<--->This is 10*******<->12345Hi!************')
        self.assertEqual(self.intel_format.formatted_str_len, 92)

        self.intel_format.full_string_limits['max_length'] = 20
        tmp_ret = self.intel_format._check_formatted()

        self.assertFalse(tmp_ret)


    def test_get_field_nums(self):
        pass

    '''

