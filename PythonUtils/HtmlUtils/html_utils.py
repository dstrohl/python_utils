'''
Created on Aug 18, 2014

@author: strohl
'''
'''
Created on Aug 8, 2014

@author: strohl
'''
import collections
import copy
from HelperUtils.helper_utils.indented_print import IndentedPrint
from operator import itemgetter


ip = IndentedPrint()

#===============================================================================
# SINGLE ATTRIB NAMED TUPLE CLASS  (used for internal storage and moving data)
#===============================================================================


AttrClass = collections.namedtuple( 'AttrClass', ['name', 'value'] )



#===============================================================================
# BASE ATTRIB CLASS
#===============================================================================


class BaseAttrib( object ):
    _return_format = '{name}="{value}"'
    empty_attrib = True
    default_match_name = 'base'
    for_match = False
    value = None
    name = None
    output_rank = 100
    output_rank_dict = {'id':1}


    def __init__( self, name = None, value = None ):


        if not name and not value:

            self._init_lists( '_attrib_starts_with_names' )
            self._init_lists( 'attrib_match_names' )
            self._init_lists( 'attrib_deny_names' )
            self._init_lists( 'attrib_instance_types', to_list = False )
            self._init_lists( 'attrib_value_match_list' )


            self.name = self.default_match_name
            for i, t in enumerate( self.attrib_match_names ):
                if not t.islower():
                    self.attrib_match_names[i] = t.lower()
                if t.endswith( '*' ):
                    self._attrib_starts_with_names.append( t.rstrip( '*' ) )

            for t in self._attrib_starts_with_names:
                tmp_name_string = t + '*'
                self.attrib_match_names.remove( tmp_name_string )

            for i, t in enumerate( self.attrib_deny_names ):
                if not t.islower():
                    self.attrib_deny_names[i] = t.lower()
            self.for_match = True


        elif not value:
            try:
                if len( name ) != 1:
                    self._value_error( 'Too many objects name field' )
                name, value = name.popitem( 0 )
            except:
                pass

        elif not name:
            self._value_error( 'NAME required for setting attribute' )

        if not self.for_match:
            # ip.pl( '[init ', self.default_match_name, '] name: ', name, ' value: ', value )
            name = str( name )
            self.name = name.lower()
            self.add( value )

        try:
            self.output_rank = self.output_rank_dict[self.name]
        except KeyError:
            pass


    def add( self, value ):
        ''' adds or updates the attrib to the internal list or database '''

        tmp_old = self.get_dict
        tmp_passed_value = value

        # ip.pl( 'add value : ' , value )

        if isinstance( value, self.__class__ ):
            if self.name == value.name:
                value = value.get_dict
            else:
                return tmp_old

        if isinstance( value, dict ):
            try:
                value = value[self.name]
            except ( TypeError, KeyError ):
                pass

        if value != None:
            self._local_parse_and_add( value )
            self._validate()
            self.empty_attrib = False
        else:
            self._value_error( 'No Value Determinable from : ', tmp_passed_value )

        return tmp_old



    def _local_parse_and_add( self, value ):

        self.value = value


    def remove( self, value = None ):
        '''
        will remove elements and return true to the parent object 
        if the entire object needs to be removed (for example, after 
        removing all items from the list, this is checked after calling

        '''
        self.empty_attrib = True
        return True

    @property
    def get_dict( self ):
        if self.empty_attrib:
            return {}
        else:
            return {self.name:self.value}

    @property
    def get_value_list( self ):
        if self.empty_attrib:
            return []
        else:
            return [self.value, ]

    @property
    def get_attrib( self ):
        if self.empty_attrib:
            return None
        else:
            return AttrClass( self.name, [self.value] )


    def _init_lists( self, list_name , to_list = True ):


        try:
            tmp_list = getattr( self, list_name )
        except:
            tmp_list = set()

        if to_list:
            tmp_list = list( tmp_list )


        setattr( self, list_name, tmp_list )



    def match_type( self, name, value ):
        ''' returns self if the name value items indicate that this is the attrib type'''
        name = str( name )
        name = name.lower()

        if name in self.attrib_match_names:
            return self.__class__( name, value )

        if self.attrib_deny_names and ( name in self.attrib_deny_names ):
            return None

        for n in self._attrib_starts_with_names:
            if name.startswith( n ):
                return self.__class__( name, value )

        if self.attrib_value_match_list and ( value in self.attrib_value_match_list ):
            return self.__class__( name, value )


        if self.attrib_instance_types and isinstance( value, self.attrib_instance_types ):
            return self.__class__( name, value )

        return None


    def _validate( self ):
        ''' validates correct data'''

        if not self.name:
            self._value_error( 'No Name Defined' )
        if not self.name.isalnum():
            self._value_error( 'Invalid Characters in name: ', self.name )
        return

        if not str( self.ret_value ):
            self._value_error( 'No Value Defined' )




    def _value_error( self, *args ):
        ''' used to centralize the error messages'''

        tmp_msg_list = []
        for arg in args:
            tmp_msg = str( arg )
            if tmp_msg:
                tmp_msg_list.append( tmp_msg )
        msg = ''.join( tmp_msg_list )

        base_msg = 'HTML Attrib Validation Error : '
        if not msg:
            msg = base_msg + ' (Name: {name}  Value: {value})'
        else:
            msg = base_msg + msg

        raise ValueError( msg.format( name = self.name, value = self.value ) )

    @property
    def _ret_value( self ):
        return self.value

    @property
    def _ret_name( self ):
        return self.name

    def render( self ):
        return str( self )


    def __str__( self ):
        if self.empty_attrib:
            return ''
        else:
            return self._return_format.format( name = self._ret_name, value = self._ret_value )

    '''
    def __repr__( self ):
        # handles returning what this should show
        return "%s ( %s )" % ( self.__class__.__name__ )
    '''

    def __len__( self ):
        # handles getting the length
        return 1

    def __contains__( self, item ):
        # handles checking for "in"
        if ( item == self.value ) or ( item == self.name ):
            return True
        else:
            return False

