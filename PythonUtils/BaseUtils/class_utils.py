#!/usr/bin/env python

"""
Helper utilities for classes.
"""

__author__ = ""
__copyright__ = ""
__credits__ = []
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = ""

__all__ = ['args_handler', 'GenericMeta', 'get_meta_attrs', 'simple_kwarg_handler', 'SimpleDataClass']

# ===============================================================================
# Simple Argument Handler
# ===============================================================================

def simple_kwarg_handler(parent_obj, kwargs, raise_on_unknown=True):
    """
    This is a simple kwarg handler that will take any kwargs passed and create them on the parent object.

    :param parent_obj:  The object that the parameters will be created on.
    :param raise_on_unknown: if the parameter is not already on the object, this will raise an attribute error.
    :param kwargs: the kwargs to save.
    :return:  None
    """
    for key, value in kwargs.items():
        if not hasattr(parent_obj, key) and raise_on_unknown:
            raise AttributeError("object does not have attribute %s" % key)
        setattr(parent_obj, key, value)


# ===============================================================================
# Simple Data Class
# ===============================================================================

class SimpleDataClass(object):
    def __init__(self, **kwargs):
        simple_kwarg_handler(self, kwargs, raise_on_unknown=False)


# ===============================================================================
# Argument Handler
# ===============================================================================


def args_handler(parent_obj,
                 args=None,
                 attr_list=None,
                 kwargs=None,
                 skip_list=None,
                 skip_startswith='-',
                 overwrite=True,
                 do_not_check_parent_attrs=False):
    """
    Args Handler that will take an args or kwargs list and set contents as attributes.  This also allows some control
    over which values to set.

    This can be used when creating that may need to take different types of arguments as it can intelligently detect
    fields passed as arguments, keyword arguments, or a dictionary of arguments, it can handle required arguments as
    as well as long lists of arguments very simply.

    Parameters:
        parent_obj: the object that gets the attributes
        args: a list from the args parameter
        kwargs: a dict from the kwargs parameter
        attr_list: a list of the attributes to use, required if args are passed

            .. note::
                * if the attribute '_attr_list' exists in the parent object, this will be used.
                * if an attr_list exists for kwargs dicts, only the keys in the args list will be included.
                * if there are more items in the args list than in the attr list, only the ones in the list will
                    be used.
                * if there are more items in the attr list than in the args list, only the ones in the args list
                    will be used.
                * if both args and kwargs are passed, the attr list will ONLY be used for the args
                * if the same attr is in both args and kwargs, kwargs will take precedence.
                * if the attribute name starts with a \*, (star) it will be required and a AttributeError will be raised
                    if it is not found in either the args or kwargs.
                * if a list of tuples can be passed to handle default settings, these should be in the format of:
                    ('attribute name',default_setting)
                    not all items need to be tuples, you can mix and match strings and tuples for fields with no
                    requirement.

        skip_list: a list of attributes to skip

            .. note::
                * if the attribute '_args_skip_list' exists in the parent object, this will be used.

        skip_startswith: skip attributes that start with this string (defaults to '_')

            .. note::
                * if the attribute '_args_skip_startswith' exists in the parent object, this will be used.

        overwrite: overwrite existing attributes, can be set to False if you do not want to update existing attributes

            .. note::
                * if the attribute '_args_overwrite' exists in the parent object, this will be used.

        do_not_check_parent_attrs: will not check parent attributes for skip parameters.  (used when these fields are
            in use in the parent object for something else)

            .. note::
                * this only happens if the parameter is not passed, otherwise the check is skipped.

        Example of use:

            class MyObject(object):

                def __init__(self, *args, **kwargs):
                    args_handler(self, args, ['f_name', 'l_name'], kwargs)
                    # this would apply the first two args as MyObject.f_name and MyObject.l_name, as well as any kwargs


        Examples of options:

            >>> tc = TmpClass()

            test_args = [1, 2, 3, 4]
            test_args_list_1 = ['t1', 't2', 't3', '_t4']
            test_kwargs = {'t5': 5, 't6': 6, 't7': 7, '_t8': 8}
            test_kwargs_ovr = {'t3': 33, '_t4': 44, 't5': 5, 't6': 6, 't7': 7, '_t8': 8}
            test_skip_list = ['t4', 't5']

            test_args_req = [1, 2, 4]
            test_args_list_req = ['t1', '*t2', 't3', '_t4', '*t6']
            test_kwargs_req = {'t5': 5, 't7': 7, '_t8': 8}

            >>> args_handler(tc, test_args, test_args_list_1)
            >>> tc.t2
            2

            >>> args_handler(tc, kwargs=test_kwargs)
            >>> tc.t5
            5

            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs)
            >>> tc.t2
            2
            >>> tc.t5
            5

            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs_ovr)
            >>> tc.t3
            33
            >>> tc.t5
            5
            >>> tc.t2
            2

            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs, skip_list=test_skip_list)
            >>> tc.t2
            2
            >>> tc.t6
            6

            tc.t1 = 11
            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs, skip_list=test_skip_list)
            >>> tc.t1
            1

            >>> tc.t1 = 11
            >>> args_handler(tc, test_args, test_args_list_1, skip_list=test_skip_list, overwrite=False)
            >>> tc.t1
            11


            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs, skip_list=test_skip_list)
            >>> tc.t2
            2
            >>> tc.t6
            6

            >>> tc._args_skip_list = test_skip_list
            >>> args_handler(tc, test_args, test_args_list_1, test_kwargs)
            >>> tc.t2
            2
            >>> tc.t6
            6

            >>> tc._args_skip_list = test_skip_list
            >>> args_handler(tc, kwargs=test_kwargs, do_not_check_parent_attrs=True)
            >>> tc.t5
            5


            >>> test_args = [1, 2, 4]
            >>> test_args_list = [('t1', 11), '*t2', 't3', '_t4', ('t5', 55), ('*t6', 66)]
            >>> test_kwargs = {'t6': 6, 't7': 7, '_t8': 8}
            >>> args_handler(tc, test_args, test_args_list, test_kwargs)

            >>> tc.t1
            1
            >>> tc.t5
            55
            >>> tc.t6
            6

    """

    def _save(save_arg, save_attr, clean_default=True):
        if _check(save_attr):
            setattr(parent_obj, save_attr, save_arg)
            if clean_default:
                try:
                    del attr_defaults[save_attr]
                except KeyError:
                    pass

    def _check(check_attr, check_present=True):
        if check_present:
            if not check_attr.startswith(skip_startswith) and check_attr not in skip_list:
                return overwrite or not hasattr(parent_obj, check_attr)
            return False
        else:
            return check_attr.startswith(skip_startswith) and check_attr not in skip_list

    def _args_list_iterator():
        for tmp_attr, tmp_arg in zip(attr_list, args):
            try:
                if tmp_attr in kwargs:
                    continue
            except TypeError:
                pass
            _save(tmp_arg, tmp_attr)

    def _args_dict_by_attrs():
        for tmp_attr in attr_list:
            try:
                _save(kwargs[tmp_attr], tmp_attr)
            except KeyError:
                pass

    def _args_dict_iterator(args_dict, clean_default=True):
        for tmp_attr, tmp_arg in args_dict.items():
            _save(tmp_arg, tmp_attr, clean_default)

    if not do_not_check_parent_attrs:
        attr_list = getattr(parent_obj, '_attr_list', attr_list)
        skip_list = getattr(parent_obj, '_args_skip_list', skip_list)
        skip_startswith = getattr(parent_obj, '_args_skip_startswith', skip_startswith)
        overwrite = getattr(parent_obj, '_args_overwrite', overwrite)

    if skip_list is None:
        skip_list = []

    attr_defaults = {}

    # ---- verify required fields and build defaults list from tuples ------
    if attr_list:
        if args:
            arg_cnt = len(args)
        else:
            arg_cnt = 0

        tmp_attr_list = []
        for offset, attr in enumerate(attr_list):
            if isinstance(attr, tuple):
                attr_defaults[attr[0]] = attr[1]
                attr = attr[0]
            attr = str(attr)
            if attr[0] == '*':
                attr = attr[1:]

                attr_found = False
                if attr in kwargs:
                    attr_found = True
                if offset <= arg_cnt:
                    attr_found = True

                if not attr_found:
                    raise AttributeError('ArgsHandler: Required attribute ' + attr + ' is not found in args or kwargs')

            tmp_attr_list.append(attr)

        attr_list = tmp_attr_list

    if attr_list is None and args:
        raise AttributeError('ArgsHandler: if args are passed, args list must not be empty')

    if kwargs:
        if attr_list and not args:
            _args_dict_by_attrs()
        else:
            _args_dict_iterator(kwargs)

    if args:
        _args_list_iterator()

    _args_dict_iterator(attr_defaults, clean_default=False)


