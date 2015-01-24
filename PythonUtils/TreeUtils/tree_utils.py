'''
Created on Jun 18, 2014

@author: strohl
'''


class TreeItem():
    _key = ''
    _parent = None
    _children = []
    _item_dict = {}

    def __init__( self,
                 key = '',
                 parent = None,
                 children = {},
                 item = {} ):
        self._key = key
        self._parent = parent
        self._children = children
        self._item_dict = item


class TreeDict():

    _root_dict = {}
    _root_node = TreeItem( key = 'root'
                          )

    def __init__( self,
                 initial_list,
                 key_field = 'key',
                 parent_key = 'parent',
                 children_field = 'children',
                 ):
        self._initial_list = initial_list
        self._key_field = key_field
        self._parent_key = parent_key
        self._children_field = children_field

        for item in initial_list:
            self._add_to_tree( item )


    def _search_tree( self, key, dict_tree ):
        if key in dict_tree:
            return dict_tree[key]
        else:
            for item in iter( dict_tree.values() ):
                if item._children:
                    return self._search_tree( key, item._children )
        return None

    def _add_to_tree( self, node_dict ):
        parent_node = None
        if node_dict[self._parent_key]:
            parent_node = self._search_tree( node_dict[self._parent_key], self._root_node._children )

        if not parent_node:
            parent_node = self._root_node

        parent_node._children[node_dict[self._key_field]] = TreeItem( key = node_dict[self._key_field],
                                                                      parent = parent_node,
                                                                      children = {},
                                                                      item = node_dict,
                                                                )

    def add_list( self, list_in ):
        for item in list_in:
            self._add_to_tree( item )


    def _get_dnk( self, dict_list ):
        tmp_list = []
        for item in iter( dict_list.values() ):
            if item._children:
                children_list = self._get_dnk( item._children )
            else:
                children_list = []

            tmp_dict = {}
            tmp_dict.update( item._item_dict )
            tmp_dict[self._children_field] = children_list

            tmp_list.append( tmp_dict )

        return tmp_list

    def get_dict_no_key( self ):
        return self._get_dnk( self._root_node._children )