#===============================================================================
# UNIQUE ATTRIB CLASS
#===============================================================================

class UniqueAttrib( BaseAttrib ):
    default_match_name = 'unique'
    attrib_match_names = ( 'id' )
    attrib_deny_names = ( 'class', 'style', 'data' )
    attrib_instance_types = ( str, )


#===============================================================================
# BOOLEAN ATTRIB CLASS
#===============================================================================

class BooleanAttrib( BaseAttrib ):
    # used for attributes that indicate true/false
    default_match_name = 'boolean'

    attrib_deny_names = ( 'id', 'class', 'data', 'style' )
    attrib_value_match_list = ( True, False, 'true', 'false', '', None )
    _return_format = '{name}'
    output_rank = 100
    output_rank_dict = {'':100}



    def _local_parse_and_add( self, value ):

        if isinstance( value, str ):
            value = value.lower()
        if value in ( self.name, 'true', True, '', None ):
            self.value = True
        else:
            self.value = False


    @property
    def get_dict( self ):
        if self.empty_attrib:
            return {}
        else:
            return {self.name:True}

    @property
    def _ret_value( self ):
        return self.name

    @property
    def get_value_list( self ):
        if self.empty_attrib:
            return []
        else:
            return [self.value, ]


    def match_type( self, name, value ):
        ''' returns self if the name value items indicate that this is the attrib type'''
        tmp_ret = super( BooleanAttrib, self ).match_type( name, value )

        if tmp_ret:
            return tmp_ret

        if name == value:
            return self.__class__( name, value )

    def __str__( self ):
        if self._ret_value == True and not self.empty_attrib:
            return self._return_format.format( name = self._ret_name, value = self._ret_value )
        else:
            return ''

#===============================================================================
# LIST ATTRIB CLASS
#===============================================================================

class ListAttrib( BaseAttrib ):
    default_match_name = 'list'
    _return_format = '{name}="{value}"'
    attrib_match_names = ( 'class', )
    attrib_instance_types = ( list, tuple )
    output_rank = 50
    output_rank_dict = {'class':5}


    def __init__( self, name = None, value = None ):
        self._value_list = []
        super( ListAttrib, self ).__init__( name, value )




    def _local_parse_and_add( self, value ):
        ''' 
        in this case, a string separated with spaces is considered
        multiple records, if you need to get a string with a space in, pass
        a list or tuple, which is not individually parsed.
        
        '''

        if isinstance( value, str ):
            value = value.split( ' ' )

        if isinstance( value, ( list, tuple ) ):
            self._value_list.extend( value )
            tmp_set = set( self._value_list )
            tmp_list = list( tmp_set )
            self._value_list = tmp_list



    @property
    def _ret_value( self ):
        return ' '.join( self._value_list )


    def remove( self, value = None ):
        # will return true to the parent object if the entire object needs to be removed (for example, after removing all items from the list, checked after calling

        if value:
            try:
                self._value_list.remove( value )
            except ValueError:
                pass

            if len( self ) == 0:
                self.empty_attrib = True
                return True

            else:
                return False
        else:
            self._value_list.clear()
            self.empty_attrib = True
            return True

    @property
    def get_dict( self ):
        if self.empty_attrib:
            return {}
        else:
            return {self.name:self._value_list}

    @property
    def get_value_list( self ):
        if self.empty_attrib:
            return []
        else:
            return self._value_list

    @property
    def get_attrib( self ):
        if self.empty_attrib:
            return None
        else:
            return AttrClass( self.name, self.value_list )



    def __len__( self ):
        # handles getting the length
        return len( self._value_list )

    def __contains__( self, item ):
        # handles checking for "in"
        if item == self.name:
            return True

        if item in self._value_list:
            return True

        return False