# ===============================================================================
# Generic Meta Object
# ===============================================================================


class GenericMeta(object):
    """
    Base object to use for creating meta objects.  This will copy all attrs from the meta object to the parent object.

    This can be used to assign lists or other mutatable objects to Classes as well as to create standard sets of metadata
    for classes that can be reused.

    This uses :py:func:`args_handler` to copy kwargs to the class on init.

    Example:

        >>> class MyObject(object):
        >>>     meta = GenericMeta(name='coolObject', number_list=[1,2,3,4])

        >>> mo = MyObject()
        >>> mo.name
        'coolObject'
        >>> mo.number_list
        [1,2,3,4]

    """

    def __init__(self, *kwargs):
        args_handler(self, kwargs=kwargs)

    def get_meta_attrs(self, parent_obj, skip_list=None, skip_startswith='_', overwrite=True):
        """
        Function to copy the atttrs.

        :param parent_obj: The object to copy the attrs TO
        :param skip_list:  A list of attrs to skip copying.
        :param skip_startswith:  If an attr starts with this (default = '_'), do not copy
        :param overwrite: if False (default = True) will not not overwrite existing attributes if they exist.
        """
        if skip_list is None:
            skip_list = []
        for attr, value in iter(self.__dict__.items()):
            if not attr.startswith(skip_startswith) and attr not in skip_list:
                if not hasattr(parent_obj, attr) or overwrite:
                    setattr(parent_obj, attr, value)


def get_meta_attrs(meta, parent_obj, skip_list=None, skip_startswith='_', overwrite=True):
    """
    Standalone version of the get_meta_attrs from the generic meta object for use in other custom classes.

    :param meta: The object to copy the attrs FROM
    :param parent_obj: The object to copy the attrs TO
    :param skip_list:  A list of attrs to skip copying.
    :param skip_startswith:  If an attr starts with this (default = '_'), do not copy
    :param overwrite: if False (default = True) will not not overwrite existing attributes if they exist.
    """
    if skip_list is None:
        skip_list = []
    for attr, value in iter(meta.__dict__.items()):
        if not attr.startswith(skip_startswith) and attr not in skip_list:
            if not hasattr(parent_obj, attr) or overwrite:
                setattr(parent_obj, attr, value)


