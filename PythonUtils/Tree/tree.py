__author__ = 'dstrohl'

from PythonUtils.BaseUtils.base_utils import _UNSET

# ===============================================================================
# Tree Node
# ===============================================================================

class BasicTreeNode():
    """
    This is a basic tree node, it can be created, then child nodes can be added, removed, etc.
    """
    key = ''
    data = None
    parent = None
    children = None
    ucid = 0
    path_sep = '.'
    my_path = ''
    root = False

    def __init__(self,
                 tree=None,
                 key=None,
                 parent=None,
                 data=_UNSET):
        self.tree = tree
        self.parent = parent
        self.children = {}
        self.data = data
        self.key = self._make_child_key(key)

        if parent is None:
            self.root = True
            self.my_path = self.key
        else:
            self.my_path = self.parent.path + self.path_sep + self.key

    def add_child(self, node=None, key=None, data=_UNSET):
        if node is None:
            key = self._make_child_key(key)
            self.children[key] = self.__class__(self.tree, key, self, data)
        else:
            self.children[node.key] = node

    def rem_child(self, node=None, key=None):
        if node is not None:
            key = node.key
        del self.children[key]

    def child(self, key):
        return self.children[key]

    @property
    def siblings(self):
        return self.parent._my_kids_sibs(self)

    def _my_kids_sibs(self, child):
        for i in self.children:
            if i != child:
                yield i

    def _make_child_key(self, key):
        if not self.root:
            if key is None:
                self.parent._ucid += 1
                return str(self.parent._ucid)
            else:
                return key
        else:
            if key is None:
                return '0'
            else:
                return key

    def __getitem__(self, item):
        return self.child(item)

    def __bool__(self):
        return self.data is not _UNSET

    def __delitem__(self, key):
        self._rem_child_entry(key)

    def __repr__(self):
        return 'TreeNode: '+self.my_path

    def __call__(self):
        return self.data

