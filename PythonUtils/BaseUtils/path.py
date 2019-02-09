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

import collections
from PythonUtils.BaseUtils.list_utils import merge_list


class Path(object):
    """
    A class for managing a path, this could be a file path, but it is more aimed at a path through modules
    or dictionaries.

    Examples:


        p = path()


    """
    _default_key_sep = '.'
    _parsed_path_obj = collections.namedtuple('parsed_path', ('is_root', 'up_levels', 'path'))

    def __init__(self, path='', key_sep=None, key_xform=None, validate_func=None,
                 raise_on_neg_path=False):
        """
        :param path: The current path to be set, this can be a text string, or it can be another :class:`path`
            object.  if this is a path object and other items are not specified, key_sep is set from the
            path object
        :param key_sep: a string used to separate parts of the path, if None, will use the first non-alpha-numeric
        char found. if none found, will use self._default_key_sep (normally set to ".")
        :param key_xform: a function that all keys will be run through, can be something like "string.lower")
        :param validate_func: will be called for each path change to verify that the resulting item is a valid path.
            this is passed the list of path elements and if there is a problem it's the functions's responsibility to
            raise an exception.
        :param raise_on_neg_path: if True, will raise an IndexError if a Path.cd("..") is tried and there is no higher
            path key available.
        """

        self._path = []
        self._validate_func = validate_func
        self._raise_on_neg_path = raise_on_neg_path
        self._key_xform_func = key_xform

        if isinstance(path, self.__class__):
            self.key_sep = key_sep or path.key_sep
        else:
            if key_sep is None:
                for c in path:
                    if not c.isalnum():
                        self.key_sep = c
                        break
                if self.key_sep is None:
                    self.key_sep = self._default_key_sep
            else:
                self.key_sep = key_sep
        self.cd(path)

    def _key_xform(self, path_in):
        if self._key_xform_func is None:
            return str(path_in)
        else:
            return self._key_xform_func(path_in)

    def cd(self, path):
        old_path = self._path.copy()
        # print(f"change dir to {path}")
        if not isinstance(path, self._parsed_path_obj):
            path = self._parse_path_in(path)

        # print(f'new path: {path}')

        if path.is_root:
            self._path.clear()

        if path.up_levels:
            try:
                for x in range(path.up_levels):
                    self._path.pop()
            except IndexError:
                if self._raise_on_neg_path:
                    raise

        self._path.extend(path.path)

        if self._validate_func is not None:
            try:
                self._validate_func(self._path)
            except Exception:
                self._path = old_path
                raise

        return self

    def copy(self, path=None, cd='', class_obj=None, **kwargs):
        """
        Creates an new path object from this one
        :param path: What is the new root path.  if None, will use current one
        :param cd: change directory of new object
        :param key_sep: new key seperator
        :param class_obj: What class object to use.
        """
        class_obj = class_obj or self.__class__

        path = path or self

        kwargs['key_sep'] = kwargs.get('key_sep', self.key_sep)
        kwargs['key_xform'] = kwargs.get('key_xform', self._key_xform)
        kwargs['validate_func'] = kwargs.get('validate_func', self._validate_func)
        kwargs['raise_on_neg_path'] = kwargs.get('raise_on_neg_path', self._raise_on_neg_path)

        tmp_ret = class_obj(path, **kwargs)
        return tmp_ret.cd(cd)

    def _parse_path_in(self, path, as_string=False, is_root=None):
        # print(f"parsing path {path}")
        if isinstance(path, self.__class__):
            if is_root is None:
                is_root = True
            if as_string:
                return self._parsed_path_obj(is_root, 0, self.key_sep.join(path._path))
            else:
                return self._parsed_path_obj(is_root, 0, path._path)

        if not isinstance(path, str):
            try:
                path = self.key_sep.join(list(path))
            except Exception:
                raise TypeError('unable to compare a path with type %s  / %r' % (path.__class__.__name__, path))

        s_count = 0

        while path and path[0] == self.key_sep:
            # print(f'removing header: {path[0]} from "{path}"')
            s_count += 1
            path = path[1:]
            # print(f'new path: {path}')

        if is_root is None:
            if s_count == 1:
                is_root = True
            else:
                is_root = False

        if s_count > 1:
            up_count = s_count - 1
        else:
            up_count = 0

        path = path.rstrip(self.key_sep)
        path = self._key_xform(path)

        if not as_string and path:
            path = path.split(self.key_sep)

        return self._parsed_path_obj(
            is_root=is_root,
            up_levels=up_count,
            path=path
        )

    def path_from(self, key):
        return self[self.find(key):]

    def path_to(self, key):
        return self[:self.find(key)+1]

    def find(self, key, start=0, end=-1):
        key = self._key_xform(key)
        return self._path.index(key, start, end)

    def to_string(self, key_sep=None, leading=True, trailing=False):
        """
        Returns a string format of the path.
        :param key_sep: allows over-writing of the key sep
        :param leading: include key_sep at beginning
        :param trailing: include key_sep at end.
        :return:
        """

        key_sep = key_sep or self.key_sep

        if leading:
            tmp_ret = key_sep
        else:
            tmp_ret = ''

        tmp_ret += key_sep.join(self._path)

        if trailing:
            tmp_ret += key_sep

        return tmp_ret

    def __contains__(self, item):
        try:
            self.find(item)
            return True
        except ValueError:
            return False

    def __call__(self, new_path=''):
        return self.cd(new_path)

    def __str__(self):
        return self.to_string()

    def __len__(self):
        return len(self._path)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._path[item]
        elif isinstance(item, slice):
            tmp_path = self._path[item]
            tmp_ret = self.copy(tmp_path)
            return tmp_ret
        else:
            raise TypeError('path indices must be integers or slices')

    def __iter__(self):
        for i in self._path:
            yield i

    def _make_comp(self, other):
        # print('testing comparison')
        return self._parse_path_in(other, as_string=True).path,  self.to_string(leading=False, trailing=False)

    def __eq__(self, other):
        if isinstance(other, int):
            return len(self) == other
        else:
            other, me = self._make_comp(other)

        return other == me

    def __gt__(self, other):
        if isinstance(other, int):
            return len(self) > other
        else:
            other, me = self._make_comp(other)
        return me.startswith(other) and not other == me

    def __lt__(self, other):
        if isinstance(other, int):
            return len(self) < other
        else:
            other, me = self._make_comp(other)
        return other.startswith(me) and not other == me

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        if isinstance(other, int):
            return len(self) <= other
        else:
            other, me = self._make_comp(other)
        return other.startswith(me) or other == me

    def __ge__(self, other):
        if isinstance(other, int):
            return len(self) >= other
        else:
            other, me = self._make_comp(other)
        return me.startswith(other) or other == me

    def __bool__(self):
        if self._path:
            return True
        else:
            return False

    def __add__(self, other):
        tmp_ret = self.copy()
        other = self._parse_path_in(other, is_root=False)
        # print(f"other path: {other}")
        return tmp_ret.cd(other)

    def __iadd__(self, other):
        other = self._parse_path_in(other, is_root=False)
        return self.cd(other)

    def _merge_list(self, other):
        other = self._parse_path_in(other).path
        me = self._path

        # print(f' combining lists for: {other}')
        # print(f'                 and: {me}')
        combined = merge_list(me, other)

        return combined

    def __and__(self, other):
        tmp_ret = self.copy()
        path = self._parsed_path_obj(
            is_root=True,
            up_levels=0,
            path=self._merge_list(other)
        )
        return tmp_ret.cd(path)

    def __iand__(self, other):
        path = self._parsed_path_obj(
            is_root=True,
            up_levels=0,
            path=self._merge_list(other)
        )
        return self.cd(path)

    __repr__ = __str__