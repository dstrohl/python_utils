import unittest

from PythonUtils.Old.Signals import *

ss = SignalsSystem()


class JunkClass(object):
    value = 10

# -----------------------------------------------------------------------------

ss.register_signal('with_ret', loop_arg=0)


class SubSigDecWithRet(SignalDecorator):
    _signal_name = 'with_ret'
    _system = ss
    _default_priority = 50


@SubSigDecWithRet()
def add_ten_returns(value, add_ten=10, **kwargs):
    return value + add_ten


@SignalDecorator(signal_name='with_ret', system=ss)
def mult_two_return(value=None, multiplier=2, **kwargs):
    return value * multiplier


def add_one_returns(value, adder=1, **kwargs):
    return value + adder


ss.with_ret.add_function(add_one_returns, priority=1)


# -----------------------------------------------------------------------------

ss.register_signal('no_ret')


@SignalDecorator(signal_name='no_ret', system=ss)
def mult_two_no_return(vc, multiplier=2, **kwargs):
    vc.value *= 2


class SubSigDecWithoutRet(SignalDecorator):
    _signal_name = 'no_ret'
    _system = ss
    _default_priority = 50

@SubSigDecWithoutRet()
def add_ten_no_ret(vc, add_ten=10, **kwargs):
    vc.value += 10


def add_one_no_ret(vc, adder=1, **kwargs):
    vc.value += adder
add_one_no_ret.priority = 1

ss.no_ret.add_function(add_one_no_ret)


# -----------------------------------------------------------------------------
ss.register_signal('no_signals', loop_arg=0)


def div_two_returns(value, divr=2, **kwargs):
    return value / divr

# -----------------------------------------------------------------------------
ss.register_signal('no_signals_no_ret')


def div_two_no_ret(vc, divr=2, **kwargs):
    vc.value /= divr


# -----------------------------------------------------------------------------
ss.register_signal('sub_signals_ret', sub_signals='foo', loop_arg=0, sub_attr_name='model')


@SignalDecorator(signal_name='sub_signals_ret', system=ss, model='foo', priority=100)
def mult_two_return(value=None, multiplier=2, **kwargs):
    return value * multiplier


# -----------------------------------------------------------------------------
ss.register_signal('sub_signals_no_ret', sub_signals=['foo', 'bar'], allow_new_subs=False)


@SignalDecorator(signal_name='sub_signals_no_ret', system=ss, sub_signals='bar', priority=100)
def mult_two_no_return(vc, multiplier=2, **kwargs):
    vc.value *= 2



class SignalsTestCase(unittest.TestCase):
    '''
    def setUp(self):
        # ss.register_signal('with_ret')
        # ss.register_signal('no_ret', has_return=False)
    '''

    def test_no_ret(self):
        jc = JunkClass()
        ss.no_ret(jc)
        self.assertEqual(42, jc.value)

    def test_with_ret(self):
        tmp_test = ss.with_ret(10)
        self.assertEquals(42, tmp_test)

    def test_run_single(self):
        tmp_ret = ss.with_ret(32, func_names='add_ten_returns')
        self.assertEqual(42, tmp_ret)

    def test_with_ret_params(self):
        tmp_test = ss.with_ret(10, adder=2, multiplier=3, add_ten=20)
        self.assertEquals(96, tmp_test)

    def test_no_signals(self):
        tmp_test = ss.no_signals(10)
        self.assertEquals(10, tmp_test)

    def test_no_signals_no_ret(self):
        jc = JunkClass()
        ss.no_signals_no_ret(jc)
        self.assertEquals(10, jc.value)

    def test_len(self):
        self.assertEqual(3, len(ss.with_ret))
        self.assertEqual(3, len(ss.no_ret))
        self.assertEqual(0, len(ss.no_signals))
        self.assertEqual(0, len(ss.no_signals_no_ret))

    def test_bool(self):
        self.assertTrue(ss.with_ret)
        self.assertTrue(ss.no_ret)
        self.assertFalse(ss.no_signals)
        self.assertFalse(ss.no_signals_no_ret)

    def test_sub_signals(self):
        jc = JunkClass()
        jc2 = JunkClass()
        ss.sub_signals_no_ret.add_function(div_two_no_ret, sub_signals=['foo', 'bar'], priority=1)
        ss.sub_signals_no_ret.add_function(add_one_no_ret, sub_signals=['foo'], priority=5)

        ss.sub_signals_no_ret.foo(jc)
        ss.sub_signals_no_ret.bar(jc2)

        self.assertEqual(6.0, jc.value)
        self.assertEqual(10.0, jc2.value)

    def test_sub_signals_add_locked_raise(self):
        with self.assertRaises(AttributeError):
            ss.sub_signals_no_ret.add_function(div_two_no_ret, sub_signals=['foo', 'blah'])

    def test_sub_signals_with_ret(self):
        ss.sub_signals_ret.add_function(div_two_returns, model=['foo', 'bar'], priority=1)
        ss.sub_signals_ret.add_function(add_one_returns, model=['foo'], priority=5)

        tmp_ret = ss.sub_signals_ret.foo(10)
        tmp_ret2 = ss.sub_signals_ret.bar(10)

        self.assertEqual(12.0, tmp_ret)
        self.assertEqual(5.0, tmp_ret2)

        with self.assertRaises(AttributeError):
            tmp_ret = ss.sub_signals_ret(10)

    def test_no_ret_min(self):
        jc = JunkClass()
        ss.no_ret(jc, func_min_pri=25)
        self.assertEqual(40, jc.value)

    def test_with_ret_max(self):
        tmp_test = ss.with_ret(10, func_max_pri=75)
        self.assertEquals(21, tmp_test)

