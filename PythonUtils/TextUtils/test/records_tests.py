__author__ = 'strohl'

import unittest
from TextUtils import Record, RecordAddFieldDisallowed, RecordReorderFieldsException

fn = ['one','two','three']
init_dict = {'one':1,'two':2,'three':3}
new_fields = ['four','five','six']
new_dict = {'four':4,'five':5,'siz':6}
all_fields = ['one','two','three','four','five','six']
all_dict = dict(init_dict)
all_dict.update(new_dict)


class TestRecords(unittest.TestCase):


    def test_add_fields_allowed(self):
        tr = Record(fn)
        self.assertEqual(fn, tr._data.fieldnames)
        tr2 = Record(fn, False)
        tr2._add_fields(new_fields)
        self.assertEqual(all_fields, tr2._data.fieldnames)


    def test_add_fields_disallowed_raise(self):
        tr2 = Record(fn, _locked=True, _on_unknown_add='raise')
        with self.assertRaises(RecordAddFieldDisallowed):
            tr2._add_fields(new_fields)

    def test_add_fields_disallowed_ignore(self):
        tr = Record(fn, _locked=True, _on_unknown_add='ignore')
        tr._add_fields(new_fields)
        self.assertEqual(fn, tr._data.fieldnames)

    def test_add_data_on_setup(self):
        tr = Record(**init_dict)
        self.assertEqual(1, tr._data.dict['one'])


    def test_add_data_with_extra_ignored(self):
        tr = Record(fn, _locked=True, _on_unknown_add='ignore')
        tr._add_data(all_dict)
        self.assertEqual(init_dict, tr._dict)

    def test_add_data_with_extra_raise(self):
        tr = Record(fn, _locked=True, _on_unknown_add='raise')
        with self.assertRaises(RecordAddFieldDisallowed):
            tr._add_data(all_dict)
            self.assertEqual(init_dict, tr._dict)

    def test_set_attr(self):
        tr = Record(fn)
        tr.one = 3
        self.assertEqual(tr.one, 3)

    def test_get_item(self):
        tr = Record(fn)
        tr['one'] = 3
        self.assertEqual(tr['one'], 3)

    def test_contains(self):
        tr = Record(fn)
        test_ret = 'one' in tr
        self.assertEqual(test_ret, True)

    def test_len(self):
        tr = Record(fn)
        self.assertEqual(len(tr), 3)







if __name__ == '__main__':
    unittest.main()
