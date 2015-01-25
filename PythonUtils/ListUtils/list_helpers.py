__author__ = 'dstrohl'


from PythonUtils.TextUtils import is_string


def make_list(in_obj):
    """
    Will take in an object, and if it is not already a list, it will convert it to one.
    :param in_obj:
    :return:
    """
    if is_string(in_obj):
        return [in_obj]
    else:
        return in_obj


def flatten(l, ltypes=(list, tuple), force=None):
    """
    Will flatten lists and tuples to a single level

    from: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html

    :param l: list or tuple to be flattened
    :param ltypes: the types of items allowed to be flattened, default = (list, tuple)
    :param force: forces return to be of this type.
    :return: single level list or tuple (same as what went in)
    """
    if is_string(l):
        if force is None:
            return []
        elif force == list:
            return [l]
        elif force == tuple:
            return tuple(l,)
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


def unpack_class_method(class_object_list, method, ret_type=str, args_list=[], kwargs_dict={}):
    """
    This will iterate through a list of objects and pull a value from each one, even if the items are functions.

    :param class_object_list: A list of objects
    :param method: the method to pull from (string)
    :param return_type: what type of data is expected to be returned. this should be a function/class that will convert
        to the type desired.
        for example, the default is str, but int, float are also options.
    :param args_list: if the method is a function, a list of arguments to pass
    :param kwargs_dict: if the method is a function, a dict of keyword arguments to pass.
    :return:
    """
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

    :param l1:
    :param l2:
    :return:
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
'''
def get_different(l1, l2):
    """


    :param l1:
    :param l2:
    :return:
    """
    tmp_set = set()
    for li in l1:
        if li in l2:
            tmp_set.append(li)

    for li in l2:
        if li in l1:
            tmp_set.append(li)
    return list(tmp_set)
'''


def remove_dupes(l1):
    """
    Returns a list with any duplicates removed.
    (while order is maintained, which duplicate is removed is not controllable)
    :param l1:
    :return:
    """
    return list(set(l1))

# ===============================================================================
# Utility counts unique values in a list or dict
# ===============================================================================


def count_unique(data_in, dict_key=None, on_key_error='raise'):
    """
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
        raise TypeError('count_unique requires a list or tuple, not a '+type(data_in).__name__)

    if dict_key:
        for item in data_in:
            try:
                tmp_list.append(item[dict_key])
            except KeyError:
                if on_key_error == 'raise':
                    raise KeyError('count_unique: dict key "'+dict_key+'" not found')
                elif on_key_error == 'count':
                    tmp_list.append('__<no_key_item>__')

    else:
        tmp_list = data_in

    return len(set(tmp_list))
