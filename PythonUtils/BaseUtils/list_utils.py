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

__all__ = ['DBList', 'max_len', 'make_list', 'flatten', 'unpack_class_method', 'get_not_in', 'get_same',
           'remove_dupes', 'list_in_list', 'list_not_in_list', 'count_unique', 'ListPlus', 'is_iterable',
           'OrderedSet', 'merge_list']

import copy
import collections


# ===============================================================================
# max_len
#  ===============================================================================


def max_len(*items_in, field_key=None) -> int:
    """
    Returns the length of the longest item

    :param items_in: the items or lists to compare.
    :param field_key: if a key is passed, the length will use that on each item assuming it's a dict like object to
        generate the list.
    :return: returns the max length.

    examples:

        >>> max_len('1', '22', '333')
        3

        >>> max_len(['1', '22', '333'], ['1'], ('1', '22', '333', '4444'))
        4

        >>> d1 = {'t1': ('1', '22', '333', '4444')}
        >>> d2 = {'t1': ('1', '22')}
        >>> d3 = {'t1': ('1', '22', '333')}

        >>> max_len(d1, d2, d3, field_key='t1')
        4
    """
    ret_max = 0
    if field_key is None:
        for l in items_in:
            l = make_list(l)
            for i in l:
                ret_max = max(ret_max, len(i))
    else:
        for l in items_in:
            ret_max = max(ret_max, len(l[field_key]))
    return ret_max




# ===============================================================================
# merge list
# ===============================================================================

def merge_list(list_a: list, list_b: list) -> list:
    """
    Merge_list will merge two lists together, but will combine any overlapping sections.

    :param list_a: first list to compare, this is the root list
    :param list_b: second list to merge onto the end of list_a
    :return: a merged list  consisting of list a + the non-overlapping parts of list_b

    examples:

    >>> merge_list([1,2,3,4], [1,2,3,4])
    [1,2,3,4]

    >>> merge_list([1,2,3,4], [2,3,4,5])
    [1,2,3,4,5]

    >>> merge_list([1,2,3,4], [1,2,3])
    [1,2,3,4,1,2,3]  # note that the second is nto any valid ending of the first.

    >>> merge_list([1,2,3,4], [5,6,7,8])
    [1,2,3,4,5,6,7,8]

    Note that we are checking for the sequence of values, so duplicate values will not count for overlap
    >>> merge_list([1,2,3,4], [1,3,4,5])
    [1,2,3,4,1,3,4,5]

    """
    list_a = list(list_a)
    list_b = list(list_b)

    offset = len(list_a) - len(list_b)
    if offset < 0:
        offset = 0

    while offset < len(list_a):
        for a, b in zip(list_a[offset:], list_b):
            print(f'comparing {a} and {b}')
            if a != b:
                print('  not equal')
                break
        else:
            if offset == 0:
                if len(list_a) > len(list_b):
                    return list_a
                else:
                    return list_b
            list_1 = list_a[:offset]
            list_2 = list_b
            tmp_ret = list_1 + list_2
            print(f'good comparison, offset = {offset}')
            print(f'   list_1: {list_1!r}')
            print(f'   list_2: {list_2!r}')
            return tmp_ret
        offset += 1

    return list_a + list_b


# ===============================================================================
# a list that allows for lookups more like a dictionary.
# ===============================================================================


class DBList(object):
    """
    This is a list type object that also allows for lookups like a dictionary based on stored dict keys.

    The only way this works if if dictionaries are stored in the list, each with a key matching the key string.

    NOTE: if there are dupe items (by defined key) in the starting list, only the last one will be kept.

    :param starting_list: A list of dictionaries, each must contain a key matching the "dict_key" field
    :param dict_key: the key used to find the keys for looking up the dictionaries.

    Example:

        >>> dict_list = [{'name':'john','age':21},{'name':'jane','age':22}]
        >>> dl = DBList(dict_list, 'name')
        >>> dl['john']
        {'name':'john','age':21}
        >>> dl['jane']['age']
        22

    """

    internal_dict = {}

    #: TODO Add rest of list and dict functionality

    def __init__(self,
                 starting_list,
                 dict_key):

        for item in starting_list:
            self.internal_dict[item[dict_key]] = item

    def __iter__(self, key):
        return self.internal_dict[key]

    def get_list(self):
        """
        returns a list of the items.
        """
        return self.internal_dict.items()

    def get_dict(self):
        """
        returns the internal dictionary.
        """
        return self.internal_dict


