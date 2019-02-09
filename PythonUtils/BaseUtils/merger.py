#!/usr/bin/env python

"""merger.py:

This is a utility that allows complex merging of objects.

By default it is set to merge lists and dicts, bit it can be modified to handle any object type you wish.

To extend this to other objects, you must sub-class the BaseMergeHandler to handle the merge processing.




"""

__author__ = "Dan Strohl"
__copyright__ = "Copyright 2019, Dan Strohl"
__credits__ = ['Dan Strohl']
__license__ = ""
__version__ = "0.9.1"
__maintainer__ = ""
__email__ = ""
__status__ = "Development"

__all__ = ['merge_object', 'MergeManager', 'MERGE_ACTION', 'BaseMergeHandler', 'merge_handler']

from enum import Enum
from copy import deepcopy
from fnmatch import fnmatch
from itertools import zip_longest
from PythonUtils.BaseUtils.general_utils import _UNSET

# ===============================================================================
# merges dictionaries recursively.
# ===============================================================================


class MERGE_ACTION(Enum):
    MERGE = 'merge'
    KEEP = 'keep'
    OVERWRITE = 'overwrote'
    RAISE = 'raise'


class BaseMergeHandler(object):
    name = 'base'
    action = MERGE_ACTION.MERGE
    path = '*'
    match_class = None
    on_failure_action = MERGE_ACTION.RAISE
    raise_at_max_depth = False
    classes_must_match = True

    """
    parameters:
        - action = what action to perform.
        - path = Allows you to have a different action for an object at a specific point in the structure.
            this is a glob matched string.  Each time this class is called, it is passed a path string which is a dot 
            seperated list of keys, indexes, or strings that tells the system it got here.
            
            for example, given this type of object:  {'lvl-1': [{lvl-2.1:2}, {lvl-2.2:3}]}
            the path to the integer 3 would be: 'lvl-1.1.lvl-2.2'.  you could address this by using a "lvl-1.1.*' as a 
            path parameter, which would take effect on any objects that match it's type from the dict key lvl-1 and the
            second item in the list on downward.
    """
    def __str__(self):
        return 'MergeHandler:%s' % self.name

    __repr__ = __str__

    def copy(self, base_obj):
        """
        this can be overwritten if needed if deepcopy does not work on the object
        :param base_obj:
        :return:
        """
        return deepcopy(base_obj)

    def detect(self, base_obj, merge_obj, path):
        tmp_base = self.detect_base_obj_type(base_obj)
        if tmp_base == 0:
            # print('base_obj type mismatch: %s v %s' % (base_obj, self.name))
            return 0
        tmp_match = self.detect_merge_obj_type(merge_obj)
        if tmp_match == 0:
            # print('%s: merge_obj type mismatch: %r  v %r' % (self.name, merge_obj, self.match_class))
            return 0
        tmp_path = self.detect_path(path)
        if tmp_path == 0:
            # print('path mismatch: %r  v %r' % (path, self.path))
            return 0

        # print('%s: Returning value of: %s + %s + %s' % (self.name, tmp_base, tmp_match, tmp_path))

        return tmp_base + tmp_match + tmp_path

    def detect_base_obj_type(self, obj):
        """
        returns:
            0: cannot process object
            500: can process object, but may not be the best (i.e., an iterable object, but not a list)
            1000: matching object
        """
        if self.match_class is None:
            return 500
        elif isinstance(obj, self.match_class):
            return 1000
        else:
            return 0

    def detect_merge_obj_type(self, obj):
        """
        returns:
            0: cannot process object
            500: can process object, but may not be the best (i.e., an iterable object, but not a list)
            1000: matching object
        """
        if self.match_class is None:
            return 500
        elif isinstance(obj, self.match_class):
            return 1000
        else:
            return 0

    def detect_path(self, path):
        """
        returns length of matching path
        """
        if fnmatch(path, self.path):
            return len(self.path)
        else:
            return 0

    def process(self, base_obj, merge_obj, parent, depth, max_depth, path):
        if depth == max_depth:
            if self.raise_at_max_depth:
                raise RecursionError('Max depth reached in merging objects')
            else:
                return self.copy(base_obj)
        if self.action == MERGE_ACTION.MERGE:
            try:
                return self.merge(base_obj=self.copy(base_obj), merge_obj=merge_obj, parent=parent, depth=depth+1, max_depth=max_depth, path=path)
            except Exception:
                if self.on_failure_action == MERGE_ACTION.RAISE:
                    raise
                elif self.on_failure_action == MERGE_ACTION.KEEP:
                    return self.copy(base_obj)
                elif self.on_failure_action == MERGE_ACTION.OVERWRITE:
                    return self.copy(merge_obj)
                else:
                    raise AttributeError('Invalid on_failure_action set: %s' % self.on_failure_action)
        elif self.action == MERGE_ACTION.KEEP:
            return base_obj
        else:
            return merge_obj

    def merge(self, base_obj, merge_obj, parent, depth, max_depth, path):
        """
        This is the primary method to modify on subclassing this class.

        This method shoudl handle doing the merge, and returning an object that is a merged combination of the two.

        If you need to handle sub-objects, you can call:

            parent.merge_item(base_obj, merge_obj, parent, depth, max_depth, path)

            you must also append to the path a new level preceedd by a ".".

        :param base_obj:
        :param merge_obj:
        :param parent:
        :param depth:
        :param max_depth:
        :param path:
        :return:
        """
        raise NotImplementedError('Must implement this method')


