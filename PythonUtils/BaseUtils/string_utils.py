#!/usr/bin/env python

"""
"""

__author__ = ""
__copyright__ = ""
__credits__ = []
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = ""

__all__ = [ 'get_between', 'get_after', 'get_before',  'index_of_count', 'replace_between', 'spinner_char', 'pluralizer',
            'format_as_decimal_string', 'unslugify', 'ellipse_trim', 'concat', 'convert_to_boolean', 'slugify',
            'indent_str', 'format_key_value']

from decimal import Decimal
import re
from unicodedata import normalize
from PythonUtils.BaseUtils.list_utils import flatten
from pprint import pformat
from json import dumps
from enum import Enum

# ===============================================================================
# text utils
# ===============================================================================


def replace_between(instring, start_key, end_key, replace, keep_keys=False, offset_count=1, count=9999):
    """
    Replace text between two keys, optionally including the keys themselves.

    :param instring: The string to search
    :param start_key: The starting boundary key
    :param end_key: The ending boundary key
    :param replace: The string to put between the boundary keys
    :param keep_keys: True/False: include the key strings in the replacement
    :param count: replace up to this many instances
    :param offset_count: start replacing after this many instances
    :return: String
    """
    instring = str(instring)

    if start_key not in instring:
        return instring

    start_pos = 0
    curs_pos = 0
    found = 0
    start_key_len = len(start_key)
    end_key_len = len(end_key)
    outstring = ''

    start_pos = index_of_count(instring, find=start_key, offset_count=offset_count, start=0)

    while True:

        if count <= found or start_pos == -1:
            break

        end_pos = instring.find(end_key, start_pos + start_key_len)

        if end_pos == -1:
            break

        if keep_keys:
            suffix = instring[end_pos:end_pos + end_key_len]
            outstring = outstring + instring[curs_pos:start_pos + start_key_len] + replace + suffix
            curs_pos = end_pos + end_key_len

        else:
            outstring = outstring + instring[curs_pos:start_pos] + replace
            curs_pos = end_pos + end_key_len

        found = found + 1

        start_pos = instring.find(start_key, curs_pos)

    return outstring + instring[curs_pos:]


def index_of_count(instring, find, offset_count=1, start=0):
    """
    Returns the string index (offset) for the x th iteration of a substring.

    :param instring: the string to search
    :param find: the string to search for
    :param offset_count: return the 'offset_count' iteration of find string
    :param start: start looking at this point in the string
    :return: the offset for the find string
    :rtype int:

    example:
        >>> index_of_count('abcd abcd abcd abcd', 'abcd', 2)
        6

    """
    if instring:
        offset_loc = start
        current_off = 0
        for i in range(offset_count):
            offset_loc = instring.find(find, current_off)
            if offset_loc > -1:
                if i == offset_count - 1:
                    return offset_loc
                current_off = offset_loc + 1
            else:
                return current_off
        return offset_loc
    return -1


def get_before(instring, find, offset_count=1):
    """
    Returns the string that occurs before the find string. If the find string is not in the string,
    this returns the entire string.

    :param instring: the string to search
    :param find: the string to look for
    :param offset_count: find the nth copy of the find string
    :return: the string that immediatly preceeds the find string.


    example:
        >>> get_before('look for the [key] in the lock','[')
        'look for the '

    """
    if find in instring:
        offset_loc = index_of_count(instring, find, offset_count)

        if offset_loc != -1:
            return instring[:offset_loc]
        return instring
    return instring


def get_after(instring, find, offset_count=1):
    """
    Returns the string that occurs after the find string. If the find string is not in the string,
    this returns the entire string.

    :param instring: the string to search
    :param find: the string to look for
    :param offset_count: find the nth copy of the find string
    :return: the string that is immediatly after the find string.


    example:
        >>> get_after('look for the [key] in the lock',']')
        ' in the lock'

    """
    if find in instring:
        offset_len = len(find)
        offset_loc = index_of_count(instring, find, offset_count)

        if offset_loc != -1:
            return_size = offset_loc + offset_len
            return instring[return_size:]
        return instring
    return instring


def get_between(instring, start_key, end_key):
    """
    Returns the string that occurs between the keys
    :param instring: the string to search
    :param start_key: the string to use to start capturing
    :param end_key: the key to use to end capturing
    :return: the string that is between the start_key and the after_key

    example:
        >>> get_betweem('look for the [key] in the lock','[',']')
        'key'

    """
    return get_after(get_before(instring, end_key), start_key)


# ===============================================================================
# Format string
# ===============================================================================

