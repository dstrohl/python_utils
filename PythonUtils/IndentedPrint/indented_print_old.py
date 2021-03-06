'''
Created on Aug 10, 2014

@author: strohl
'''
__author__ = 'strohl'

import inspect
import pprint
from PythonUtils.TermColor.termcolor import colored
from PythonUtils.IndentedPrint.color_wrap import ColorWrap
from os import path
# import copy
# from sys import stdout

class IndentedPrintHelper(object):
    """
        Methods:

        That return itself are:  (these can be chained together)

            p(*objects [sep = ''] [end='\n']):
                Print the attached objects using the normal 'print' command.
            i( [indent = 0]):
                Sets the indent level
            a([indent = 1]):
                Adds [indent] to the current indent level
            s([indent = 1]):
                Subtracts [indent] from the current indent level
            ms([key = None], [indent = None]):
                Sets [indent] or the current indent level to a memory location at [key]
            mr([key = None]):
                Sets the current indent level to the one at memory location [key]
            push():
                Ads the current indent level to a FILO cache.
            pop():
                Returns the last indent level from the cache.

        The "g" method will return the string that would be printed by 'p' for use by logging functions or other programatic systems.
           g( *objects,  [sep = ''], [end = '\n']):

        Initialization parameters:

        IndentedPrint(
                        [indent_spaces],  (default = 3)
                        [silence],      (default = False)
                        [inc_stack],        (default = False)
                        [stack_format],        (default =)
                        [stack_length_limits],
                        [line_format],   (default - see below)


            indent_spaces: The multiplier used for indenting.
                For example, if this is set at 5, the indent levels will be 5, 10, 15, 20...

            silence: used to silence all printing (does not impact using the "g" commend)

            caller: will include the called function or method in the string

            stack_format: defines the format of the called function or method (see below)

            stack_length_limits: expects a dictionary that defines the max length of the stack printed section. (see below)

            line_format: uses a formatting string that details where the main sections are on the line.  See below for args and default


        Line Format args:
            {padding}
            {stack}
            {line}
            {end}

            default line format is: '{padding}{stack}{line}{end}'


        for the stack format string, allowed args are:
            {'full_path'}
            {'line_num'}
            {'caller_name'}
            {'start_path'}
            {'last_dir'}
            {'file_name'}

        Stack length limits dict options (with defaults):
            max_length = None
            min_length = 10
            do_not_show_length = 4
            pad_to_max  = False
            justification = 'left'   (options are 'left', 'right', and 'center')
            end_string = ''
            padding_string = ' '
            trim_string = '+'
            trim_priority = 1
                Trim priority is used to determine which objects should be trimmed.  first
                    - priority of 0 indicates no trimming allowed
                    - fields with the same trim priority will be trimmed to equal lengths to fit the overall max string length
                    - after set 1 is trimmed to all min length, set 2 is trimmed and so on.
                    - if all trim priority sets are trimmed to min length, and the string is still too long, everything is trimmed equally below the min length other than lines marked with a 0.
                    - if strings fall below "do_not_show_length", they are excluded.
                    - if final string is still over __full_string__.max_length, the full string will be trimmed to max_length



        Stack length limits dict definition (and defaults)
            {'__full_string__': {'max_length':40,
                            'pad_to_max':True,
                            'end_string':'|',
            'line_num': {'trim_priority':0}
            'caller_name': {'max_length':15,
            'last_dir': {'max_length':40,
            'file_name': {'max_length':40,
                          }
    """

    stack_format = '{caller_name} [{last_dir}.{file_name}:{line_num}] |'
    stack_length_limits = {'__full_string__': {'max_length':40,
                                               'pad_to_max':True,
                                               'end_string':'|'},
                            'line_num':       {'trim_priority':0}
                            }

    line_format = '{padding}{stack}{line}{end}'
    render_queue = ''
    cw = ColorWrap()
    color_string = None
    _currently_colored = False

    def __init__(self,
                  line_format = None,
                  inc_stack = False,
                  stack_format = None,
                  stack_length_limits = None):

        self.indent_spaces = indent_spaces
        self.silence = silence
        self.inc_stack = inc_stack
        if stack_format:
            self.stack_format = stack_format
        if stack_length_limits:
            self.stack_length_limits = stack_length_limits
        if line_format:
            self.line_format = line_format
        self.counters = {}
        self.counters['__default__'] = 0
        self.indent_mems = {}
        self.pop_queue = []
        self.string_lookup = {}
        self.flags = []
        self.trouble_flag = False
        self._pp = pprint.PrettyPrinter(indent=3)

    # ====================================
    # color
    # ====================================

    def color(self, color=None):
        self.color_string = color

    # ====================================
    # counter methods
    # ====================================

    def counter_add(self, count_diff=1, counter_key=None):
        self._update_counter(counter_key, count_diff)
        return self

    def counter_sub(self, count_diff=1, counter_key=None):
        count_diff = count_diff * -1
        self._update_counter(counter_key, count_diff)
        return self

    def counter_clear(self, count = 0, counter_key=None):
        self._update_counter(counter_key, count, reset=True)
        return self

    def counter(self, counter_key=None, counter_inc_after=0, counter_inc_before=0):
        if not counter_key:
            counter_key = '__default__'
        try:
            tmp_ret = self.counters[counter_key]
        except KeyError:
            tmp_ret = 0
        return tmp_ret

    def _update_counter(self, counter_key, counter_change=0, reset=False):
        if not counter_key:
            counter_key = '__default__'

        if reset:
            cur_cnt = counter_change
        else:
            try:
                cur_cnt = self.counters[counter_key]
            except KeyError:
                cur_cnt = 0
            cur_cnt = cur_cnt + counter_change

        if cur_cnt < 1:
            try:
                del self.counters[counter_key]
            except KeyError:
                pass
        else:
            self.counters[counter_key] = cur_cnt

    # ====================================
    # printing methods
    # ====================================

    def print(self, *args , **kwargs):
        kwargs['end'] = ''
        self._print(*args, **kwargs)
        return self

    def println(self, *args , **kwargs):
        kwargs['end'] = '\n'
        self._print(*args, **kwargs)
        return self

    def pretty_print(self, *args, **kwargs):
        self.__pprint(*args, **kwargs)
        return self

    def new_line(self, new_line_count = 1):
        self._print(mt_lines = new_line_count)
        return self

    def sep_line(self, sep_str='-', strlen=80, indent=None):
        sep_line = ''.ljust(strlen, sep_str)
        if indent:
            self.ms('__internal_seperator__').i(indent)
        self._print(sep_line, inc_stack=False)

        if indent:
            self.mr('__internal_seperator__')
        return self

    def func_name(self, add_offset=0):
        try:
            tmp_trace = traceback.extract_stack(None)
            offset = len(tmp_trace) - 3 + add_offset
            self.println('function: ', traceback.extract_stack(None)[offset][2])
        except UnboundLocalError:
            import traceback
            tmp_trace = traceback.extract_stack(None)
            offset = len(tmp_trace) - 3 + add_offset
            self.println('function: ', traceback.extract_stack(None)[offset][2])
        return self

    # ====================================
    # keystring saving methods
    # ====================================

    def keystring_save(self, key, *args, **kwargs):
        self.string_lookup[key] = {'args': args, 'kwargs': kwargs}
        return self

    def keystring_print(self, key):
        try:
            self.println(*self.string_lookup[key]['args'], **self.string_lookup[key]['kwargs'])
        except KeyError:
            pass
        return self

    # ====================================
    # indent control methods
    # ====================================

    def indent(self, indent=0):
        self.current_indent = indent
        return self

    def indent_add(self, indent=1):
        self.current_indent += indent
        return self

    def indent_sub(self, indent=1):
        self.current_indent -= indent
        if self.current_indent < 0:
            self.current_indent = 0
        return self

    def indent_mem_save(self, key=None, indent=None):
        if indent:
            tmp_indent = indent
        else:
            tmp_indent = self.current_indent

        if key:
            self.indent_mems[key] = tmp_indent
        else:
            self.pop_queue.append(tmp_indent)
        return self

    def indent_mem(self, key=None):
        if key:
            try:
                self.current_indent = self.indent_mems[key]
            except KeyError:
                pass
        else:
            self.pop()
        return self

    def push(self):
        self.pop_queue.append(self.current_indent)
        return self

    def pop(self):
        self.current_indent = self.pop_queue.pop()
        return self

    # ====================================
    # support methods
    # ====================================

    def _print(self, *args , mt_lines = None, end = '', inc_stack = None):
        self._trouble_print()
        if not self.silence:
            if mt_lines:
                for i in range(mt_lines):
                    print('',)
            if args:
                print_str = self.g(*args, end = end, inc_stack = inc_stack, console = True)
                # if self.color_str:
                #    print_str = self.cw.wrap(self.color_str, print_str)
                print(print_str , end = end)
            # print(tmp_padding, *args)

    def __pprint(self, *args, outside_sep = "=", inside_sep = "-", indent = 3):
        self._trouble_print()
        self.pl()
        if outside_sep:
            self.sep(sep_str=outside_sep,indent=0)

        prnt_sep = False
        for arg in args:
            if prnt_sep:
                self.sep(sep_str=inside_sep, indent=0)
            self._pp.pprint(arg)
            prnt_sep = True

        if outside_sep:
            self.sep(sep_str=outside_sep,indent=0)
        self.pl()

    def g(self, *args , **kwargs):
        end = kwargs.get('end', '\n')
        sep = kwargs.get('sep', '')
        console = kwargs.get('console', False)
        inc_stack = kwargs.get('inc_stack', self.inc_stack)
        tmp_stack_str = ''
        tmp_list = []

        padding = ' '.ljust(self.current_indent * self.indent_spaces)

        for s in args:
            tmp_list.append(self._stringify_with_vars(s, console = console))
            # if self._currently_colored and console:
            #    tmp_list.append(self.cw.default)

        if inc_stack:
            tmp_stack_str = self._parse_stack()

        return self.line_format.format(padding = padding, stack = tmp_stack_str, line = sep.join(tmp_list), end = end)

    def _stringify_with_vars(self, item, console = True):
        tmp_ret = ''
        if isinstance(item, str):
            if item.startswith('#[') and item.endswith(']#'):
                tmp_str = item[2:-2]
                tmp_split = tmp_str.split(':')
                tmp_var = tmp_split[0]

                try:
                    tmp_sub_var = tmp_split[1]
                except:
                    tmp_sub_var = None

                if tmp_var == 'counter':

                    if tmp_sub_var:
                        tmp_ret = str(self.get_c(tmp_sub_var))
                    else:
                        tmp_ret = str(self.get_c())

                if tmp_var == 'color':
                    if tmp_sub_var:
                        if tmp_sub_var == 'default':
                            self._currently_colored = False
                        else:
                            self._currently_colored = tmp_sub_var
                        return ''

                    else:
                        self._currently_colored = False
                        return ''


                    '''
                    if console:
                        if tmp_sub_var:
                            if tmp_sub_var == 'default':
                                self._currently_colored = False
                            else:
                                self._currently_colored = True
                            return self.cw[tmp_sub_var]

                        else:
                            self._currently_colored = False
                            return self.cw.default
                    else:
                        return ''

                    '''
        tmp_ret = str(item)

        if self._currently_colored:
            return colored(tmp_ret, self._currently_colored)
        else:
            return tmp_ret

    def _combine_strings(self, *args, **kwargs):
        end = kwargs.get('end', '')
        sep = kwargs.get('sep', '')
        tmp_list = []

        for s in args:
            tmp_str = str(s)
            tmp_list.append(tmp_str)
        tmp_list.append(end)
        return sep.join(tmp_list)



    def stack(self):
        self._print('', inc_stack = True)
        return self


    def _parse_stack(self):
        off_path = 1
        off_line = 2
        off_attrib = 3
        tmp_attribs = dir(self)
        my_attribs = []
        format_kwargs = {}

        stack = inspect.stack()

        for s in tmp_attribs:
            if not s.startswith('__'):
                my_attribs.append(s)


        for s in stack:
            if not s[off_attrib] in my_attribs:

                format_kwargs['full_path'] = s[off_path]
                format_kwargs['line_num'] = s[off_line]
                format_kwargs['caller_name'] = s[off_attrib]
                break

        format_kwargs.update(self._parse_path(format_kwargs['full_path']))

        tmp_ret = self.stack_format.format(**format_kwargs)
        return tmp_ret

    def _parse_path(self, in_path):
        tmp_path, tmp_fn = path.split(in_path)
        tmp_path, tmp_dir = path.split(tmp_path)
        return {'start_path':tmp_path, 'last_dir':tmp_dir, 'file_name':tmp_fn}



    def troubleshoot(self, troubleshoot = False):
        self.trouble_flag = troubleshoot

    def _trouble_print(self):
        if self.trouble_flag:
            print('Indent Spaces  : ', self.indent_spaces)
            print('Current Indent : ', self.current_indent)
            print('Silence        : ', self.silence)
            print('Counters       : ', self.counters)
            print('Memories       : ', self.indent_mems)
            print('Push Queue     : ', self.pop_queue)
            print('Flags          : ', self.flags)


    '''
    def fa(self, flag):
        if flag not in self.flags:
            self.flags.append(flag)

        return self

    def fr(self, flag):
        try:
            self.flags.remove(flag)
        except:
            pass
        return self


    def ff(self, flag = None):

        if flag:

            self.allowed_flags.append = flag
            self.silence = True




        self.filter_scope = all_except

        if all_except:
            self.silence = True
        else:
            self.silence = False



        if flag:

            if flag in self.flags:
                self.silence = self._swap_bool(self.silence)

        else:
            self.silence = False

        return self

    def _check_filter(self):
    '''

    def _swap_bool(self, bool_in):
        if bool_in == True:
            return  False
        else:
            return True

    def silent(self, silence):
        self.silence = silence
        return self

    # ====================================
    # call parser
    # ====================================

    def __call__(self, *args, **kwargs):
        """
        :param args: string or strings to print
        :param kwargs:

            silent = False

            pre_indent = 0
            pre_pop = False
            pre_push = False
            pre_new_lines = 0
            pre_sep = False

            post_indent = 0
            post_pop = False
            post_push = False
            post_new_lines = 0
            post_sep = False

        :return: self
        """

        try:
            self.silent(kwargs['silent'])
        except KeyError:
            pass

        # -------- pre-actions ---------

        try:
            self.indent_add(kwargs['pre_indent'])
        except KeyError:
            pass

        try:
            self.indent_sub(kwargs['pre_outdent'])
        except KeyError:
            pass

        try:
            self.new_line(new_line_count=kwargs['pre_new_lines'])
        except KeyError:
            pass

        try:
            if kwargs['pre_pop']:
                self.pop()
        except KeyError:
            pass

        try:
            if kwargs['pre_push']:
                self.push()
        except KeyError:
            pass

        try:
            if kwargs['pre_sep']:
                self.sep_line()
        except KeyError:
            pass


        # ---- actions ---------------

        self.println(*args)

        #  ----- post actions ---------

        try:
            self.indent_add(kwargs['post_indent'])
        except KeyError:
            pass

        try:
            self.indent_sub(kwargs['post_outdent'])
        except KeyError:
            pass

        try:
            self.new_line(kwargs['post_new_lines'])
        except KeyError:
            pass

        try:
            if kwargs['post_pop']:
                self.pop()
        except KeyError:
            pass

        try:
            if kwargs['post_push']:
                self.push()
        except KeyError:
            pass

        try:
            if kwargs['post_sep']:
                self.sep_line()
        except KeyError:
            pass

    # ====================================
    # Shortcuts
    # ====================================

    def co(self, color=None):
        return self.color(color)

    def ca(self, count_diff=1, counter_key=None):
        return self.counter_add(count_diff, counter_key)

    def cs(self, count_diff=1, counter_key=None):
        return self.counter_sub(count_diff, counter_key)

    def cc(self, count=0, counter_key=None):
        return self.counter_clear(count, counter_key)

    @property
    def c(self):
        return self.get_counter()

    def p(self, *args , **kwargs):
        return self.print(*args, **kwargs)

    def pl(self, *args , **kwargs):
        return self.println(*args, **kwargs)

    def ks(self, key, *args, **kwargs):
        return self.keystring_save(key, *args, **kwargs)

    def kp(self, key):
        return self.keystring_print(key)

    def pp(self, *args, **kwargs):
        return self.pretty_print(*args, **kwargs)

    def lp(self, *args, **kwargs):
        return self.println(*args, **kwargs)

    def nl(self, new_line_count=1):
        return self.new_line(new_line_count)

    def i(self, indent=0):
        return self.indent(indent)

    def a(self, indent=1):
        return self.indent_add(indent)

    def s(self, indent=1):
        return self.indent_sub(indent)

    def ms(self, key=None, indent=None):
        return self.indent_mem_save(key, indent)

    def mr(self, key=None):
        return self.indent_mem(key)

    def sep(self, sep_str='-', strlen=80, indent=None):
        return self.sep_line(sep_str, strlen, indent)

    def f(self, offset=0):
        return self.func_name(offset)


