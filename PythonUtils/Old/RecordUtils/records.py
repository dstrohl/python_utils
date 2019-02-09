__author__ = 'strohl'

from TextUtils.detection import is_string, make_list
from TextUtils.lists import get_not_in, get_different

class RecordAddFieldDisallowed(Exception):
    def __init__(self, fieldname = '', message=None):
        if message:
            self.message = message
        else:
            if fieldname:
                self.message = 'Field {} cannot be added, record locked'.format(fieldname)
            else:
                self.message = 'Field cannot be added, record locked'


    def __str__(self):
        return self.message

class RecordReorderFieldsException(Exception):
    def __init__(self, message=None):
        if message:
            self.message = message
        else:
            self.message = 'Error reordering field list, passed list did not contain the same fields'

    def __str__(self):
        return self.message

class RecordNoDataException(Exception):
    def __init__(self, fieldname=None, message=None):
        if message:
            self.message = message
        else:
            if fieldname:
                self.message = 'Field {} is empty'.format(fieldname)
            else:
                self.message = 'Field is empty'

    def __str__(self):
        return self.message


class RecordData(object):

    def __init__(self, default=None):
        self.dict = {}
        self.fieldnames = []
        self.default = default

    def __getitem__(self, item):
        if item in self.fieldnames:
            try:
                return self.dict[item]
            except KeyError:
                if self.default == 'raise':
                    raise RecordNoDataException(item)
                return self.default
        else:
            raise RecordNoDataException(item)

    def __contains__(self, item):
        return item in self.fieldnames

    def __iter__(self):
        for fn in self.fieldnames:
            yield fn

'''
class ArgsEvaluator(object):

    def __init__(self):
        self.in_args = set()
        self.in_kwargs = {}

    def evaluate(self, looking_for, args=None, kwargs=None):
        self.fieldnames = []
        self.datalist = []
        self.fielddict = {}

        output_count = 0

        in_args_list = []
        tmp_fieldnames = []
        tmp_in_dict = {}

        for a in args:
            if isinstance(a, dict):
                if kwargs:
                    tmp_in_dict.update(a)
                else:
                    tmp_in_dict = args

            if isinstance(a, str):
                in_args_list.append(a)

            if isinstance(a, (list,tuple,set)):
                in_args_list.extend(a)

        if kwargs:
            if '_fieldnames' in kwargs:
                tmp_fieldnames = kwargs.pop('_fieldnames')

            for f in list(kwargs):
                if f[0] == '_':
                    tmp_message  = 'Invalid fieldname: {}'.format(f)
                    raise AttributeError(tmp_message)

            tmp_in_dict = kwargs

        if in_args_list and tmp_fieldnames:
            if len(in_args_list) >= len(tmp_fieldnames):
                cnt = len(tmp_fieldnames)
            else:
                cnt = len(in_args_list)

            for i in range(cnt):
                tmp_in_dict[tmp_fieldnames[i]] = in_args_list[i]

        self.fielddict = tmp_in_dict

        if self.fieldnames:
            output_count += 1
            tmp_output = self.fieldnames

        if self.fielddict:
            output_count += 1
            tmp_output = self.fielddict

        if self.datalist:
            output_count += 1
            tmp_output = self.datalist

        if looking_for == 'fieldnames':
            if in_args_list:
                self.fieldnames = in_args_list
            if tmp_fieldnames:
                self.fieldnames = tmp_fieldnames

        else:
            if in_args_list:
                self.datalist = in_args_list

        if tmp_output > 1:
            return tmp_output
        else:
            return None
'''

class Record(object):
    #arg_eval = ArgsEvaluator()

    def __init__(self, *args, **kwargs):
        '''
        *args:
            if a list is passed, this becomes the fieldname list
            if a dict is passed, this is used as the initial fieldnames and data

        **kwargs:
            _locked: restricts new fields from being added
            _fieldnames: sets initial list of fieldnames
            _on_unknown_add: 'raise'/'ignore' action to take if new field tries to be added
        '''

        tmp_data = {}
        tmp_locked = kwargs.pop('_locked', False)
        tmp_fieldnames = kwargs.pop('_fieldames', None)
        on_unknown_add = kwargs.pop('_on_unknown_add','ignore')

        #self.arg_eval.evaluate(args, kwargs)

        if args:
            if isinstance(args[0], dict):
                tmp_data = args[0]
            elif isinstance(args[0], list):
                if tmp_fieldnames:
                    tmp_data = args[0]
                else:
                    tmp_fieldnames = args[0]

        tmp_rec_data = RecordData()

        super(Record,self).__setattr__('_locked', False)
        super(Record,self).__setattr__('_data', RecordData())
        super(Record,self).__setattr__('_on_unknown_add', on_unknown_add)

        if kwargs:
            tmp_data.update(kwargs)

        if tmp_fieldnames:
            self._add_fields(tmp_fieldnames)
            self._locked = tmp_locked

        self._add_data(**tmp_data)


    @property
    def _fieldnames(self):
        return self._data.fieldnames

    def _add_field(self, fieldname, value=None):
        if fieldname not in self._data.fieldnames:
            if self._locked:
                if self._on_unknown_add == 'raise':
                    raise RecordAddFieldDisallowed(fieldname)
            else:
                self._data.fieldnames.append(fieldname)
                self._data.dict[fieldname] = value
        elif value:
            self._data.dict[fieldname] = value


    def _add_fields(self, fields_list):
        for field in make_list(fields_list):
            self._add_field(field)

    def _add_dict(self, in_dict):
        for key, item in iter(in_dict.items()):
            self._add_field(key, item)

    def _add_data(self, *args, **kwargs):
        if len(args) == 1:
            if isinstance(args[0], dict):
                self._add_dict(args[0])
        elif args:
            i = 0
            args = make_list(args)
            for a in args:
                try:
                    self._data.dict[self._data.fieldnames[i]] = a
                except IndexError:
                    if self._on_unknown_add == 'raise':
                        raise RecordAddFieldDisallowed('Error adding un-named data')
                i += 1

        if kwargs:
            self._add_dict(kwargs)

    @property
    def _dict(self):
        return self._data.dict

    @property
    def _list(self):
        tmp_ret = []
        for fn in self._data:
            tmp_ret.append(self._data[fn])
        return tmp_ret


    def _reorder_list(self, fieldlist):
        test_list = get_different(fieldlist, self._data.fieldnames)
        if test_list:
            raise RecordReorderFieldsException()
        else:
            self._data.fieldnames = fieldlist

    def __getitem__(self, item):
        return self._data.dict[item]

    def __setitem__(self, key, value):
        self._add_field(key, value)

    def __getattr__(self, item):
        if item in self.__dict__['_data'].dict:
            return self.__dict__['_data'].dict[item]
        else:
            raise AttributeError


    def __setattr__(self, key, value):
        try:
            self.__data.dict[key] = value
        except AttributeError:
            super(Record, self).__setattr__(key, value)

    def __delattr__(self, item):
        if item in self.__data.dict:
            del self.__dict__['__data'].dict[item]
        else:
            raise AttributeError()

    def __contains__(self, item):
        return item in self._data.fieldnames

    def __len__(self):
        return len(self._data.dict)

    def __repr__(self):
        return 'Record: '+str(self._data.dict)