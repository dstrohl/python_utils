__author__ = 'strohl'

import unittest
from TextUtils import CSVData

tf = 'csvtest.csv'


class TestCSVData(unittest.TestCase):

    def test_load_data(self):
        c = CSVData(tf, 'key')
        self.assertEqual(8, len(c.data))

    def test_load_no_key(self):
        c = CSVData(tf)
        self.assertEqual(8, len(c))

    def test_get_data(self):
        c = CSVData(tf, key_field='key')
        self.assertEqual('E', c['EF']['first'])

    def test_search_key(self):
        c = CSVData(tf, key_field='key')
        tmp = c.find('key', 'EF')
        self.assertEqual('E', tmp['first'])

    def test_search_non_key(self):
        c = CSVData(tf, key_field='key')
        tmp = c.find('first','E')
        self.assertEqual('F', tmp['last'])

    def test_row(self):
        c = CSVData(tf, key_field='key')
        tmp = c.row(3)
        self.assertEqual('K', tmp['last'])

    def test_empty_search(self):
        c = CSVData(tf, key_field='key')
        tmp = c.find('first','z')
        self.assertEqual(None, tmp)

    def test_raise_on_dupe_key(self):
        with self.assertRaises(KeyError):
            c = CSVData(tf, key_field='last')
            tmp = c['Q']

    def test_first_on_dupe_key(self):
        c = CSVData(tf, key_field='last', duplicate_keys='first')
        tmp = len(c)
        self.assertEqual(7, tmp)

    def test_append_counter_on_dupe_key(self):
        c = CSVData(tf, key_field='last', duplicate_keys='append')
        tmp = len(c)
        self.assertEqual(8, tmp)


    def test_append_counter_on_dupe_key(self):
        c = CSVData(tf, key_field='last', duplicate_keys='dupe{__dupe_count__}')
        tmp = c['dupe1']['first']
        self.assertEqual('R', tmp)


    def test_raise_on_invalid_key(self):
        with self.assertRaises(AttributeError):
            c = CSVData(tf, key_field='not_there')
            tmp = c['Q']

if __name__ == '__main__':
    unittest.main()
