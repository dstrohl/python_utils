__author__ = 'strohl'

import collections
from django.utils.text import slugify

LookupTuple = collections.namedtuple('LookupTuple',['stored','display','reference'])


class LookupItem(LookupTuple):

    '''
    def __init__(self, *args, **kwargs):
        super(LookupItem, self).__init__(*args, **kwargs)
        if not self.reference:
            self.reference = copy.deepcopy(self.stored)
        self.reference = slugify(self.reference)
    '''
    def __str__(self):
        return self.stored

class LookupManager(object):


    def __init__(self,lookup_list):
        """
        :param lookup_list:
                lookup list is a list of tuples (stored_value, display_value [, referenced_name] ):
                    stored value = the value that would be stored in the db
                    representative value = the value that is used for display
                    referenced value is the name used in coding (if not present stored_value is used)
        :param case_sensitive:
                determines if lookups are case sensitive or not.
        """
        self.stored_dict = {}
        self.display_dict = {}
        self.reference_dict = {}
        self.data_list = []
        self.lookup_list = []
        self.master_dict = {}

        for l in lookup_list:

            tmp_l = LookupItem(*l)

            self.stored_dict[tmp_l.stored] = tmp_l
            self.display_dict[tmp_l.display] = tmp_l
            self.reference_dict[slugify(tmp_l.reference)] = tmp_l
            self.data_list.append(tmp_l)
            self.lookup_list.append( (tmp_l.stored, tmp_l.display ))
            self.master_dict[tmp_l.stored] = tmp_l
            self.master_dict[tmp_l.display] = tmp_l
            self.master_dict[slugify(tmp_l.reference)] = tmp_l

    def __iter__(self):
        for i in self.lookup_list:
            yield i

    def __getattr__(self, item):
        return self.reference_dict[item]

    def __getitem__(self, item):
        return self.master_dict[item]

    def get_by_stored(self,item):
        return self.stored_dict[item]

    def get_by_display(self, item):
        return self.display_dict[item]


