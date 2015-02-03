'''
Created on Aug 16, 2014

@author: Dan Strohl
'''
import unittest
from PythonUtils.IndentedPrint.indented_print import IndentedPrinter, IndentedPrintHelper, Colorizer

class Test(unittest.TestCase):





    def test_colorizer(self):
        c = Colorizer()
        c['test_preset'] = 'bold'
        t1 = c('underline red on_white')+'RED'+c()
        t2 = c['test_preset']+'BOLD'+c()+' NOT BOLD'
        print(t2)


    def test_ip_helper(self):
        iph = IndentedPrintHelper()

        self.assertEqual(iph.crlf, '\n')
        self.assertEqual(iph.f(), 'test_ip_helper')

        self.assertEqual(iph('this is a test{crlf}'), 'this is a test\n')
        self.assertEqual(iph('this is a test {counter()}'), 'this is a test 1')
        self.assertEqual(iph('this is a test {counter}'), 'this is a test 2')


    """
    def test_init( self ):

        IP = IndentedPrint( indent_spaces = 5, silence = True, inc_stack = True, stack_format = '{stack}', stack_length_limits = {'test':12} )
        self.assertEqual( IP.indent_spaces, 5 )
        self.assertEqual( IP.silence, True )
        self.assertEqual( IP.inc_stack, True )
        self.assertEqual( IP.stack_format, '{stack}' )
        self.assertEqual( IP.stack_length_limits, {'test':12} )

    def test_i( self ):
        IP = IndentedPrint()
        IP.i( 10 )
        self.assertEqual( IP.current_indent, 10 )

    def test_a( self ):
        IP = IndentedPrint()
        IP.a()
        self.assertEqual( IP.current_indent, 1 )
        IP.a( 1 ).a( 1 )
        self.assertEqual( IP.current_indent, 3 )
        IP.a( 10 )
        self.assertEqual( IP.current_indent, 13 )



    def test_s( self ):
        IP = IndentedPrint()
        IP.s( 2 )
        self.assertEqual( IP.current_indent, 0 )
        IP.a( 10 ).s( 5 )
        self.assertEqual( IP.current_indent, 5 )


    def test_call(self):
        IP = IndentedPrint()

        IP.p('this is the initial line')
        self.assertEqual( IP.current_indent, 0)
        IP('this is a test', pre_indent=5, post_outdent=5)
        self.assertEqual( IP.current_indent, 0)
        IP.p('this is the final line')




    def test_ms( self ):
        IP = IndentedPrint()
        IP.ms( indent = 30 )
        self.assertEqual( IP.current_indent, 0 )


        IP.i( 10 )
        IP.mr()

        self.assertEqual( IP.current_indent, 30 )

        IP.i( 10 )
        IP.ms( 'test' )
        self.assertEqual( IP.current_indent, 10 )



        IP.a( 5 )
        self.assertEqual( IP.current_indent, 15 )

        IP.mr( 'test' )
        self.assertEqual( IP.current_indent, 10 )

        IP.push()

        pass


    def test_stack( self ):
        IP = IndentedPrint( inc_stack = True )
        IP.i( 2 )
        IP.ca()
        IP.ca( 3, 'test_key' )
        IP.sep().pl( '#[]#', ' this is a test ', '#[test_key]#' ).sep().nl( 3 )

    """

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()



