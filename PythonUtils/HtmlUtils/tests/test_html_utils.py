'''
Created on Aug 18, 2014

@author: strohl
'''
import copy
from helper_utils import html_utils
import unittest

ip = html_utils.ip


class Test_HTML_Element_helper( unittest.TestCase ):

    ''' Test of adding data '''

    def setUp( self ):
        self.heh = html_utils.HTMLElementHelper()


    def test_add_params( self ):

        # ip.lp( '#[color:cyan]#', 'this is a test', '#[color]#', ' of the broadcast system' )

        self.heh.add( 'class', 'collapse' )
        self.assertEqual( self.heh.render(), 'class="collapse"' )
        self.heh.add( 'TEST', 'response' )
        self.assertEqual( self.heh.render( render_attrib = 'class' ), 'class="collapse"' )


    def test_add_dict( self ):
        self.heh.add( {'class':'collapse'} )
        self.assertEqual( self.heh.render(), 'class="collapse"' )


    def test_add_html_element( self ):
        heh2 = html_utils.HTMLElementHelper( 'test', 'test_attr' )

        self.heh.add( {'class':'collapse2'} )
        self.heh.add( heh2 )

        self.assertEqual( self.heh.render(), 'class="collapse2" test="test_attr"' )

    def test_set_dict( self ):
        self.heh['class'] = 'collapse5'
        self.heh.add( {'class':'collapse5'} )


    def test_setattr( self ):
        self.heh._class = 'collapse3'
        self.heh.add( {'class':'collapse3'} )

    def test_add_attrib_class( self ):
        attrib = html_utils.UniqueAttrib( 'test2', 'test_attr2' )

        self.heh.add( {'class':'collapse4'} )
        self.heh.add( attrib )

        self.assertEqual( self.heh.render(), 'class="collapse4" test2="test_attr2"' )


    ''' Test of removing data '''

    def test_remove_params( self ):
        self.heh.add( {'class':'collapse another_collapse', 'TEST':'response'} )
        self.assertEqual( len( self.heh ), 2 )
        self.heh.remove( 'class', 'another_collapse' )
        self.assertEqual( len( self.heh ), 2 )
        self.heh.remove( 'TEST', 'response' )
        self.assertEqual( len( self.heh ), 1 )
        self.heh.remove( 'class', 'collapse' )
        self.assertEqual( len( self.heh ), 0 )
        self.heh.add( {'class':'collapse another_collapse', 'TEST':'response'} )
        self.assertEqual( len( self.heh ), 2 )
        self.heh.remove( 'class' )
        self.assertEqual( len( self.heh ), 1 )
        self.heh.add( {'class':'collapse another_collapse', 'TEST':'response'} )
        self.assertEqual( len( self.heh ), 2 )
        self.heh.remove_all()
        self.assertEqual( len( self.heh ), 0 )


    def test_remove_dict( self ):
        self.heh.add( {'class':'collapse another_collapse', 'TEST':'response'} )
        self.assertEqual( len( self.heh ), 2 )
        del self.heh['TEST']
        self.assertEqual( len( self.heh ), 1 )



    def test_remove_html_element( self ):
        heh2 = html_utils.HTMLElementHelper( 'test6', 'test_attr6' )

        self.heh.add( {'class':'collapse6', 'test6':'test_attr6'} )
        self.heh.remove( heh2 )

        self.assertEqual( self.heh.render(), 'class="collapse6"' )

    '''
    def test_delattr( self ):
        self.heh.add( {'class':'collapse8', 'test8':'test_attr8'} )
        self.heh.test8 = None

        self.assertEqual( self.heh.render(), 'class="collapse8"' )
    '''

    def test_remove_attrib_class( self ):
        attrib = html_utils.UniqueAttrib( 'test7', 'test_attr7' )

        self.heh.add( {'class':'collapse7', 'test7':'test_attr7'} )
        self.heh.remove( attrib )

        self.assertEqual( self.heh.render(), 'class="collapse7"' )

    ''' tests of getting data '''


    def test_get_attr( self ):



        self.heh.add( {'class':'collapse9', 'test9':'test_attr9'} )
        self.assertEqual( self.heh.get_list( 'class' ), ['collapse9'] )

    def test_get_dict( self ):
        self.heh.add( {'class':'collapse10', 'test11':'test_attr11'} )
        self.assertEqual( self.heh['class']._value_list, ['collapse10'] )

    def test_iter( self ):
        self.heh.add( {'class':'collapse10', 'test11':'test_attr11', 'id':'newstuff'} )
        i = 0
        for h in self.heh:
            i += 1
        self.assertEqual( i, 3 )


    ''' tests of ID management '''

    def test_id_from_parent( self ):
        heh2 = html_utils.HTMLElementHelper( {'test6':'test_attr6', 'id':'parent_heh'} )

        self.heh.add( {'class':'collapse6', 'test6':'test_attr6'} )
        self.heh.update_parent( parent = heh2, suffix = 'child' , make_id = True )

        self.assertEqual( self.heh.render( render_attrib = 'id' ), 'id="parent_heh_child_2"' )

    '''
    def test_deepcopy( self ):
        self.heh.add( {'class':'collapse6', 'test6':'test_attr6', 'id':'heh_id'} )
        heh2 = copy.deepcopy( self.heh )
        self.assertEqual( heh2.render( 'id' ), 'id="heh_id_new"' )
    '''

    ''' tests of comparisons '''

    def test_contains( self ):
        self.heh.add( {'class':'collapse12', 'test12':'test_attr12', 'id':'heh_id3'} )
        test_resp = 'class' in self.heh
        self.assertEqual( test_resp, True )

        test_resp = 'junk' in self.heh
        self.assertEqual( test_resp, False )

        test_resp = {'test12':'test_attr12'} in self.heh
        self.assertEqual( test_resp, True )

    def test_non_zero( self ):
        resp_flag = False
        self.heh.add( {'class':'collapse12', 'test12':'test_attr12', 'id':'heh_id3'} )

        if self.heh:
            resp_flag = True
        self.assertEqual( resp_flag, True )

        resp_flag = False

        self.heh.remove_all()

        if not self.heh:
            resp_flag = True

        self.assertEqual( resp_flag, True )


    ''' tests of rendering '''

    def test_str( self ):


        self.heh.add( {'class':'collapse12', 'checked':'checked', 'id':'heh_id3'} )
        tmp_resp = str( self.heh )
        tmp_compare = 'id="heh_id3" class="collapse12" checked'
        self.assertEqual( tmp_resp, tmp_compare )


    def test_render( self ):
        self.heh.add( {'class':'collapse12', 'checked':'checked', 'id':'heh_id3'} )
        tmp_compare = 'id="heh_id3" class="collapse12" checked'
        self.assertEqual( self.heh.render(), tmp_compare )

    def test_render_with_onetime( self ):
        self.heh.add( {'class':'collapse12', 'checked':'checked', 'id':'heh_id3'} )
        tmp_compare_with_add = 'id="heh_onetime" class="collapse12 onetime_ADD" style="border:none;" checked data-test="test data"'
        onetime_add = {'id':'heh_onetime', 'class':'onetime_ADD', 'style':"border:none;", 'data':{'test':"test data"}}
        tmp_compare = 'id="heh_id3" class="collapse12" checked'
        self.assertEqual( self.heh.render( onetime_add ), tmp_compare_with_add )
        self.assertEqual( self.heh.render(), tmp_compare )



    def test_tags( self ):
        self.heh.add( {'class':'collapse12', 'checked':'checked', 'id':'heh_id3'} )
        self.heh.element = 'div'
        tmp_compare = '<div id="heh_id3" class="collapse12" checked >'
        self.assertEqual( self.heh.opening_tag(), tmp_compare )

        self.assertEqual( self.heh.closing_tag(), '</div>' )



    '''
    def test_wrap( self ):
        self.heh.add( {'class':'collapse12', 'checked':'checked', 'id':'heh_id3'} )
        self.heh.element = 'div'
        tmp_compare = '<div class="collapse12" checked id="heh_id2">This is a test</div>'
        self.assertEqual( self.heh.wrap( 'This is a test' ), tmp_compare )

    def test_wrap_children( self ):

        heh2 = html_utils.HTMLElementHelper( {'test6':'test_attr6', 'id':'parent_heh'}, element = 'div' )
        self.heh.add( {'class':'collapse6', 'test6':'test_attr6'}, element = 'span', parent = heh2, make_id = True )

        self.assertEqual( self.heh.render( 'id' ), 'id="parent_heh_child"' )

        tmp_compare = '<div test6="test_attr6" id="parent_heh"><span id="parent_heh_child" class="collapse6" test6="test_attr6">This is a test</span></div>'
        self.assertEqual( self.heh.wrap( 'This is a test', children = True ), tmp_compare )
    '''

