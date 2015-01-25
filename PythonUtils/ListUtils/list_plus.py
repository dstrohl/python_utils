__author__ = 'dstrohl'

import copy


class ListPlus(list):
    """
    adds some additional features to the list object.
        ListPlus.add             : allows insert new records past the existing last record
        ListPlus.update          : allows updating records or adding them past the existing last record
        ListPlus[key] = value    : sale as list2.update though uses list key notation
        ListPlus.get             : allows for setting a default response instead of generating an error if rec does not exist.
    """

    def _update_function(self, curr_obj, new_obj ):
        """
        Allows overriding to allow for manipulating or validating updated information if needed'

        this is called anytime something is updated (not for new records though)

        :param curr_obj: this passes the current object in the list
        :param new_obj: this passes the new object
        :return: returns the object to be saved.
        """
        return new_obj

    def add(self, i, x, **kwargs):
        """
        Will add any needed items to a list to add the new item at the indexed spot.

        :param i: list offset to add item to.
            If this is lower than or equal to the size fo the list, the items will be added directly to the end.
            If this is larger than the list length, new items will be added to the list to pad it out long enough
            to reach this length.
        :param x: the new item to add to the list
        :param new_item_default: the default item that will be added as padding if needed.
            this overrides the class setting if present.
        """
        # print( 'l:', l )
        # print( 'i:', i )
        new_item_default = kwargs.get('new_item_default', self.new_item_default)
        if i >= len(self):
            l = len(self)
            mt_items = i - l
            for ni in range(mt_items):
                self.append(new_item_default)
            self.append(x)
        else:
            self.insert(i, x)

    def set_new_item_default(self, new_item_default):
        """
        This sets the default new item object for when blank items must be added
        :param new_item_default: the item that will be used for blank new items.
        """
        self._new_item_default = new_item_default

    @property
    def new_item_default(self):
        try:
            return self._new_item_default
        except AttributeError:
            self.set_new_item_default(None)
            return self._new_item_default

    def update(self, i, x, **kwargs):
        """
        Updates a specific item at a specific offset, if that item does not exist, padding items will
        be added to the list lengthen it.

        :param i: list offset to update.
        :param x: the new item to update in the list
        :param new_items_default: the default item that will be added as padding if needed,
        this overrides the class setting if present
        """
        new_item_default = kwargs.get('new_item_default', self.new_item_default)

        try:
            tmp_value = self._update_function(copy.deepcopy(self[i]), x)
        except (IndexError, TypeError):
            tmp_value = self._update_function(None, x)

        try:
            self[i] = tmp_value
        except IndexError:
            l = len(self)
            mt_items = i - l
            for ni in range(mt_items):
                self.append(new_item_default)
            self.append(tmp_value)

    def get(self, *args):
        i = args[0]
        if len(args) == 1:
            return self[i]
        elif len(args) == 2:
            try:
                return self[i]
            except IndexError:
                return args[1]
        else:
            raise TypeError('ListPlus takes at most 2 arguments, '+str(len(args))+' given')

    '''
    def __setitem__(self, i, x):
        if isinstance(i, int):
            self.update(i, x)
        else:
            raise TypeError('ListPlus indices must be integers, not '+type(i).__name__)
    '''