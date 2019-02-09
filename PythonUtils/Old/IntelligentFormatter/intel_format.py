__author__ = 'dstrohl'

import copy
from PythonUtils import ListPlus


class IntFmtList(ListPlus):
    """
    Modifies the List Plus Class for the intelligent formatter
    """
    def _update_function(self, old, new):
        if old:
            old.add(new)
            return old
        else:
            tmp_new = PriGroup(new)
            return tmp_new

class IntelligentFormat(object):
    fields_list = []
    priority_list = IntFmtList()
    fields_dict = {}
    full_string_rec = None


    def __init__(self, length_limits_dict, format_str, fields_dict = None):
        field_names = find_enclosed(format_str, '{', '}', ignore_after = ':')
        field_formats = find_enclosed(format_str, '{', '}')

        for field_name, format_string in zip(field_names, field_formats):
            field_def = length_limits_dict.get(field_name, {})

            initial_string = None
            if fields_dict:
                initial_string = fields_dict.get(field_name, None)

            tmp_field = FormatField(
                                field_name,
                                format_string,
                                field_def,
                                initial_string)
            self.fields_list.append(tmp_field)
            self.fields_dict[field_name] = tmp_field

            self.priority_list.update(tmp_field.trim_priority, tmp_field, [])

        self.full_string_rec = FormatFullString(
                                                '__full_string__',
                                                format_string,
                                                fields_dict['__full_string__'])
        self.full_string_rec.set_string(self.fields_list)


class IntelligentFormatOld(object):
    default_dict = {
                    'max_length': None,
                    'min_length': 10,
                    'do_not_show_length': 4,
                    'pad_to_max': False,
                    'justification':'left',
                    'end_string': '',
                    'padding_string': ' ',
                    'trim_string': '+',
                    'trim_priority': 1, }

    fields_dict = {}
    fields_def_dict = {}
    priority_list = IntFmtList()
    max_pri_depth = 0
    template_overhead = 0

    field_list = []

    def __init__(self, length_limits_dict, format_str, fields_dict=None, **kwargs):

        field_names = find_enclosed(format_str, '{', '}', ignore_after = ':')
        field_formats = find_enclosed(self.format_str, '{', '}')

        for field_name, field_format in zip(field_names, field_formats):
            field_def = length_limits_dict.get(field_name, {})



        self.length_limits_dict = length_limits_dict
        self.format_str = format_str

        self.generate_field_limits_dict()

        if fields_dict:
            self.fields_dict = fields_dict
        elif kwargs:
            self.fields_dict = kwargs






    def generate_field_limits_dict(self):

        self.full_fields_list = find_enclosed(self.format_str, '{', '}', ignore_after = ':')


        self.full_string_limits = copy.deepcopy(self.default_dict)
        self.full_string_limits.update(self.length_limits_dict.get('__full_string__', {}))

        self.fields_def_dict = {}
        tmp_fields_dict = {}
        self.priority_list.clear()

        for field in self.full_fields_list:
            tmp_limits_dict = copy.deepcopy(self.default_dict)
            tmp_limits_dict.update(self.length_limits_dict.get(field, {}))
            self.fields_def_dict[field] = tmp_limits_dict
            tmp_pri = self.fields_def_dict[field]['trim_priority']
            self.priority_list.update(tmp_pri, field, [])
            tmp_fields_dict[field] = ''

        self.max_pri_depth = len(self.priority_list)

        # print(tmp_fields_dict)

        tmp_str = self.format_str.format(**tmp_fields_dict)
        self.template_overhead = len(tmp_str)


    def format(self, fields_dict = None, **kwargs):

        max_length = 0
        format_overhead = 0
        pri_0_length = 0

        rem_space_avail = 0

        if fields_dict:
            self.fields_dict = fields_dict
        elif kwargs:
            self.fields_dict = kwargs

        self._verify_fields()

        # trim to field level max's
        self._trim_fields()

        # apply padding to pri 0 fields so we get their sixzes right
        self._pad_fields(set_num = 0)


        if self._check_formatted():
            pass
            # return self._final_format_step()



        # self.orig_fields_dict = copy.deepcopy(self.fields_dict)



    def _pad_fields(self, field = None, set_num = None):
        if field:
            tmp_field = self.fields_dict[field]
            tmp_max = self.fields_def_dict[field]['max_length']
            if tmp_max and self.fields_def_dict[field]['pad_to_max']:
                pad_needed = len(tmp_field) - tmp_max

                if pad_needed > 0:

                    tmp_padding = str(self.fields_def_dict[field]['padding_string'])
                    tmp_just = self.fields_def_dict[field]['justification']

                    if tmp_just == 'left':
                        if pad_needed <= 2:
                            tmp_padding = ' '
                        tmp_field = tmp_field + ' '
                        tmp_field = tmp_field.ljust(tmp_max, tmp_padding)

                    elif tmp_just == 'right':
                        if pad_needed <= 4:
                            tmp_padding = ' '
                        tmp_field = ' ' + tmp_field
                        tmp_field = tmp_field.rjust(tmp_max, tmp_padding)


                    elif tmp_just == 'center':
                        if pad_needed <= 2:
                            tmp_padding = ' '
                        tmp_field = ' ' + tmp_field + ' '
                        tmp_field = tmp_field.center(tmp_max, tmp_padding)

        elif set_num:
            for fieldname in self.priority_list[set_num]:
                self._trim_fields(field = fieldname)
        else:
            for fieldname in self.full_fields_list:
                self._trim_fields(field = fieldname)




    def _trim_fields(self, field = None, set_num = None, max_len = None, ignore_min = False):
        if field:
            if max_len:
                tmp_max = max_len
            else:
                tmp_max = self.fields_def_dict[field]['max_length']
            if len(self.fields_dict[field]) >= tmp_max:
                self.fields_dict[field] = self.fields_dict[field][:tmp_max - 1] + self.fields_def_dict[field]['trim_string']


        elif set_num:
            for fieldname in self.priority_list[set_num]:
                self._trim_fields(field = fieldname, max = max, ignore_min = ignore_min)
        else:
            for fieldname in self.full_fields_list:
                self._trim_fields(field = fieldname, max = max, ignore_min = ignore_min)



    def _get_priority_set_nums (self, pri_set):

        set_text_len = 0
        set_min_len = 0
        set_max_len = 0

        for field in self.priority_list[pri_set]:
            tmp_t, tmp_min, tmp_max = self._get_field_nums(field)
            set_text_len = set_text_len + tmp_t
            set_min_len = set_min_len + tmp_min
            set_max_len = set_max_len + tmp_max

        return set_text_len, set_min_len, set_max_len


    def _get_field_nums(self, field_name):
        tmp_text_len = len(self.fields_dict[field_name])
        tmp_min_len = self.fields_def_dict[field_name]['min_length']
        tmp_max_len = self.fields_def_dict[field_name]['max_length']
        return tmp_text_len, tmp_min_len, tmp_max_len



    def _verify_fields(self):

        try_again = False

        if not self.fields_dict:
            raise ValueError('Fields Dictionary not defined')

        for field in self.full_fields_list:
            try:
                tmp_fld = self.fields_def_dict[field]
            except KeyError:
                self.generate_field_limits_dict()
                try_again = True
                break

        if try_again:
            for field in self.full_fields_list:
                if field not in self.fields_dict:
                    raise ValueError('fields in dict do not match template')


    def _final_format_step(self):
        pass

    def _format_str (self):
        self.formatted_str = self.format_str.format(**self.fields_dict)
        self.formatted_str_len = len(self.formatted_str)
        if self.full_string_limits['max_length']:
            self.length_ok = self.formatted_str_len <= self.full_string_limits['max_length']
        else:
            self.length_ok = True

    def _formatted_length(self):
        self._format_str()
        return self.formatted_str_len

    def _check_formatted(self):
        self._format_str()
        return self.length_ok