class Test_UniqueAttrib( unittest.TestCase ):

    def test_match( self ):
        tst = None
        tst_match = html_utils.UniqueAttrib()
        tst = tst_match.match_type( 'ID', 'TEST' )
        self.assertEqual( tst.render(), 'id="TEST"' )

        tst2 = tst_match.match_type( 'class', 'TEST' )
        self.assertEqual( tst2, None )


    def test_init( self ):
        tst = None
        tst = html_utils.UniqueAttrib( 'ID', 'TEST' )
        self.assertEqual( tst.render(), 'id="TEST"' )

    def test_str( self ):
        tst = None
        tst = html_utils.UniqueAttrib( 'ID', 'TEST' )
        self.assertEqual( str( tst ), 'id="TEST"' )

    def test_add( self ):
        tst = None
        tst = html_utils.UniqueAttrib( 'ID', 'TEST' )
        tst.add( 'test2' )
        self.assertEqual( tst.render(), 'id="test2"' )

    def test_remove( self ):
        tst = None
        tst = html_utils.UniqueAttrib( 'ID', 'TEST' )
        tst_rest = tst.remove( 'test2' )
        self.assertEqual( tst_rest, True )

    def test_contains( self ):
        tst = None
        tst = html_utils.UniqueAttrib( 'ID', 'TEST' )
        tst_rest = 'test2' in tst
        self.assertEqual( tst_rest, False )

        tst_rest = 'TEST' in tst
        self.assertEqual( tst_rest, True )