#===============================================================================
# STYLE ATTRIB CLASS
#===============================================================================

class StyleAttrib( BaseAttrib ):
    default_match_name = 'style'
    _return_format = '{name}="{value}"'
    _value_format = '{attrib}:{setting};'
    attrib_match_names = ( 'style', )
    output_rank = 75
    output_rank_dict = {'style':75}


    def __init__( self, name = None, value = None ):
        self._value_dict = {}
        super( StyleAttrib, self ).__init__( name, value )


    def _validate( self ):
        super( StyleAttrib, self )._validate()

        # ip.pl( 'Class: ', self.default_match_name, ' values: ', self._value_dict )

        del_list = []


        for key, value in iter( self._value_dict.items() ):
            if value == None:
                del_list.append( key )
        for item in del_list:
            del self._value_dict[item]

        if len( self._value_dict ) == 0:
            self._value_error( 'Error adding styles, no styles found!' )

    def _local_parse_and_add( self, value ):
        self._value_dict.update( self._split_style( value ) )

    @property
    def get_dict( self ):
        if self.empty_attrib:
            return {}
        else:
            return {self.name:self._value_dict}

    @property
    def get_value_list( self ):
        if self.empty_attrib:
            return []
        else:
            return list( iter( self._value_dict.values() ) )

    @property
    def get_attrib( self ):
        if self.empty_attrib:
            return None
        else:
            return AttrClass( self.name, self._value_dict )



    def _split_style( self, styles ):
        tmp_ret_dict = {}
        tmp_list = []

        if isinstance( styles, dict ):
            return styles
        elif isinstance( styles, str ):
            tmp_list = styles.split( ';' )
        elif isinstance( styles, ( list, tuple ) ):
            tmp_list = styles

        tmp_attr_list = []

        for attr in tmp_list:
            attr = attr.strip()
            if len( attr ) > 1:
                if '=' in attr:
                    tmp_attr_list = attr.split( '=' )
                elif ':' in attr:
                    tmp_attr_list = attr.split( ':' )
                else:
                    tmp_attr_list = [attr, None]

                tmp_ret_dict[tmp_attr_list[0]] = tmp_attr_list[1]
        return tmp_ret_dict


    @property
    def _ret_value( self ):
        tmp_value_list = []
        for attrib, setting in iter( self._value_dict.items() ) :
            tmp_value_list.append( self._value_format.format( attrib = attrib, setting = setting ) )
        return ''.join( tmp_value_list )


    def remove( self, value = None ):
        '''
        will remove elements and return true to the parent object 
        if the entire object needs to be removed (for example, after 
        removing all items from the list, this is checked after calling

        '''

        if value:
            tmp_dict = self._split_style( value )

            for val in iter( tmp_dict.keys() ):

                try:
                    del self._value_dict[val]
                except KeyError:
                    pass

            if len( self ) == 0:
                return True
            else:
                return False
        else:
            self._value_dict = {}
            self._empty_attrib = True
            return True



    def __len__( self ):
        # handles getting the length
        return len( self._value_dict )

    def __contains__( self, item ):
        # handles checking for "in"
        if item == self.name:
            return True

        if item in self._value_dict:
            return True

        for value in iter( self._value_dict.values() ):
            if value == item:
                return True

        return False

#===============================================================================
# DATA ATTRIB CLASS
#===============================================================================

