#!/usr/bin/env python


__all__ = ['UnSet', '_UNSET', 'LookupManager', 'Error', 'swap', 'NextItem']

import collections
from PythonUtils.BaseUtils.string_utils import slugify

# ===============================================================================
# Error Class
# ===============================================================================

class Error(Exception):
    """Base class for custom exceptions."""

    def __init__(self, msg='', *args, **kwargs):
        self.message = str(msg).format(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__


# ===============================================================================
# UnSet Class
# ===============================================================================

class UnSet(object):
    """
    Used in places to indicated an unset condition where None may be a valid option

    .. note:: *I borrowed the concept from* :py:mod:`configparser` *module*

    Example:
        For an example of this, see :py:class:`MultiLevelDictManager.get`

    if "_UNSET" is used (an instantiated version of thsi) can be used like:

    a = _UNSET
    b = _UNSET

    a == b
    a is b
    a is _UNSET

    """
    UnSetValidationString = '_*_This is the Unset Object_*_'

    def __repr__(self):
        return 'Empty Value'

    def __str__(self):
        return 'Empty Value'

    def __eq__(self, other):
        return isinstance(other, UnSet)

    def __bool__(self):
        return False

_UNSET = UnSet()



# ===============================================================================
# swap tool
# ===============================================================================


def swap(item: any, opt1: any = True, opt2: any = False)-> any:
    """
    This will take an item and swap it for another item.  By default this is True/False, so if True is passed, False
    is returned.  However, any pair of items can be passed and swapped

    This is used to simplify coding when you dot'n want to do lots of if **not** that and the variable can be
    permenantly changed, or when you are swapping non-boolean values.

    :param item: the item to swap
    :param opt1: (default = True) option 1
    :param opt2: (default = False) option 2
    :return: the option that is not used.

    Examples:
        >>> swap(True)
        False
        >>> swap(False)
        True
        >>> swap('Blue', 'Blue', 'Red')
        'Red'

    """
    if item == opt1:
        return opt2
    elif item == opt2:
        return opt1
    else:
        raise AttributeError(str(item) + ' not in available options')


class NextItem(collections.UserList):
    """
    on calling, will return the current item, then increment a pointer to the next one.
    you can include an offset on calling to tell NextItem how far to increment.

    Examples:
        >>> tn = NextItem([10, 20, 30, 40])

        >>> tn()
        10
        >>> tn(2)
        20
        >>> tn()
        40
        >>> tn()
        10
        >>> tn(-1)
        20
        >>> tn(0)
        10
        >>> tn(-10)
        10
        >>> tn(0)
        30
    """

    def __init__(self, *args, initial_offset=0):
        self.offset = initial_offset
        super(NextItem, self).__init__(*args)

    def __call__(self, offset_change: int = 1) -> any:
        # print(f'offset: {self.offset}')
        tmp_ret = self.data[self.offset]

        self.offset += offset_change
        while self.offset >= len(self):
            self.offset = self.offset - len(self)

        while self.offset < 0:
            self.offset = self.offset + len(self)

        return tmp_ret



# ===============================================================================
# Lookup Manager
# ===============================================================================

LookupTuple = collections.namedtuple('LookupTuple', ['stored', 'display', 'reference'])


class LookupItem(LookupTuple):
    '''
    def __init__(self, *args, **kwargs):
        super(LookupItem, self).__init__(*args, **kwargs)
        if not self.reference:
            self.reference = copy.deepcopy(self.stored)
        self.reference = slugify(self.reference)
    '''

    def __init__(self, *args):
        self.stored = args[0]
        self.display = args[1]
        try:
            self.reference = args[2]
        except IndexError:
            pass

    def __str__(self):
        return self.stored


class LookupManager(object):
    def __init__(self, lookup_list):
        """
        This handles a list of tuples where you want to have one string for a lookup, which returns a
        different string, and is called by a third thing.

        This takes a list of tuples and

        :param lookup_list:
                lookup list is a list of tuples (stored_value, display_value [, referenced_name] ):
                    stored value = the value that would be stored in the db
                    representative value = the value that is used for display
                    referenced value is the name used in coding (if not present stored_value is used)
        :param case_sensitive:
                determines if lookups are case sensitive or not.

        .. warning:: still needs work

        """
        #: TODO fix this, needs more thought in how it works
        self.stored_dict = {}
        self.display_dict = {}
        self.reference_dict = {}
        self.data_list = []
        self.lookup_list = []
        self.master_dict = {}

        for l in lookup_list:
            tmp_l = LookupItem(*l)

            self.stored_dict[tmp_l.stored] = tmp_l
            self.display_dict[tmp_l.display] = tmp_l
            self.reference_dict[slugify(tmp_l.reference)] = tmp_l
            self.data_list.append(tmp_l)
            self.lookup_list.append((tmp_l.stored, tmp_l.display ))
            self.master_dict[tmp_l.stored] = tmp_l
            self.master_dict[tmp_l.display] = tmp_l
            self.master_dict[slugify(tmp_l.reference)] = tmp_l

    def __iter__(self):
        for i in self.lookup_list:
            yield i

    def __getattr__(self, item):
        return self.reference_dict[item]

    def __getitem__(self, item):
        return self.master_dict[item]

    def get_by_stored(self, item):
        return self.stored_dict[item]

    def get_by_display(self, item):
        return self.display_dict[item]