# ===============================================================================
# general list utilities.
# ===============================================================================


def make_list(in_obj):
    """
    Will take in an object, and if it is not already a list or other iterables, it will convert it to one.

    This is helpfull when you dotn know if someone will pass a single string, or a list of strings (since strings
    are iterable you cant just assume)

    This uses the :py:func:`is_iterable` function from this module.

    :param in_obj: list, string, or other iterable.
    :return: a list object.
    """

    if is_iterable(in_obj):
        return in_obj
    else:
        return [in_obj]


def flatten(l, ltypes=(list, tuple), force=None):
    """
    Will flatten lists and tuples to a single level

    .. note:: from: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html

    :param l: list or tuple to be flattened
    :param ltypes: the types of items allowed to be flattened, default = (list, tuple)
    :param force: forces return to be of this type.
    :return: single level list or tuple (same as what went in)

    Example:
        >>> l = [1, 2, 3, [4, 5, [6, 7]]]
        >>> flatten(l)
        [1, 2, 3, 4, 5, 6, 7]

    """

    if isinstance(l, str):
        if force is None:
            return []
        elif force == list:
            return [l]
        elif force == tuple:
            return tuple(l, )
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    if force is None:
        return ltype(l)
    else:
        return force(l)


def unpack_class_method(class_object_list, method, ret_type=str, args_list=None, kwargs_dict=None):
    """
    This will iterate through a list of objects and pull a value from each one, even if the items are functions.

    :param class_object_list: A list of objects
    :param method: the method to pull from (string)
    :param return_type: what type of data is expected to be returned. this should be a function/class that will convert
        to the type desired.
        for example, the default is str, but int, float are also options.
    :param args_list: if the method is a function, a list of arguments to pass
    :param kwargs_dict: if the method is a function, a dict of keyword arguments to pass.

    """
    if args_list is None:
        args_list = []
    if kwargs_dict is None:
        kwargs_dict = {}

    tmpretset = []
    class_object_list = flatten(class_object_list)
    for obj in class_object_list:
        func = getattr(obj, method, None)
        if callable(func):
            tmpret = ret_type(func(*args_list, **kwargs_dict))
        else:
            tmpret = ret_type(func)
        tmpretset.append(tmpret)
    return tmpretset


def get_same(l1, l2):
    """
    Returns a list with any items that are the same in both lists

    :param l1: list 1
    :param l2: list 2
    :return: a list of items in both "list 1" and "list 2"
    """
    tmp_list = []
    for li in l1:
        if li in l2:
            tmp_list.append(li)
    return tmp_list


def get_not_in(check_for, check_in):
    """
    Returns a list of items that are NOT in another list

    :param check_for: a list of items to check for
    :param check_in: a list to check
    :return: a list of the items in "check_in" that are NOT in "check_for"
    """
    tmp_list = []
    for li in check_for:
        if li not in check_in:
            tmp_list.append(li)
    return tmp_list


def remove_dupes(l1):
    """
    Returns a list with any duplicates removed.
    (while order is maintained, which duplicate is removed is not controllable)
    :param l1:
    :return:
    """
    return list(set(l1))


# ===============================================================================
# checking for the presence (or absence) of lists in other lists
# ===============================================================================


def list_in_list(is_this, in_this):
    """
    Checks to see if ALL of the items in a list are in the other list

    :param is_this: list of items to check for
    :param in_this: list of items to check against
    :return: booleanTrue if all items in is_this are in in_this.

    .. Warning: currently broken!!!

    """
    #: TODO FIX THIS!!
    is_this = make_list(is_this)
    for item in is_this:
        if item in in_this:
            return True
    return False


def list_not_in_list(is_this, not_in_this):
    is_this = make_list(is_this)
    for item in is_this:
        if item in not_in_this:
            return False
    return True


