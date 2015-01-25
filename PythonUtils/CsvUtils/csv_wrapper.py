__author__ = 'strohl'

import csv
import copy

class CSVData():
    def __init__(self, filename, key_field=None, fieldnames=None, duplicate_keys='raise', **kwargs):
        '''
        This is a wrapper for csv.DictReader.
        :param filename:  filename to read
        :param key_field:  key field to use for lookups
        :param fieldnames:  list of fieldnames (assumes that first line is then not fieldnames
        :param duplicate_keys:  'raise' / 'first' / 'append'
             'raise' will raise a AttributeError exception
             'first' will allow the first key through, and ignore the rest
             'append' will append '[dupe count]' to the end of the key
             '<format string>' will format the key string using the following keys
                {__count__} : line number
                {__dupe_count__} : dupe counter
                {__key__} : defined key field
                {<record field>} : any field from the record dictionary
        :param kwargs: kwargs to pass to DictReader
        :return:
        '''
        self.filename = filename
        self._key_lookup = {}
        self._data = None
        self.fieldnames = fieldnames
        self._reader_args = kwargs
        self._key_field = key_field
        self._key_cache = None
        self._duplicate_key_action = duplicate_keys

        if fieldnames and key_field:
            if key_field not in fieldnames:
                raise AttributeError("Key field is not in the list of fieldnames")

    @property
    def data(self):
        if self._data:
            return self._data
        else:
            self._data = []
            return self._load_data()

    def _load_data(self):
        if self._data:
            return None
        self._data = []
        tmp_encoding = self._reader_args.pop('encoding', None)
        with open(self.filename, newline='', encoding=tmp_encoding) as infile:
            reader = csv.DictReader(infile, fieldnames=self.fieldnames, **self._reader_args)
            if not self.fieldnames:
                self.fieldnames = reader.fieldnames
            if self._key_field:
                if self._key_field not in self.fieldnames:
                    raise AttributeError('Key field is not in the list of fieldnames')
            count = 0
            for row in reader:
                if self._key_field:
                    tmp_key, tmp_rec = self.dupe_key_check(row, self._key_field, self._duplicate_key_action, self._key_lookup, self._data, self._key_cache)
                else:
                    tmp_rec = row
                    tmp_key = count

                if tmp_rec:
                    self._key_lookup[tmp_key] = count
                    self._data.append(tmp_rec)
                    count += 1

        return self._data

    def __getitem__(self, item):
        self._load_data()
        tmp_row = self._key_lookup[item]
        return self.data[tmp_row]

    def __iter__(self):
        for row in self.data:
            yield row

    def __len__(self):
        return len(self.data)

    def find(self, field, item):
        self._load_data()
        if field == self._key_field:
            try:
                return self[item]
            except KeyError:
                return None

        if field not in self.fieldnames:
            raise AttributeError('Field not a valid field')

        for row in self:
            if row[field] == item:
                return row

        return None

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def row(self, row):
        return self.data[row]

    def dupe_key_check(self,
                       row,
                       key_field,
                       action_string,
                       key_lookup,
                       data_list,
                       key_cache):
        '''
        This is intended to be over-ridden if different duplicate operations is desired
        :param row: row record being imported
        :param key_field: key field
        :param action_string:  action string from init
        :param key_lookup: the key lookup dict
        :param data_list: the data list
        :param key_cache: a cache used for storing first key instance info
        :return: key, data_row (or None/None if nothing to be saved)
        '''

        tmp_key = row[key_field]
        if tmp_key not in key_lookup:
            return tmp_key, row

        if action_string == 'raise':
            old_row = key_lookup[tmp_key]
            tmp_msg = 'Key field duplicated, in rows {} and {}.'.format(old_row+1, len(data_list)+1)
            raise KeyError(tmp_msg)
            return None, None

        if action_string == 'first':
            return None, None

        if action_string:

            if action_string == 'append':
                tmp_format = '{__key__}[{__dupe_count__}]'
            else:
                tmp_format = action_string

            if key_cache is None:
                key_cache = {}
            try:
                dupe_cnt = key_cache[tmp_key]
            except KeyError:
                dupe_cnt = 0

            dupe_cnt += 1
            tmp_fields = {}
            tmp_fields.update(row)
            tmp_fields['__key__'] = tmp_key
            tmp_fields['__dupe_count__'] = dupe_cnt
            tmp_fields['__count__'] = len(data_list)+1

            new_key = tmp_format.format(**tmp_fields)

            key_cache[tmp_key] = dupe_cnt

            return new_key, row

        return None, None