class Test_BooleanAttrib( unittest.TestCase ):

    def test_match( self ):
        tst = None
        tst_match = html_utils.BooleanAttrib()
        tst = tst_match.match_type( 'Checked', 'Checked' )
        self.assertEqual( tst.render(), 'checked' )

        tst2 = tst_match.match_type( 'ID', 'TEST' )
        self.assertEqual( tst2, None )


    def test_init( self ):
        tst = None
        tst = html_utils.BooleanAttrib( 'TEST', True )
        self.assertEqual( tst.render(), 'test' )

    def test_str( self ):
        tst = None
        tst = html_utils.BooleanAttrib( 'TEST', 'true' )
        self.assertEqual( str( tst ), 'test' )

    def test_add( self ):
        tst = None
        tst = html_utils.BooleanAttrib( 'test', True )
        tst.add( False )
        self.assertEqual( tst.render(), '' )

    def test_remove( self ):
        tst = None
        tst = html_utils.BooleanAttrib( 'TEST', 'TEST' )
        tst_rest = tst.remove( 'TEST' )
        self.assertEqual( tst_rest, True )

    def test_contains( self ):
        tst = None
        tst = html_utils.BooleanAttrib( 'TEST', '' )
        tst_rest = 'test2' in tst
        self.assertEqual( tst_rest, False )

        tst_rest = 'test' in tst
        self.assertEqual( tst_rest, True )



class Test_ListAttrib( unittest.TestCase ):

    def test_match( self ):
        tst = None
        tst_match = html_utils.ListAttrib()
        tst = tst_match.match_type( 'class', 'collapse' )
        self.assertEqual( tst.render(), 'class="collapse"' )

        tst2 = tst_match.match_type( 'ID', 'TEST' )
        self.assertEqual( tst2, None )


    def test_init( self ):
        tst = None
        tst = html_utils.ListAttrib( 'class', 'collapse' )
        self.assertEqual( tst.render(), 'class="collapse"' )

    def test_str( self ):
        tst = None
        tst = html_utils.ListAttrib( 'class', 'collapse' )
        self.assertEqual( str( tst ), 'class="collapse"' )

    def test_add( self ):
        tst = None
        tst = html_utils.ListAttrib( 'class', 'collapse' )
        tst.add( 'row_test' )
        self.assertIn( 'collapse', tst.render() )
        self.assertIn( 'row_test', tst.render() )

    def test_remove( self ):
        tst = None
        tst = html_utils.ListAttrib( 'class', 'collapse row_test col_test' )
        tst_rest = tst.remove( 'row_test' )
        self.assertEqual( tst_rest, False )

        self.assertIn( 'collapse', tst.render() )
        self.assertIn( 'col_test', tst.render() )

        tst_rest = tst.remove( 'col_test' )
        self.assertEqual( tst_rest, False )

        self.assertEqual( tst.render(), 'class="collapse"' )
        tst_rest = tst.remove( 'collapse' )
        self.assertEqual( tst_rest, True )


    def test_contains( self ):
        tst = None
        tst = html_utils.ListAttrib( 'class', 'collapse row_test col_test' )
        tst_rest = 'row_test' in tst
        self.assertEqual( tst_rest, True )

        tst_rest = 'row_not_in_test' in tst
        self.assertEqual( tst_rest, False )