class IndentedPrinter(object):
    """
        Methods:
        
        That return itself are:  (these can be chained together)

            p(*objects [sep = ''] [end='\n']):
                Print the attached objects using the normal 'print' command.
            i( [indent = 0]):
                Sets the indent level
            a([indent = 1]):
                Adds [indent] to the current indent level
            s([indent = 1]):
                Subtracts [indent] from the current indent level
            ms([key = None], [indent = None]):
                Sets [indent] or the current indent level to a memory location at [key]
            mr([key = None]):
                Sets the current indent level to the one at memory location [key]
            push():
                Ads the current indent level to a FILO cache.
            pop():
                Returns the last indent level from the cache.
        
        The "g" method will return the string that would be printed by 'p' for use by logging functions or other programatic systems.
           g( *objects,  [sep = ''], [end = '\n']):
       
        Initialization parameters:
        
        IndentedPrint(
                        [indent_spaces],  (default = 3)
                        [silence],      (default = False)
                        [inc_stack],        (default = False)
                        [stack_format],        (default =)
                        [stack_length_limits],
                        [line_format],   (default - see below)
                        
        
            indent_spaces: The multiplier used for indenting.
                For example, if this is set at 5, the indent levels will be 5, 10, 15, 20...
                
            silence: used to silence all printing (does not impact using the "g" commend)
            
            caller: will include the called function or method in the string
            
            stack_format: defines the format of the called function or method (see below)
                            
            stack_length_limits: expects a dictionary that defines the max length of the stack printed section. (see below)
            
            line_format: uses a formatting string that details where the main sections are on the line.  See below for args and default
            
            
        Line Format args:
            {padding}
            {stack}
            {line}
            {end}
            
            default line format is: '{padding}{stack}{line}{end}'
            
        
        for the stack format string, allowed args are:
            {'full_path'}
            {'line_num'}
            {'caller_name'}
            {'start_path'}
            {'last_dir'}
            {'file_name'}

        Stack length limits dict options (with defaults):
            max_length = None
            min_length = 10
            do_not_show_length = 4
            pad_to_max  = False
            justification = 'left'   (options are 'left', 'right', and 'center')
            end_string = ''
            padding_string = ' '
            trim_string = '+'
            trim_priority = 1
                Trim priority is used to determine which objects should be trimmed.  first
                    - priority of 0 indicates no trimming allowed
                    - fields with the same trim priority will be trimmed to equal lengths to fit the overall max string length
                    - after set 1 is trimmed to all min length, set 2 is trimmed and so on.
                    - if all trim priority sets are trimmed to min length, and the string is still too long, everything is trimmed equally below the min length other than lines marked with a 0.
                    - if strings fall below "do_not_show_length", they are excluded.
                    - if final string is still over __full_string__.max_length, the full string will be trimmed to max_length
                    
        
            
        Stack length limits dict definition (and defaults)
            {'__full_string__': {'max_length':40,
                            'pad_to_max':True,
                            'end_string':'|',
            'line_num': {'trim_priority':0}        
            'caller_name': {'max_length':15,
            'last_dir': {'max_length':40,
            'file_name': {'max_length':40,
                          }
    """

    current_indent = 0
    inc_stack = False
    stack_format = '{caller_name} [{last_dir}.{file_name}:{line_num}] |'
    stack_length_limits = {'__full_string__': {'max_length':40,
                                               'pad_to_max':True,
                                               'end_string':'|'},
                            'line_num':       {'trim_priority':0}
                            }

    line_format = '{padding}{stack}{line}{end}'
    render_queue = ''
    cw = ColorWrap()
    color_string = None
    _currently_colored = False

    def __init__(self,
                  indent_spaces = 5,
                  silence = False,
                  line_format = None,
                  inc_stack = False,
                  stack_format = None,
                  stack_length_limits = None):

        self.indent_spaces = indent_spaces
        self.silence = silence
        self.inc_stack = inc_stack
        if stack_format:
            self.stack_format = stack_format
        if stack_length_limits:
            self.stack_length_limits = stack_length_limits
        if line_format:
            self.line_format = line_format
        self.counters = {}
        self.counters['__default__'] = 0
        self.indent_mems = {}
        self.pop_queue = []
        self.string_lookup = {}
        self.flags = []
        self.trouble_flag = False
        self._pp = pprint.PrettyPrinter(indent=3)

    # ====================================
    # color
    # ====================================

    def color(self, color=None):
        self.color_string = color
        return self

    # ====================================
    # counter methods
    # ====================================

    def counter_add(self, count_diff=1, counter_key=None):
        self._update_counter(counter_key, count_diff)
        return self

    def counter_sub(self, count_diff=1, counter_key=None):
        count_diff = count_diff * -1
        self._update_counter(counter_key, count_diff)
        return self

    def counter_clear(self, count = 0, counter_key=None):
        self._update_counter(counter_key, count, reset=True)
        return self

    def get_counter(self, counter_key=None):
        if not counter_key:
            counter_key = '__default__'
        try:
            tmp_ret = self.counters[counter_key]
        except KeyError:
            tmp_ret = 0
        return tmp_ret

    def _update_counter(self, counter_key, counter_change=0, reset=False):
        if not counter_key:
            counter_key = '__default__'

        if reset:
            cur_cnt = counter_change
        else:
            try:
                cur_cnt = self.counters[counter_key]
            except KeyError:
                cur_cnt = 0
            cur_cnt = cur_cnt + counter_change

        if cur_cnt < 1:
            try:
                del self.counters[counter_key]
            except KeyError:
                pass
        else:
            self.counters[counter_key] = cur_cnt

    # ====================================
    # printing methods
    # ====================================

    def print(self, *args , **kwargs):
        kwargs['end'] = ''
        self._print(*args, **kwargs)
        return self

    def println(self, *args , **kwargs):
        kwargs['end'] = '\n'
        self._print(*args, **kwargs)
        return self

    def pretty_print(self, *args, **kwargs):
        self.__pprint(*args, **kwargs)
        return self

    def new_line(self, new_line_count = 1):
        self._print(mt_lines = new_line_count)
        return self

    def sep_line(self, sep_str='-', strlen=80, indent=None):
        sep_line = ''.ljust(strlen, sep_str)
        if indent:
            self.ms('__internal_seperator__').i(indent)
        self._print(sep_line, inc_stack=False)

        if indent:
            self.mr('__internal_seperator__')
        return self

    def func_name(self, add_offset=0):
        try:
            tmp_trace = traceback.extract_stack(None)
            offset = len(tmp_trace) - 3 + add_offset
            self.println('function: ', traceback.extract_stack(None)[offset][2])
        except UnboundLocalError:
            import traceback
            tmp_trace = traceback.extract_stack(None)
            offset = len(tmp_trace) - 3 + add_offset
            self.println('function: ', traceback.extract_stack(None)[offset][2])
        return self

    # ====================================
    # keystring saving methods
    # ====================================

    def keystring_save(self, key, *args, **kwargs):
        self.string_lookup[key] = {'args': args, 'kwargs': kwargs}
        return self

    def keystring_print(self, key):
        try:
            self.println(*self.string_lookup[key]['args'], **self.string_lookup[key]['kwargs'])
        except KeyError:
            pass
        return self

    # ====================================
    # indent control methods
    # ====================================

    def indent(self, indent=0):
        self.current_indent = indent
        return self

    def indent_add(self, indent=1):
        self.current_indent += indent
        return self

    def indent_sub(self, indent=1):
        self.current_indent -= indent
        if self.current_indent < 0:
            self.current_indent = 0
        return self

    def indent_mem_save(self, key=None, indent=None):
        if indent:
            tmp_indent = indent
        else:
            tmp_indent = self.current_indent

        if key:
            self.indent_mems[key] = tmp_indent
        else:
            self.pop_queue.append(tmp_indent)
        return self

    def indent_mem(self, key=None):
        if key:
            try:
                self.current_indent = self.indent_mems[key]
            except KeyError:
                pass
        else:
            self.pop()
        return self

    def push(self):
        self.pop_queue.append(self.current_indent)
        return self

    def pop(self):
        self.current_indent = self.pop_queue.pop()
        return self

    # ====================================
    # support methods
    # ====================================

    def _print(self, *args , mt_lines = None, end = '', inc_stack = None):
        self._trouble_print()
        if not self.silence:
            if mt_lines:
                for i in range(mt_lines):
                    print('',)
            if args:
                print_str = self.g(*args, end = end, inc_stack = inc_stack, console = True)
                # if self.color_str:
                #    print_str = self.cw.wrap(self.color_str, print_str)
                print(print_str , end = end)
            # print(tmp_padding, *args)

    def __pprint(self, *args, outside_sep = "=", inside_sep = "-", indent = 3):
        self._trouble_print()
        self.pl()
        if outside_sep:
            self.sep(sep_str=outside_sep,indent=0)

        prnt_sep = False
        for arg in args:
            if prnt_sep:
                self.sep(sep_str=inside_sep, indent=0)
            self._pp.pprint(arg)
            prnt_sep = True

        if outside_sep:
            self.sep(sep_str=outside_sep,indent=0)
        self.pl()

    def g(self, *args , **kwargs):
        end = kwargs.get('end', '\n')
        sep = kwargs.get('sep', '')
        console = kwargs.get('console', False)
        inc_stack = kwargs.get('inc_stack', self.inc_stack)
        tmp_stack_str = ''
        tmp_list = []

        padding = ' '.ljust(self.current_indent * self.indent_spaces)

        for s in args:
            tmp_list.append(self._stringify_with_vars(s, console = console))
            # if self._currently_colored and console:
            #    tmp_list.append(self.cw.default)

        if inc_stack:
            tmp_stack_str = self._parse_stack()

        return self.line_format.format(padding = padding, stack = tmp_stack_str, line = sep.join(tmp_list), end = end)

    def _stringify_with_vars(self, item, console = True):
        tmp_ret = ''
        if isinstance(item, str):
            if item.startswith('#[') and item.endswith(']#'):
                tmp_str = item[2:-2]
                tmp_split = tmp_str.split(':')
                tmp_var = tmp_split[0]

                try:
                    tmp_sub_var = tmp_split[1]
                except:
                    tmp_sub_var = None

                if tmp_var == 'counter':

                    if tmp_sub_var:
                        tmp_ret = str(self.get_c(tmp_sub_var))
                    else:
                        tmp_ret = str(self.get_c())

                if tmp_var == 'color':
                    if tmp_sub_var:
                        if tmp_sub_var == 'default':
                            self._currently_colored = False
                        else:
                            self._currently_colored = tmp_sub_var
                        return ''

                    else:
                        self._currently_colored = False
                        return ''


                    '''
                    if console:
                        if tmp_sub_var:
                            if tmp_sub_var == 'default':
                                self._currently_colored = False
                            else:
                                self._currently_colored = True
                            return self.cw[tmp_sub_var]

                        else:
                            self._currently_colored = False
                            return self.cw.default
                    else:
                        return ''
                        
                    '''
        tmp_ret = str(item)

        if self._currently_colored:
            return colored(tmp_ret, self._currently_colored)
        else:
            return tmp_ret

    def _combine_strings(self, *args, **kwargs):
        end = kwargs.get('end', '')
        sep = kwargs.get('sep', '')
        tmp_list = []

        for s in args:
            tmp_str = str(s)
            tmp_list.append(tmp_str)
        tmp_list.append(end)
        return sep.join(tmp_list)



    def stack(self):
        self._print('', inc_stack = True)
        return self


    def _parse_stack(self):
        off_path = 1
        off_line = 2
        off_attrib = 3
        tmp_attribs = dir(self)
        my_attribs = []
        format_kwargs = {}

        stack = inspect.stack()

        for s in tmp_attribs:
            if not s.startswith('__'):
                my_attribs.append(s)


        for s in stack:
            if not s[off_attrib] in my_attribs:

                format_kwargs['full_path'] = s[off_path]
                format_kwargs['line_num'] = s[off_line]
                format_kwargs['caller_name'] = s[off_attrib]
                break

        format_kwargs.update(self._parse_path(format_kwargs['full_path']))

        tmp_ret = self.stack_format.format(**format_kwargs)
        return tmp_ret

    def _parse_path(self, in_path):
        tmp_path, tmp_fn = path.split(in_path)
        tmp_path, tmp_dir = path.split(tmp_path)
        return {'start_path':tmp_path, 'last_dir':tmp_dir, 'file_name':tmp_fn}



    def troubleshoot(self, troubleshoot = False):
        self.trouble_flag = troubleshoot

    def _trouble_print(self):
        if self.trouble_flag:
            print('Indent Spaces  : ', self.indent_spaces)
            print('Current Indent : ', self.current_indent)
            print('Silence        : ', self.silence)
            print('Counters       : ', self.counters)
            print('Memories       : ', self.indent_mems)
            print('Push Queue     : ', self.pop_queue)
            print('Flags          : ', self.flags)


    '''
    def fa(self, flag):
        if flag not in self.flags:
            self.flags.append(flag)

        return self

    def fr(self, flag):
        try:
            self.flags.remove(flag)
        except:
            pass
        return self


    def ff(self, flag = None):

        if flag:

            self.allowed_flags.append = flag
            self.silence = True




        self.filter_scope = all_except

        if all_except:
            self.silence = True
        else:
            self.silence = False



        if flag:

            if flag in self.flags:
                self.silence = self._swap_bool(self.silence)

        else:
            self.silence = False

        return self

    def _check_filter(self):
    '''

    def _swap_bool(self, bool_in):
        if bool_in == True:
            return  False
        else:
            return True

    def silent(self, silence):
        self.silence = silence
        return self

    # ====================================
    # call parser
    # ====================================

    def __call__(self, *args, **kwargs):
        """
        :param args: string or strings to print
        :param kwargs:

            silent = False

            pre_indent = 0
            pre_pop = False
            pre_push = False
            pre_new_lines = 0
            pre_sep = False

            post_indent = 0
            post_pop = False
            post_push = False
            post_new_lines = 0
            post_sep = False

        :return: self
        """

        try:
            self.silent(kwargs['silent'])
        except KeyError:
            pass

        # -------- pre-actions ---------

        try:
            self.indent_add(kwargs['pre_indent'])
        except KeyError:
            pass

        try:
            self.indent_sub(kwargs['pre_outdent'])
        except KeyError:
            pass

        try:
            self.new_line(new_line_count=kwargs['pre_new_lines'])
        except KeyError:
            pass

        try:
            if kwargs['pre_pop']:
                self.pop()
        except KeyError:
            pass

        try:
            if kwargs['pre_push']:
                self.push()
        except KeyError:
            pass

        try:
            if kwargs['pre_sep']:
                self.sep_line()
        except KeyError:
            pass


        # ---- actions ---------------

        self.println(*args)

        #  ----- post actions ---------

        try:
            self.indent_add(kwargs['post_indent'])
        except KeyError:
            pass

        try:
            self.indent_sub(kwargs['post_outdent'])
        except KeyError:
            pass

        try:
            self.new_line(kwargs['post_new_lines'])
        except KeyError:
            pass

        try:
            if kwargs['post_pop']:
                self.pop()
        except KeyError:
            pass

        try:
            if kwargs['post_push']:
                self.push()
        except KeyError:
            pass

        try:
            if kwargs['post_sep']:
                self.sep_line()
        except KeyError:
            pass

    # ====================================
    # Shortcuts
    # ====================================

    def co(self, color=None):
        return self.color(color)

    def ca(self, count_diff=1, counter_key=None):
        return self.counter_add(count_diff, counter_key)

    def cs(self, count_diff=1, counter_key=None):
        return self.counter_sub(count_diff, counter_key)

    def cc(self, count=0, counter_key=None):
        return self.counter_clear(count, counter_key)

    @property
    def c(self):
        return self.get_counter()

    def p(self, *args , **kwargs):
        return self.print(*args, **kwargs)

    def pl(self, *args , **kwargs):
        return self.println(*args, **kwargs)

    def ks(self, key, *args, **kwargs):
        return self.keystring_save(key, *args, **kwargs)

    def kp(self, key):
        return self.keystring_print(key)

    def pp(self, *args, **kwargs):
        return self.pretty_print(*args, **kwargs)

    def lp(self, *args, **kwargs):
        return self.println(*args, **kwargs)

    def nl(self, new_line_count=1):
        return self.new_line(new_line_count)

    def i(self, indent=0):
        return self.indent(indent)

    def a(self, indent=1):
        return self.indent_add(indent)

    def s(self, indent=1):
        return self.indent_sub(indent)

    def ms(self, key=None, indent=None):
        return self.indent_mem_save(key, indent)

    def mr(self, key=None):
        return self.indent_mem(key)

    def sep(self, sep_str='-', strlen=80, indent=None):
        return self.sep_line(sep_str, strlen, indent)

    def f(self, offset=0):
        return self.func_name(offset)


'''
class FakeIndentedPrint(object):
    def __getattr__(self, name):
        def foo(self):
            return self
        return self

    def __setattr__(self, name, value):
        def foo(self):
            return self
        return self
'''


class IP(IndentedPrinter):
    pass

'''
class IndentedPrint(IndentedPrinter):
    pass


ip = IndentedPrint()
'''