def format_as_decimal_string(num, max_decimal_points=6):
    """
    This will format a number as a string including decimals, but will correctly trim the decimal.
    :param num: number to format
    :param max_decimal_points: the max decimals to show
    :return: a string of the number with decimals.

    Examples:
        >>> format_as_decimal_string(1.234)
        '1.234'       # this would normally be '1.234000' when done by the normal format

    """
    if isinstance(num, str):
        if num.isnumeric():
            num = Decimal(num)
        else:
            return ''

    if (num % 1 == 0) or (num > 100):
        return '{:,.0f}'.format(num)
    else:
        tmp_dec_pl = '{}'.format(max_decimal_points)
        tmp_format = '{0:.' + tmp_dec_pl + 'g}'
        tmp_num_str = tmp_format.format(num)
        tmp_num_str = tmp_num_str.rstrip('0').rstrip('.')
        return tmp_num_str


def indent_str(data, next_lines=4, first_line=None, indent_char=' ', trim_lines=False):
    if first_line is None:
        first_line = next_lines
    data = data.splitlines()
    first_line_str = indent_char * first_line
    next_lines_str = indent_char * next_lines
    for index in range(len(data)):
        tmp_line = data[index]
        if trim_lines:
            tmp_line = tmp_line.strip()
        if index == 0:
            data[index] = first_line_str + tmp_line
        else:
            data[index] = next_lines_str + tmp_line
    return '\n'.join(data)


class NumberFormatHelper(object):
    def __init__(self, value, decimal_places):
        self.value = value
        self.decimal_places = decimal_places
        self.has_neg = False
        self.my_dec_len = 0
        self.my_int_len = 0
        self.int_value = ''
        self.dec_value = ''

        if value < 0:
            self.has_neg = True

        tmp_str = '{value:,.{decimal_places}f}'.format(value=value, decimal_places=abs(decimal_places))
        tmp_str = tmp_str.split('.', maxsplit=1)
        if len(tmp_str) == 1:
            self.int_value = tmp_str[0]
        else:
            self.int_value = tmp_str[0]
            self.dec_value = tmp_str[1]

        if self.decimal_places < 0:
            self.dec_value = self.dec_value.rstrip('0')

        self.my_dec_len = len(self.dec_value)
        self.my_int_len = len(self.int_value)

    def get(self, max_dec, max_int):
        # if with_neg and not self.has_neg:
        #     tmp_ret = ' '
        # else:
        #     tmp_ret = ''

        tmp_ret = self.int_value.rjust(max_int)

        if max_dec:
            tmp_ret += '.'
            tmp_ret += self.dec_value.ljust(max_dec, '0')
        return tmp_ret


class FORMAT_RETURN_STYLE(Enum):
    STRING = 'string'
    LIST = 'list'
    DICT = 'dict'
    TUPLES = 'tuples'