class DataAttrib( StyleAttrib ):
    default_match_name = 'data'
    _return_format = 'data-{attrib}="{value}"'
    attrib_match_names = ( 'data', )
    output_rank = 200
    output_rank_dict = {'data':200}

    def __init__( self, name = None, value = None ):

        if name:
            name = str( name )
            name = name.lower()
            if value:
                if name.startswith( 'data-' ):
                    value = {name[5:]:value}
                    name = 'data'

        super( DataAttrib, self ).__init__( name = name, value = value )


    def match_type( self, name, value ):
        '''
        This is looking specifically for "data-"
        '''


        name = str( name )
        name = name.lower()

        if name.startswith( 'data-' ):
            name = 'data',
            value = {name[5:]:value}

        return super( DataAttrib, self ).match_type( name, value )

    def _local_parse_and_add( self, value ):
        self._value_dict.update( self._find_data( value ) )



    def _find_data( self, value ):
        tmp_ret = {}

        if isinstance( value, dict ):
            return value

        if isinstance( value, str ):
            value = [value, ]

        if isinstance( value, ( list, tuple ) ):
            for v in value:
                if '=' in v:
                    tmp_attr_list = v.split( '=' )
                elif ':' in v:
                    tmp_attr_list = v.split( ':' )
                else:
                    tmp_attr_list = [v, None]

                tmp_attrib = tmp_attr_list[0]
                tmp_value = tmp_attr_list[1]

                tmp_attrib = tmp_attrib.replace( ' ', '-' )

                tmp_ret[tmp_attrib] = tmp_value

        return tmp_ret




    @property
    def _ret_value( self ):

        tmp_ret_list = []
        for attrib, value in iter( self._value_dict.items() ):
            if value:
                tmp_ret_list.append( self._return_format.format( attrib = attrib, value = value ) )

        return ' '.join( tmp_ret_list )

    def __str__( self ):
        return self._ret_value

    def remove( self, value = None ):
        # will return true to the parent object if the entire object needs to be removed (for example, after removing all items from the list, checked after calling

        if value:
            tmp_dict = self._find_data( value )

            for val in iter( tmp_dict.keys() ):
                try:
                    del self._value_dict[val]
                except KeyError:
                    pass

            if len( self ) == 0:
                return True
                self.empty_attrib = True
            else:
                return False

        else:
            self._value_dict = {}
            self._empty_attrib = True
            return True


#===============================================================================
# ALL ATTR LOOKUP CLASS
#===============================================================================

class AllAttrs( object ):

    def __init__( self ):
        self.attrs_dict = {}
        self.sort_order = []

    def _update_sort_order( self ):
        self.sort_order = sorted( iter( self.attrs_dict.values() ), key = itemgetter( 'order' ) )


    def __getitem__( self, key ):
        return self.attrs_dict[key]['obj']

    def __setitem__( self, key, value ):
        tmp_dict = {}
        tmp_dict['name'] = key
        tmp_dict['order'] = value.output_rank
        tmp_dict['obj'] = value
        self.attrs_dict[key] = tmp_dict

        self._update_sort_order()

    def __delitem__( self, key ):
        del self.attrs_dict[key]

        self._update_sort_order()

    def __iter__( self ):
        for item in self.sort_order:
            yield item['obj']

    def __contains__( self, item ):
        if item in self.attrs_dict:
            return True
        else:
            return False

    def __len__( self ):
        return len( self.attrs_dict )

    def __nonzero__( self ):
        if self.attrs_dict:
            return True
        else:
            return False

    def clear( self ):
        self.attrs_dict.clear()
        self.sort_order.clear()

    def get( self, *args ):
        tmp_ret = self.attrs_dict.get( *args )
        return tmp_ret['obj']

    def update( self, *args, **kwargs ):
        tmp_dict = {}
        tmp_dict.update( *args, **kwargs )
        for name, value in iter( tmp_dict.items() ):
            self[name] = value


#===============================================================================
# HTML ELEMENT Collection
#===============================================================================


class HTMLElementCollection( object ):

    _common_set = None


    def __init__( self ):
        self.element_set = {}


    def add( self, item, *args, **kwargs ):

        if isinstance( item, str ):
            item = [item, ]

        for field in item:
            try:
                self.element_set[field].add( *args, **kwargs )
            except KeyError:
                self.element_set[field] = HTMLElementHelper( *args, **kwargs )



    def __getitem__( self, key ):

        try:
            return self.element_set[key]
        except KeyError:
            return None


#===============================================================================
# HTML ATTRIBUTES CONTAINER CLASS
#===============================================================================


