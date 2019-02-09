

__all__ = ['DictKey2Method', 'AdvDict', 'TreeDict', 'TreeItem', 'MultiLevelDictManager', 'BasicTreeNode', 'DictOfDict',
           'DictOfList', 'flatten_dict']

import collections
from PythonUtils.BaseUtils.general_utils import _UNSET
from PythonUtils.BaseUtils.path import Path

# ===============================================================================
# Flatten Dictionaries
# ===============================================================================


def flatten_dict(dict_in, depth=0, max_depth=10, remove_empty=True, flatten_single=False):
    """
    Removes empty sub dictionaries and takes dictionaries with only one value and replaces the dict with the value.

    :param dict_in:  the dictionary to process
    :param max_depth: the maximum depth of dictionaries to process
    :param remove_empty: True/False: removes any empty dictionaries
    :param flatten_single:  True/False: takes any dicts with one value and replaces the dict with the value.
    :return:

    Examples:


        >>> tmp_in = {'l1': [1, 2, 3, 4]}
        >>> flatten_dict(tmp_in, flatten_single=True)
        [1, 2, 3, 4]

        >>> tmp_in = {'l1': [1, 2, 3, 4], 'l1.2': 'foobar'}
        >>> flatten_dict(tmp_in)
        {'l1': [1, 2, 3, 4], 'l1.2': 'foobar'}

        >>> tmp_in = {'l1.1': {'l2.1': {}}, 'l1.2': 'foobar'}
        >>> flatten_dict(tmp_in, flatten_single=True)
        'foobar'

        >>> tmp_in = {'l1.1': {'l2.1': {}}, 'l1.2': 'foobar'}
        >>> flatten_dict(tmp_in)
        {'l1.2': 'foobar'}

        >>> tmp_in = {'l1.1': {'l2.1': {}, 'l2.2': [1, 2, 3, 4]}, 'l1.2': 'foobar'}
        >>> flatten_dict(tmp_in, flatten_single=True)
        {'l1.1': [1, 2, 3, 4], 'l1.2': 'foobar'}

    """
    if flatten_single and len(dict_in) == 1:
        return list(dict_in.values())[0]
    elif remove_empty and len(dict_in) == 0:
        return None

    tmp_ret = {}

    for key, value in dict_in.items():
        if isinstance(value, dict):
            if depth >= max_depth:
                continue
            tmp_dict = flatten_dict(value, depth=depth+1, max_depth=max_depth,
                                    flatten_single=flatten_single, remove_empty=remove_empty)
            if not tmp_dict:
                continue
            tmp_ret[key] = tmp_dict
        else:
            tmp_ret[key] = value

    if flatten_single and len(tmp_ret) == 1:
        return list(tmp_ret.values())[0]
    elif remove_empty and len(tmp_ret) == 0:
        return None

    return tmp_ret


# ===============================================================================
# Multilevel dictionary
# ===============================================================================