def format_key_value(data,
                     key_format='left',
                     value_format='auto',
                     decimal_places=-2,
                     sep=' : ',
                     indent=0,
                     value_indent=0,
                     indent_wrapped=True,
                     return_style=FORMAT_RETURN_STYLE.STRING,
                     join_str='\n'
                     ):

    """
    Formats a key, value pair into a cleaner string or other returned object.

    :param data: a dictionary or iterator of tuples
    :param sep: the string used to separate key and value for LIST and STRING returns
    :param value_indent: if you wish values to be indented an additional amount.
    :param indent_wrapped: set to False to disable auto indenting to the depth of the keys for wrapped values.
    :param return_style: can be any of:
        FORMAT_RETURN_STYLE.LIST: returns a list of strings
        FORMAT_RETURN_STYLE.TUPLES: returns a list of tuples (key, value)
        FORMAT_RETURN_STYLE.DICT: returns a dict with the keys and values formatted
        FORMAT_RETURN_STYLE.STRING: returns a string combined with join_str
    :param join_str: if returning a string, this is the string used to join lines.
    :param key_format:
        any of:
            'left': default, left justifies the key, but pads it to the length of the longest key
            'left_trimmed': left justifies the key,
            'right': right justifies the key, padding to fit all values starting at the same place
            'skip': does not return any key values.  (does not work for DICT return types)
    :param value_format:
            'repr': returns a repr of the value
            'pprint': runs pretty_print on the value
            'json': runs json formatter on the value
            'str': runs 'str' on the value
            'number': returns numbers right justified by the longest number.
            'auto' <default>:
                strings are formatted with "str",
                objects are formatted using repr
                numbers are formatted using 'number'
            'skip':  does not return any values, just returns the keys list (with no sep)
                (does not work for DICT return types.)
            'none': does not format values, will return them as passed.
                (may not work for STRING / LIST return types)
                value indents will be ignored with this option.
    :param indent: indents the key this many spaces
    :param decimal_places: if positive, will force the number to that many places
        if negative, will use the least number of decimal places possible, up to that number.
        if zero, will always return integers.
            so:
                decimal_places=2 would return
                    1      as 1.00
                    1.12   as 1.12
                    1.4567 as 1.45
                decimal_places -3 would return
                    for a list of [1, 1.12, 1.12345], [1.000, 1.120, 1.123]
                    for a list of [1, 2, 3, 4] would return [1, 2, 3, 4]
    :return:
    """
    if isinstance(data, dict):
        data = list(data.items())

    max_key = 0
    # has_neg = False
    max_dec = 0
    max_int = 0

    if return_style == FORMAT_RETURN_STYLE.DICT and (value_format == 'skip' or key_format == 'skip'):
        raise AttributeError('DICT return types cannot be used when skipping keys or values')

    for index in range(len(data)):
        key, value = data[index]

        if key_format != 'left_trimmed':
            max_key = max(max_key, len(key))

        if value_format == 'number' and not isinstance(value, (int, float, Decimal)):
            try:
                value = float(value)
            except TypeError:
                try:
                    value = int(value)
                except TypeError:
                    value = str(value)
                    value = float(value)

        if value_format in ('number', 'auto') and isinstance(value, (int, float, Decimal)):
            value = NumberFormatHelper(value, decimal_places=decimal_places)
            # has_neg = has_neg or value.has_neg
            max_dec = max(max_dec, value.my_dec_len)
            if key_format != 'left_trimmed':
                max_int = max(max_int, value.my_int_len)
        data[index] = key, value

    if return_style == FORMAT_RETURN_STYLE.DICT:
        tmp_ret = {}
    else:
        tmp_ret = []

    for key, value in data:
        tmp_line = ''
        if key_format != 'skip':
            if key_format == 'left':
                tmp_line = key.ljust(max_key)
            elif key_format == 'left_trimmed':
                tmp_line = key
            elif key_format == 'right':
                tmp_line = key.rjust(max_key)
            else:
                raise AttributeError('Invalid key_format value of %s, should be one of ["left", "left_trimmed", "right"]' % key_format)

            if indent:
                tmp_indent = ' ' * indent
                tmp_line = tmp_indent + tmp_line
            if return_style in (FORMAT_RETURN_STYLE.LIST, FORMAT_RETURN_STYLE.STRING):
                if value_format not in ('skip', 'none'):
                    tmp_line += sep

        if value_format == 'skip':
            value = ''
        elif value_format == 'repr':
            value = repr(value)
        elif value_format == 'pprint':
            value = pformat(value, indent=4)
        elif value_format == 'json':
            value = dumps(value, indent=4)
        elif value_format == 'str':
            value = str(value)
        elif value_format == 'number':
            value = value.get(max_int=max_int, max_dec=max_dec)  # , has_neg=has_neg)
        elif value_format == 'auto':
            if isinstance(value, NumberFormatHelper):
                value = value.get(max_int=max_int, max_dec=max_dec) # , has_neg=has_neg)
            elif isinstance(value, str):
                value = str(value)
            else:
                try:
                    value = dumps(value, indent=4)
                except Exception:
                    try:
                        value = pformat(value, indent=4)
                    except Exception:
                        value = repr(value)
        elif value_format != 'none':
            raise AttributeError(
                'Invalid key_format value of %s, should be one of ["left", "left_trimmed", "right"]' % key_format)
        if value_format not in ('none', 'skip'):
            if indent_wrapped:
                value = indent_str(value, next_lines=len(tmp_line), first_line=0, indent_char=' ', trim_lines=False)
            if value_indent:
                value = indent_str(value, value_indent)

        if return_style == FORMAT_RETURN_STYLE.DICT:
            tmp_ret[tmp_line] = value
        elif return_style == FORMAT_RETURN_STYLE.TUPLES:
            if value_format == 'skip':
                tmp_ret.append((tmp_line, ))
            elif key_format == 'skip':
                tmp_ret.append((value, ))
            else:
                tmp_ret.append((tmp_line, value))
        else:
            tmp_ret.append(tmp_line + value)

    if return_style == FORMAT_RETURN_STYLE.STRING:
        return join_str.join(tmp_ret)
    return tmp_ret

# ===============================================================================
# Slugify string
# ===============================================================================