# ===============================================================================
# Utility counts unique values in a list or dict
# ===============================================================================


def count_unique(data_in, dict_key=None, on_key_error='raise'):
    """
    Counts the unique items a list of items, or counts the unique keys in a list of dicts.

    :param data_in: list or tuple of items to be counted
    :param dict_key: if data_in is a list of dict's, this is the key for which item to compare
    :param on_key_error:
        what to do if there is a KeyError when looking up the dict_key:
        * 'raise' = (default) Raises KeyError
        * 'skip' = skips KeyErrors
        * 'count' = counts KeyErrors as 1
    :return: integer

    """

    tmp_list = []

    if not isinstance(data_in, (list, tuple)):
        raise TypeError('count_unique requires a list or tuple, not a ' + type(data_in).__name__)

    if dict_key:
        for item in data_in:
            try:
                tmp_list.append(item[dict_key])
            except KeyError:
                if on_key_error == 'raise':
                    raise KeyError('count_unique: dict key "' + dict_key + '" not found')
                elif on_key_error == 'count':
                    tmp_list.append('__<no_key_item>__')

    else:
        tmp_list = data_in

    return len(set(tmp_list))


# ===============================================================================
# Advanced List Object
# ===============================================================================


class ListPlus(list):
    """
    adds some additional features to the list object.

    =====================    ===========================================================================================
    ListPlus.add             allows insert new records past the existing last record
    ListPlus.update          allows updating records or adding them past the existing last record
    ListPlus[key] = value    same as listPlus.update though uses list key notation
    ListPlus.get             allows for setting a default response instead of generating an error if rec does not exist.
    =====================    ===========================================================================================
    """

    def _update_function(self, curr_obj, new_obj):
        """
        Allows overriding to allow for manipulating or validating updated information if needed'

        this is called anytime something is updated (not for new records though)

        :param curr_obj: this passes the current object in the list
        :param new_obj: this passes the new object
        :return: returns the object to be saved.
        """
        return new_obj

    def add(self, i, x, **kwargs):
        """
        Will add any needed items to a list to add the new item at the indexed spot.

        :param i: list offset to add item to.
            If this is lower than or equal to the size fo the list, the items will be added directly to the end.
            If this is larger than the list length, new items will be added to the list to pad it out long enough
            to reach this length.
        :param x: the new item to add to the list
        :param new_item_default: the default item that will be added as padding if needed.
            this overrides the class setting if present.
        """
        # print( 'l:', l )
        # print( 'i:', i )
        new_item_default = kwargs.get('new_item_default', self.new_item_default)
        if i >= len(self):
            l = len(self)
            mt_items = i - l
            for ni in range(mt_items):
                self.append(new_item_default)
            self.append(x)
        else:
            self.insert(i, x)

    def set_new_item_default(self, new_item_default):
        """
        This sets the default new item object for when blank items must be added
        :param new_item_default: the item that will be used for blank new items.
        """
        self._new_item_default = new_item_default

    @property
    def new_item_default(self):
        try:
            return self._new_item_default
        except AttributeError:
            self.set_new_item_default(None)
            return self._new_item_default

    def update(self, i, x, **kwargs):
        """
        Updates a specific item at a specific offset, if that item does not exist, padding items will
        be added to the list lengthen it.

        :param i: list offset to update.
        :param x: the new item to update in the list
        :param new_items_default: the default item that will be added as padding if needed,
            this overrides the class setting if present
        """
        new_item_default = kwargs.get('new_item_default', self.new_item_default)

        try:
            tmp_value = self._update_function(copy.deepcopy(self[i]), x)
        except (IndexError, TypeError):
            tmp_value = self._update_function(None, x)

        try:
            self[i] = tmp_value
        except IndexError:
            l = len(self)
            mt_items = i - l
            for ni in range(mt_items):
                self.append(new_item_default)
            self.append(tmp_value)

    def get(self, *args):
        i = args[0]
        if len(args) == 1:
            return self[i]
        elif len(args) == 2:
            try:
                return self[i]
            except IndexError:
                return args[1]
        else:
            raise TypeError('ListPlus.get takes at most 2 arguments, ' + str(len(args)) + ' given')

    '''
    def __setitem__(self, i, x):
        if isinstance(i, int):
            self.update(i, x)
        else:
            raise TypeError('ListPlus indices must be integers, not '+type(i).__name__)
    '''



