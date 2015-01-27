__author__ = 'dstrohl'

import copy

def args_handler(parent_obj,
                 args=None,
                 attr_list=None,
                 kwargs=None,
                 skip_list=None,
                 skip_startswith='_',
                 overwrite=True,
                 do_not_check_parent_attrs=False):
    """
    Args Handler that will take an args or kwargs list and set contents as attributes.  This also allows some control
    over which values to set

    :param parent_obj: the object that gets the attributes
    :param args: a list from the args parameter
    :param kwargs: a dict from the kwargs parameter
    :param attr_list: a list of the attributes to use, required if args are passed
        * if the attribute '_attr_list' exists in the parent object, this will be used.
        * if an attr_list exists for kwargs dicts, only the keys in the args list will be included.
        * if there are more items in the args list than in the attr list, only the ones in the list will be used.
        * if there are more items in the attr list than in the args list, only the ones in the args list will be used.
        * if both args and kwargs are passed, the attr list will ONLY be used for the args
        * if the same attr is in both args and kwargs, kwargs will take precedence.
        * if the attribute name starts with a /*, (star) it will be required and a AttributeError will be raised
            if it is not found in either the args or kwargs.
        * if a list of tuples can be passed to handle default settings, these should be in the format of:
            ('attribute name',default_setting)
            not all items need to be tuples, you can mix and match strings and tuples for fields with no requirement.
    :param skip_list: a list of attributes to skip
        * if the attribute '_args_skip_list' exists in the parent object, this will be used.
    :param skip_startswith: skip attributes that start with this string (defaults to '_')
        * if the attribute '_args_skip_startswith' exists in the parent object, this will be used.
    :param overwrite: overwrite existing attributes, can be set to False if you do not want to update existing attributes
        * if the attribute '_args_overwrite' exists in the parent object, this will be used.
    :param do_not_check_parent_attrs: will not check parent attributes for skip parameters.  (used when these fields are
        in use in the parent object for something else)
        * this only happens if the parameter is not passed, otherwise the check is skipped.
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
                    raise AttributeError('ArgsHandler: Required attribute '+attr+' is not found in args or kwargs')

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