def unslugify(text, case='caps', end=''):
    """
    Converts a string to a more clean version.
    :param text:
    :param case: ['caps','upper','lower','title']
    :param end:
    :return:
    """
    tmp_str = ''
    for c in text:
        if c.isupper():
            tmp_str += ' '
        tmp_str += c
    tmp_str = tmp_str.replace('_', ' ').strip()
    if case == 'caps':
        tmp_str = tmp_str.capitalize()
    elif case == 'title':
        tmp_str = tmp_str.title()
    elif case == 'upper':
        tmp_str = tmp_str.upper()
    elif case == 'lower':
        tmp_str = tmp_str.lower()
    tmp_str += end
    return tmp_str


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify2(text, delim=u'-'):
    """Generates a slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    print('sluggify result:', result)
    return str(delim.join(result))


def slugify(text, delim='_', case='lower', allowed=None, punct_replace='', encode=None):
    """
    generates a simpler text string.

    :param text:
    :param delim: a string used to delimit words
    :param case: ['lower'/'upper'/'no_change']
    :param allowed: a string of characters allowed that will not be replaced.  (other than normal alpha-numeric which
        are never replaced.
    :param punct_replace: a string used to replace punctuation characters, if '', the characters will be deleted.
    :param encode: Will encode the result in this format.
    :return:
    """
    punct = '[\t!"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+'
    if allowed is not None:
        for c in allowed:
            punct = punct.replace(c, '')

    result = []

    for word in text.split():
        word = normalize('NFKD', word)
        for c in punct:
            word = word.replace(c, punct_replace)
        result.append(word)

    delim = str(delim)
    # print('sluggify results: ', result)
    text_out = delim.join(result)

    if encode is not None:
        text_out.encode(encode, 'ignore')

    if case == 'lower':
        return text_out.lower()
    elif case == 'upper':
        return text_out.upper()
    else:
        return text_out



# ===============================================================================
# text / string utils
# ===============================================================================


def ellipse_trim(instr, trim_length, elipse_string='...'):
    """
    Makes sure strings are less than a specified length, and adds an elipse if it needed to trim them.

    :param instr: The String to trim
    :param trim_length: The max length, INCLUDING the elipse
    :param elipse_string: the string used for the elipse.  Default: '...'
    :return: Trimmed string

    Examples:
        >>> elipse_trim('this is a long string',10)
        'this is...'

    """
    instr = str(instr)
    str_len = trim_length - len(elipse_string)
    if len(instr) > trim_length:
        return '{}{}'.format(instr[:str_len], elipse_string)
    else:
        return instr


def concat(*args, separator=' ', trim_items=True):
    """
    Concatenates strings or iterables

    :param args: strings or iterables
    :param separator: the string that will be used between strings.  Default: ' '
    :param trim_items: True/False, trim strings before concatenating.
    :return: string created from contents passed
    """
    # tmp_str = ""

    args = flatten(args)
    tmp_args = []
    for a in args:
        if trim_items:
            tmp_args.append(str(a).strip())
        else:
            tmp_args.append(str(a))
    return separator.join(tmp_args)


# ===============================================================================
# return boolean from varied strings
# ===============================================================================

def convert_to_boolean(obj):
    """
    Converts an object to a boolean, mostly for strings, but can also accept objects that will convert correctly.
    :param obj: the object to convert
    :return: a boolean representing the object

    Examples:
        >>> convert_to_boolean('yes')
        True
        >>> convert_to_boolean(0)
        False

    """
    istrue = ('true', 'yes', 'ok', '1', 'on', '+', 'True', 'Yes', 'Ok', 'On', 'TRUE', 'YES', 'OK', 'ON', 1, 1.0)
    isfalse = ('false', 'no', '0', '-', 'off', 'False', 'No', 'Off', 'FALSE', 'NO', 'OFF', 0, 0.0)

    if isinstance(obj, (str, int, float)):
        if obj in istrue:
            return True
        elif obj in isfalse:
            return False
        else:
            raise TypeError('could not convert to boolean')

    elif hasattr(obj, '__bool__'):
        return bool(obj)

    raise TypeError('could not convert to boolean')

# ===============================================================================
# spinner (working) character generator
# ===============================================================================

def spinner_char(state=0, spinner_chars='|/-\\', not_started_state=None, finished_state=None, not_started_ret=' ',
                 finished_ret="x"):
    if not_started_state is not None and state <= not_started_state:
        return not_started_ret
    elif finished_state is not None and state >= finished_state:
        return finished_ret
    return spinner_chars[state % len(spinner_chars)]


# ===============================================================================
# spinner (working) character generator
# ===============================================================================

def pluralizer(number_in, singular, plural=None):
    if number_in == 1:
        return singular
    elif plural is None:
        return singular + 's'
    else:
        return plural