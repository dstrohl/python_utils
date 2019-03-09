#!/usr/bin/env python

"""
Some small common test utilities
"""
from collections import OrderedDict
from pprint import pformat
from json import dumps, JSONEncoder
from textwrap import indent
from PythonUtils.BaseUtils import format_key_value, _UNSET, StringList

__all__ = ['make_exp_act_str', 'make_msg', 'TestMsgHelper']

__author__ = ""
__copyright__ = ""
__credits__ = []
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = ""


class JSONFlexEncoder(JSONEncoder):

    def default(self, o):
        try:
            return JSONEncoder.default(self, o)
        except TypeError:
            try:
                iterable = iter(o)
            except TypeError:
                pass
            else:
                return list(iterable)

        # Let the base class default method raise the TypeError
            return repr(o)

def fix_unserialized(o):
    try:
        iterable = iter(o)
    except TypeError:
        pass
    else:
        return list(iterable)

    return repr(o)


def make_exp_act_str(exp, act, header='\n\n', footer='\n', format_type='json', **format_kwargs):

    multi_line_sep = ' : '
    tmp_format_kwargs = {'default': fix_unserialized, 'sort_keys': True}
    tmp_format_kwargs.update(format_kwargs)
    if format_type == 'json':
        tmp_exp = dumps(exp, **tmp_format_kwargs)
        tmp_act = dumps(act, **tmp_format_kwargs)
    elif format_type == 'str':
        tmp_exp = str(exp)
        tmp_act = str(act)
    elif format_type == 'repr':
        tmp_exp = repr(exp)
        tmp_act = repr(act)
    else:
        tmp_act = act
        tmp_exp = exp

    tmp_exp = tmp_exp.splitlines()
    tmp_act = tmp_act.splitlines()

    new_tmp_exp = []
    new_tmp_act = []

    for l in tmp_exp:
        new_tmp_exp.append('=>%s<=' % l)
    for l in tmp_act:
        new_tmp_act.append('=>%s<=' % l)
    tmp_exp = '\n'.join(new_tmp_exp)
    tmp_act = '\n'.join(new_tmp_act)

    if '\n' in tmp_exp or '\n' in tmp_act:
        multi_line_sep = ' :\n'
        tmp_exp = indent(tmp_exp, '    ')
        tmp_act = indent(tmp_act, '    ')

    tmp_exp = 'Expected' + multi_line_sep + tmp_exp
    tmp_act = 'Actual  ' + multi_line_sep + tmp_act

    tmp_ret = []
    if header is not None:
        tmp_ret.append(header)
    tmp_ret.append(tmp_exp)
    tmp_ret.append(tmp_act)
    if footer is not None:
        tmp_ret.append(footer)

    return '\n'.join(tmp_ret)


def make_msg(*levels, config=None, header=None, footer=None, act=_UNSET, exp=_UNSET, msg=None, format_kwargs=None, **other_objs):
    """
    returns:
    \n
    ***********************************************************************
        header
    ***********************************************************************
        Levels:  xxx
    -----------------------------------------------------------------------
        Config: xxx
    -----------------------------------------------------------------------
        Act:
        exp:
    -----------------------------------------------------------------------
        other_objs
    -----------------------------------------------------------------------
        msg
    ***********************************************************************
        footer
    ***********************************************************************
    \n
    \n
    """
    stars = '*' * 80
    dashes = '-' * 80
    dashes = '\n' + dashes + '\n'
    tmp_ret = ['', '', stars]
    if header is not None:
        header = indent(header, '    ')
        tmp_ret.append(header)
        tmp_ret.append(stars)

    tmp_msg = []
    if levels:
        if isinstance(levels, (list, tuple)):
            tmp_msg.append(' - '.join(levels))
        else:
            tmp_msg.append(str(levels))
    if act is not _UNSET and exp is not _UNSET:
        format_kwargs = format_kwargs or {}
        tmp_msg.append('Results:\n' + indent(make_exp_act_str(act=act, exp=exp, **format_kwargs), '    '))
    if msg is not None:
        tmp_msg.append('Initial Message:\n' + indent(msg, '    '))
    if config:
        tmp_msg.append('Config:\n' + indent(format_key_value(config), '    '))
    if other_objs:
        tmp_msg.append('Other Objects\n' + indent(format_key_value(other_objs), '    '))

    tmp_ret.append(dashes.join(tmp_msg))

    if footer is not None:
        tmp_ret.append(stars)
        footer = indent(footer, '    ')
        tmp_ret.append(footer)
    tmp_ret.append(stars)
    tmp_ret.append('')
    tmp_ret.append('')

    return '\n'.join(tmp_ret)


class TestMsgHelper(object):
    def __init__(self, sep=' - ', exp=_UNSET, act=_UNSET, levels=None, config=None, header=None, footer=None, msg=None, format_kwargs=None, clear=True, **other_objs):
        self.levels = StringList(levels, sep=sep)
        self.config = config
        self.header = header
        self.footer = footer
        self.act = act
        self.exp = exp
        self.msg = msg
        self.format_kwargs = format_kwargs or {}
        self.other_objs = other_objs

    def clear_test(self):
        self.act = _UNSET
        self.exp = _UNSET
        self.msg = None

    def clear(self):
        self.levels.clear()
        self.config = None
        self.header = None
        self.footer = None
        self.act = _UNSET
        self.exp = _UNSET
        self.msg = None
        self.format_kwargs.clear()
        self.other_objs.clear()

    def make_msg(self, exp=_UNSET, act=_UNSET, level=None, config=None, header=None, footer=None, msg=None, format_kwargs=None, clear=True, **other_objs):
        self.levels += level
        if config:
            self.config.update(config)
        self.header = header or self.header
        self.footer = footer or self.footer
        self.act = act or self.act
        self.exp = exp or self.exp
        self.msg = msg or self.msg
        self.format_kwargs = format_kwargs or self.format_kwargs
        self.other_objs.update(other_objs)
        if clear:
            tmp_ret = str(self)
            self.clear_test()
            return tmp_ret
        return str(self)

    def __str__(self):
        return make_msg(
            *self.levels.data,
            config=self.config,
            header=self.header,
            footer=self.footer,
            act=self.act,
            exp=self.exp,
            msg=self.msg,
            format_kwargs=self.format_kwargs,
            **self.other_objs
        )

    def __class(self, **kwargs):
        tmp_ret = self.__class__(
            sep=self.levels.sep, exp=self.exp, act=self.act, levels=self.levels.data, config=self.config, header=self.header,
            footer=self.footer, msg=self.msg, format_kwargs=self.format_kwargs, **self.other_objs)
        for key, value in kwargs.items():
            setattr(tmp_ret, key, value)
        return tmp_ret

    def copy(self):
        return self.__class()

    def __iadd__(self, other):
        self.levels += str(other)
        return self

    def __isub__(self, other):
        self.levels -= str(other)
        return self

    def __add__(self, other):
        tmp_ret = self.__class()
        tmp_ret.levels += str(other)
        return tmp_ret

    def __sub__(self, other):
        tmp_ret = self.__class()
        tmp_ret.levels -= str(other)
        return tmp_ret


