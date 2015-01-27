__author__ = 'dstrohl'


def _check_and_save(parent_obj, arg, attr, handler_config):
    if _check_not_skip(attr, handler_config, parent_obj):
            setattr(parent_obj, attr, arg)

def _check_not_skip(attr, handler_config, parent_obj=None):
    if parent_obj:
        if not attr.startswith(handler_config['skip_startswith']) and attr not in handler_config['skip_list']:
            return handler_config['overwrite'] or not hasattr(parent_obj, attr)
        return False
    else:
        return attr.startswith(handler_config['skip_startswith']) and attr not in handler_config['skip_list']

def _args_iterator(parent_obj, inargs, handler_config):

    if handler_config['attr_list'] is None:
        if isinstance(inargs, dict):
            for attr, arg in inargs.items():
                _check_and_save(parent_obj, arg, attr, handler_config)
        else:
            raise TypeError('inargs is not a dictionary and no args_list passed')
    else:
        if isinstance(inargs, (list, tuple)):
            for attr, arg in zip(handler_config['attr_list'], inargs):
                _check_and_save(parent_obj, arg, attr, handler_config)
        else:
            for attr in handler_config['attr_list']:
                if not attr.startswith(handler_config['skip_startswith']) and attr not in handler_config['skip_list']:
                    try:
                        _check_and_save(parent_obj, inargs[attr], attr, handler_config)
                    except KeyError:
                        pass


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
    :param skip_list: a list of attributes to skip
        * if the attribute '_args_skip_list' exists in the parent object, this will be used.
    :param skip_startswith: skip attributes that start with this string (defaults to '_')
        * if the attribute '_args_skip_startswith' exists in the parent object, this will be used.
    :param overwrite: overwrite existing attributes, can be set to False if you do not want to update existing attributes
        * if the attribute '_args_overwrite' exists in the parent object, this will be used.
    :param do_not_check_parent_attrs: will not check parent attributes for skip parameters.  (used when these fields are
        in use in the parent object for something else)
    """
    if not do_not_check_parent_attrs:
        attr_list = getattr(parent_obj, '_attr_list', attr_list)
        skip_list = getattr(parent_obj, '_args_skip_list', skip_list)
        skip_startswith = getattr(parent_obj, '_args_skip_startswith', skip_startswith)
        overwrite = getattr(parent_obj, '_args_overwrite', overwrite)

    if skip_list is None:
        skip_list = []

    handler_config = {
        'attr_list': attr_list,
        'skip_list': skip_list,
        'skip_starts_with': skip_startswith,
        'overwrite': overwrite}

    required_list = []
    furthest_required = 0
    if args:
        arg_cnt = len(args)
    else:
        arg_cnt = 0

    if attr_list:
        for offset, attr in enumerate(handler_config['attr_list']):
            if attr[0] == '*':
                attr = attr[2:]

                attr_found = False
                if attr in kwargs:
                    attr_found = True
                if

                required_list.append(attr)
                if furthest_required < offset:
                    furthest_required = offset



    if attr_list is None and args:
        raise AttributeError('ArgsHandler: if args are passed, args list must not be empty')

    if kwargs:
        if args:
            tmp_attr_list = None
        else:
            tmp_attr_list = attr_list
        _args_iterator(parent_obj, kwargs, handler_config)

    if args:
        if kwargs:
            skip_list.extend(list(kwargs))
        _args_iterator(parent_obj, args, handler_config)

