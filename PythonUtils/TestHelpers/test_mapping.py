# pulled from the CPython core: https://raw.githubusercontent.com/python/cpython/master/Lib/test/mapping_tests.py
# and modified to test a passed object to make sure it conforms to mapping methods and processes.

# tests common to dict and UserDict


import unittest
import collections
import sys

class NxtNum(object):
    _max_item = 26
    _cur_item = None
    _min_item = 1
    _inc_by = 1

    def clear(self):
        self._cur_item = None

    @property
    def cur_item(self):
        if self._cur_item is None:
            self._cur_item = self._min_item
        return self._cur_item

    def get(self, item=None):
        if item is None:
            item = self.cur_item
        return self._get(item)

    def _get(self, item):
        return item

    @property
    def next_item(self):
        if self._cur_item is None:
            self._cur_item = self._min_item
        else:
            self._cur_item = self._cur_item + self._inc_by
            if self._cur_item >= self._max_item:
                self._cur_item = self._min_item
        return self._cur_item

    @property
    def next(self):
        return self.get(self.next_item)
    n = next

    def next_X(self, qty):
        tmp_ret = []
        for i in range(qty):
            tmp_ret.append(self.n)
        return tmp_ret

    @property
    def g(self):
        return self.get()

    def set(self, item):
        self._cur_item = item


class NxtAlpha(NxtNum):
    alphas = 'abcdefghijklmnopqrstuvwxyz'

    def _get(self, item):
        return self.alphas[item-1]

    def set(self, item):
        if isinstance(item, str):
            self._cur_item = self.alphas.index(item) + 1
        else:
            self._cur_item = item


class NxtSet(NxtNum):
    _inc_by = 3

    def get(self, item, length=3):
        if item is None:
            item = self.next_item
        return self._get(item, length)

    def _get(self, item, length=3):
        tmp_ret = []
        for i in range(length):
            tmp_ret.append(item)
            item += 1
        return set(tmp_ret)


TestData = collections.namedtuple('TestData', ['keys', 'values', 'items', 'all', 'dict', 'test_obj', 'next_keys', 'next_values'])


class TestDataManager(object):

    def __init__(self, nums=None, alphas=None, sets=None, default_pattern='an', test_obj=None):
        self.test_obj = test_obj
        self.nums = nums or NxtNum()
        self.alphas = alphas or NxtAlpha()
        self.sets = sets or NxtSet()
        self.default_pattern = default_pattern

    def clear(self):
        self.nums.clear()
        self.alphas.clear()
        self.sets.clear()

    def _get_next_round_robin_int(self, current, max, min=1):
        if current >= max:
            return min
        else:
            return current + 1

    def _make_pattern_list(self, qty=1, pattern_in=None):
        tmp_ret = []
        if pattern_in:
            if not isinstance(pattern_in, (list, tuple)):
                pattern_in = [pattern_in]
        else:
            pattern_in = ['an']

        pattern_len = len(pattern_in)
        offset = 0
        for x in range(qty):
            tmp_ret.append(pattern_in[offset])
            offset = self._get_next_round_robin_int(offset, pattern_len - 1)

        return tmp_ret

    def _make_data_item(self, pattern):
        if pattern == 'nn':
            key = self.alphas.n
            value = key
        elif pattern == 'an':
            key = self.alphas.n
            value = self.nums.n
        elif pattern == 'na':
            key = self.nums.n
            value = self.alphas.n
        elif pattern == 'aa':
            key = self.alphas.n
            value = key
        elif pattern.startswith('as'):
            key = self.alphas.n
            value = self.sets.n
        else:
            if isinstance(pattern, (list, tuple)):
                key = pattern[0]
                value = pattern[1]
            else:
                key = pattern
                value = pattern
        return key, value

    def make(self, *args):
        """
        'na', 'nn', 'aa', 'an', 'as', 'ns'
        10, 'na'
        10
        <None>
        :param args:
        :return:
        """
        tmp_keys = []
        tmp_values = []
        tmp_dict = {}
        tmp_items = []
        tmp_all = []
        tmp_next_key = []
        tmp_next_value = []

        if len(args) == 0:
            pattern = self._make_pattern_list(7)

        elif len(args) >= 1 and isinstance(args[0], int):
            data_len = args[0] + 5
            args = args[1:]
            pattern = self._make_pattern_list(data_len, args)
        else:
            data_len = len(args) + 5
            pattern = self._make_pattern_list(data_len, args)

        test_obj = self.test_obj()
        for i, pat in enumerate(pattern):
            tmp_key, tmp_value = self._make_data_item(pat)
            if i < len(pat) - 5:
                tmp_keys.append(tmp_key)
                tmp_values.append(tmp_value)
                tmp_dict[tmp_key] = tmp_value
                test_obj[tmp_key] = tmp_value
                tmp_items.append((tmp_key, tmp_value))
                tmp_all.append(tmp_key)
                tmp_all.append(tmp_value)
            else:
                tmp_next_key.append(tmp_key)
                tmp_next_value.append(tmp_value)

        tmp_ret = TestData(
            test_obj=test_obj,
            keys=tmp_keys,
            values=tmp_values,
            items=tmp_items,
            dict=tmp_dict,
            all=tmp_all,
            next_keys=tmp_next_key,
            next_values=tmp_next_value
        )

        return tmp_ret