class MultiLevelDictManager(object):
    """
    This provides a dictionary view that can be accessed via a :py:class:`Path` object or string.

    Examples:
        >>> mld = MultiLevelDictManager()

        >>> test_dict = {
                'level': '1',
                'l2a': {
                    'level': '2a',
                    'l3aa': {
                        'level': '3aa',
                        'l4aaa': {'level': '4aaa'},
                        'l4aab': {'level': '4aab'}},
                    'l3ab': {
                        'level': '3ab',
                        'l4aba': {'level': '4aba'},
                        'l4abb': {'level': '4abb'}}},
                'l2b': {
                    'level': '2b',
                    'l3ba': {
                        'level': '3ba',
                        'l4baa': {'level': '4baa'},
                        'l4bab': {'level': '4bab'}},
                    'l3bb': {
                        'level': '3bb',
                        'l4bba': {'level': '4bba'},
                        'l4bbb': {'level': '4bbb'}}}
                }


        >>> mldm = MultiLevelDictManager(test_dict)

        >>> mldm.cd['level']
        1

        >>>mldm['.l2a.level']
        '2a'

        >>>mldm('.l2a.')
        >>>mldm.get('level')
        '2a'

        >>>mldm.cd('.l2b.l3bb')
        >>>mldm['..level']
        '2b'

        >>>mldm.cd('.l2b.l3bb.l4bbb')
        >>>mldm['....level']
        '1'

        >>>mldm.cd('.l2b.l3bb.14bbb')
        >>>mldm['......level']
        '1'

        >>>mldm.cd('.l2b.l3bb.l4bbb')
        >>>mldm.get('......leddvel', 'noanswer')
        'noanswer'

        >>>mldm.cd('.l2b.l3bb.l4bbb')
        >>>mldm.pwd
        'l2b.l3bb.l4bbb'

        >>>mldm.cd('.')
        >>>mldm.get('l2b.l3bb.l4bbb.level', cwd=True)
        '4bbb'

        >>>mldm.get('..level', cwd=True)
        '3bb'


    """
    dict_db = None
    key_sep = '.'

    def __init__(self,
                 dict_db=None,
                 current_path='',
                 key_sep='.'):
        """
        :param dict_db: the dictionary to use for lookups.  The keys for this must be strings.
        :param current_path: the current path string (see :py:class:`Path` for more info on path strings)
        :param key_sep: the string to use to seperate the keys in the path, by default '.'
        """
        self.dict_db = dict_db
        if isinstance(current_path, str):
            current_path += key_sep
        self.path = Path(current_path, key_sep=key_sep)
        # self.key_sep = key_sep

    def load(self,
             dict_db,
             current_path=''):
        """
        Allows you to load a new dictionary, the path will be reset unless passed
        :param dict_db: The new dictionary for lookups
        :param current_path: The new path to use (will be reset to '.' unless passed)
        """
        self.dict_db = dict_db
        self.path(current_path)

    def cd(self, key):
        """
        Change directory path to a new path string (key)

        :param key: the new path string to chance to, see :py:class:`Path` for info on path strings
        :return:
        """
        self.path.cd(key)
        # self._pwd = self._parse_full_path(key)

    def get(self, key, default=_UNSET, cwd=False):
        """
        will get the data from the specified path string

        :param key: The path string to use (see :py:class:`Path` for info on path strings)
        :param default: if passed, a default to return if the key is not found at any level.
        :param cwd: Will change the current path to the path of the key passed.
        """

        cur_resp = self.dict_db
        tmp_path = Path(self.path, key)
        # key_path = self._parse_full_path(key)

        for k in tmp_path:
            try:
                cur_resp = cur_resp[k]
            except KeyError:
                if default is not _UNSET:
                    return default
                else:
                    msg = 'Key: "{}" not found in dict: {}'.format(k, self.dict_db)
                    raise KeyError(msg)
            except TypeError:
                msg = "parameter passed is not a dict or does not implement key lookups"
                raise TypeError(msg)

        if cwd:
            self.path = tmp_path

        return cur_resp

    def cwd(self, key):
        """
        Changes the current working directory to the passed path string (key).

        This is a shortcut for having to pass a path with a '.' at the end to signify a path

        :param key: The path string to use (see :py:class:`Path` for info on path strings)
        """
        self.path.cwd(key)

    @property
    def pwd(self):
        """
        Returns the current working directory and item (if present)
        """

        return self.path.path_str()
        # return self.key_sep.join(self._pwd)

    def __getitem__(self, item):
        return self.get(item)

    def __repr__(self):
        return 'MultiLevelLookupDict: current_path:{}  Dict:{}'.format(self.path, self.dict_db)

    __call__ = get


# ===============================================================================
# Dictionary Helper Objects
# ===============================================================================


class DictKey2Method(object):
    """
    Helper utility to allow dict keys to be accessed by attrs.

    Example:

        >>> d = {'one': 1, 'two': 2}
        >>> dk2m = DictKey2Method(d)
        >>> dk2m.one
        1
        >>> dk2m.two
        2
    """

    def __init__(self, mydict):
        self.mydict = mydict

    def __getattr__(self, item):
        try:
            return self.mydict[item]
        except KeyError:
            raise KeyError(item, ' is not a valid key for this dictionary')

    def __setattr__(self, key, value):
        if key in ('mydict',):
            self.__dict__[key] = value
        else:
            self.mydict[key] = value


