'''
Created on Jun 18, 2014

@author: strohl
'''

class DBList():
    '''
    this is a list type object that also allows for lookups like a dictionary
    this assumes a list of dictionary entries.
    
    NOTE: if there are dupe items (by defined key) in the starting list, only the last one will be kept.

    '''
    internal_dict = {}


    def __init__( self,
                 starting_list,
                 dict_key,
                 ):
        for item in starting_list:
            self.internal_dict[item[dict_key]] = item

    def __iter__( self, key ):
        return self.internal_dict[key]

    def get_list( self ):
        return internal_dict.items()

    def get_dict( self ):
        return self.internal_dict






