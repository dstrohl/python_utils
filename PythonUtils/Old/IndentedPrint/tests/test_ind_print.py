'''
Created on Aug 16, 2014

@author: Dan Strohl
'''
import unittest
import logging
from PythonUtils.Old.IndentedPrint.indented_print import IndentedPrinter, IndentedPrintHelper


class TestHelpers(unittest.TestCase):

    iph = IndentedPrintHelper()

    '''
    def test_colorizer(self):
        c = Colorizer()
        c['test_preset'] = 'bold'
        t1 = c('underline red on_white')+'RED'+c()
        t2 = c['test_preset']+'BOLD'+c()+' NOT BOLD'

        self.assertEqual(t1, '\x1b[4m\x1b[47m\x1b[31mRED\x1b[0m|')
        self.assertEqual(t2, '\x1b[4m\x1b[47m\x1b[31mRED\x1b[0m|')
    '''

    def test_ip_helper_string(self):
        self.assertEqual(self.iph('test'), 'test')
        self.assertEqual(self.iph('test {t1} {t2}', t1='test1', t2='test2'), 'test test1 test2')
        self.assertEqual(self.iph('test {} {}', 1, 2), 'test 1 2')

    def test_ip_helper_function(self):
        self.assertEqual(self.iph.f(), 'test_ip_helper_function')

    def test_iph_crlf(self):
        self.assertEqual(self.iph.crlf, '\n')
        self.assertEqual(self.iph('this is a test{crlf}'), 'this is a test\n')

    def test_iph_counter(self):
        self.assertEqual(self.iph('this is a test {counter()}'), 'this is a test 1')
        self.assertEqual(self.iph('this is a test {counter}'), 'this is a test 2')

    def test_iph_color(self):
        print(self.iph('this is a test {color(red)}RED{color} this should be normal'))
        #self.assertEqual(self.iph('this is a test {color(red)}RED{color}'), 'this is a test \x1b[31mRED')


class TestIndentedPrinter(unittest.TestCase):

    def setUp(self):
        self.ip = IndentedPrinter()

    def test_basic_get(self):
        self.assertEqual(self.ip.get('test'), 'test')

    def test_indent_get(self):
        self.assertEqual(self.ip.a().get('test'), '     test')

    def test_indent_minus_get(self):
        self.ip.a(2).s()
        self.assertEqual(self.ip.get('test'), '     test')

    def test_indent_push_pop_get(self):
        self.ip.a().push().a()
        self.assertEqual(self.ip.get('test'), '          test')
        self.ip.pop()
        self.assertEqual(self.ip.get('test'), '     test')

    def test_indent_mem_get(self):
        self.ip.a().ms('zero', 0).a()
        self.assertEqual(self.ip.get('test'), '          test')
        self.ip.mr('zero')
        self.assertEqual(self.ip.get('test'), 'test')

    def test_silence_get(self):
        self.ip.a().ms('zero', 0).a().toggle_silent()
        self.assertEqual(self.ip.get('test'), '')
        self.ip.toggle_silent().mr('zero')
        self.assertEqual(self.ip.get('test'), 'test')

    def test_call(self):
        pass

    def test_buffer(self):
        self.ip.b('this').b('is').b('a').b('test')
        self.assertEqual(self.ip.getln('test'), 'thisisatesttest')
        self.assertEqual(self.ip.getln('test'), 'test')

    def test_flags(self):
        self.ip.fc('t1').fi('t1')
        self.assertEqual(self.ip.get('test'), 'test')
        self.ip.fc('-t1').p()
        self.assertEqual(self.ip.get('test'), '')

    def test_prefix(self):
        self.ip.set_prefix('prefix-')
        self.assertEqual(self.ip.get('test'), 'prefix-test')

    def test_suffix(self):
        self.ip.set_suffix('-suffix')
        self.assertEqual(self.ip.get('test'), 'test-suffix')

    def test_logging_existing_logger(self):
        with self.assertLogs('IP Log') as cm:
            self.ip.set_logger().info('test')
            self.assertEqual(cm.output, ['INFO:IP Log:test'])


    def test_logging_create_logger(self):
        with self.assertLogs('test_log') as cm:
            l = logging.getLogger('test_log')
            self.ip.set_logger(l).info('test')
            self.assertEqual(cm.output, ['INFO:test_log:test'])


