#!/usr/bin/env python

"""
Take lines or data and dump to a clean string.
"""

__author__ = ""
__copyright__ = ""
__credits__ = []
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = ""

from unittest import TestCase
from PythonUtils.LineReporter.line_reporter import LineReporter

class TestLineReporter(TestCase):

    def test_with_data(self):
        """
        l1
        l2
        l3
        """    
        data = ['l1', 'l2', 'l3']
        lr = LineReporter(*data)
        self.assertEqual(0, len(lr))    
        self.assertFalse(lr)
        exp = 'l1\n' \
              'l2\n' \
              'l3'
        self.assertEqual(3, len(lr))    
        self.assertTrue(lr)
        self.assertEqual(exp, str(lr))
        self.assertEqual(data, list(lr))

    def test_with_data_dict_in_new_sep(self):
        """    
        l1 : data
        l2 : data
        l3 : data
        """    
        lr = LineReporter(sep='|')
        lr += {'l1': 'data1', 'l2': 'data2', 'l3': 'data3'}
        exp = 'l1|data1\n' \
              'l2|data2\n' \
              'l3|data3'
        self.assertEqual(3, len(lr))    
        self.assertTrue(lr)
        self.assertEqual(exp, lr.to_string())

    def test_with_data_indent_out(self):
        """    
        l1 : data
        l2 : data
        l3 : data
        """    
        lr = LineReporter(sep='|')
        lr += {'l1': 'data1', 'l2': 'data2', 'l3': 'data3'}
        exp = '  l1 = data1\n' \
              '  l2 = data2\n' \
              '  l3 = data3'
        self.assertEqual(3, len(lr))    
        self.assertTrue(lr)
        self.assertEqual(exp, lr.to_string(indent=2, sep=' = '))

    def test_with_decimal_indents(self):
        """        
        l1____ :   1.0
        l2__   :  11.0
        l3     : 111.0 
        """    
        lr = LineReporter()
        lr += {'l1___': 1.0, 'l2__': 11.1, 'l3_': 111.2}
        exp = 'l1___ :   1.0\n' \
              'l2__  :  11.1\n' \
              'l3_   : 111.2'
        self.assertEqual(exp, lr.to_string())

        exp = 'l1___ :   1.00\n' \
              'l2__  :  11.10\n' \
              'l3_   : 111.20'
        self.assertEqual(exp, lr.to_string(decimals=2))
        
        exp = 'l1___ :   1\n' \
              'l2__  :  11\n' \
              'l3_   : 111'
        self.assertEqual(exp, lr.to_string(decimals=0))
        
    def test_with_mixed_data(self):
        """    
        l1____ :   1.0
        l2__   :  11.0
        l3     : 111.0 
        l4     : True
        l5     : Range(1:2)
        """
        lr = LineReporter()
        lr += {'l1___': 1.0, 'l2__': 11.1, 'l3_': 111.2}
        lr.add('l4', True, lookup={'true': 'No Prob', 'false': 'not gonna happen'})
        lr.add('l5', range(1, 2), title_align='right', title_len=10)
        exp = 'l1___      :   1.0\n' \
              'l2__       :  11.1\n' \
              'l3_        : 111.2\n' \
              'l4         : No Prob\n' \
              '        l5 : Range(1, 2)'
        self.assertEqual(exp, lr.to_string())

    def test_with_sections(self):
        """    
        s1:
            l1 : fooba... [+18 char]
            l2 : bar
        s2:
            l1 : foo2
            l2 : bar2
        """    
        lr = LineReporter(value_trim_to=5)
        with lr.section('s1') as sec:
            sec.add('l1', 'foobar is the way to go')
            sec.add('l2', 'bar')
        lr.add_section('s2')
        lr.add({'l1': 'foo2', 'l2': 'bar2'})
        lr.end_section()
        lr.add('l3', value='sna2')
        
        exp = 's1:\n' \
              '    l1 : fooba... [+18 char]\n' \
              '    l2 : bar\n' \
              's2:\n' \
              '    l1 : foo2\n' \
              '    l2 : bar2\n' \
              'l3 : sna2'

        self.assertEqual(exp, str(lr))


    def test_with_header_footer_lines(self):
        """    
        title1
        ------------------------
        s1:
            l1 : foo
            ====================
            l2 : bar
            ++++++++++++++++++++
            l3 : l3.1 : snafu
                 l3.2 : foobar
        l4 : hello
        ------------------------           
        footer
        """    
        sls = LineReporter({'13.1': 'snafu', '13.2': 'foobar'})
        
        slr = LineReporter(line_char='+', line_len=20)
        slr += ('l1', 'foo')
        slr.add_line('=')
        slr.add('l2', 'bar')
        slr.add_line('l3', sls)
        
        lr = LineReporter(footer='footer', footer_sep='-')
        with lr.section(indent=6) as sec:
            sec += slr
        lr.add('l4', value='hello')

        exp = 'title1\n' \
              '--------------------------\n' \
              '      l1 : foo\n' \
              '      ====================\n' \
              '      l2 : bar\n' \
              '      ++++++++++++++++++++\n' \
              '      l3 : l3.1 : snafu\n' \
              '           l3.2 : foobar\n' \
              'l4 : hello\n' \
              '--------------------------\n' \           
              'footer'
        
        self.assertEqual(exp, lr.to_string(header='title', header_sep='-'))


    def test_with_flag(self):
        """    
            l1 : data
          * l2 : data
            l3 : data
        """    
        lr = LineReporter()
        lr2 = lr + ('l1', 'data1')
        lr2.add('l2', 'data2', flag='* ')
        lr2 += 'l3', 'data3'
        
        exp = '  l1 : data1\n' \
              '* l2 : data2\n' \
              '  l3 : data3'
        self.assertEqual(exp, lr2)

    def test_with_formatted_replacements_inline(self):
        """    
          l1 : data
          l2 : data
          l3 : data
        """    
        lr = LineReporter()
        lr.add('l1', '{data1}%s','bar', data1='foo')
        lr.add('l2', '{}%(data2)s' 'sna', data2='fu')
        lr.add('l3', '{}()', 'ro', 'fl', data='foo')

        exp = 'l1 : foobar\n' \
              'l2 : snafu\n' \
              'l3 : rofl'
        self.assertEqual(exp, lr)

    def test_with_formatted_replacements_post(self):
        """    
          l1 : data
          l2 : data
          l3 : data
        """    
        lr = LineReporter()
        lr.add('l1', '{data1}bar')
        lr.add('l2', 'sna%(data2)s')
        lr.add('l3', '{}()', format_args=['ro', 'fl'])

        exp = 'l1 : foobar\n' \
              'l2 : snafu\n' \
              'l3 : rofl'
        self.assertEqual(exp, lr.to_string(data1='foo', data2='fu'))

    def test_with_string_bracketing_w_skip_empty(self):
        """    

          l1 : =>data1<=
          l2 : =>data2<=
          l3 : =>data2<=
               =>another data<=
        """
        lr = LineReporter(bracket_strings=True, skip_on_none=True)
        lr += {'l1': 'data1', 'l2': 'data2', 'l3': ['data3', 'another data'], 'l4': None}
        exp = 'l1 : =>data1<=\n' \
              'l2 : =>data2<=\n' \
              'l3 : =>data3<=\n' \
              '     =>another data<='
        self.assertEqual(exp, lr.to_string())

    def test_with_return_as_none(self):
        """    
        l1 : data
        l2 : data
        l3 : data
        """    
        lr = LineReporter()
        lr += {'l1': {'l1.1': 'data1'}, 'l2': {'l2.1': 'data2', 'l2.2': 'data22'}, 'l3': {'l3.1': 'data3'}}
        exp = 'l1 : l1.1 : data1\n' \
              'l2 : l2.1 : data2\n' \
              '     12.2 : data22\n' \
              'l3 : l3.1 : data3'
        self.assertEqual(exp, lr.to_string())

    def test_with_return_as_json(self):
        """    
        l1 : data
        l2 : data
        l3 : data
        """    
        lr = LineReporter(return_as='json')
        lr += {'l1': {'l1.1': 'data1'}, 'l2': {'l2.1': 'data2', 'l2.2': 'data22'}, 'l3': {'l3.1': 'data3'}}
        exp = 'l1 : {"l1.1": "data1"}\n' \
              'l2 : {"l2.1": "data2", "12.2": "data22"}\n' \
              'l3 : {"l3.1" : "data3"}'
        self.assertEqual(exp, lr.to_string())

    def test_with_return_as_repr(self):
        """    
        l1 : data
        l2 : data
        l3 : data
        """    
        lr = LineReporter(return_as='json')
        lr += {'l1': {'l1.1': 'data1'}, 'l2': {'l2.1': 'data2', 'l2.2': 'data22'}, 'l3': {'l3.1': 'data3'}}
        exp = "l1 : {l1.1 : 'data1'}\n" \
              "l2 : {\n" \
              "        l2.1 : 'data2'}\n" \
              "        12.2 : 'data22'\n" \
              "      }\n" \
              "l3 : {l3.1 : 'data3'}"
        
        self.assertEqual(exp, lr.to_string(return_as='repr'))

    def test_with_return_as_mixed(self):
        """    
        l1 : data
        l2 : data
        l3 : data
        """    
        lr = LineReporter(return_as='json')
        lr.add('l1', {'l1.1': 'data1'}, format_as='str')
        lr.add('l2', {'l2.1': 'data2', 'l2.2': 'data22'}, format_as=None)
        lr.add('l3', {'l3.1': 'data3'}, format_as='repr')
        exp = 'l1 : {l1.1 : data1}\n' \
              'l2 : l2.1 : data2\n' \
              '     12.2 : data22\n' \
              'l3 : {l3.1 : "data3"}'
        self.assertEqual(exp, lr.to_string())

    def test_with_common_data_indent(self):
        """    
          s1:
              s1.l1     : foo
              s1.l2     : bar
              
          l2         : foobar
          s2:
              s2.l1     : foo2
              s2.s3:
                  s2.s3.l1 : s2.s2.l1.l1 : foobar3
                             s2.s3.l1.l2 : snafu4
                             
                  s2.s3.l2 : bar3
        """    
        lr2 = LineReporter({'a1.l1__': 'foo', 's1.l2': 'bar'})
        lr = LineReporter()
        lr.add_section('s2', data=lr2)
        lr += ''
        lr += 'l2', 'foobar'
        with lr.section('s2') as sec:
            sec.add('s2.l1___', 'foo2')
            with sec.section('s2.s3') as sec2:
                lr3 = LineReporter({'s2.s2.l1.l1': 'foobar4', 's2.s3.l1.l2': 'snafu4'})
                sec2.add('s2.s3.l1', lr3)
                sec2.add_space()
                sec2 += 's2.s3.l2____', 'bar3'
        exp = 's1:\n' \
              '    s1.l1__           : foo\n' \
              '    s1.l2             : bar\n' \
              '\n' \
              'l2                    : foobar\n' \
              's2:\n' \
              '    s2.l1___          : foo2\n' \
              '    s2.s3:\n' \
              '        s2.s3.l1      : s2.s2.l1.l1 : foobar3\n' \
              '                       s2.s3.l1.l2 : snafu4\n' \
              '\n' \
              '        s2.s3.l2____  : bar3\n'
        self.assertEqual(exp, lr.to_string(section_key_padding='common'))

    def test_with_independent_data_indent(self):
        lr2 = LineReporter({'a1.l1__': 'foo', 's1.l2': 'bar'})
        lr = LineReporter()
        lr.add_section('s2', data=lr2)
        lr += ''
        lr += 'l2', 'foobar'
        with lr.section('s2') as sec:
            sec.add('s2.l1___', 'foo2')
            with sec.section('s2.s3') as sec2:
                lr3 = LineReporter({'s2.s2.l1.l1': 'foobar4', 's2.s3.l1.l2': 'snafu4'})
                sec2.add('s2.s3.l1', lr3)
                sec2.add_space()
                sec2 += 's2.s3.l2____', 'bar3'
        exp = 's1:\n' \
              '    s1.l1__  : foo\n' \
              '    s1.l2    : bar\n' \
              '\n' \
              'l2 : foobar\n' \
              's2:\n' \
              '    s2.l1___ : foo2\n' \
              '    s2.s3:\n' \
              '        s2.s3.l1     : s2.s2.l1.l1 : foobar3\n' \
              '                       s2.s3.l1.l2 : snafu4\n' \
              '\n' \
              '        s2.s3.l2____ : bar3\n'
        self.assertEqual(exp, lr.to_string(section_key_padding='by_level'))
        
    def test_with_default_data_indent(self):
        lr2 = LineReporter({'a1.l1__': 'foo', 's1.l2': 'bar'})
        lr = LineReporter()
        lr.add_section('s2', data=lr2)
        lr += ''
        lr += 'l2', 'foobar'
        with lr.section('s2') as sec:
            sec.add('s2.l1___', 'foo2')
            with sec.section('s2.s3') as sec2:
                lr3 = LineReporter({'s2.s2.l1.l1': 'foobar4', 's2.s3.l1.l2': 'snafu4'})
                sec2.add('s2.s3.l1', lr3)
                sec2.add_space()
                sec2 += 's2.s3.l2____', 'bar3'
        exp = 's1:\n' \
              '    s1.l1__ : foo\n' \
              '    s1.l2   : bar\n' \
              '\n' \
              'l2 : foobar\n' \
              's2:\n' \
              '    s2.l1___ : foo2\n' \
              '    s2.s3:\n' \
              '        s2.s3.l1      : s2.s2.l1.l1 : foobar3\n' \
              '                        s2.s3.l1.l2 : snafu4\n' \
              '\n' \
              '        s2.s3.l2____  : bar3\n'
        self.assertEqual(exp, lr.to_string())
      
    def test_add(self):
        """    
          l1 : data
        * l2 : data
          l3 : data
        """
        lr = LineReporter()
        lr2 = lr + ('l1', 'data1')
        
        lr3 = LineReporter()
        lr3 += 'l3', 'data3'
        
        lr2.add('l2', 'data2', flag='* ')
        lr4 = lr2 + lr3
        
        exp = '  l1 : data1\n' \
            '* l2 : data2\n' \
            '  l3 : data3'
        self.assertEqual(exp, lr4)

      
      
      
      
