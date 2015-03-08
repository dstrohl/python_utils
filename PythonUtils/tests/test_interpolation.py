__author__ = 'dstrohl'

import unittest
from PythonUtils import interpolate


'''
def interpolate(in_string,
                field_map,
                depth=0,
                max_depth=10,
                key='%',
                key_sep='.',
                fixed_path_depth=0,
                default_path='',
                on_key_error='raise',
                error_replace='',
                errors_to_except=None):
'''

class InterpolationTest(unittest.TestCase):

    test_map = {
        'fname': 'john',
        'lname': 'buck',
        'zip': '12345',
        'street': 'main st.',
        'city': 'anytown',
        'address': '%(zip) %(street)',
        'fullname': '%(fname) %(lname)',
        'perc': '%%',
        'all': '%(perc) %(fullname) %(address) %% ',
        'spouse': '%(.2.fullname)'
    }

    test_map_2 = {
        'fname': 'jane',
        'lname': 'doe',
        'zip': '67890',
        'street': 'broad st.',
        'city': 'anycity',
        'address': '%(zip) %(street)',
        'fullname': '%(fname) %(lname)',
        'perc': '%%',
        'all': '%(perc) %(fullname) %(address) %% ',
        'spouse': '%(.1.fullname)'
    }

    test_map_both = {'1': test_map, '2': test_map_2}

    def test_simple_string_return(self):
        test_ret = interpolate('name', self.test_map)
        self.assertEqual(test_ret, 'name')

    def test_non_string_return(self):
        test_ret = interpolate(123, self.test_map)
        self.assertEqual(test_ret, 123)

    def test_simple_lookup_return(self):
        test_ret = interpolate('name: %(fname)', self.test_map)
        self.assertEqual(test_ret, 'name: john')

    def test_2_level_lookup_return(self):
        test_ret = interpolate('name: %(1.fname)', self.test_map_both)
        self.assertEqual(test_ret, 'name: john')


    def test_2_level_with_def_path(self):
        test_ret = interpolate('name: %(fname)', self.test_map_both, current_path='2')
        self.assertEqual(test_ret, 'name: jane')

    def test_mult_key(self):
        test_ret = interpolate('name: %(fname) %(lname)', self.test_map)
        self.assertEqual(test_ret, 'name: john buck')

    def test_recursive_return(self):
        test_ret = interpolate('name: %(fullname)', self.test_map)
        self.assertEqual(test_ret, 'name: john buck')

    def test_2_level_recursive_return(self):
        test_ret = interpolate('name: %(1.spouse)', self.test_map_both)
        self.assertEqual(test_ret, 'name: jane doe')

    def test_replace_on_error(self):
        test_ret = interpolate('name: %(dumnname)', self.test_map, on_key_error='replace', error_replace='unknown')
        self.assertEqual(test_ret, 'name: unknown')


    def test_skip_on_error(self):
        test_ret = interpolate('name: %(dumnname)', self.test_map, on_key_error='skip')
        self.assertEqual(test_ret, 'name: ')