# ===============================================================================
# Ordered Set
# ===============================================================================


"""
An OrderedSet is a custom MutableSet that remembers its order, so that every
entry has an index that can be looked up.

Based on a recipe originally posted to ActiveState Recipes by Raymond Hettiger,
and released under the MIT license.

Rob Speer's changes are as follows:

    - changed the content from a doubly-linked list to a regular Python list.
      Seriously, who wants O(1) deletes but O(N) lookups by index?
    - add() returns the index of the added item
    - index() just returns the index of an item
    - added a __getstate__ and __setstate__ so it can be pickled
    - added __getitem__
"""

SLICE_ALL = slice(None)


def is_iterable(obj):
    """
    Are we being asked to look up a list of things, instead of a single thing?
    We check for the `__iter__` attribute so that this can cover types that
    don't have to be known by this module, such as NumPy arrays.

    Strings, however, should be considered as atomic values to look up, not
    iterables.

    We don't need to check for the Python 2 `unicode` type, because it doesn't
    have an `__iter__` attribute anyway.
    """
    return hasattr(obj, '__iter__') and not isinstance(obj, str)


class OrderedSet(collections.MutableSet):
    """
    An OrderedSet is a custom MutableSet that remembers its order, so that
    every entry has an index that can be looked up.


    Based on a recipe originally posted to ActiveState Recipes by Raymond Hettiger,
    and released under the MIT license.

    Rob Speer's changes are as follows:

    * changed the content from a doubly-linked list to a regular Python list.
        Seriously, who wants O(1) deletes but O(N) lookups by index?
    * add() returns the index of the added item
    * index() just returns the index of an item
    * added a __getstate__ and __setstate__ so it can be pickled
    * added __getitem__
    """


    def __init__(self, iterable=None):
        self.items = []
        self.map = {}
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        """
        Get the item at a given index.

        If `index` is a slice, you will get back that slice of items. If it's
        the slice [:], exactly the same object is returned. (If you want an
        independent copy of an OrderedSet, use `OrderedSet.copy()`.)

        If `index` is an iterable, you'll get the OrderedSet of items
        corresponding to those indices. This is similar to NumPy's
        "fancy indexing".
        """
        if index == SLICE_ALL:
            return self
        elif hasattr(index, '__index__') or isinstance(index, slice):
            result = self.items[index]
            if isinstance(result, list):
                return OrderedSet(result)
            else:
                return result
        elif is_iterable(index):
            return OrderedSet([self.items[i] for i in index])
        else:
            raise TypeError("Don't know how to index an OrderedSet by %r" %
                            index)

    def copy(self):
        return OrderedSet(self)

    def __getstate__(self):
        if len(self) == 0:
            # The state can't be an empty list.
            # We need to return a truthy value, or else __setstate__ won't be run.
            #
            # This could have been done more gracefully by always putting the state
            # in a tuple, but this way is backwards- and forwards- compatible with
            # previous versions of OrderedSet.
            return (None,)
        else:
            return list(self)

    def __setstate__(self, state):
        if state == (None,):
            self.__init__([])
        else:
            self.__init__(state)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        """
        Add `key` as an item to this OrderedSet, then return its index.

        If `key` is already in the OrderedSet, return the index it already
        had.
        """
        if key not in self.map:
            self.map[key] = len(self.items)
            self.items.append(key)
        return self.map[key]

    append = add

    def index(self, key):
        """
        Get the index of a given entry, raising an IndexError if it's not
        present.

        `key` can be an iterable of entries that is not a string, in which case
        this returns a list of indices.
        """
        if is_iterable(key):
            return [self.index(subkey) for subkey in key]
        return self.map[key]

    def discard(self, key):
        raise NotImplementedError(
            "Cannot remove items from an existing OrderedSet"
        )

    def __iter__(self):
        return iter(self.items)

    def __reversed__(self):
        return reversed(self.items)

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and self.items == other.items
        return set(self) == set(other)



