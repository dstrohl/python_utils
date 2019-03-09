#!/usr/bin/env python

"""
Take lines or data and dump to a clean string.
"""

__author__ = ""
__copyright__ = ""
__credits__ = []
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = ""

from PythonUtils.BaseUtils import iif

class LineItem(object):
    def __init__(self,
                 parent,
                 key=None,
                 value=None,
                 flag=None,
                 indent=0,

                 value_trim_to=None,
                 value_trim_elipse=True,

                 lookup=None,
                 key_align='left',
                 key_len=None,
                 format_args=None,
                 return_as=None,
                 **format_kwargs):

        self.key = key
        self.value = value
        self.parent = parent
        self.flag = flag
        self.indent=indent
        self.lookup = lookup
        self.key_align = key_align
        self.return_as = return_as
        if key_len is not None:
            self.key_len = key_len
        elif key is None:
            self.key_len = 0
        else:
            self.key_len = len(key)

        self.format_kwargs = format_kwargs
        self.format_args = format_args
        self.value_trim_to = value_trim_to
        self.value_trim_elipse = value_trim_elipse


class LineSepItem(object):
    def __init__(self, parent, line_char='-', line_len=None, indent=0):
        self.parent = parent
        self.line_char = line_char
        self.line_len = line_len
        self.indent = indent


class SpaceSepItem(object):
    def __init__(self, parent):
        self.parent = parent


class LineReporter(object):
    def __init__(self,
                 *data_in,
                 sep=' : ',
                 value_trim_to=None,
                 value_trim_elipse=True,
                 line_char='-',
                 line_len=None,

                 header=None,
                 header_sep='=',
                 footer=None,
                 footer_sep='=',

                 bracket_strings=False,
                 skip_on_none=False,
                 skip_on_empty=False,
                 return_as=None,
                 ):
        self.data = []
        self.section_queue = []
        self.sep = sep
        self.value_trim_to = value_trim_to
        self.value_trim_elipse = value_trim_elipse
        self.line_char = line_char
        self.line_len = line_len
        self.header = header
        self.header_sep = header_sep
        self.footer = footer
        self.footer_sep = footer_sep
        self.bracket_strings = bracket_strings
        self.skip_on_none = skip_on_none
        self.skip_on_empty = skip_on_empty
        self.return_as = return_as

    def add(self, *args, **kwargs):
        tmp_item = LineItem(self, *args, **kwargs)
        self.data.append(tmp_item)

    def extend(self, data_in, indent=None, lookup=None, key_align=None, key_len=None, value_len=None, format_args=None, **format_kwargs):
    
    def add_line(self, line_char=None, line_len=None, line_count=1, indent=None):
        line_char = line_char or self.line_char
        line_len = line_len or self.line_len
        for i in range(line_count):
            tmp_add = LineSepItem(self, line_char=line_char, line_len=line_len, indent=indent)
            self.data.append(tmp_add)

    def add_space(self, space_count=1):
        for i in range(space_count):
            tmp_add = SpaceSepItem(self)
            self.data.append(tmp_add)

    def add_section(self, sec_name, data, indent=None):


    def section(self, sec_name):


    def to_string(self, *args, **kwargs):
        tmp_ret = []
        for i in self.data:
            tmp_ret.append(i.get(*args, **kwargs))
        return '\n'.join(tmp_ret)

    def __len__(self):
        return len(self.data)

    def __bool__(self):
        return bool(self.data)

    def __iadd__(self, other):


    def __add__(self, other):

