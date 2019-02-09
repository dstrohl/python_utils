
class StopSignal(Exception):
    def __init__(self, ret_value=None):
        self.return_value = ret_value


class RunSubSignal(object):
    def __init__(self, parent, sub_kwargs):
        self.parent = parent
        self.sub_kwargs = sub_kwargs

    def __call__(self, *args, **kwargs):
        kwargs.update(self.sub_kwargs)
        return self.parent.run(*args, **kwargs)


class NoRetSignal(object):

    def __init__(self, name, sub_signals=None, sub_attr_name=None, allow_new_subs=True):
        self.name = name

        self._sub_attr_name = sub_attr_name or 'sub_signals'
        self._allow_new_subs = True

        self._sub_signals = {}
        self.add_sub_signal(sub_signals)

        self._allow_new_subs = allow_new_subs
        self._funcs = {}
        self._func_list = []
        self.has_ops = False

    def add_sub_signal(self, names):
        if names is not None:
            if not isinstance(names, (list, tuple)):
                names = [names]

            for name in names:
                if name not in self._sub_signals:
                    if not self._allow_new_subs:
                        raise AttributeError('New sub signals are not allowed to be added')
                    self._sub_signals[name] = RunSubSignal(self, sub_kwargs={'func_sub_signal': name})

    def add_function(self, function, priority=100, name=None, **kwargs):
        if name is None:
            name = function.__name__
        if name in self._funcs:
            name = '%s_%s' % (name, len(self._funcs)+2)
        if self._sub_attr_name in kwargs:
            sub_signal_name = kwargs[self._sub_attr_name]
            self.add_sub_signal(sub_signal_name)
        else:
            sub_signal_name = []

        try:
            priority = function.priority
        except AttributeError:
            pass

        self._funcs[name] = function

        self._func_list.append(dict(
            func=function,
            pri=priority,
            name=name,
            subs=sub_signal_name))

        self.has_ops = True

        self._func_list.sort(key=lambda func: func['pri'])

    def _signal_iter(self, func_names=None, func_sub_signal=None, func_min_pri=-1, func_max_pri=9999):
        """
        :keyword func_names: name or list of names to limit by
        :keyword func_sub_signal: sub_signal to limit by
        :keyword func_min_pri: minimum priority to include
        :keyword func_max_pri: maximum priority to include
        :return: iterator for function dictionary
        """
        if func_names is not None:
            if not isinstance(func_names, (list, tuple)):
                func_names = [func_names]

            if func_sub_signal is None:
                for f in self._func_list:
                    if f['name'] in func_names and func_min_pri < f['pri'] < func_max_pri:
                        yield f
            else:
                for f in self._func_list:
                    if f['name'] in func_names and func_min_pri < f['pri'] < func_max_pri and func_sub_signal in f['subs']:
                        yield f

        else:
            if func_sub_signal is None:
                for f in self._func_list:
                    if func_min_pri < f['pri'] < func_max_pri:
                        yield f
            else:
                for f in self._func_list:
                    if func_min_pri < f['pri'] < func_max_pri and func_sub_signal in f['subs']:
                        yield f

    def __iter__(self):
        for f in self._func_list:
            yield f

    def _run_func(self, func_iter, args, kwargs):
        # print('init: ', args[0].value)

        for func in func_iter:
            try:
                # print('  ', func['name'], 'in: ', args[0].value)

                func['func'](*args, **kwargs)
            except StopSignal as stop_sig:
                # print(func['name'], 'final: ', args[0].value)
                return
            # print('  ', func['name'], 'out: ', args[0].value)
        # print('final: ', args[0].value)

    def _get_shortcut_ret(self, args, kwargs):
        return

    def run(self, *args, func_names=None, func_sub_signal=None, func_min_pri=-1, func_max_pri=9999, **kwargs):
        if not self:
            return self._get_shortcut_ret(args, kwargs)
        if self._sub_signals and func_sub_signal is None:
            raise AttributeError('Sub signal required if any sub signals are defined.')

        if func_names is None and func_sub_signal is None and func_min_pri == -1 and func_max_pri == 9999:
            tmp_iter = self
        else:
            tmp_iter = self._signal_iter(func_names=func_names, func_sub_signal=func_sub_signal,
                                         func_min_pri=func_min_pri, func_max_pri=func_max_pri)

        return self._run_func(tmp_iter, args, kwargs)

    __call__ = run

    def __len__(self):
        return len(self._funcs)

    def __bool__(self):
        return self.has_ops

    def __getattr__(self, item):
        return self._sub_signals[item]

    __getitem__ = __getattr__


class RetSignal(NoRetSignal):

    def __init__(self, name, loop_arg, **kwargs):
        super().__init__(name, **kwargs)
        self._loop_arg = loop_arg

    def _get_shortcut_ret(self, args, kwargs):
        return args[self._loop_arg]

    def _run_func(self, func_iter, args, kwargs):
        args = list(args)
        # print('init: ', args[0])
        for f in func_iter:

            # print('  ', f['name'], 'in: ', args[0])

            try:
                tmp_ret = f['func'](*args, **kwargs)
                args[self._loop_arg] = tmp_ret
            except StopSignal as stop_sig:
                # print(f['name'], 'final: ', args[0])
                return stop_sig.return_value

            # print('  ', f['name'], 'out: ', args[0])

        # print('final: ', tmp_ret)

        return tmp_ret


class SignalsSystem(object):
    def __init__(self):
        self._signals = {}

    def register_signal(self, name, loop_arg=None, **kwargs):
        if isinstance(name, (NoRetSignal, RetSignal)):
            self._signals[name.name] = name
        else:
            if loop_arg is not None:
                self._signals[name] = RetSignal(name, loop_arg=loop_arg, **kwargs)
            else:
                self._signals[name] = NoRetSignal(name, **kwargs)

    def __getattr__(self, signal):
        return self._signals[signal]

    def __getitem__(self, signal):
        return self._signals[signal]

signal_system = SignalsSystem()


class SignalDecorator(object):
    _system = signal_system
    _signal_name = None
    _default_priority = 100

    def __init__(self, name=None, signal_name=None, priority=None, system=None, **kwargs):
        self._signal_name = signal_name or self._signal_name
        self._signal_priority = priority or self._default_priority
        self._system = system or self._system
        self._name = name
        self._kwargs = kwargs

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            return f(*args, **kwargs)

        name = self._name or f.__name__
        try:
            pri = f.priority
        except AttributeError:
            pri = self._signal_priority

        self._system[self._signal_name].add_function(wrapped_f, name=name, priority=pri, **self._kwargs)

        return wrapped_f


"""
example decorator

@SignalDecorator(signal_name="before_action_signal", priority=100, system=signal_system_object)
def my_function(arg, arg, kwarg1='foo', kwarg2='bar')
    blah = kwarg1
    return kwarg2

"""