class Test_StyleAttrib( unittest.TestCase ):

    test_name = 'style'
    test_value1 = 'border-top:100px'
    test_value2 = 'border-top:100px;width:10%;'
    test_value3 = 'width=10%;'
    test_value4 = 'width=200px'

    test_resp1 = 'style="border-top:100px;"'
    test_resp2 = 'style="border-top:100px;width:10%;"'

    def test_match( self ):
        tst = None
        tst_match = html_utils.StyleAttrib()
        tst = tst_match.match_type( self.test_name, self.test_value1 )
        self.assertEqual( tst.render(), self.test_resp1 )

        tst2 = tst_match.match_type( 'ID', 'TEST' )
        self.assertEqual( tst2, None )


    def test_init( self ):
        tst = None
        tst = html_utils.StyleAttrib( self.test_name, self.test_value1 )
        self.assertEqual( tst.render(), self.test_resp1 )

    def test_str( self ):
        tst = None
        tst = html_utils.StyleAttrib( self.test_name, self.test_value1 )
        self.assertEqual( str( tst ), self.test_resp1 )

    def test_add( self ):
        tst = None
        tst = html_utils.StyleAttrib( self.test_name, self.test_value1 )
        tst.add( self.test_value3 )
        self.assertIn( 'width:10%', tst.render() )
        self.assertIn( 'border-top:100px', tst.render() )

        tst.add( self.test_value4 )
        self.assertIn( 'width:200px', tst.render() )
        self.assertNotIn( 'width:10%', tst.render() )



    def test_remove( self ):
        tst = None
        tst = html_utils.StyleAttrib( self.test_name, self.test_value2 )
        tst_rest = tst.remove( self.test_value3 )
        self.assertEqual( tst_rest, False )
        self.assertEqual( tst.render(), self.test_resp1 )

        tst_rest = tst.remove( self.test_value1 )
        self.assertEqual( tst_rest, True )


    def test_contains( self ):
        tst = None
        tst = html_utils.StyleAttrib( self.test_name, self.test_value2 )
        tst_rest = 'width' in tst
        self.assertEqual( tst_rest, True )

        tst_rest = 'row_not_in_test' in tst
        self.assertEqual( tst_rest, False )


class Test_DataAttrib( unittest.TestCase ):

    def test_match( self ):
        tst = None
        tst_match = html_utils.DataAttrib()
        tst = tst_match.match_type( 'data', 'test:testdata' )
        self.assertEqual( tst.render(), 'data-test="testdata"' )

        tst2 = tst_match.match_type( 'ID', 'TEST' )
        self.assertEqual( tst2, None )


    def test_init( self ):
        tst = None
        tst = html_utils.DataAttrib( 'data-test', 'testdata' )
        self.assertEqual( tst.render(), 'data-test="testdata"' )

    def test_str( self ):
        tst = None
        tst = html_utils.DataAttrib( 'data', 'test=testdata' )
        self.assertEqual( str( tst ), 'data-test="testdata"' )

    def test_add( self ):
        tst = None
        tst = html_utils.DataAttrib( 'data', 'test:testdata' )
        tst.add( 'another-test:moredata' )
        tst_resp = tst.render()
        self.assertIn( 'data-test="testdata"', tst_resp )
        self.assertIn( 'data-another-test="moredata"' , tst_resp )

        tst.add( ['more-test:more data to test', 'still another test=still more data to test'] )
        tst_resp = tst.render()
        self.assertIn( 'data-test="testdata"', tst_resp )
        self.assertIn( 'data-another-test="moredata"', tst_resp )
        self.assertIn( 'data-more-test="more data to test"', tst_resp )
        self.assertIn( 'data-still-another-test="still more data to test"', tst_resp )

        tst_resp = tst.remove()
        self.assertEqual( tst.render(), '' )
        self.assertEqual( tst_resp, True )

    def test_add_dict( self ):
        tst = None
        tst = html_utils.DataAttrib( 'data', 'test=testdata' )
        tst_add_dict = {'test_number':12, 'test-other-data':'other data sets'}
        tst.add( tst_add_dict )

        tst_resp = str( tst )

        self.assertIn( 'data-test="testdata"', tst_resp )
        self.assertIn( 'data-test_number="12"', tst_resp )
        self.assertIn( 'data-test-other-data="other data sets"', tst_resp )


    def test_remove( self ):
        tst = None
        tst = html_utils.DataAttrib( 'data', ['test:testdata', 'another-test-row:anothertest'] )
        tst_rest = tst.remove( 'another-test-row' )
        self.assertEqual( tst_rest, False )
        self.assertEqual( tst.render(), 'data-test="testdata"' )

        tst_rest = tst.remove( 'test' )
        self.assertEqual( tst_rest, True )


    def test_contains( self ):
        tst = None
        tst = html_utils.DataAttrib( 'data', ( 'test:testdata', 'another-test-row:anothertest' ) )
        tst_rest = 'testdata' in tst
        self.assertEqual( tst_rest, True )

        tst_rest = 'another-test-row' in tst
        self.assertEqual( tst_rest, True )

        tst_rest = 'row_not_in_test' in tst
        self.assertEqual( tst_rest, False )



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