class HTMLElementHelper( object ):

    attrib_types = [
                    UniqueAttrib(),
                    BooleanAttrib(),
                    StyleAttrib(),
                    DataAttrib(),
                    ListAttrib(),
                    ]

    _copies = 0
    _parent = None
    _element = 'div'
    _closing_tag = True
    _make_id = False
    _child_id_suffix_format = '{parent_id}_{suffix}_{counter}'
    _child_id_suffix = 'child'


    def __init__( self, *args, **kwargs ):
        ''' 
            element
            parent
            make_id
            suffix
        
        '''
        self.attrib_recs_dict = AllAttrs()
        self.onetime_attrib_recs_dict = AllAttrs()
        self._children = []
        kwargs = self._grab_kwargs( kwargs )
        self.add( *args, **kwargs )


    def _parse_attributes( self, *args, **kwargs ):

        tmp_attr_list = []


        # when passed directly as kwargs
        tmp_name = kwargs.get( 'name' )
        tmp_value = kwargs.get( 'value' )
        if tmp_name:
            tmp_attr_list.append( AttrClass( tmp_name, tmp_value ) )

        # if only 2 arguments, and both are strings, we assume name, value
        if len( args ) == 2:
            if isinstance( args[0], str ) and isinstance( args[1], str ):
                return [ AttrClass( args[0], args[1] )]

        # if arguments, but not above, try these:
        for arg in args:

            # if it is a string, assume this is a name only item
            if isinstance( arg, str ):
                tmp_attr_list.append( AttrClass( arg, None ) )

            # if this is an instance of the HTML Helper
            if isinstance( arg, self.__class__ ):
                # iterate add the get_dict returns from each attrib class
                for attrib in arg:
                    tmp_attr_list.append( attrib.get_attrib )

            if isinstance( arg, AttrClass.__class__ ):
                tmp_attr_list.append( arg )

            # if it is a dictionary, simply add it
            if isinstance( arg, dict ):
                for name, value in iter( arg.items() ):
                    tmp_attr_list.append( AttrClass( name, value ) )


            # if it is a list, recursivly run this proc again.
            if isinstance( arg, ( list, tuple ) ):
                tmp_attr_list.extend( self._parse_attributes( arg ) )

            # if nothing else, assume it is a attrib class and try a get_dict
            try:
                tmp_attr_list.append( arg.get_attrib )
            except:
                pass

        return tmp_attr_list

    def _add_attribute( self, name, value = None , ot_dict = False ):
        if ot_dict:
            use_dict = self.onetime_attrib_recs_dict
        else:
            use_dict = self.attrib_recs_dict

        try:
            use_dict[name].add( value )
        except KeyError:
            for at_type in self.attrib_types:
                tmp_ret = at_type.match_type( name, value )
                if tmp_ret:
                    use_dict[name] = tmp_ret

    def _rem_attribute( self, name, value = None ):
        rem_object = False
        try:
            rem_object = self.attrib_recs_dict[name].remove( value )
        except KeyError:
            pass
        if rem_object:
            del self.attrib_recs_dict[name]

    def add_or_del_by_flag( self, flag, *args, **kwargs ):

        attrib_list = self._parse_attributes( *args, **kwargs )

        if flag:
            for item in attrib_list:
                self._add_attribute( item.name, item.value )

        else:
            for item in attrib_list:
                self._rem_attribute( item.name, item.value )



    def add( self, *args, **kwargs ):

        ot_dict = kwargs.pop( 'ot_dict', False )

        if not ot_dict:
            kwargs = self._grab_kwargs( kwargs )

        attrib_list = self._parse_attributes( *args, **kwargs )

        for item in attrib_list:
            if item.name == 'element':
                self._element = item.value
            else:
                self._add_attribute( item.name, item.value, ot_dict )



        if not ot_dict:
            self.update_parent()

    def get_list( self, *args ):
        tmp_resp = []
        if args:
            for attr in self:
                if attr.name in args:
                    tmp_resp.extend( attr.get_value_list )
        else:
            for attr in self:
                tmp_resp.extend( attr.get_value_list )

        return tmp_resp

    def get_dict( self, *args ):
        tmp_resp = {}
        if args:
            for attr in self:
                if attr.name in args:
                    tmp_resp.update( attr.get_dict )
        else:
            for attr in self:
                tmp_resp.update( attr.get_dict )

        return tmp_resp

    def _grab_kwargs( self, kwargs ):
        self._child_id_suffix = kwargs.pop( 'suffix', self._child_id_suffix )
        self._make_id = kwargs.pop( 'make_id', self._make_id )
        self._parent = kwargs.pop( 'parent', None )
        self._element = kwargs.pop( 'element', self._element )
        self._closing_tag = kwargs.pop( 'closing_tag', self._closing_tag )
        return kwargs

    def update_parent( self, **kwargs ):

        old_parent = kwargs.pop( 'old_parent', None )
        if kwargs:
            kwargs = self._grab_kwargs( kwargs )

        if self._parent:
            if self not in self._parent._children:
                self._parent._children.append( self )
            if self._make_id and not self.id and self._parent.id:
                tmp_cnt = len( self._parent._children ) + 1
                self['id'] = self._child_id_suffix_format.format( parent_id = self._parent.id,
                                                                 suffix = self._child_id_suffix,
                                                                 counter = tmp_cnt )
        else:
            if old_parent:
                try:
                    old_parent._children.remove( self )
                except:
                    pass



    def remove( self, *args, **kwargs ):
        tmp_parent = self._parent
        kwargs = self._grab_kwargs( kwargs )

        attrib_list = self._parse_attributes( *args, **kwargs )
        for item in attrib_list:
            self._rem_attribute( item.name, item.value )


        self.update_parent( old_parent = tmp_parent )

    def remove_all( self ):
        self.attrib_recs_dict.clear()


    @property
    def id( self ):
        try:
            return self.attrib_recs_dict['id'].value
        except KeyError:
            return None


    def opening_tag( self, **kwargs ):
        kwargs = self._grab_kwargs( kwargs )

        if self._closing_tag:
            opening_end = ''
        else:
            opening_end = '/'

        return '<{} {} {}>'.format( self._element, self.render(), opening_end )

    def closing_tag( self, **kwargs ):
        kwargs = self._grab_kwargs( kwargs )

        if self._closing_tag:
            return '</{}>'.format( self._element )
        else:
            return ''



    def render( self, *args, **kwargs ):
        tmp_name = kwargs.pop( 'render_attrib', None )
        tmp_list = []

        tmp_helper = None

        if args or kwargs:

            tmp_helper = HTMLElementHelper( self )
            tmp_helper.add( *args, **kwargs )


        else:
            tmp_helper = self  #  .attrib_recs_dict

        if tmp_name:
            return str( tmp_helper[tmp_name] )
        else:
            tmp_ret = ''
            for atr in tmp_helper.attrib_recs_dict:
                tmp_list.append( str( atr ) )
                tmp_ret = ' '.join( tmp_list )
            return tmp_ret



    def __getitem__( self, name ):
        return self.attrib_recs_dict[name]


    def __setitem__( self, name, value ):
        self.add( name = name, value = value )

    def __getattr__( self, name ):
        try:
            return self.__dict__['attrib_recs_dict'][name]
        except KeyError:
            msg = '(' + name + ') attribute not found!'
            raise AttributeError( msg )

    def get_attrs( self, name ):
        try:
            return self.attrib_recs_dict[name]._ret_value
        except KeyError:
            return ''


    def get( self, name ):
        try:
            tmp_dict = self.attrib_recs_dict
            return tmp_dict[name]
        except KeyError:
            return None


    def __iter__( self ):
        for attr in self.attrib_recs_dict:
            yield attr


    def __nonzero__( self ):
        if self.attrib_recs_dict:
            return True
        else:
            return False

    def __len__( self ):
        return len( self.attrib_recs_dict )

    '''
    def __repr__( self ):
        # handles returning what this should show
        return "%s ( %s )" % ( self.__class__.__name__, self.__str__ )
    '''
    def __contains__( self, *args, **kwargs ):
        tmp_attr = self._parse_attributes( *args, **kwargs )

        for item in tmp_attr:
            if item.value:
                try:
                    return item.value in self[item.name]
                except KeyError:
                    pass
            else:
                return item.name in self.attrib_recs_dict

        return False

    def __str__( self ):
        return self.render()


    def __delitem__( self, key ):
        self.remove( key )

    def __add__( self, other ):
        tmp_ret = HTMLElementHelper( self )
        tmp_ret.add( other )
        return tmp_ret



    def _value_error( self, msg = '' ):
        base_msg = 'HTML Attrib Validation Error:'
        if not msg:
            msg = base_msg + ' (Name: {name}  Value: {value})'
        else:
            msg = base_msg + msg

        raise ValueError( msg.format( name = self.name, value = self.value ) )

#===============================================================================
# UTILITY FUNCTIONS
#===============================================================================

def combine_strings( *args, **kwargs ):
    end = kwargs.get( 'end', '' )
    sep = kwargs.get( 'sep', '' )
    tmp_list = []

    for s in args:
        tmp_str = str( s )
        tmp_list.append( tmp_str )
    tmp_list.append( end )
    return sep.join( tmp_list )

