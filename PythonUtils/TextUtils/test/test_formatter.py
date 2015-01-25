'''
Created on Aug 10, 2014

@author: strohl
'''
import unittest

from PythonUtils.TextUtils.formatter import find_enclosed, IntelligentFormat, FormatField, FormatTest

class TestTestFormatter( unittest.TestCase ):

    def test_format_test( self ):
        t = FormatTest()

        f = t.format( '{test!s:.^25}', test = 'testing' )
        print( f )


class TestFieldHandler( unittest.TestCase ):

    ff = None
    fields = []
    field_instrings = []

    default_dict = {
                    'max_length': None,
                    'min_length': 10,
                    'do_not_show_length': 4,
                    'pad_to_max': False,
                    'justification':'left',
                    'end_string': '',
                    'padding_string': ' ',
                    'trim_string': '+',
                    'trim_priority': 1, }


    def load_data( self,
                       counter = 0,
                       init_size = 40,
                       format_string = None,
                       field_def = {},
                       ):



        name = 'name_{}'.format( counter )
        if not format_string:
            format_string = '{' + name + '}'
        in_string = 'name_'.ljust( init_size, '*' )
        # print( 'in_string:', in_string )
        # print( 'in_size:', init_size )

        self.ff = FormatField( 
                         name,
                         format_string,
                         field_def,
                         initial_string = in_string
                         )


    def test_formatfield_full( self ):
        self.load_data( 1 )

        self.assertEqual( self.ff.length_ok, True )
        self.assertEqual( self.ff.curr_length, 40 )


    def test_formatfield_20( self ):
        self.load_data( 1 )
        self.ff.max_length( 20 )
        self.assertEqual( self.ff.length_ok, False )

    def test_formatfield_mt( self ):
        self.load_data( 1 )
        self.ff._trim_me()
        self.assertEqual( self.ff.length_ok, True )
        self.assertEqual( self.ff.curr_length, 40 )


    def test_formatfield_15( self ):
        self.load_data( 1 )
        self.ff._trim_me( 15 )
        self.assertEqual( self.ff.curr_length, 15 )


    def test_formatfield_7( self ):
        self.load_data( 1 )
        self.ff._trim_me( 7, True )
        self.assertEqual( self.ff.curr_length, 7 )

    def test_formatfield_2( self ):
        self.load_data( 1 )
        self.ff._trim_me( 2 )
        self.assertEqual( self.ff.curr_length, 10 )

    def test_formatfield_2_ignore_min( self ):
        self.load_data( 1 )
        self.ff._trim_me( 2 , True )
        self.assertEqual( self.ff.curr_length, 0 )


    def test_formatfield_pad_none( self ):
        self.load_data( 1, 12 )
        self.ff._pad_me()
        self.assertEqual( self.ff.curr_length, 12 )

    def test_formatfield_pad_to_max_no_max( self ):
        self.load_data( 1, 12 )
        self.ff.pad_to_max = True
        self.ff._pad_me()
        self.assertEqual( self.ff.curr_length, 12 )

    def test_formatfield_pad_to_max_max_40( self ):
        self.load_data( 1, 12 )
        self.ff.pad_to_max = True
        self.ff.max_length( 40 )
        self.ff.padding_string = '.'
        self.ff._pad_me()
        # print( self.ff )
        self.assertEqual( self.ff.curr_length, 40 )
        self.assertEqual( self.ff.current_string, 'name_******* ...........................' )

    def test_formatfield_pad_to_max_left( self ):
        self.load_data( 1, 12 )
        self.ff.pad_to_max = True
        self.ff.max_length( 40 )
        self.ff.padding_string = '.'
        self.ff.justification = 'left'
        self.ff._pad_me()
        # print( self.ff )
        self.assertEqual( self.ff.curr_length, 40 )
        self.assertEqual( self.ff.current_string, 'name_******* ...........................' )

    def test_formatfield_pad_to_max_right( self ):
        self.load_data( 1, 12 )
        self.ff.pad_to_max = True
        self.ff.max_length( 40 )
        self.ff.padding_string = '.'
        self.ff.justification = 'right'
        self.ff._pad_me()
        # print( self.ff )
        self.assertEqual( self.ff.curr_length, 40 )
        self.assertEqual( self.ff.current_string, '........................... name_*******' )

    def test_formatfield_pad_to_max_center( self ):
        self.load_data( 1, 12 )
        self.ff.pad_to_max = True
        self.ff.max_length( 40 )
        self.ff.padding_string = '.'
        self.ff.justification = 'center'
        self.ff._pad_me()
        # print( self.ff )
        self.assertEqual( self.ff.curr_length, 40 )
        self.assertEqual( self.ff.current_string, '............. name_******* .............' )


