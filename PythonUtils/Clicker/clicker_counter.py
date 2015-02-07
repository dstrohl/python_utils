__author__ = 'dstrohl'

import sys

# ===============================================================================
# counter Class
# ===============================================================================


class ClickItem(object):

    def __init__(self,
                 clicker,
                 name,
                 initial=None,
                 step=None,
                 max_value=None,
                 min_value=None,
                 console_format=None,
                 return_format=None,
                 return_every=None,
                 rollover=None,
                 rollunder=None):
        self._clicker = clicker
        self._name = name
        self._initial = initial
        self._step = step
        self._max_value = max_value
        self._min_value = min_value
        self._console_format = console_format
        self._format = return_format
        self._return_every = return_every
        self._rollover = rollover
        self._rollunder = rollunder

        self._current = self.initial

    def _change(self, change_by):
        change_by = int(change_by) * self.step
        self._current += change_by
        while self._current > self.max_value or self._current < self.min_value:
            if self._current > self.max_value:
                if self.rollover:
                    extra = self._current - self.max_value - 1
                    self._current = self.min_value + extra
                else:
                    self._current = self.max_value
            elif self._current < self.min_value:
                if self.rollunder:
                    extra = self.min_value - self._current - 1
                    self._current = self.max_value - extra
                else:
                    self._current = self.min_value

    def a(self, num_to_add=1):
        self.add(num_to_add)

    def add(self, num_to_add=1):
        self._change(num_to_add)
        return self

    def __iadd__(self, other):
        return self.add(other)

    def __add__(self, other):
        return self.add(other)

    def sub(self, num_to_sub=1):
        self._change(num_to_sub*-1)
        return self

    def __isub__(self, other):
        return self.sub(other)

    def __sub__(self, other):
        return self.sub(other)

    def __int__(self):
        return self._current

    def __repr__(self):
        'CounterItem: {} Current Count: {}'.format(self.name, self.get)
        return

    def __bool__(self):
        return self.get == self.initial

    def __len__(self):
        return self.max_value - self.min_value

    def __call__(self, increment=1):
        self._change(increment)
        return self.get

    @property
    def get(self):
        return self._current

    @property
    def perc(self):
        ran = self.max_value - self.min_value
        dist = self.get - self.min_value
        return ran / dist * 100

    def __str__(self):
        return self.return_format.format(self._dict)

    @property
    def _dict(self):
        tmp_dict = {'counter': self.get,
                    'min': self.min_value,
                    'max': self.max_value,
                    'name': self.name,
                    'perc': self.perc}
        return tmp_dict

    @property
    def get_console(self):
        return self.console_format.format(self._dict)

    def reset(self, new_value=None):
        if new_value:
            self._current = new_value
        else:
            self._current = self.initial
        return self

    @property
    def name(self):
        return self._name

    def _check_and_return(self, attr):
        local_attr = '_'+attr
        if getattr(self, local_attr):
            return getattr(self, local_attr)
        else:
            return getattr(self._clicker, attr)

    @property
    def initial(self):
        return self._check_and_return('initial')

    @property
    def step(self):
        return self._check_and_return('step')

    @property
    def max_value(self):
        return self._check_and_return('max_value')

    @property
    def min_value(self):
        return self._check_and_return('min_value')

    @property
    def console_format(self):
        return self._check_and_return('console_format')

    @property
    def return_format(self):
        return self._check_and_return('return_format')

    @property
    def return_every(self):
        tmp_ret = self._check_and_return('return_every')
        if tmp_ret >= 1 or tmp_ret == 0:
            return tmp_ret
        else:
            ran = self.max_value - self.min_value
            return round(ran * tmp_ret)

    @property
    def rollover(self):
        return self._check_and_return('rollover')

    @property
    def rollunder(self):
        return self._check_and_return('rollunder')


class Clicker():
    '''
    Arguments:
        initial = initial counter number
        echo = print each set to console
        step = print only on increments of x
        name = name of clicker
        max = max number (when set, echo will return %xx)
        format = format to use for echo, default = '{name} : {counter}'
    '''

    default_name = '__default__'

    def __init__(self, **kwargs):

        self._counters = {}

        self.initial = kwargs.get('initial', 0)
        self.step = kwargs.get('step', 1)
        self.max_value = kwargs.get('max_value', sys.maxsize)
        self.min_value = kwargs.get('min_value', 0)
        self.console_format = kwargs.get('console_format', '{counter}')
        self.format = kwargs.get('return_format', '{counter')
        self.return_every = kwargs.get('return_every', 1)
        self.rollover = kwargs.get('rollover', False)
        self.rollunder = kwargs.get('rollunder', False)
        self.autoadd = kwargs.get('autoadd', True)
        self.autoadd_name_prefix = kwargs.get('AutoCounter_', True)

        self.add_counter(self.default_name)
        self._default_counter = self._counters[self.default_name]

    def add_counter(self, name, **kwargs):
        self._counters[name] = ClickItem(self, name, **kwargs)

    def del_counter(self, name):
        del self._counters[name]

    def __getattr__(self, item):
        return getattr(self._default_counter, item)

    def __getitem__(self, item):
        if self.autoadd:
            if item not in self:
                self.add_counter(item)
        return self._counters[item]

    def __contains__(self, item):
        return item in self._counters

    def __len__(self):
        return len(self._counters)

    def __delitem__(self, key):
        del self._counters[key]

    def __call__(self, *args):
        tmp_name = self.default_name
        tmp_change = 1
        if args:
            if isinstance(args[0], str):
                tmp_name = args[0]
                if len(args) == 2:
                    tmp_change = args[1]
            else:
                tmp_change = args[0]
        tmp_cnt = self[tmp_name]

        return tmp_cnt(tmp_change)