class AdvDict(dict):
    """
    A dictionary that allows you to access contents as if they were methods.

    This uses the :py:class:`DictKey2Method` class and wraps it in a :py:class:`dict`.  This also forces the method
    lookups to use a special method name, thus minimizing conflicts with the existing dict methods.

    :param property_name: The name of the property to use to access the fields. (Default = 'key')

    Example:

        >>> d = AdvDict()
        >>> d['one'] = 1
        >>> d['two'] = 2
        >>> d['three'] = 3
        >>> d.key.one
        1

        >>> d = AdvDict(property_name='number')
        >>> d['one'] = 1
        >>> d['two'] = 2
        >>> d['three'] = 3
        >>> d.number.two
        2

    """

    def __init__(self, *args, **kwargs):
        property_name = kwargs.pop('property_name', 'key')
        super(AdvDict, self).__init__(*args, **kwargs)
        setattr(self, property_name, DictKey2Method(self))


# ===============================================================================
# Tree dictionary
# ===============================================================================


class TreeItem():
    _key = ''
    _parent = None
    _children = []
    _item_dict = {}

    def __init__(self,
                 key='',
                 parent=None,
                 children={},
                 item={}):
        self._key = key
        self._parent = parent
        self._children = children
        self._item_dict = item


class TreeDict():
    _root_dict = {}
    _root_node = TreeItem(key='root'
    )

    def __init__(self,
                 initial_list,
                 key_field='key',
                 parent_key='parent',
                 children_field='children'):
        self._initial_list = initial_list
        self._key_field = key_field
        self._parent_key = parent_key
        self._children_field = children_field

        for item in initial_list:
            self._add_to_tree(item)


    def _search_tree(self, key, dict_tree):
        if key in dict_tree:
            return dict_tree[key]
        else:
            for item in iter(dict_tree.values()):
                if item._children:
                    return self._search_tree(key, item._children)
        return None

    def _add_to_tree(self, node_dict):
        parent_node = None
        if node_dict[self._parent_key]:
            parent_node = self._search_tree(node_dict[self._parent_key], self._root_node._children)

        if not parent_node:
            parent_node = self._root_node

        parent_node._children[node_dict[self._key_field]] = TreeItem(key=node_dict[self._key_field],
                                                                     parent=parent_node,
                                                                     children={},
                                                                     item=node_dict,
        )

    def add_list(self, list_in):
        for item in list_in:
            self._add_to_tree(item)


    def _get_dnk(self, dict_list):
        tmp_list = []
        for item in iter(dict_list.values()):
            if item._children:
                children_list = self._get_dnk(item._children)
            else:
                children_list = []

            tmp_dict = {}
            tmp_dict.update(item._item_dict)
            tmp_dict[self._children_field] = children_list

            tmp_list.append(tmp_dict)

        return tmp_list

    def get_dict_no_key(self):
        return self._get_dnk(self._root_node._children)


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


# ===============================================================================
# Tree Node
# ===============================================================================

class DictOfDict(collections.UserDict):
    """
    This is a quick dict utility that assumes that all sub fields are dicts, and if you do a
    a lookup on a field which is not there, it will create it as a dict.

    this is mostly intended for cases where you have a dict in a dict and you want to lookup on the
    second level regularly.
    """
    sub_type = dict
    sub_type_kwargs = None

    def __getattr__(self, item):
        if item not in self:
            if self.sub_type_kwargs is not None:
                self[item] = self.sub_type(**self.sub_type_kwargs)
            else:
                self[item] = self.sub_type()

        return super(DictOfDict, self).__getattr__(item)


class DictOfList(DictOfDict):

    """
    same as above but this auto-creates things as lists.
    """
    sub_type = list