"""

class TestDataGenerator(object):
    default_allowed_patterns = ['nn', 'aa', 'an', 'na', 'asn', 'asa']

    def __init__(self, allowed_patterns=None):
        self.allowed_patterns = allowed_patterns or self.default_allowed_patterns
        self.alphas = 'abcdefghijklmnopqrstuvwxyz'
        self.last_int_used = -1
        self.last_alpha_used = -2
        self.active_dict = {}
        self.active_pattern = -1
        self.active_patterns = None

    def clear(self):
        self.active_dict.clear()
        self.active_pattern = -1
        self.last_alpha_used = -1
        self.last_int_used = 0

    def set_data(self, data_in):
        self.active_dict.clear()
        self.update(data_in)

    def update(self, data_in):
        self.active_dict.update(data_in)

    def _get_next_round_robin_int(self, current, max, min=1):
        if current >= max:
            return min
        else:
            return current + 1

    def _make_pattern_list(self, qty=1, pattern_in=None):
        tmp_ret = []
        if pattern_in:
            if not isinstance(pattern_in, (list, tuple)):
                pattern_in = [pattern_in]
            save_offset = False
            offset = 0
        else:
            save_offset = True
            pattern_in = self.allowed_patterns
            offset = self.active_pattern

        pattern_len = len(pattern_in)

        for x in range(qty):
            tmp_ret.append(pattern_in[offset])
            offset = self._get_next_round_robin_int(offset, pattern_len - 1)

        if save_offset:
            self.active_pattern = offset

        return tmp_ret

    def _next_alpha(self):
        self.last_alpha_used = self._get_next_round_robin_int(self.last_alpha_used, len(self.alphas))
        return self.alphas[self.last_alpha_used]

    def _next_num(self):
        self.last_int_used += 1
        return self.last_int_used

    def _make_data_item(self, pattern):
        if pattern not in self.allowed_patterns:
            pattern[0] = 'a'
        if pattern not in self.allowed_patterns:
            raise AttributeError('Disallowed Pattern: %r' % pattern)
        if pattern == 'nn':
            key = self._next_num()
            value = key
        elif pattern == 'an':
            key = self._next_alpha()
            value = self._next_num()
        elif pattern == 'na':
            key = self._next_num()
            value = self._next_alpha()
        elif pattern == 'aa':
            key = self._next_alpha()
            value = key
        elif pattern.startswith('asa'):
            if len(pattern) > 3:
                qty = int(pattern[3:])
            else:
                qty = 3
            key = self._next_alpha()
            value = []
            for x in range(qty):
                value.append(self.alphas[x])
            value = set(value)
        elif pattern.startswith('asn'):
            if len(pattern) > 3:
                qty = int(pattern[3:])
            else:
                qty = 3
            key = self._next_alpha()
            value = set(range(qty))
        else:
            if isinstance(pattern, (list, tuple)):
                key = pattern[0]
                value = pattern[1]
            else:
                key = pattern
                value = pattern
        return key, value

    def make_data(self, *args, save=True):
        self.clear()
        tmp_ret = {}

        data_len = 1
        if len(args) >= 1 and isinstance(args[0], int):
            data_len = args[0]
            args = args[1:]
        elif len(args) >= 1:
            data_len = len(args)

        patterns = self._make_pattern_list(data_len, args)

        for pat in patterns:
            data_len -= 1
            tmp_key, tmp_value = self._make_data_item(pat)
            tmp_ret[tmp_key] = tmp_value

        if save:
            self.set_data(tmp_ret)
            self.active_patterns = patterns

        return tmp_ret

    def invalid_key(self, pattern=None):
        if pattern is None:
            if self.active_patterns:
                pattern = self.active_patterns[0]
            else:
                pattern = self.allowed_patterns[0]

        key = None

        while key is not None and key in self.active_dict:
            key, value = self._make_data_item(pattern)
        return key

    def keys(self):
        return self.active_dict.keys()

    def values(self):
        return self.active_dict.values()

    def items(self):
        return self.active_dict.items()

    def data(self):
        return self.active_dict

    def __setitem__(self, key, value):
        self.active_dict[key] = value

    def __getitem__(self, item):
        return self.active_dict[item]

    __call__ = make_data

AA = TestDataGenerator(['aa'])
NN = TestDataGenerator(['nn'])
AN = TestDataGenerator(['an'])
ASN = TestDataGenerator(['asn'])

"""


