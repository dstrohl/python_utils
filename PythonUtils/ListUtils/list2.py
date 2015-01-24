'''
Created on Aug 16, 2014

@author: strohl
'''
import copy


class list2( list ):


    _def_update_function = None

    '''
    adds some additional features to the list object.
        list2.add             : allows insert new records past the existing last record
        list2.update          : allows updating records or adding them past the existing last record
        list2[key] = value    : sale as list2.update though uses list key notation
        list2.get             : allows for setting a default response instead of generating an error if rec does not exist.
    '''

    '''
    def __init__( self, *args, **kwargs ):
        tmp_u_f = kwargs.pop( 'funct', None )
        if tmp_u_f:
            self._def_update_function = tmp_u_f
        elif not self._update_function( 'abcdef', 'hijklmn' ) == self:
            self._def_update_function = self._update_function
        super( list2, self ).__init__( *args, **kwargs )
    '''
    def _update_function( self, curr_obj, new_obj ):
        ' can be over-ridden to allow for a default update function if needed'
        return new_obj

    def add( self, i, x, new_items = '' ):
        ''' 
        list2.add will insert any needed items to a list to add the new item at the indexed spot.
        i = list offset
        x = object to add
        new_items = default object for any new list items added
        funct = function to run against any existing entries.
        '''
        # print( 'l:', l )
        # print( 'i:', i )
        if i >= len( self ):
            l = len( self )
            mt_items = i - l
            for ni in range( mt_items ):
                self.append( new_items )
            self.append( x )
        else:
            self.insert( i, x )

    def update( self, i, x, new_items = '' ):
        ''' 
        list2.update will add any needed items to a list to update or add the new item at the indexed spot.
        i = list offset
        x = object to add
        new_items = default object for any new list items added
        '''
        try:
            tmp_value = self._update_function( copy.deepcopy( self[i] ), x )
        except ( IndexError, TypeError ):
            tmp_value = self._update_function( None, x )


        try:
            self[i] = tmp_value
        except IndexError:
            l = len( self )
            mt_items = i - l
            for ni in range( mt_items ):
                self.append( new_items )
            self.append( tmp_value )


    def get( self, i, default = None ):
        try:
            return self[i]
        except IndexError:
            return default

