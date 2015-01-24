'''
Created on Jun 18, 2014

@author: strohl
'''
import unittest
from common.tree_utils import TreeDict

TEST_TREE_1 = [
               {'key': 'one',
                'parent': '',
                'children': [],
                'name': 'name-one',
                'lname': 'lanem-one',
                'sal': 'sal-one'},


                 {'key': 'two',
                'parent': '',
                'children': [],
                'name': 'name-two',
                'lname': 'lanem-two',
                'sal': 'sal-two'},

               {'key': 'three',
                'parent': 'one',
                'children': [],
                'name': 'name-three',
                'lname': 'lanem-three',
                'sal': 'sal-three'},

                 {'key': 'four',
                'parent': 'two',
                'children': [],
                'name': 'name-four',
                'lname': 'lanem-four',
                'sal': 'sal-four'},


                 {'key': 'five',
                'parent': 'three',
                'children': [],
                'name': 'name-five',
                'lname': 'lanem-five',
                'sal': 'sal-five'},

               ]

def setup_tree( width, depth ):

    parent_string = ''
    tmp_tree = []

    for i in range( width ):
        tmp_node = {'key':str( i ),
                    'parent' : '',
                    'children' : [],
                    'other1' : 'test other item {}'.format( i )
                    }
        tmp_tree.append( tmp_node )
    return tmp_tree



class Test( unittest.TestCase ):


    def testSimpleLoad( self ):
        # test_list = setup_tree( 2, 0 )
        test_list = TEST_TREE_1
        test_tree = TreeDict( test_list )
        test_return = test_tree.get_dict_no_key()
        print( test_return )




if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