class TestIntelFormat( unittest.TestCase ):

    limits_dict = {
                   '__full_str__':{'max_length':50, 'pax_to_max':True},
                   'f1':{'max_length': 38},
                   'f2':{'min_length':10,
                         'trim_priority':2},
                   'f3':{'max_length':10,
                         'trim_priority':0},
                   'f4':{'min_length':3},
                   }

    data_dict = {
                 'f1':'This is a test of the max length field*********',
                 'f2':'This is 10*******',
                 'f3':12345,
                 'f4':'Hi!************',
                 'f5':'More Text',
                 'f6':'and still more text that is not in the template'
                 }

    format_str = '{f1}<--->{f2}<->{f3}{f4}'


    intel_format = None

    def test_find_enclosed( self ):

        test_list = [
                     {'args':( '[this] is a test', '[', ']' ),
                      'kwargs':{},
                      'return':['this']
                      },
                     {'args':( 'this [is] a test', '[', ']' ),
                      'kwargs':{},
                      'return':['is']
                      },

                     {'args':( '[this] is [a] test', '[', ']' ),
                      'kwargs':{},
                      'return':['this', 'a']
                      },

                     {'args':( 'this [is] a [test]', '[', ']' ),
                      'kwargs':{},
                      'return':['is', 'test']
                      },

                     {'args':( 'this is [a test', '[', ']' ),
                      'kwargs':{},
                      'return':[]
                      },

                     {'args':( 'this is a] test', '[', ']' ),
                      'kwargs':{},
                      'return':[]
                      },

                     {'args':( 'this [is] [a] [test]', '[', ']' ),
                      'kwargs':{'include_all':False},
                      'return':'is'
                      },

                     {'args':( 'this is a] test', '[', ']' ),
                      'kwargs':{'include_all':False},
                      'return':''
                      },

                     {'args':( 'this is a] test', '[', ']' ),
                      'kwargs':{'default':'rat bastard'},
                      'return':['rat bastard']
                      },

                     {'args':( 'this is a] test', '[', ']' ),
                      'kwargs':{'default':'junk', 'include_all':False},
                      'return':'junk'
                      },
                     {'args':( 'this is [a |test]', '[', ']' ),
                      'kwargs':{'ignore_after':'|'},
                      'return':['a ']
                      },
                     ]

    def run_find_enclosed_test( self, test_def ):

        test_ret = find_enclosed( *test_def['args'], **test_def['kwargs'] )
        self.assertEqual( test_ret, test_def['return'] )

    def setup_intel_format( self ):


        self.intel_format = IntelligentFormat( self.limits_dict, self.format_str )


        '''
    def test_verify_fields( self ):
        self.setup_intel_format()

        self.assertEqual( self.intel_format.full_fields_list ,
                         ['f1', 'f2', 'f3', 'f4'] )

        self.assertEqual( len( self.intel_format.fields_def_dict ) , 4 )


        self.assertEqual( self.intel_format.priority_list  ,
                         [['f3'], ['f1', 'f4'], ['f2']] )

        self.assertEqual( self.intel_format.template_overhead , 8 )



    def test_check_formatted( self ):
        self.setup_intel_format()
        self.intel_format.fields_dict = self.data_dict

        tmp_ret = self.intel_format._check_formatted()

        self.assertTrue( tmp_ret )
        self.assertEqual( self.intel_format.formatted_str, 'This is a test of the max length field*********<--->This is 10*******<->12345Hi!************' )
        self.assertEqual( self.intel_format.formatted_str_len, 92 )

        self.intel_format.full_string_limits['max_length'] = 20
        tmp_ret = self.intel_format._check_formatted()

        self.assertFalse( tmp_ret )


    def test_get_field_nums( self ):
        pass

        '''