class AnyAddHandler(BaseMergeHandler):
    name = 'AnyAdd'

    def merge(self, base_obj, merge_obj, parent, depth, max_depth, path):
        return base_obj + merge_obj


class AnyOverwriteHandler(BaseMergeHandler):
    name = 'AnyOverwrite'
    action = MERGE_ACTION.OVERWRITE


class MergeDictHandler(BaseMergeHandler):
    name = 'Dict'
    match_class = dict
    action_on_dupe_key = MERGE_ACTION.MERGE

    def merge(self, base_obj, merge_obj, parent, depth, max_depth, path):
        for key, value in merge_obj.items():
            if key in base_obj:
                if self.action_on_dupe_key == MERGE_ACTION.MERGE:
                    if path == '':
                        path = key
                    else:
                        path += '.' + key
                    base_obj[key] = parent.merge_item(base_obj[key], value, depth=depth, max_depth=max_depth, path=path)
                elif self.action_on_dupe_key == MERGE_ACTION.KEEP:
                    continue
                elif self.action_on_dupe_key == MERGE_ACTION.OVERWRITE:
                    base_obj[key] = self.copy(merge_obj)
                elif self.action_on_dupe_key == MERGE_ACTION.RAISE:
                    raise KeyError('Duplicate Key found: %s' % key)
            else:
                base_obj[key] = value
        return base_obj


class MergeListHandler(BaseMergeHandler):
    name = 'List'
    match_class = (list, tuple)

    def merge(self, base_obj, merge_obj, parent, depth, max_depth, path):
        index = -1
        for base, merge in zip_longest(base_obj, merge_obj, fillvalue=_UNSET):
            index += 1
            if path == '':
                path = str(index)
            else:
                path += '.' + str(index)

            if base is _UNSET:
                base_obj.append(merge)
            elif merge is _UNSET:
                break
            else:
                base_obj[index] = parent.merge_item(base, merge, depth=depth, max_depth=max_depth, path=path)
        return base_obj

class MergeManager(object):

    def __init__(self, *merge_handlers, max_depth=10):
        self.handlers = []
        self.max_depth = max_depth
        for h in merge_handlers:
            self.add_handler(h)

    def add_handler(self, handler):
        handler = handler()
        self.handlers.append(handler)

    def merge_item(self, base_obj, merge_obj, depth, max_depth, path):
        merge_handler = None
        level = 0
        for h in self.handlers:
            h_level = h.detect(base_obj, merge_obj, path)
            # print('%r responded with value: %r' % (h, h_level))
            if h_level > level:
                level = h_level
                merge_handler = h

        if level == 0 or merge_handler is None:
            raise AttributeError('No handler found for items: %r <and> %r' % (base_obj, merge_obj))
        indent = ''.rjust(depth * 3)
        # print('%s %s is Merging path: %s, items: %r and %r' % (indent, merge_handler.name, path, base_obj, merge_obj))
        return merge_handler.process(base_obj, merge_obj, parent=self, depth=depth, max_depth=max_depth, path=path)

    def merge(self, *items, max_depth=None):
        if not items:
            raise AttributeError('At least one object must be passed to merge')

        base_obj = items[0]

        if len(items) == 1:
            return base_obj

        if max_depth is None:
            max_depth = self.max_depth

        for item in items[1:]:
            base_obj = self.merge_item(base_obj=base_obj, merge_obj=item, depth=0, max_depth=max_depth, path='')

        return base_obj


merge_handler = MergeManager(MergeDictHandler, MergeListHandler, AnyOverwriteHandler)


def merge_object(*items, max_depth=10):
    return merge_handler.merge(*items, max_depth=max_depth)
