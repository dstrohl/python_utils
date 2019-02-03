


from enum import Enum
from copy import deepcopy
from fnmatch import fnmatch
from itertools import zip_longest
from PythonUtils.pyutils.base_utils import _UNSET

# ===============================================================================
# merges dictionaries recursively.
# ===============================================================================


class MERGE_ACTION(Enum):
    MERGE = 'merge'
    KEEP = 'keep'
    OVERWRITE = 'overwrote'
    RAISE = 'raise'


class BaseMergeHandler(object):
    action = MERGE_ACTION.MERGE
    path = '*'
    match_class = None
    on_failure_action = MERGE_ACTION.RAISE
    raise_at_max_depth = False
    classes_must_match = True

    @classmethod
    def copy(self, base_obj):
        return deepcopy(base_obj)

    @classmethod
    def detect(self, base_obj, merge_obj, path):
        tmp_base = self.detect_base_obj_type(base_obj)
        if tmp_base == 0:
            return 0
        tmp_match = self.detect_merge_obj_type(merge_obj)
        if tmp_match != 1000:
            if self.classes_must_match or tmp_base == 0:
                return 0
        tmp_path = self.detect_path(path)
        if tmp_path == 0:
            return 0
        return tmp_base + tmp_match + tmp_path

    @classmethod
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

    @classmethod
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

    @classmethod
    def detect_path(self, path):
        """
        returns length of matching path
        """
        if fnmatch(path, self.path):
            return len(path)
        else:
            return 0

    @classmethod
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

    @classmethod
    def merge(self, base_obj, merge_obj, parent, depth, max_depth, path):
        raise NotImplementedError('Must implement this method')


class AnyAddHandler(object):
    @classmethod
    def merge(self, base_obj, merge_obj, parent, depth, max_depth):
        return base_obj + merge_obj


class AnyOverwriteHandler(object):
    action = MERGE_ACTION.OVERWRITE


class MergeDictHandler(BaseMergeHandler):
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
    match_class = (list, tuple)

    @classmethod
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
                parent.merge_item(base, merge, depth=depth, max_depth=max_depth)


class MergeManager(object):

    def __init__(self, *merge_handlers, max_depth=10):
        self.handlers = []
        self.max_depth = max_depth
        for h in merge_handlers:
            self.add_handler(h)

    def add_handler(self, handler):
        self.handlers.append(handler)

    def merge_item(self, base_obj, merge_obj, depth, max_depth, path):
        merge_handler = None
        level = 0
        for h in self.handlers:
            h_level = h.detect(base_obj, merge_obj, path)
            if h_level > level:
                level = h_level
                merge_handler = h

        if level == 0 or merge_handler is None:
            raise AttributeError('No handler found for items')

        return merge_handler.process(base_obj, merge_handler, parent=self, depth=depth, max_depth=max_depth, path=path)

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


mh = MergeManager(MergeDictHandler, MergeListHandler, AnyOverwriteHandler)


def merge_object(*items, max_depth=10):
    return mh.merge(*items, max_depth=max_depth)
