'''
Created on Aug 16, 2014

@author: strohl
'''
import unittest
from helper_utils.list2 import list2


class TestList2( unittest.TestCase ):


    def test_list_2_basic_list( self ):
        l = list2()
        l.append( 'test' )
        self.assertEqual( l, ['test'] )

    def test_list_2_add( self ):
        l = list2()
        l.append( 'test' )

        l.add( 1, 'test_2' )
        self.assertEqual( l, ['test', 'test_2'] )

        l.add( 1, 'test_3' )
        self.assertEqual( l, ['test', 'test_3', 'test_2'] )

        l.add( 4, 'test_4' )
        self.assertEqual( l, ['test', 'test_3', 'test_2', '', 'test_4'] )

        l.add( 6, 'test_5', new_items = 'test_new' )
        self.assertEqual( l, ['test', 'test_3', 'test_2', '', 'test_4', 'test_new', 'test_5'] )



    def test_list2_update( self ):
        l = list2()
        l.append( 'test' )

        l.update( 1, 'test_2' )
        self.assertEqual( l, ['test', 'test_2'] )

        l.update( 1, 'test_3' )
        self.assertEqual( l, ['test', 'test_3'] )

        l.update( 4, 'test_4' )
        self.assertEqual( l, ['test', 'test_3', '', '', 'test_4'] )

        l.update( 6, 'test_5', new_items = 'test_new' )
        self.assertEqual( l, ['test', 'test_3', '', '', 'test_4', 'test_new', 'test_5'] )


    def test_list2_get( self ):
        l = list2()
        l.append( 'test' )
        l.add( 1, 'test_2' )

        tmp_ret = l.get( 1 )
        self.assertEqual( tmp_ret, 'test_2' )

        tmp_ret = l.get( 4 )
        self.assertEqual( tmp_ret, None )

        tmp_ret = l.get( 4 , default = 'test_3' )
        self.assertEqual( tmp_ret, 'test_3' )


    '''
    def test_list2_indexed( self ):
        l = list2( ['test_1', 'test_2', 'test_3'] )
        l[4] = 'test_4'
        self.assertEqual( l, ['test', 'test_3', '', '', 'test_4'] )
    '''



    '''
    def test_list2_update_external_funct( self ):
        l = list2( funct = test_list_update )

        l.append( 1 )
        l.add( 0, 1 )
        self.assertEqual( l, [1, 1] )

        l.update( 0, 2 )
        self.assertEqual( l, [3, 1] )

        # l[0] = 3
        # self.assertEqual( l, [6, 1] )
    '''

    def test_list2_update_override_internal_funct( self ):
        l = list3()

        l.append( 5 )
        l.add( 0, 5 )
        self.assertEqual( l, [5, 5] )

        l.update( 0, 2 )
        self.assertEqual( l, [3, 5] )

        # l[0] = 4
        # self.assertEqual( l, [-1, 5] )

    '''
    def test_list2_update_external_cl_pass_funct( self ):
        l = list2()

        l.append( 1 )
        l.add( 0, 1 )
        self.assertEqual( l, [1, 1] )

        l.update( 0, 2 )
        self.assertEqual( l, [2, 1] )

        # l[0] = 3
        # self.assertEqual( l, [3, 1] )

        l.update( 0, 2, funct = test_list_update )
        self.assertEqual( l, [4, 1] )
    '''




def test_list_update( old, new ):
    return old + new

class list3( list2 ):
    def _update_function( self, old, new ):
        # print( old, '-', new, '=', old - new )
        return old - new


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