def find_enclosed(in_string, start, end, include_all=True, default='', ignore_after=None):
    all_returns = []

    if not isinstance(in_string, str):
        in_string = str(in_string)

    empty_ret = False
    if not check_in(in_string, start, end):
        empty_ret = True

    if not empty_ret:
        if include_all:
            while check_in(in_string, start, end):
                found_string, in_string = find_in(in_string, start, end, ignore_after)
                all_returns.append(found_string)
            return all_returns
        else:
            found_str, remaining_str = find_in(in_string, start, end, ignore_after)
            return found_str

    else:
        if include_all:
            return [default, ]
        else:
            return default


def find_in(in_string, start, end, ignore_after):
    before_start, after_start = in_string.split(start, 1)
    found_str, remaining_str = after_start.split(end, 1)
    if ignore_after:
        try:
            found_str, junk_str = found_str.split(ignore_after, 1)
        except ValueError:
            pass

    return found_str, remaining_str


def check_in(in_string, start, end):
    if start not in in_string:
        return False

    if end not in in_string:
        return False

    return True



class FormatField(object):
    init_max_length = None
    min_length = 10
    do_not_show_length = 4
    pad_to_max = False
    justification = 'left'
    end_string = ''
    padding_string = ' '
    trim_string = '+'
    trim_priority = 1

    current_max_length = None
    ignore_min = False

    current_string = ''
    field_dict = {}
    format_string = ''
    rendered_string = ''

    curr_length = 0

    _length_ok = False

    def __init__(self,
                 name,
                 format_string,
                 field_def_dict,
                 initial_string = None,
                ):

        self.name = name
        self.format_string = format_string
        if initial_string:
            self.initial_string = initial_string
            self.current_string = initial_string
            self._try_format()


        self.init_max_length = field_def_dict.get('max_length', self.init_max_length)
        self.min_length = field_def_dict.get('min_length', self.min_length)
        self.do_not_show_length = field_def_dict.get('do_not_show_length', self.do_not_show_length)
        self.pad_to_max = field_def_dict.get('pad_to_max', self.pad_to_max)
        self.justification = field_def_dict.get('justification', self.justification)
        self.end_string = field_def_dict.get('end_string', self.end_string)
        self.padding_string = field_def_dict.get('padding_string', self.padding_string)
        self.trim_string = field_def_dict.get('trim_string', self.trim_string)
        self.trim_priority = field_def_dict.get('trim_priority', self.trim_priority)

    def __str__(self):
        return self.current_string

    @property
    def rendered_str(self):
        self._try_format()
        return self.rendered_string

    def _update_field_dict(self):
        self.field_dict = {}
        self.field_dict[self.name] = self.current_string

    def _try_format(self):
        self._update_field_dict()

        # print(self.field_dict)
        # print(self.format_string)

        if self.current_max_length == 0:
            self.rendered_string = ''
            self.curr_length = 0
        else:
            self.rendered_string = self.format_string.format(**self.field_dict)
            self.curr_length = len(self.rendered_string)

        if self.current_max_length:
            self._length_ok = self.curr_length <= self.current_max_length
            return

        self._length_ok = True

        # print('-- Format --')

        # print('current  : ', self.current_string)
        # print('rendered : ', self.rendered_string)
        # print('length   : ', self.curr_length)


        # print('------------')




    def max_length(self, max_len = None , ignore_min = None):
        if max_len:
            self.current_max_length = max_len

        if ignore_min != None:
            self.ignore_min = ignore_min

        if ignore_min:
            if self.current_max_length <= self.do_not_show_length:
                self.current_max_length = 0
        else:
            if self.current_max_length <= self.min_length:
                self.current_max_length = self.min_length


        self._try_format()
        return self._length_ok

    def set_string(self, initial_string):
        self.initial_string = initial_string
        self.current_string = initial_string
        self._try_format()
        return self._length_ok

    @property
    def length_ok(self):
        self._try_format()
        return self._length_ok

    def _pad_me(self):
        # print('max:', self.current_max_length)
        # print('pad:', self.pad_to_max)
        if self.current_max_length and self.pad_to_max:
            self._try_format()

            pad_needed = self.current_max_length - self.curr_length
            # print('needed', pad_needed)

            if pad_needed > 0:

                tmp_padding = self.padding_string
                if self.justification == 'left':
                    if pad_needed <= 2:
                        tmp_padding = ' '
                    self.current_string = self.current_string + ' '
                    self.current_string = self.current_string.ljust(self.current_max_length, tmp_padding)

                elif self.justification == 'right':
                    if pad_needed <= 4:
                        tmp_padding = ' '
                    self.current_string = ' ' + self.current_string
                    self.current_string = self.current_string.rjust(self.current_max_length, tmp_padding)


                elif self.justification == 'center':
                    if pad_needed <= 2:
                        tmp_padding = ' '
                    self.current_string = ' ' + self.current_string + ' '
                    self.current_string = self.current_string.center(self.current_max_length, tmp_padding)
            self._try_format()


    def _trim_me(self, max_length = None, ignore_min = None):

        # print('trim to:', max_length)

        if max_length or ignore_min:
            self.max_length(max_length, ignore_min)

        if self.current_max_length:
            if self.curr_length >= self.current_max_length:
                if self.current_max_length == 0:
                    self.current_string = ''
                else:
                    # print ('cur max length: ', self.current_max_length)
                    self.current_string = self.initial_string[:self.current_max_length - 1] + self.trim_string

        self._try_format()



class FormatFullString(FormatField):

    full_rendered_string = ''
    full_format_string = ''
    field_list = []

    def set_string(self, field_list):
        self.field_list = field_list
        self._try_format()
        return self._length_ok

    def _update_field_dict(self):

        self.field_dict = {}
        for f in self.field_list:
            self.field_dict[f.name] = f.current_string




class PriGroup(object):
    field_list = []
    priority = 0

    total_current_length = 0
    total_max_current_length = 0
    total_min_length = 0


    def __init__(self, new_field = None):
        if new_field:
            self.add(new_field)


    def add(self, new_field):
        self.field_list.append(new_field)
        self.priority = new_field.trim_priority

    def _recalc(self):

        for f in self.field_list:
            self.total_current_length = self.total_current_length + f.current_length
            self.total_max_current_length = self.total_max_current_length + f.current_max_length
            self.total_min_length = self.total_min_length + f.min_length