class TestDictLikeObject(unittest.TestCase):
    # This base class can be used to check that an object conforms to the
    # mapping protocol

    # Functions that can be useful to override to adapt to dictionary
    # semantics
    type2test = dict  # which class is being tested (overwrite in subclasses)

    alph = NxtAlpha
    nums = NxtNum
    sets = NxtSet
    only_string_keys = False
    skip_tests_ids = None
    test_skip_names = {}

    def __init__(self, *args, **kw):
        self.tdm = TestDataManager(alphas=self.alph, nums=self.nums, sets=self.sets, test_obj=self.type2test)
        tmp_skips = []
        for s in self.skip_tests_ids:
            if s in self.test_skip_names:
                tmp_item = self.test_skip_names[s]
                if not isinstance(tmp_item, (list, tuple)):
                    tmp_item = [tmp_item]

                for i in tmp_item:
                    tmp_skips.append('.' + i)
            else:
                tmp_skips.append('.' + s)
        self.skip_tests_ids = tmp_skips

        unittest.TestCase.__init__(self, *args, **kw)
        self.reference = self._reference().copy()

        # A (key, value) pair not in the mapping
        key, value = self.reference.popitem()
        self.other = {key: value}

        # A (key, value) pair in the mapping
        key, value = self.reference.popitem()
        self.inmapping = {key: value}
        self.reference[key] = value

    def setUp(self):
        tmp_id = self.id()
        tmp_id = '.' + tmp_id.rsplit('.', maxsplit=1)[1]
        if tmp_id in self.skip_tests_ids:
            self.skipTest('In Skip List')
        else:
            self.tdm.clear()
            self.m(set=True)
            self.em = self._empty_mapping()

    def m(self, *args, set=False):
        tmp_ret = self.tdm.make(*args)
        if set:
            self.td = tmp_ret
        return tmp_ret

    def _reference(self):
        """Return a dictionary of values which are invariant by storage
        in the object under test."""
        # return {"one": "two", "key1": "value1", "key2": (1, 2, 3)}
        tmp_td = self.m('aa', 'aa', 'as')
        return tmp_td.dict

    def _empty_mapping(self):
        """Return an empty mapping object"""
        return self.type2test()

    def _full_mapping(self, *args, **kwargs):
        if kwargs:
            x = self._empty_mapping()
            for key, value in kwargs.items():
                x[key] = value
            return x
        else:
            if not args:
                args = ['an', 'an']
            elif isinstance(args[0], dict):
                x = self._empty_mapping()
                for key, value in args[0].items():
                    x[key] = value
                return x
            return self.m(*args).test_obj

    def test_read(self):
        # Test for read only operations on mapping
        p = self._empty_mapping()
        p1 = dict(p)  # workaround for singleton objects
        d = self._full_mapping(self.reference)
        if d is p:
            p = p1
        # Indexing
        for key, value in self.reference.items():
            self.assertEqual(d[key], value)
        knownkey = list(self.other.keys())[0]
        self.assertRaises(KeyError, lambda: d[knownkey])
        # len
        self.assertEqual(len(p), 0)
        self.assertEqual(len(d), len(self.reference))
        # __contains__
        for k in self.reference:
            self.assertIn(k, d)
        for k in self.other:
            self.assertNotIn(k, d)
        # cmp
        self.assertEqual(p, p)
        self.assertEqual(d, d)
        self.assertNotEqual(p, d)
        self.assertNotEqual(d, p)
        # bool
        if p: self.fail("Empty mapping must compare to False")
        if not d: self.fail("Full mapping must compare to True")

        # keys(), items(), iterkeys() ...
        def check_iterandlist(iter, lst, ref):
            self.assertTrue(hasattr(iter, '__next__'))
            self.assertTrue(hasattr(iter, '__iter__'))
            x = list(iter)
            self.assertTrue(set(x) == set(lst) == set(ref))

        check_iterandlist(iter(d.keys()), list(d.keys()),
                          self.reference.keys())
        check_iterandlist(iter(d), list(d.keys()), self.reference.keys())
        check_iterandlist(iter(d.values()), list(d.values()),
                          self.reference.values())
        check_iterandlist(iter(d.items()), list(d.items()),
                          self.reference.items())
        # get
        key, value = next(iter(d.items()))
        knownkey, knownvalue = next(iter(self.other.items()))
        self.assertEqual(d.get(key, knownvalue), value)
        self.assertEqual(d.get(knownkey, knownvalue), knownvalue)
        self.assertNotIn(knownkey, d)

    def test_write(self):
        # Test for write operations on mapping
        p = self._empty_mapping()
        # Indexing
        for key, value in self.reference.items():
            p[key] = value
            self.assertEqual(p[key], value)
        for key in self.reference.keys():
            del p[key]
            self.assertRaises(KeyError, lambda: p[key])
        p = self._empty_mapping()
        # update
        p.update(self.reference)
        self.assertEqual(dict(p), self.reference)
        items = list(p.items())
        p = self._empty_mapping()
        p.update(items)
        self.assertEqual(dict(p), self.reference)
        d = self._full_mapping(self.reference)
        # setdefault
        key, value = next(iter(d.items()))
        knownkey, knownvalue = next(iter(self.other.items()))
        self.assertEqual(d.setdefault(key, knownvalue), value)
        self.assertEqual(d[key], value)
        self.assertEqual(d.setdefault(knownkey, knownvalue), knownvalue)
        self.assertEqual(d[knownkey], knownvalue)
        # pop
        self.assertEqual(d.pop(knownkey), knownvalue)
        self.assertNotIn(knownkey, d)
        self.assertRaises(KeyError, d.pop, knownkey)
        default = 909
        d[knownkey] = knownvalue
        self.assertEqual(d.pop(knownkey, default), knownvalue)
        self.assertNotIn(knownkey, d)
        self.assertEqual(d.pop(knownkey, default), default)
        # popitem
        key, value = d.popitem()
        self.assertNotIn(key, d)
        self.assertEqual(value, self.reference[key])
        p = self._empty_mapping()
        self.assertRaises(KeyError, p.popitem)

    def test_constructor(self):
        self.assertEqual(self._empty_mapping(), self._empty_mapping())
        # from mapping
        self.assertTrue(self._empty_mapping() is not self._empty_mapping())
        self.assertEqual(self.type2test(**self.td.dict), self.td.dict)

    def test_bool(self):
        self.assertTrue(not self._empty_mapping())
        self.assertTrue(self.reference)
        self.assertTrue(bool(self._empty_mapping()) is False)
        self.assertTrue(bool(self.reference) is True)
        # from mapping
        self.assertTrue(not self._empty_mapping())
        self.assertTrue(self.td.test_obj)
        self.assertTrue(bool(self._empty_mapping()) is False)
        self.assertTrue(bool(self.td.test_obj is True))

    def test_keys(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.keys()), [])
        d = self.reference
        self.assertIn(list(self.inmapping.keys())[0], d.keys())
        self.assertNotIn(list(self.other.keys())[0], d.keys())
        self.assertRaises(TypeError, d.keys, None)
        # from mapping
        d = self._empty_mapping()
        self.assertEqual(list(d.keys()), [])
        d = self.td.test_obj
        k = d.keys()
        self.assertIn(self.td.keys[0], k)
        self.assertIn(self.td.keys[0], k)
        self.assertNotIn('__foobar__', k)


    def test_values(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.values()), [])

        self.assertRaises(TypeError, d.values, None)

        # from mapping
        self.assertEqual(list(self.td.test_obj.values()), self.td.values)



    def test_items(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.items()), [])

        self.assertRaises(TypeError, d.items, None)

        #from mapping
        self.assertEqual(list(self.td.items()), self.td.items)


    def test_contains(self):
        # from mapping
        d = self._empty_mapping()
        self.assertNotIn('a', d)
        self.assertTrue(not ('a' in d))
        self.assertTrue('a' not in d)
        self.assertIn(self.td.keys[0], self.td.test_obj)
        self.assertIn(self.td.keys[1], self.td.test_obj)
        self.assertNotIn('__foobar__', d)

        self.assertRaises(TypeError, d.__contains__)


    def test_len(self):
        d = self._empty_mapping()
        self.assertEqual(len(d), 0)

        # from mapping
        self.assertEqual(len(self.td.test_obj), len(self.td.keys))

    def test_getitem(self):
        d = self.reference
        self.assertEqual(d[list(self.inmapping.keys())[0]],
                         list(self.inmapping.values())[0])

        self.assertRaises(TypeError, d.__getitem__)

        # from mapping

        self.assertEqual(self.td.test_obj[self.td.keys[0]], self.td.values[0])
        self.assertEqual(self.td.test_obj[self.td.keys[1]], self.td.values[1])

        self.td.test_obj[self.td.next_keys[0]] = self.td.next_values[0]
        self.td.test_obj[self.td.keys[0]] = self.td.next_values[1]
        self.assertEqual(self.td.test_obj[self.td.next_keys[0]], self.td.next_values[0])
        self.assertEqual(self.td.test_obj[self.td.keys[0]], self.td.next_values[1])
        del self.td.test_obj[self.td.keys[1]]
        self.assertEqual(self.td.test_obj, {self.td.keys[0]: self.td.next_values[1], self.td.next_keys[0]: self.td.next_values[0]})

        self.assertRaises(TypeError, self.td.test_obj.__getitem__)

        # from hash

        TestMappingProtocol.test_getitem(self)
        class Exc(Exception): pass

        class BadEq(object):
            def __eq__(self, other):
                raise Exc()
            def __hash__(self):
                return 24

        d = self._empty_mapping()
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.__getitem__, x)


    def test_update(self):
        # mapping argument
        d = self._empty_mapping()
        d.update(self.other)
        self.assertEqual(list(d.items()), list(self.other.items()))

        # No argument
        d = self._empty_mapping()
        d.update()
        self.assertEqual(d, self._empty_mapping())

        # item sequence
        d = self._empty_mapping()
        d.update(self.other.items())
        self.assertEqual(list(d.items()), list(self.other.items()))

        # Iterator
        d = self._empty_mapping()
        d.update(self.other.items())
        self.assertEqual(list(d.items()), list(self.other.items()))

        # FIXME: Doesn't work with UserDict
        # self.assertRaises((TypeError, AttributeError), d.update, None)
        self.assertRaises((TypeError, AttributeError), d.update, 42)

        outerself = self

        class SimpleUserDict:
            def __init__(self):
                self.d = outerself.reference

            def keys(self):
                return self.d.keys()

            def __getitem__(self, i):
                return self.d[i]

        d.clear()
        d.update(SimpleUserDict())
        i1 = sorted(d.items())
        i2 = sorted(self.reference.items())
        self.assertEqual(i1, i2)

        class Exc(Exception):
            pass

        d = self._empty_mapping()

        class FailingUserDict:
            def keys(self):
                raise Exc

        self.assertRaises(Exc, d.update, FailingUserDict())

        d.clear()

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = 1

                    def __iter__(self):
                        return self

                    def __next__(self):
                        if self.i:
                            self.i = 0
                            return 'a'
                        raise Exc

                return BogonIter()

            def __getitem__(self, key):
                return key

        self.assertRaises(Exc, d.update, FailingUserDict())

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = ord('a')

                    def __iter__(self):
                        return self

                    def __next__(self):
                        if self.i <= ord('z'):
                            rtn = chr(self.i)
                            self.i += 1
                            return rtn
                        raise StopIteration

                return BogonIter()

            def __getitem__(self, key):
                raise Exc

        self.assertRaises(Exc, d.update, FailingUserDict())

        d = self._empty_mapping()

        class badseq(object):
            def __iter__(self):
                return self

            def __next__(self):
                raise Exc()

        self.assertRaises(Exc, d.update, badseq())

        self.assertRaises(ValueError, d.update, [(1, 2, 3)])

        # from mapping

        # mapping argument
        d = self._empty_mapping()
        self.m(3, 'nn', set=True)
        d.update({self.td.keys[0]:100})
        d.update({self.td.keys[1]:20})
        d.update(self.td.dict)
        self.assertEqual(d, self.td.dict)

        # no argument
        d.update()
        self.assertEqual(d, self.td.dict)

        # keyword arguments
        d = self._empty_mapping()
        self.m(3, 'an', set=True)
        kw1 = {self.td.keys[0]: 100}
        kw2 = {self.td.keys[1]: 20}
        d.update(**kw1)
        d.update(**kw2)
        d.update(**self.td.dict)
        self.assertEqual(d, self.td.dict)

        # item sequence
        self.m(2, 'an', set=True)
        d = self._empty_mapping()
        d.update(self.td.items)
        self.assertEqual(d, self.td.dict)

        # Both item sequence and keyword arguments
        d = self._empty_mapping()
        d.update(self.td.items, **self.td.dict)
        self.assertEqual(d, self.td.dict)

        # iterator
        td1 = self.m(2, 'nn')
        td2 = self.m(3, 'nn')
        td1.test_obj.update(td2.test_obj.items())
        te = td1.dict
        te.update(td2.dict)
        self.assertEqual(td1, te)

        class SimpleUserDict:
            def __init__(self):
                self.d = {1:1, 2:2, 3:3}
            def keys(self):
                return self.d.keys()
            def __getitem__(self, i):
                return self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        self.assertEqual(d, {1:1, 2:2, 3:3})



    # no test_fromkeys or test_copy as both os.environ and selves don't support it

    def test_fromkeys(self):
        # from mapping
        self.assertEqual(self.type2test.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        d = self._empty_mapping()
        self.assertTrue(not(d.fromkeys('abc') is d))
        self.assertEqual(d.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        self.assertEqual(d.fromkeys((4,5),0), {4:0, 5:0})
        self.assertEqual(d.fromkeys([]), {})
        def g():
            yield 1
        self.assertEqual(d.fromkeys(g()), {1:None})
        self.assertRaises(TypeError, {}.fromkeys, 3)
        class dictlike(self.type2test): pass
        self.assertEqual(dictlike.fromkeys('a'), {'a':None})
        self.assertEqual(dictlike().fromkeys('a'), {'a':None})
        self.assertTrue(dictlike.fromkeys('a').__class__ is dictlike)
        self.assertTrue(dictlike().fromkeys('a').__class__ is dictlike)
        self.assertTrue(type(dictlike.fromkeys('a')) is dictlike)
        class mydict(self.type2test):
            def __new__(cls):
                return collections.UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, {'a':None, 'b':None})
        self.assertIsInstance(ud, collections.UserDict)
        self.assertRaises(TypeError, dict.fromkeys)

        class Exc(Exception): pass

        class baddict1(self.type2test):
            def __init__(self):
                raise Exc()

        self.assertRaises(Exc, baddict1.fromkeys, [1])

        class BadSeq(object):
            def __iter__(self):
                return self
            def __next__(self):
                raise Exc()

        self.assertRaises(Exc, self.type2test.fromkeys, BadSeq())

        class baddict2(self.type2test):
            def __setitem__(self, key, value):
                raise Exc()

        self.assertRaises(Exc, baddict2.fromkeys, [1])

        # from hash

        TestMappingProtocol.test_fromkeys(self)
        class mydict(self.type2test):
            def __new__(cls):
                return collections.UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, {'a':None, 'b':None})
        self.assertIsInstance(ud, collections.UserDict)



    def test_copy(self):
        # from mapping
        d = self._full_mapping({1:1, 2:2, 3:3})
        self.assertEqual(d.copy(), {1:1, 2:2, 3:3})
        d = self._empty_mapping()
        self.assertEqual(d.copy(), d)
        self.assertIsInstance(d.copy(), d.__class__)
        self.assertRaises(TypeError, d.copy, None)




    def test_clear(self):
        # from mapping
        self.td.test_obj.clear()
        self.assertEqual(self.td.test_obj, {})

        self.assertRaises(TypeError, self.td.test_obj.clear, None)


    def test_get(self):
        d = self._empty_mapping()
        self.assertTrue(d.get(list(self.other.keys())[0]) is None)
        self.assertEqual(d.get(list(self.other.keys())[0], 3), 3)
        d = self.reference
        self.assertTrue(d.get(list(self.other.keys())[0]) is None)
        self.assertEqual(d.get(list(self.other.keys())[0], 3), 3)
        self.assertEqual(d.get(list(self.inmapping.keys())[0]),
                         list(self.inmapping.values())[0])
        self.assertEqual(d.get(list(self.inmapping.keys())[0], 3),
                         list(self.inmapping.values())[0])
        self.assertRaises(TypeError, d.get)
        self.assertRaises(TypeError, d.get, None, None, None)

        # from mapping
        BasicTestMappingProtocol.test_get(self)
        d = self._empty_mapping()
        self.assertTrue(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        d = self._full_mapping({'a' : 1, 'b' : 2})
        self.assertTrue(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)



    def test_setdefault(self):
        d = self._empty_mapping()
        self.assertRaises(TypeError, d.setdefault)

        # from mapping
        d = self._empty_mapping()
        self.assertTrue(d.setdefault('key0') is None)
        d.setdefault('key0', [])
        self.assertTrue(d.setdefault('key0') is None)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)

        # from hash

        TestMappingProtocol.test_setdefault(self)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.setdefault, x, [])


    def test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)
        self.assertRaises(TypeError, d.popitem, 42)

        # from mapping

        BasicTestMappingProtocol.test_popitem(self)
        for copymode in -1, +1:
            # -1: b has same structure as a
            # +1: b is a.copy()
            for log2size in range(12):
                size = 2**log2size
                a = self._empty_mapping()
                b = self._empty_mapping()
                for i in range(size):
                    a[repr(i)] = i
                    if copymode < 0:
                        b[repr(i)] = i
                if copymode > 0:
                    b = a.copy()
                for i in range(size):
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, int(ka))
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, int(kb))
                    self.assertTrue(not(copymode < 0 and ta != tb))
                self.assertTrue(not a)
                self.assertTrue(not b)



    def test_pop(self):
        d = self._empty_mapping()
        k, v = list(self.inmapping.items())[0]
        d[k] = v
        self.assertRaises(KeyError, d.pop, list(self.other.keys())[0])

        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)

        self.assertRaises(KeyError, d.pop, k)

        # from mapping


        # Tests for pop with specified key
        d = self._empty_mapping()
        k, v = 'abc', 'def'

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)

        # from hash

        TestMappingProtocol.test_pop(self)

        class Exc(Exception):
            pass

        class BadHash(object):
            fail = False

            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.pop, x)

    def test_mutatingiteration(self):
        # from hash
        d = self._empty_mapping()
        d[1] = 1
        try:
            for i in d:
                d[i+1] = 1
        except RuntimeError:
            pass
        else:
            self.fail("changing dict size during iteration doesn't raise Error")

    def test_repr(self):
        # from hash
        d = self._empty_mapping()
        self.assertEqual(repr(d), '{}')
        d[1] = 2
        self.assertEqual(repr(d), '{1: 2}')
        d = self._empty_mapping()
        d[1] = d
        self.assertEqual(repr(d), '{1: {...}}')

        class Exc(Exception): pass

        class BadRepr(object):
            def __repr__(self):
                raise Exc()

        d = self._full_mapping({1: BadRepr()})
        self.assertRaises(Exc, repr, d)

    def test_repr_deep(self):
        # from hash
        d = self._empty_mapping()
        for i in range(sys.getrecursionlimit() + 100):
            d0 = d
            d = self._empty_mapping()
            d[1] = d0
        self.assertRaises(RecursionError, repr, d)

    def test_eq(self):
        # from hash
        self.assertEqual(self._empty_mapping(), self._empty_mapping())
        self.assertEqual(self._full_mapping({1: 2}),
                         self._full_mapping({1: 2}))

        class Exc(Exception): pass

        class BadCmp(object):
            def __eq__(self, other):
                raise Exc()
            def __hash__(self):
                return 1

        d1 = self._full_mapping({BadCmp(): 1})
        d2 = self._full_mapping({1: 1})
        self.assertRaises(Exc, lambda: BadCmp()==1)
        self.assertRaises(Exc, lambda: d1==d2)


