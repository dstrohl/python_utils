
class MetaBaseParser(type):
    class MetaBaseParser(type):
        def __new__(cls, name, bases, dct):
            tmp_ret = type.__new__(cls, name, bases, dct)

            def _update_obj(field_name):

                if hasattr(tmp_ret, field_name):
                    _counter = 0
                    while True:
                        tmp_name = '%s__%s' % (field_name, _counter)
                        if not hasattr(tmp_ret, tmp_name):
                            setattr(tmp_ret, tmp_name, getattr(tmp_ret, field_name))
                            delattr(tmp_ret, field_name)
                            break
                        _counter += 1
                        if _counter > 100:
                            break

            if hasattr(tmp_ret, '_meta_keys'):
                for key in tmp_ret._meta_keys:
                    _update_obj(key)
            return tmp_ret


class ConfigObject(object):

    def __init__(self, skip_keys=None):
        """
        :param args:
        :param arg_list:
        :param kwargs:
        """
        self._data = {}
        self._arg_list = []
        self._skip_keys = []
        self._spec_args = {}
        if skip_keys:
            self._add_skip_keys(skip_keys)

    def _load(self, from_obj, _force_set=False):
        self._cleanup(from_obj)
        try:
            self._add_args_item(from_obj._args_list)
        except AttributeError:
            pass
        try:
            self._add_skip_keys(from_obj._skip_keys)
        except AttributeError:
            pass
        for item in dir(from_obj):
            if item[0] != '_':
                if self._set_field(item, getattr(from_obj, item), self._data, _force_set=_force_set):
                    delattr(from_obj, item)

    @staticmethod
    def _cleanup(from_obj):
        if hasattr(from_obj, '_meta_keys'):
            for field in from_obj._meta_keys:
                tmp_data = None
                is_dict = False
                counter = 0
                while True:
                    tmp_name = '%s__%s' % (field, counter)
                    counter += 1
                    if not hasattr(from_obj, tmp_name):
                        break

                    tmp_field = getattr(from_obj, tmp_name)
                    if tmp_data is None:
                        if isinstance(tmp_field, dict):
                            tmp_data = {}
                            is_dict = True
                        else:
                            tmp_data = []
                            is_dict = False
                    if is_dict:
                        tmp_data.update(tmp_field)
                    else:
                        tmp_data.extend(make_list(tmp_field))
                setattr(from_obj, field, tmp_data)

    def _update(self, *args, _force_set=False, _to_data=None, _skip_keys=None, _args_list=None, _update_only=False, **kwargs):
        _to_data = _to_data or self._data
        self._add_skip_keys(_skip_keys)
        self._add_args_item(_args_list)
        for field, arg in zip(self._arg_list, args):
            self._set_field(field, arg, _to_data=_to_data, _force_set=_force_set, _update_only=_update_only)
        for field in list(kwargs):
            value = kwargs[field]
            if self._set_field(field, value, _to_data=_to_data, _force_set=_force_set, _update_only=_update_only):
                del kwargs[field]
        if len(args) > len(self._arg_list):
            ret_args = args[len(self._arg_list):]
        else:
            ret_args = []
        return ret_args, kwargs

    def _add_args_item(self, arg_items):
        if arg_items:
            self._arg_list.extend(make_list(arg_items))

    def _add_skip_keys(self, skip_keys):
        if skip_keys:
            self._skip_keys.extend(make_list(skip_keys))

    def _set(self, *args, **kwargs):
        self._update(*args, _force_set=True, **kwargs)

    def _set_field(self, field, value, _to_data, _force_set=False, _update_only=False):

        if field[0] == '_' or field in self._skip_keys:
            return False

        if field not in _to_data and not _force_set:
            if _update_only:
                return False
            if isinstance(value, (list, tuple)):
                self._spec_args[field] = 'list'
                _to_data[field] = []
            elif isinstance(value, dict):
                self._spec_args[field] = 'dict'
                _to_data[field] = {}

        if not _force_set and field in self._spec_args:
            if self._spec_args[field] == 'list':
                if value is not None:
                    if isinstance(value, (list, tuple)):
                        _to_data[field].extend(value)
                    else:
                        _to_data[field].append(value)
            elif self._spec_args[field] == 'dict':
                if value is not None:
                    _to_data[field].update(value)
            else:
                raise AttributeError('Invalid data type: %s' % self._spec_args[field])
        else:
            _to_data[field] = value
        return True

    def _kwargs(self, *args, **kwargs):
        tmp_data = self._data.copy()
        self._update(*args, _to_data=tmp_data, **kwargs)
        return tmp_data

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError('Invalid Attribute: %s' % item)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._set_field(key, value, self._data)

    def __contains__(self, item):
        return item in self._data

    def __iter__(self):
        for item in self._data.keys():
            yield item

    def __repr__(self):
        return 'ConfigObject(%s)' % ', '.join(self._data.keys())