'''

class BasicTestMappingProtocol(object):
    # This base class can be used to check that an object conforms to the
    # mapping protocol

    # Functions that can be useful to override to adapt to dictionary
    # semantics
    type2test = None  # which class is being tested (overwrite in subclasses)

    alph = NxtAlpha
    nums = NxtNum
    sets = NxtSet

    def setUp(self):
        self.tdm.clear()
        self.m(set=True)
        super(BasicTestMappingProtocol, self).setUp()
    
    def m(self, *args, set=False):
        tmp_ret = self.tdm.make(*args)
        if set:
            self.td = tmp_ret
        return tmp_ret

    def _reference(self):
        """Return a dictionary of values which are invariant by storage
        in the object under test."""
        # return {"one": "two", "key1": "value1", "key2": (1, 2, 3)}
        tmp_td = self.m('aa', 'aa', 'as')
        return tmp_td.dict

    def _empty_mapping(self):
        """Return an empty mapping object"""
        return self.type2test()


    def _full_mapping(self, *args, **kwargs):
        if kwargs:
            x = self._empty_mapping()
            for key, value in kwargs.items():
                x[key] = value
            return x
        else: 
            if not args:
                args = ['an', 'an']
            elif isinstance(args[0], dict):
                x = self._empty_mapping()
                for key, value in args[0].items():
                    x[key] = value
                return x
            return self.m(*args).test_obj
        
    def __init__(self, *args, **kw):
        self.tdm = TestDataManager(alphas=self.alph, nums=self.nums, sets=self.sets, test_obj=self.type2test)
        unittest.TestCase.__init__(self, *args, **kw)
        self.reference = self._reference().copy()

        # A (key, value) pair not in the mapping
        key, value = self.reference.popitem()
        self.other = {key: value}

        # A (key, value) pair in the mapping
        key, value = self.reference.popitem()
        self.inmapping = {key: value}
        self.reference[key] = value

    def test_read(self):
        # Test for read only operations on mapping
        p = self._empty_mapping()
        p1 = dict(p) #workaround for singleton objects
        d = self._full_mapping(self.reference)
        if d is p:
            p = p1
        #Indexing
        for key, value in self.reference.items():
            self.assertEqual(d[key], value)
        knownkey = list(self.other.keys())[0]
        self.assertRaises(KeyError, lambda:d[knownkey])
        #len
        self.assertEqual(len(p), 0)
        self.assertEqual(len(d), len(self.reference))
        #__contains__
        for k in self.reference:
            self.assertIn(k, d)
        for k in self.other:
            self.assertNotIn(k, d)
        #cmp
        self.assertEqual(p, p)
        self.assertEqual(d, d)
        self.assertNotEqual(p, d)
        self.assertNotEqual(d, p)
        #bool
        if p: self.fail("Empty mapping must compare to False")
        if not d: self.fail("Full mapping must compare to True")
        # keys(), items(), iterkeys() ...
        def check_iterandlist(iter, lst, ref):
            self.assertTrue(hasattr(iter, '__next__'))
            self.assertTrue(hasattr(iter, '__iter__'))
            x = list(iter)
            self.assertTrue(set(x)==set(lst)==set(ref))
        check_iterandlist(iter(d.keys()), list(d.keys()),
                          self.reference.keys())
        check_iterandlist(iter(d), list(d.keys()), self.reference.keys())
        check_iterandlist(iter(d.values()), list(d.values()),
                          self.reference.values())
        check_iterandlist(iter(d.items()), list(d.items()),
                          self.reference.items())
        #get
        key, value = next(iter(d.items()))
        knownkey, knownvalue = next(iter(self.other.items()))
        self.assertEqual(d.get(key, knownvalue), value)
        self.assertEqual(d.get(knownkey, knownvalue), knownvalue)
        self.assertNotIn(knownkey, d)

    def test_write(self):
        # Test for write operations on mapping
        p = self._empty_mapping()
        #Indexing
        for key, value in self.reference.items():
            p[key] = value
            self.assertEqual(p[key], value)
        for key in self.reference.keys():
            del p[key]
            self.assertRaises(KeyError, lambda:p[key])
        p = self._empty_mapping()
        #update
        p.update(self.reference)
        self.assertEqual(dict(p), self.reference)
        items = list(p.items())
        p = self._empty_mapping()
        p.update(items)
        self.assertEqual(dict(p), self.reference)
        d = self._full_mapping(self.reference)
        #setdefault
        key, value = next(iter(d.items()))
        knownkey, knownvalue = next(iter(self.other.items()))
        self.assertEqual(d.setdefault(key, knownvalue), value)
        self.assertEqual(d[key], value)
        self.assertEqual(d.setdefault(knownkey, knownvalue), knownvalue)
        self.assertEqual(d[knownkey], knownvalue)
        #pop
        self.assertEqual(d.pop(knownkey), knownvalue)
        self.assertNotIn(knownkey, d)
        self.assertRaises(KeyError, d.pop, knownkey)
        default = 909
        d[knownkey] = knownvalue
        self.assertEqual(d.pop(knownkey, default), knownvalue)
        self.assertNotIn(knownkey, d)
        self.assertEqual(d.pop(knownkey, default), default)
        #popitem
        key, value = d.popitem()
        self.assertNotIn(key, d)
        self.assertEqual(value, self.reference[key])
        p=self._empty_mapping()
        self.assertRaises(KeyError, p.popitem)

    def test_constructor(self):
        self.assertEqual(self._empty_mapping(), self._empty_mapping())

    def test_bool(self):
        self.assertTrue(not self._empty_mapping())
        self.assertTrue(self.reference)
        self.assertTrue(bool(self._empty_mapping()) is False)
        self.assertTrue(bool(self.reference) is True)

    def test_keys(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.keys()), [])
        d = self.reference
        self.assertIn(list(self.inmapping.keys())[0], d.keys())
        self.assertNotIn(list(self.other.keys())[0], d.keys())
        self.assertRaises(TypeError, d.keys, None)

    def test_values(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.values()), [])

        self.assertRaises(TypeError, d.values, None)

    def test_items(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.items()), [])

        self.assertRaises(TypeError, d.items, None)

    def test_len(self):
        d = self._empty_mapping()
        self.assertEqual(len(d), 0)

    def test_getitem(self):
        d = self.reference
        self.assertEqual(d[list(self.inmapping.keys())[0]],
                         list(self.inmapping.values())[0])

        self.assertRaises(TypeError, d.__getitem__)

    def test_update(self):
        # mapping argument
        d = self._empty_mapping()
        d.update(self.other)
        self.assertEqual(list(d.items()), list(self.other.items()))

        # No argument
        d = self._empty_mapping()
        d.update()
        self.assertEqual(d, self._empty_mapping())

        # item sequence
        d = self._empty_mapping()
        d.update(self.other.items())
        self.assertEqual(list(d.items()), list(self.other.items()))

        # Iterator
        d = self._empty_mapping()
        d.update(self.other.items())
        self.assertEqual(list(d.items()), list(self.other.items()))

        # FIXME: Doesn't work with UserDict
        # self.assertRaises((TypeError, AttributeError), d.update, None)
        self.assertRaises((TypeError, AttributeError), d.update, 42)

        outerself = self
        class SimpleUserDict:
            def __init__(self):
                self.d = outerself.reference
            def keys(self):
                return self.d.keys()
            def __getitem__(self, i):
                return self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        i1 = sorted(d.items())
        i2 = sorted(self.reference.items())
        self.assertEqual(i1, i2)

        class Exc(Exception): pass

        d = self._empty_mapping()
        class FailingUserDict:
            def keys(self):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        d.clear()

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = 1
                    def __iter__(self):
                        return self
                    def __next__(self):
                        if self.i:
                            self.i = 0
                            return 'a'
                        raise Exc
                return BogonIter()
            def __getitem__(self, key):
                return key
        self.assertRaises(Exc, d.update, FailingUserDict())

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = ord('a')
                    def __iter__(self):
                        return self
                    def __next__(self):
                        if self.i <= ord('z'):
                            rtn = chr(self.i)
                            self.i += 1
                            return rtn
                        raise StopIteration
                return BogonIter()
            def __getitem__(self, key):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        d = self._empty_mapping()
        class badseq(object):
            def __iter__(self):
                return self
            def __next__(self):
                raise Exc()

        self.assertRaises(Exc, d.update, badseq())

        self.assertRaises(ValueError, d.update, [(1, 2, 3)])

    # no test_fromkeys or test_copy as both os.environ and selves don't support it

    def test_get(self):
        d = self._empty_mapping()
        self.assertTrue(d.get(list(self.other.keys())[0]) is None)
        self.assertEqual(d.get(list(self.other.keys())[0], 3), 3)
        d = self.reference
        self.assertTrue(d.get(list(self.other.keys())[0]) is None)
        self.assertEqual(d.get(list(self.other.keys())[0], 3), 3)
        self.assertEqual(d.get(list(self.inmapping.keys())[0]),
                         list(self.inmapping.values())[0])
        self.assertEqual(d.get(list(self.inmapping.keys())[0], 3),
                         list(self.inmapping.values())[0])
        self.assertRaises(TypeError, d.get)
        self.assertRaises(TypeError, d.get, None, None, None)

    def test_setdefault(self):
        d = self._empty_mapping()
        self.assertRaises(TypeError, d.setdefault)

    def test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)
        self.assertRaises(TypeError, d.popitem, 42)

    def test_pop(self):
        d = self._empty_mapping()
        k, v = list(self.inmapping.items())[0]
        d[k] = v
        self.assertRaises(KeyError, d.pop, list(self.other.keys())[0])

        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)

        self.assertRaises(KeyError, d.pop, k)

class TestMappingProtocol(BasicTestMappingProtocol):
    def test_constructor(self):
        BasicTestMappingProtocol.test_constructor(self)
        self.assertTrue(self._empty_mapping() is not self._empty_mapping())
        self.assertEqual(self.type2test(**self.td.dict), self.td.dict)

    def test_bool(self):
        BasicTestMappingProtocol.test_bool(self)
        self.assertTrue(not self._empty_mapping())
        self.assertTrue(self.td.test_obj)
        self.assertTrue(bool(self._empty_mapping()) is False)
        self.assertTrue(bool(self.td.test_obj is True)

    def test_keys(self):
        BasicTestMappingProtocol.test_keys(self)
        d = self._empty_mapping()
        self.assertEqual(list(d.keys()), [])
        d = self.td.test_obj
        k = d.keys()
        self.assertIn(self.td.keys[0], k)
        self.assertIn(self.td.keys[0], k)
        self.assertNotIn('__foobar__', k)

    def test_values(self):
        BasicTestMappingProtocol.test_values(self)
        self.assertEqual(list(self.td.test_obj.values()), self.td.values)

    def test_items(self):
        BasicTestMappingProtocol.test_items(self)
        self.assertEqual(list(self.td.items()), self.td.items)

    def test_contains(self):
        d = self._empty_mapping()
        self.assertNotIn('a', d)
        self.assertTrue(not ('a' in d))
        self.assertTrue('a' not in d)
        self.assertIn(self.td.keys[0], self.td.test_obj)
        self.assertIn(self.td.keys[1], self.td.test_obj)
        self.assertNotIn('__foobar__', d)

        self.assertRaises(TypeError, d.__contains__)

    def test_len(self):
        BasicTestMappingProtocol.test_len(self)
        self.assertEqual(len(self.td.test_obj), len(self.td.keys))

    def test_getitem(self):
        BasicTestMappingProtocol.test_getitem(self)

        self.assertEqual(self.td.test_obj[self.td.keys[0]], self.td.values[0])
        self.assertEqual(self.td.test_obj[self.td.keys[1]], self.td.values[1])

        self.td.test_obj[self.td.next_keys[0]] = self.td.next_values[0]
        self.td.test_obj[self.td.keys[0]] = self.td.next_values[1]
        self.assertEqual(self.td.test_obj[self.td.next_keys[0]], self.td.next_values[0])
        self.assertEqual(self.td.test_obj[self.td.keys[0]], self.td.next_values[1])
        del self.td.test_obj[self.td.keys[1]]
        self.assertEqual(self.td.test_obj, {self.td.keys[0]: self.td.next_values[1], self.td.next_keys[0]: self.td.next_values[0]})

        self.assertRaises(TypeError, self.td.test_obj.__getitem__)

    def test_clear(self):

        self.td.test_obj.clear()
        self.assertEqual(self.td.test_obj, {})

        self.assertRaises(TypeError, self.td.test_obj.clear, None)

    def test_update(self):
        BasicTestMappingProtocol.test_update(self)
        # mapping argument
        d = self._empty_mapping()
        self.m(3, 'nn', set=True)
        d.update({self.td.keys[0]:100})
        d.update({self.td.keys[1]:20})
        d.update(self.td.dict)
        self.assertEqual(d, self.td.dict)

        # no argument
        d.update()
        self.assertEqual(d, self.td.dict)

        # keyword arguments
        d = self._empty_mapping()
        self.m(3, 'an', set=True)
        kw1 = {self.td.keys[0]: 100}
        kw2 = {self.td.keys[1]: 20}
        d.update(**kw1)
        d.update(**kw2)
        d.update(**self.td.dict)
        self.assertEqual(d, self.td.dict)

        # item sequence
        self.m(2, 'an', set=True)
        d = self._empty_mapping()
        d.update(self.td.items)
        self.assertEqual(d, self.td.dict)

        # Both item sequence and keyword arguments
        d = self._empty_mapping()
        d.update(self.td.items, **self.td.dict)
        self.assertEqual(d, self.td.dict)

        # iterator
        td1 = self.m(2, 'nn')
        td2 = self.m(3, 'nn')
        td1.test_obj.update(td2.test_obj.items())
        te = td1.dict
        te.update(td2.dict)
        self.assertEqual(td1, te)

        class SimpleUserDict:
            def __init__(self):
                self.d = {1:1, 2:2, 3:3}
            def keys(self):
                return self.d.keys()
            def __getitem__(self, i):
                return self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        self.assertEqual(d, {1:1, 2:2, 3:3})

    def test_fromkeys(self):
        self.assertEqual(self.type2test.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        d = self._empty_mapping()
        self.assertTrue(not(d.fromkeys('abc') is d))
        self.assertEqual(d.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        self.assertEqual(d.fromkeys((4,5),0), {4:0, 5:0})
        self.assertEqual(d.fromkeys([]), {})
        def g():
            yield 1
        self.assertEqual(d.fromkeys(g()), {1:None})
        self.assertRaises(TypeError, {}.fromkeys, 3)
        class dictlike(self.type2test): pass
        self.assertEqual(dictlike.fromkeys('a'), {'a':None})
        self.assertEqual(dictlike().fromkeys('a'), {'a':None})
        self.assertTrue(dictlike.fromkeys('a').__class__ is dictlike)
        self.assertTrue(dictlike().fromkeys('a').__class__ is dictlike)
        self.assertTrue(type(dictlike.fromkeys('a')) is dictlike)
        class mydict(self.type2test):
            def __new__(cls):
                return collections.UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, {'a':None, 'b':None})
        self.assertIsInstance(ud, collections.UserDict)
        self.assertRaises(TypeError, dict.fromkeys)

        class Exc(Exception): pass

        class baddict1(self.type2test):
            def __init__(self):
                raise Exc()

        self.assertRaises(Exc, baddict1.fromkeys, [1])

        class BadSeq(object):
            def __iter__(self):
                return self
            def __next__(self):
                raise Exc()

        self.assertRaises(Exc, self.type2test.fromkeys, BadSeq())

        class baddict2(self.type2test):
            def __setitem__(self, key, value):
                raise Exc()

        self.assertRaises(Exc, baddict2.fromkeys, [1])

    def test_copy(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        self.assertEqual(d.copy(), {1:1, 2:2, 3:3})
        d = self._empty_mapping()
        self.assertEqual(d.copy(), d)
        self.assertIsInstance(d.copy(), d.__class__)
        self.assertRaises(TypeError, d.copy, None)

    def test_get(self):
        BasicTestMappingProtocol.test_get(self)
        d = self._empty_mapping()
        self.assertTrue(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        d = self._full_mapping({'a' : 1, 'b' : 2})
        self.assertTrue(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)

    def test_setdefault(self):
        BasicTestMappingProtocol.test_setdefault(self)
        d = self._empty_mapping()
        self.assertTrue(d.setdefault('key0') is None)
        d.setdefault('key0', [])
        self.assertTrue(d.setdefault('key0') is None)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)

    def test_popitem(self):
        BasicTestMappingProtocol.test_popitem(self)
        for copymode in -1, +1:
            # -1: b has same structure as a
            # +1: b is a.copy()
            for log2size in range(12):
                size = 2**log2size
                a = self._empty_mapping()
                b = self._empty_mapping()
                for i in range(size):
                    a[repr(i)] = i
                    if copymode < 0:
                        b[repr(i)] = i
                if copymode > 0:
                    b = a.copy()
                for i in range(size):
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, int(ka))
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, int(kb))
                    self.assertTrue(not(copymode < 0 and ta != tb))
                self.assertTrue(not a)
                self.assertTrue(not b)

    def test_pop(self):
        BasicTestMappingProtocol.test_pop(self)

        # Tests for pop with specified key
        d = self._empty_mapping()
        k, v = 'abc', 'def'

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)


class TestHashMappingProtocol(TestMappingProtocol):

    def test_getitem(self):
        TestMappingProtocol.test_getitem(self)
        class Exc(Exception): pass

        class BadEq(object):
            def __eq__(self, other):
                raise Exc()
            def __hash__(self):
                return 24

        d = self._empty_mapping()
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.__getitem__, x)

    def test_fromkeys(self):
        TestMappingProtocol.test_fromkeys(self)
        class mydict(self.type2test):
            def __new__(cls):
                return collections.UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, {'a':None, 'b':None})
        self.assertIsInstance(ud, collections.UserDict)

    def test_pop(self):
        TestMappingProtocol.test_pop(self)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.pop, x)

    def test_mutatingiteration(self):
        d = self._empty_mapping()
        d[1] = 1
        try:
            for i in d:
                d[i+1] = 1
        except RuntimeError:
            pass
        else:
            self.fail("changing dict size during iteration doesn't raise Error")

    def test_repr(self):
        d = self._empty_mapping()
        self.assertEqual(repr(d), '{}')
        d[1] = 2
        self.assertEqual(repr(d), '{1: 2}')
        d = self._empty_mapping()
        d[1] = d
        self.assertEqual(repr(d), '{1: {...}}')

        class Exc(Exception): pass

        class BadRepr(object):
            def __repr__(self):
                raise Exc()

        d = self._full_mapping({1: BadRepr()})
        self.assertRaises(Exc, repr, d)

    def test_repr_deep(self):
        d = self._empty_mapping()
        for i in range(sys.getrecursionlimit() + 100):
            d0 = d
            d = self._empty_mapping()
            d[1] = d0
        self.assertRaises(RecursionError, repr, d)

    def test_eq(self):
        self.assertEqual(self._empty_mapping(), self._empty_mapping())
        self.assertEqual(self._full_mapping({1: 2}),
                         self._full_mapping({1: 2}))

        class Exc(Exception): pass

        class BadCmp(object):
            def __eq__(self, other):
                raise Exc()
            def __hash__(self):
                return 1

        d1 = self._full_mapping({BadCmp(): 1})
        d2 = self._full_mapping({1: 1})
        self.assertRaises(Exc, lambda: BadCmp()==1)
        self.assertRaises(Exc, lambda: d1==d2)

    def test_setdefault(self):
        TestMappingProtocol.test_setdefault(self)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.setdefault, x, [])
    
'''
