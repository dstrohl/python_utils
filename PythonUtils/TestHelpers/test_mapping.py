# pulled from the CPython core: https://raw.githubusercontent.com/python/cpython/master/Lib/test/mapping_tests.py
# and modified to test a passed object to make sure it conforms to mapping methods and processes.

# tests common to dict and UserDict

# ******************************************************************************
# Test Dictionary Like Objects TestCase
# ******************************************************************************


class TestDictLikeObject(unittest.TestCase):
    maxDiff = None
    # This base class can be used to check that an object conforms to the
    # mapping protocol

    # Functions that can be useful to override to adapt to dictionary
    # semantics
    type2test = dict  # which class is being tested (overwrite in subclasses)


    # alph = NxtAlpha
    # nums = NxtNum
    # sets = NxtSet
    max_keys = 25 * 25 * 25

    only_string_keys = False
    skip_test_names = []
    allow_numeric_values = True
    allow_numeric_keys = True

    expected_repr_mt = None
    expected_repr_base = None

    keys_report = True

    options_to_test = [
        'clear',
        'copy',
        'copy_func', # tests using copy() builtin instead of dict.copy()
        'deepcopy',
        'fromkeys',
        'items',
        'keys',
        'values',
        'dict_view_returned',  # tests that object returnd from keys, items, values is a dict_view
        'get',
        'pop',
        'popitem',
        'setdefault',
        'update',
        '__contains__',
        '__bool__',
        '__delitem__',
        '__eq__',
        '__init__',
        '__iter__',
        '__len__',
        '__new__',
        '__ne__',
        '__repr__',  # should update expected __repr__ strings
        '__setitem__', # REQUIRED to work for tests
        '__getitem__', # REQUIRED to work for tests
        '__sizeof__',  # Or Length
        'only_hashable_keys', # tests that non-hashable keys fail
        'subclass', # tests subclassing
        'subfail',  # tests that the object is not masking exceptions
        'ordered', # tests that returned values are ordered.
        'invalid_arg',  # tests that invalid args will raise exc.
        'invalid_attr',  # tests that methods called as attrs raise exc..
        'keyerror',  # raises keyerror on no match
        'no_userdict', # some tests will fail on UserDict based classes.
        'scale', # tests with larger numbers of objects.
        'raise',  # Test to make sure object is raising correct exceptions
    ]

    @classmethod
    def setUpClass(cls):

        cls.items = None
        cls.values = None
        cls.keys = None
        cls.dict_size = 0
        cls.dict = None
        cls.mt = None
        cls.test_obj = None
        cls._skip_keys = {}
        cls._missing_skip_keys = None
        cls._test_count = 0

        cls.possible_values_list = None
        cls.possible_keys_list = None
        cls.possible_alpha_keys_list = None
        cls.invalid_keys_list = None
        cls.invalid_values_list = None

        cls._all_keys = TestDictLikeObject.options_to_test
        cls._missing_skip_keys = cls._all_keys.copy()

        class userdict(cls.type2test):

            def __new__(self):
                return collections.UserDict()

        cls.userdict = userdict

        class baddict1(cls.type2test):

            def __init__(self):
                raise FixtureExc()

        cls.bad_init = baddict1

        class BadSeq(object):

            def __iter__(self):
                return self

            def __next__(self):
                raise FixtureExc()

        cls.bad_next = BadSeq

        class baddict2(cls.type2test):

            def __setitem__(self, key, value):
                raise FixtureExc()

        cls.bad_subclass_setitem = baddict2

        class BadEq(object):

            def __eq__(self, other):
                raise FixtureExc()

            def __hash__(self):
                return 24

        cls.bad_eq = BadEq

        class BadHash(object):
            fail = False

            def __hash__(self):
                if self.fail:
                    raise FixtureExc()
                else:
                    return 42

        cls.bad_hash_on_call = BadHash

        class SameHashNe(object):

            def __init__(self, value):
                self.value=value

            def __eq__(self, other):
                return other == self.value

            def __hash__(self):
                return 42

            def __repr__(self):
                return "SameHash:%s (hash: %s)" % (self.value, hash(self))

        cls.same_hash_ne = SameHashNe

        class SameHashEq(object):
            validate_str = '__Validate__'

            def __init__(self, value):
                self.value=value

            def __eq__(self, other):
                return other.validate_str == self.validate_str

            def __hash__(self):
                return 42

            def __repr__(self):
                return "SameHash:%s (hash: %s)" % (self.value, hash(self))

        cls.same_hash_eq = SameHashEq

        class BadHash2(object):

            def __hash__(self):
                raise FixtureExc()

        cls.bad_hash = BadHash2

        class SimpleUserDict(object):

            def __init__(self, dict_in):
                self.d = dict_in

            def keys(self):
                return self.d.keys()

            def __getitem__(self, i):
                return self.d[i]

        cls.user_dict = SimpleUserDict

        class FailingUserDict(object):

            def keys(self):
                raise FixtureExc

        cls.bad_keys = FailingUserDict

        class FailingUserDict2(object):

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
                        raise FixtureExc

                return BogonIter()

            def __getitem__(self, key):
                return key

        cls.bad_user_next = FailingUserDict2

        class FailingUserDict3(object):

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
                raise FixtureExc

        cls.bad_user_getitem = FailingUserDict3

        class BadRepr(object):

            def __repr__(self):
                raise FixtureExc()

        cls.bad_repr = BadRepr

        class BadCmp(object):

            def __eq__(self, other):
                raise FixtureExc()

            def __hash__(self):
                return 1

        cls.bad_cmp = BadCmp



    """
    def __init__(self, *args, **kw):

        self.items = None
        self.values = None
        self.keys = None
        self.dict_size = 0
        self.dict = None
        self.mt = None
        self.test_obj = None
        self._skip_keys = {}
        self._missing_skip_keys = None
        self._test_count = 0
        self.possible_values_list = self._get_values()
        self.possible_keys_list = self._get_keys()
        self.possible_alpha_keys_list = self._get_alpha_keys()
        self.invalid_keys_list = self._get_invalid_keys()
        self.invalid_values_list = self._get_invalid_values()

        class userdict(self.type2test):

            def __new__(cls):
                return collections.UserDict()

        self.userdict = userdict

        class baddict1(self.type2test):

            def __init__(self):
                raise FixtureExc()

        self.bad_init = baddict1

        class BadSeq(object):

            def __iter__(self):
                return self

            def __next__(self):
                raise FixtureExc()

        self.bad_next = BadSeq

        class baddict2(self.type2test):

            def __setitem__(self, key, value):
                raise FixtureExc()

        self.bad_subclass_setitem = baddict2

        class BadEq(object):

            def __eq__(self, other):
                raise FixtureExc()

            def __hash__(self):
                return 24

        self.bad_eq = BadEq

        class BadHash(object):
            fail = False

            def __hash__(self):
                if self.fail:
                    raise FixtureExc()
                else:
                    return 42

        self.bad_hash_on_call = BadHash

        class SameHashNe(object):

            def __init__(self, value):
                self.value=value

            def __eq__(self, other):
                return other == self.value

            def __hash__(self):
                return 42

            def __repr__(self):
                return "SameHash:%s (hash: %s)" % (self.value, hash(self))

        self.same_hash_ne = SameHashNe

        class SameHashEq(object):
            validate_str = '__Validate__'

            def __init__(self, value):
                self.value=value

            def __eq__(self, other):
                return other.validate_str == self.validate_str

            def __hash__(self):
                return 42

            def __repr__(self):
                return "SameHash:%s (hash: %s)" % (self.value, hash(self))

        self.same_hash_eq = SameHashEq

        class BadHash2(object):

            def __hash__(self):
                raise FixtureExc()

        self.bad_hash = BadHash2

        class SimpleUserDict(object):

            def __init__(self, dict_in):
                self.d = dict_in

            def keys(self):
                return self.d.keys()

            def __getitem__(self, i):
                return self.d[i]

        self.user_dict = SimpleUserDict

        class FailingUserDict(object):

            def keys(self):
                raise FixtureExc

        self.bad_keys = FailingUserDict

        class FailingUserDict2(object):

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
                        raise FixtureExc

                return BogonIter()

            def __getitem__(self, key):
                return key

        self.bad_user_next = FailingUserDict2

        class FailingUserDict3(object):

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
                raise FixtureExc

        self.bad_user_getitem = FailingUserDict3

        class BadRepr(object):

            def __repr__(self):
                raise FixtureExc()

        self.bad_repr = BadRepr

        class BadCmp(object):

            def __eq__(self, other):
                raise FixtureExc()

            def __hash__(self):
                return 1

        self.bad_cmp = BadCmp

        unittest.TestCase.__init__(self, *args, **kw)
    """
    
    def _make_value_list(self, qty, allow_numeric=True):
        alphas = 'abcdefghijklmnopqrstuvwxyz'

        def _get_next_round_robin_int(current):
            if current >= 25:
                return 1
            else:
                return current + 1

        chr_1_offset = -1
        chr_2_offset = -1
        chr_3_offset = -1

        tmp_ret = []

        i = 0
        while len(tmp_ret) < qty:
            i += 1
            chr_3_offset = _get_next_round_robin_int(chr_3_offset)
            if chr_3_offset == 1:
                chr_2_offset = _get_next_round_robin_int(chr_2_offset)
                if chr_2_offset == 1:
                    chr_1_offset = _get_next_round_robin_int(chr_1_offset)
            tmp_key = alphas[chr_1_offset] + alphas[chr_2_offset] + alphas[chr_3_offset]
            tmp_ret.append(tmp_key)
            # print('Offsets: %s:%s:%s, key: %s' % (chr_1_offset, chr_2_offset, chr_3_offset, tmp_key))

            if allow_numeric:
                tmp_ret.append(i)
        return tmp_ret

    def _convert_test_obj_dict(self, result_obj):
        """
        override this if test_dict does not support conversion this way, this should convert the object to a
        standard dictionary for data_validation

        :param result_obj: your test_object
        :return: a standard dictionary
        """
        return dict(result_obj)

    def _get_values(self):
        """
        should return a list of at least 100 values that are valid to use (can return as low as 10 if the ordering tests are skipped)

        by default this returns a list of strings and numbers, if allow_numeric_values == True (interspersed).
        :return:
        """
        return self._make_value_list(100, allow_numeric=self.allow_numeric_values)

    def _get_invalid_values(self):
        """
        should return a list of any invalid values that will raise an exception. along wth the exception expected.
        for example:
            [(<invalid_value>, KeyError), (<invalid_value>, AttributeError)]

        By default, this returns []
        :return:
        """
        return []

    def _get_keys(self):
        """
        should return a list of at least 100 values that are valid to use.  (can return as low as 10 if the ordering tests are skipped)

        by default this returns a list of strings and numbers, if allow_numeric_keys == True (interspersed).
        :return:
        """
        return self._make_value_list(100, allow_numeric=self.allow_numeric_keys)

    def _get_alpha_keys(self):
        """
        should return a list of at least 100 values that are valid to use (should only return alpha chars).  (can return as low as 10 if the ordering tests are skipped)

        this list is used when testing using keys as kwargs

        by default this returns a list of strings and numbers, if allow_numeric_keys == True (interspersed).
        :return:
        """
        return self._make_value_list(100, allow_numeric=False)

    def _get_invalid_keys(self):
        """
        should return a list of any invalid values that will raise an exception. along wth the exception expected.
        for example:
            [([1,2,3], TypeError), (None, TypeError)]
        by default, this returns a list of non-hashable objects.
        """
        return [
            ([1, 2, 3], TypeError),
        ]
    
    def _make_obj(self, *args, **kwargs):
        """
        overwrite if needed to modify the constructor of the test.
        """
        return self.type2test(*args, **kwargs)        

    def _set_data(self, *args, __size__=2, __alpha_only__=False, **kwargs):
        self.next_values = self.possible_values_list.copy()
        if __alpha_only__:
            self.next_keys = self.possible_alpha_keys_list.copy()
        else:
            self.next_keys = self.possible_keys_list.copy()

        self.dict = dict()
        if args or kwargs:
            self.dict = dict(*args, **kwargs)
        elif __size__:
            for i in range(__size__):
                self._shift_data(update=False) 

        if self.dict:
            self.test_obj = self._make_obj(self.dict)
        else:
            self.test_obj = self._make_obj()

        self.mt = self._make_obj()
        self._update_data()

    def _update_data(self):
        self.items = list(self.dict.items())
        self.keys = list(self.dict.keys())
        self.values = list(self.dict.values())
        self.dict_size = len(self.keys)
        for key in self.keys:
            if key in self.next_keys:
                self.next_keys.remove(key)

    def _shift_data(self, update=True):
        self.dict_size += 1
        next_key = self.next_keys.pop(-1)
        next_value = self.next_values.pop(-1)
        self.dict[next_key] = next_value
        if update:
            self._update_data()        

    def _init_tests_(self):
        self.possible_values_list = self._get_values()
        self.possible_keys_list = self._get_keys()
        self.possible_alpha_keys_list = self._get_alpha_keys()
        self.invalid_keys_list = self._get_invalid_keys()
        self.invalid_values_list = self._get_invalid_values()
        # self._all_keys = TestDictLikeObject.options_to_test
        # self._missing_skip_keys = self._all_keys.copy()

    def setUp(self):
        if self.possible_keys_list is None:
            self._init_tests_()

        self.bad_hash_on_call.fail = False

        self._test_count += 1
        tmp_id = self.id()
        tmp_id = '.' + tmp_id.rsplit('.', maxsplit=1)[1]
        if tmp_id in self.skip_test_names:
            self.skipTest('In Skip List')
        else:
            self._set_data()

    def td_len(self, result_obj=None):
        tmp_dict = self._convert_test_obj_dict(result_obj)
        return len(tmp_dict)

    def verify_dict(self, result_dict=None, expected_dict=None, **kwargs):
        if expected_dict is None:
            expected_dict = self.dict.copy()

        if kwargs:
            for key, value in kwargs.items():
                if value == '__del__':
                    del expected_dict[key]
                else:
                    expected_dict[key] = value                

        result_dict = self._convert_test_obj_dict(result_dict)

        self.assertEqual(expected_dict, result_dict)

    def verify_td(self, expected_dict=None):
        self.verify_dict(result_dict=self.test_obj, expected_dict=expected_dict)

    def verify_mt(self, expected_dict=None):
        self.verify_dict(result_dict=self.mt, expected_dict=expected_dict)
    
    def check_for_skip(self, *args):

        if not args:
            raise AttributeError('No options defined for this test')
        for a in args:
            if a not in self._all_keys:
                raise AttributeError('Invalid Skip Key Found: %r in %s' % (a, self.id()))
            if a not in self.options_to_test:
                self.skipTest('%s not a selected option to test' % a)
            if a in self._missing_skip_keys:
                self._missing_skip_keys.remove(a)

            if a in self._skip_keys:
                self._skip_keys[a] += 1
            else:
                self._skip_keys[a] = 1

    def test_zzz(self):
        # runs after all other tests reporting on test status
        print('Test_Count: %s' % self._test_count)
        print('Tests Skipped: %s' % self._missing_skip_keys)
        print('Tests Run: %s' % self._skip_keys)

    def test_verify_value_builder(self):

        test_obj = {}

        def run_verify(key_list, check_str=True):
            test_obj.clear()
            for i, key in enumerate(key_list):
                if key in test_obj:
                    self.fail('Duplicate key found: %s (at count %s of %s)' % (key, i, len(key_list)))
                if check_str and not isinstance(key, str):
                    self.fail('Non-str key found: %s (at count %s of %s)' % (key, i, len(key_list)))
                test_obj[key] = None

        run_verify(self._make_value_list(self.max_keys), check_str=False)
        run_verify(self._make_value_list(self.max_keys, allow_numeric=False), check_str=True)
        run_verify(self.possible_keys_list, check_str=False)
        run_verify(self.possible_alpha_keys_list, check_str=True)

    def test_constructor_basic(self):
        self.assertEqual(self.mt, self._make_obj())

    def test_constructor_makes_new_obj(self):
        self.assertTrue(self._make_obj() is not self._make_obj())

    def test_constructor_from_kwargs(self):
        self._set_data(__alpha_only__=True)
        self.verify_dict(self.type2test(**self.dict), self.dict)

    def test_constrictor_fromkeys_str(self):
        self.check_for_skip('fromkeys')
        self.verify_dict(self.type2test.fromkeys('abc'), {'a': None, 'b': None, 'c': None})

    def test_constructor_fromkeys_str_makes_new(self):
        self.check_for_skip('fromkeys')
        self.assertTrue(not(self.mt.fromkeys('abc') is self.mt))

    def test_constructor_fromkeys_set_with_values(self):
        self.check_for_skip('fromkeys')
        self.verify_dict(self.mt.fromkeys('abc'), {'a': None, 'b': None, 'c': None})
        self.verify_dict(self.mt.fromkeys((self.keys[0],self.keys[1]),self.values[0]),
                         {self.keys[0]:self.values[0], self.keys[1]:self.values[0]})
        self.verify_dict(self.mt.fromkeys([]), {})

    def test_constructor_fromkeys_set_overwrite(self):
        self.check_for_skip('fromkeys')
        self.verify_dict(self.mt.fromkeys('abc'), {'a': None, 'b': None, 'c': None})
        self.verify_dict(self.mt.fromkeys([]), {})

    def test_constructor_fromkeys_iterator(self):
        self.check_for_skip('fromkeys')
        self.verify_dict(self.mt.fromkeys(iterator_fixture()), {1:None})
    
    def test_constructor_fromkeys_single_arg_raises(self):
        self.check_for_skip('fromkeys', 'raise')
        self.assertRaises(TypeError, self.mt.fromkeys, 3)

    def test_subclass(self):
        self.check_for_skip('subclass', 'fromkeys')
        class dictlike(self.type2test): pass
        self.verify_dict(dictlike.fromkeys('a'), {'a': None})
        self.verify_dict(dictlike().fromkeys('a'), {'a': None})
        self.assertTrue(dictlike.fromkeys('a').__class__ is dictlike)
        self.assertTrue(dictlike().fromkeys('a').__class__ is dictlike)
        self.assertTrue(type(dictlike.fromkeys('a')) is dictlike)

    def test_subclass_new_to_userdict(self):
        self.check_for_skip('subclass', 'raise')
        # Not sure what this one is supposed to test, but it was in the python test set.
        # To me, this seems like it is really only testing that UserDict works.
        ud = self.userdict.fromkeys('ab')
        self.assertEqual(ud, {'a':None, 'b':None})
        self.assertIsInstance(ud, collections.UserDict)
        self.assertRaises(TypeError, dict.fromkeys)

    def test_subclass_init_raises(self):
        self.check_for_skip('subclass', 'subfail')
        self.assertRaises(FixtureExc, self.bad_init.fromkeys, [1])

    def test_constructor_fromkeys_bad_seq_raises(self):
        self.check_for_skip('subfail')
        self.assertRaises(FixtureExc, self.type2test.fromkeys, self.bad_next())

    def test_subclass_setitem_raises(self):
        self.check_for_skip('subfail')
        self.assertRaises(FixtureExc, self.bad_subclass_setitem.fromkeys, [1])

    def test__bool__empty_not_true(self):
        self.check_for_skip('__bool__')
        self.assertTrue(not self.mt)

    def test__bool__not_empty_true(self):
        self.check_for_skip('__bool__')
        self.assertTrue(self.test_obj)

    def test_bool_empty_is_false(self):
        self.check_for_skip('__bool__')
        self.assertTrue(bool(self.mt) is False)

    def test_bool_not_empty_is_true(self):
        self.check_for_skip('__bool__')
        self.assertTrue(bool(self.test_obj) is True)

    def test_mt_keys(self):
        self.check_for_skip('keys')
        self.assertCountEqual(list(self.mt.keys()), [])

    @SkipIfPyLower(3, 7)
    def test_mt_keys_ordered(self):
        self.check_for_skip('keys', 'ordered')
        self.assertEqual(list(self.mt.keys()), [])

    def test_key_in_keys(self):
        self.check_for_skip('keys')
        self.assertIn(self.keys[0], self.test_obj.keys())

    def test_keys_len(self):
        self.check_for_skip('keys')
        self.assertEqual(len(self.keys), len(self.test_obj.keys()))

    def test_keys_iter(self):
        self.check_for_skip('keys')
        self.assertCountEqual(self.keys, list(self.test_obj.keys()))

    def test_key_not_in_keys(self):
        self.check_for_skip('keys')
        self.assertNotIn(self.next_keys[0], self.test_obj.keys())

    def test_keys_raises(self):
        self.check_for_skip('keys', 'invalid_arg', 'raise')
        self.assertRaises(TypeError, self.test_obj.keys, None)

    def test_mt_values(self):
        self.check_for_skip('values')
        self.assertEqual(list(self.mt.values()), [])

    def test_values_in_keys(self):
        self.check_for_skip('values')
        self.assertIn(self.values[0], self.test_obj.values())

    def test_values_len(self):
        self.check_for_skip('values')
        self.assertEqual(len(self.values), len(self.test_obj.values()))

    def test_values_iter(self):
        self.check_for_skip('values')
        self.assertCountEqual(self.values, list(self.test_obj.values()))

    @SkipIfPyLower(3, 7)
    def test_values_iter_ordered(self):
        self.check_for_skip('values', 'ordered')
        self.assertEqual(self.values, list(self.test_obj.values()))

    def test_items_not_in_values(self):
        self.check_for_skip('values')
        self.assertNotIn(self.next_values[0], self.test_obj.values())

    def test_values_raises(self):
        self.check_for_skip('values', 'invalid_arg', 'raise')
        self.assertRaises(TypeError, self.test_obj.values, None)

    def test_mt_items(self):
        self.check_for_skip('items')
        self.assertEqual(list(self.mt.items()), [])

    def test_items_in_items(self):
        self.check_for_skip('items')
        self.assertIn(self.items[0], self.test_obj.items())

    def test_items_len(self):
        self.check_for_skip('items')
        self.assertEqual(len(self.items), len(self.test_obj.items()))

    def test_items_iter(self):
        self.check_for_skip('items')
        self.assertCountEqual(self.items, list(self.test_obj.items()))

    @SkipIfPyLower(3, 7)
    def test_items_iter_ordered(self):
        self.check_for_skip('items', 'ordered')
        self.assertEqual(self.items, list(self.test_obj.items()))

    def test_items_not_in_items(self):
        self.check_for_skip('items')
        self.assertNotIn((self.next_keys[0], self.next_values[0]), self.test_obj.items())

    def test_items_raises(self):
        self.check_for_skip('items', 'invalid_arg', 'raise')
        self.assertRaises(TypeError, self.test_obj.items, None)

    def test_view_object_returned_from_keys(self):
        self.check_for_skip('keys', 'dict_view_returned')
        self.assertIsInstance(self.test_obj.keys(), self.dict.keys().__class__)

    def test_view_object_returned_from_items(self):
        self.check_for_skip('items', 'dict_view_returned')
        self.assertIsInstance(self.test_obj.items(), self.dict.items().__class__)

    def test_view_object_returned_from_values(self):
        self.check_for_skip('values', 'dict_view_returned')
        self.assertIsInstance(self.test_obj.values(), self.dict.values().__class__)

    def test_keys_object_del_from_dict(self):
        self.check_for_skip('dict_view_returned', 'keys', '__delitem__')
        tmp_keys = self.test_obj.keys()
        self.assertEqual(self.dict_size, len(tmp_keys))
        del self.test_obj[self.keys[0]]
        self.assertEqual(self.dict_size - 1, len(tmp_keys))

    def test_values_object_del_from_dict(self):
        self.check_for_skip('dict_view_returned', 'values', '__delitem__')
        tmp_values = self.test_obj.values()
        self.assertEqual(self.dict_size, len(tmp_values))
        self.assertEqual(self.values, list(tmp_values))
        del self.test_obj[self.keys[0]]
        self.assertEqual(self.dict_size - 1, len(tmp_values))

    def test_items_object_del_from_dict(self):
        self.check_for_skip('dict_view_returned', 'items', '__delitem__')
        tmp_items = self.test_obj.items()
        self.assertEqual(self.dict_size, len(tmp_items))
        del self.test_obj[self.keys[0]]
        self.assertEqual(self.dict_size - 1, len(tmp_items))

    def test_values_object_update_from_dict(self):
        self.check_for_skip('dict_view_returned', 'values')
        tmp_values = self.test_obj.values()
        self.assertEqual(self.values[0], list(tmp_values)[0])
        self.test_obj[self.keys[0]] = self.next_values[0]
        self.assertEqual(self.next_values[0], list(tmp_values)[0])

    def test_items_object_update_from_dict(self):
        self.check_for_skip('dict_view_returned', 'items')
        tmp_items = self.test_obj.items()
        self.assertEqual(self.items[0], list(tmp_items)[0])
        self.test_obj[self.keys[0]] = self.next_values[0]
        self.assertEqual(self.next_values[0], list(tmp_items)[0][1])


    def test_contains_assert_not_in_empty(self):
        self.check_for_skip('__contains__')
        self.assertNotIn('a', self.mt)

    def test_not_contains_in_empty(self):
        self.check_for_skip('__contains__')
        self.assertTrue(not ('a' in self.mt))

    def test_contains_not_in_empty(self):
        self.check_for_skip('__contains__')
        self.assertTrue('a' not in self.mt)

    def test_contains_true(self):
        self.check_for_skip('__contains__')
        self.assertIn(self.keys[0], self.test_obj)
        self.assertIn(self.keys[1], self.test_obj)

    def test_contains_not_in_full(self):
        self.check_for_skip('__contains__')
        self.assertNotIn('__foobar__', self.test_obj)

    def test_contains_raises(self):
        self.check_for_skip('__contains__', 'invalid_attr', 'raise')
        self.assertRaises(TypeError, self.test_obj.__contains__)

    def test_mt_len(self):
        self.check_for_skip('__sizeof__')
        self.assertEqual(len(self.mt), 0)

    def test_full_len(self):
        self.check_for_skip('__sizeof__')
        # from mapping
        self.assertEqual(len(self.test_obj), len(self.keys))

    def test_getitem(self):
        self.assertEqual(self.test_obj[self.keys[0]], self.values[0])
        self.assertEqual(self.test_obj[self.keys[1]], self.values[1])

    def test_get_item_raises(self):
        self.check_for_skip('invalid_attr', 'raise')
        self.assertRaises(TypeError, self.test_obj.__getitem__)

    def test_getitem_raises_no_match(self):
        self.check_for_skip('keyerror', 'raise')
        with self.assertRaises(KeyError):
            t = self.test_obj[self.next_keys[0]]

    def test_getitem_raises_mt_no_match(self):
        self.check_for_skip('keyerror', 'raise')
        with self.assertRaises(KeyError):
            t = self.mt[self.next_keys[0]]

    def test_getitem_item_raises_on_eq(self):
        self.check_for_skip('invalid_arg', 'raise', 'keyerror')
        self.mt[self.bad_eq] = 42
        self.assertRaises(KeyError, self.mt.__getitem__, 23)

    def test_getitem_item_raises_on_hash(self):
        self.check_for_skip('only_hashable_keys')
        x = self.bad_hash_on_call()
        self.mt[x] = 42
        x.fail = True
        self.assertRaises(FixtureExc, self.mt.__getitem__, x)

    def test_getitem_same_hash_diff_item(self):
        self.check_for_skip('only_hashable_keys')
        # This should create two items since Python checks BOTH the hash and the item.
        x = self.same_hash_ne(12)
        y = self.same_hash_ne(110)
        self.assertNotEqual(x, y)
        self.mt[x] = self.next_values[0]
        self.mt[y] = self.next_values[1]
        # print(self.mt)
        self.assertEqual(2, len(self.mt))
        self.assertEqual(self.next_values[0], self.mt[x])
        self.assertEqual(self.next_values[1], self.mt[y])

    def test_getitem_same_hash_diff_eq_item(self):
        self.check_for_skip('only_hashable_keys')
        # This should create one item since Python checks BOTH the hash and the item.
        x = self.same_hash_eq(12)
        y = self.same_hash_eq(110)
        self.assertEqual(x, y)
        self.mt[x] = self.next_values[0]
        self.mt[y] = self.next_values[1]
        self.assertEqual(1, len(self.mt))
        self.assertEqual(self.next_values[1], self.mt[x])
        self.assertEqual(self.next_values[1], self.mt[y])

    def test_setitem(self):
        for key, value in self.items:
            self.mt[key] = value
            self.assertEqual(self.mt[key], value)

    def test_setitem_unhashable_raises(self):
        self.check_for_skip('only_hashable_keys')
        with self.assertRaises(TypeError):
            self.mt[[1,2,3]] = self.next_values[0]

    def test_setitem_hash_raises(self):
        self.check_for_skip('only_hashable_keys')
        x = self.bad_hash()
        with self.assertRaises(FixtureExc):
            self.mt[x] = self.next_values[0]

    def test_delitem(self):
        self.check_for_skip('__delitem__')
        self.test_obj[self.next_keys[0]] = self.next_values[0]
        self.test_obj[self.keys[0]] = self.next_values[1]
        self.assertEqual(self.test_obj[self.next_keys[0]], self.next_values[0])
        self.assertEqual(self.test_obj[self.keys[0]], self.next_values[1])
        del self.test_obj[self.keys[1]]
        self.verify_td({self.keys[0]: self.next_values[1], self.next_keys[0]: self.next_values[0]})

    def test_delitem2(self):
        self.check_for_skip('__delitem__', 'keyerror', 'raise')
        for key in self.keys:
            del self.test_obj[key]
            self.assertRaises(KeyError, lambda: self.test_obj[key])

    def test_delitem_raises(self):
        self.check_for_skip('__delitem__', 'keyerror', 'raise')
        with self.assertRaises(KeyError):
            del self.test_obj[self.next_keys[0]]

    def test_update_from_kwargs(self):
        self.check_for_skip('update')
        self._set_data(__alpha_only__=True)
        self.mt.update(**self.dict)
        self.verify_mt()

    def test_update_from_items(self):
        self.check_for_skip('update')
        self.mt.update(self.items)
        self.verify_mt()

    def test_update_from_mapping(self):
        self.check_for_skip('update')
        # mapping argument
        self.mt.update(self.dict)
        self.verify_mt()

    def test_update_no_arg(self):
        self.check_for_skip('update')
        self.mt.update()
        self.assertEqual(self.mt, self._make_obj())

    def test_update_with_sequence(self):
        self.check_for_skip('update')
        tmp_seq = []
        for i in self.items:
            tmp_seq.append(i[0])
            tmp_seq.append(i[1])
        self.mt.update(self.items)
        self.verify_mt()

    def test_update_with_iterator(self):
        self.check_for_skip('update')
        # Iterator
        self.mt.update(iter(self.items))
        self.verify_mt()

    def test_update_raises_with_none(self):
        self.check_for_skip('update', 'no_userdict', 'raise')
        # FIXME: Doesn't work with UserDict
        self.assertRaises((TypeError, AttributeError), self.mt.update, None)

    def test_update_raises_with_single_arg(self):
        self.check_for_skip('update', 'invalid_arg', 'raise')
        self.assertRaises((TypeError, AttributeError), self.mt.update, 42)

    def test_update_from_customdict(self):
        self.check_for_skip('update', 'subclass')
        self.mt.update(self.user_dict(self.dict))
        self.verify_mt()

    def test_update_raises_failing_keys_obj(self):
        self.check_for_skip('update', 'subfail')
        self.assertRaises(FixtureExc, self.mt.update, self.bad_keys())

    def test_update_failed_bad_keys_iterator(self):
        self.check_for_skip('update', 'subfail')
        self.assertRaises(FixtureExc, self.mt.update, self.bad_user_next())

    def test_update_failed_bad_getitem(self):
        self.check_for_skip('update', 'subfail')
        self.assertRaises(FixtureExc, self.mt.update, self.bad_user_getitem())

    def test_update_failed_bad_next(self):
        self.check_for_skip('update', 'subfail')
        self.assertRaises(FixtureExc, self.mt.update, self.bad_next())

    def test_update_failed_invalid_set(self):
        self.check_for_skip('update', 'invalid_arg', 'raise')
        self.assertRaises(ValueError, self.mt.update, [(1, 2, 3)])

    def test_update_overwrite(self):
        self.check_for_skip('update')
        # mapping argument
        self.mt.update({self.keys[0]: 100})
        self.mt.update({self.keys[1]: 20})
        self.mt.update(self.dict)
        self.verify_mt()

    def test_update_no_data(self):
        self.check_for_skip('update')
        self.test_obj.update()
        self.verify_td()

    def test_updaate_seq_and_kwargs(self):
        self.check_for_skip('update')
        self._set_data(__alpha_only__=True)
        self.mt.update(self.items, **self.dict)
        self.verify_mt()

    def test_copy(self):
        self.check_for_skip('copy')
        self.verify_dict(dict(self.test_obj.copy()))

    def test_copy_empty(self):
        self.check_for_skip('copy')
        self.assertEqual(self.mt.copy(), self.mt)

    def test_copy_is_same_class(self):
        self.check_for_skip('copy')
        self.assertIsInstance(self.mt.copy(), self.mt.__class__)

    def test_copy_as_attr_raises(self):
        self.check_for_skip('copy', 'invalid_arg', 'raise')
        self.assertRaises(TypeError, self.mt.copy, None)

    def test_copy_moves_refs(self):
        self.check_for_skip('copy')
        tmp_dict = self.dict.copy()
        self.mt[self.next_keys[0]] = tmp_dict
        new = self.mt.copy()
        self.verify_mt({self.next_keys[0]: tmp_dict})
        tmp_dict[self.keys[0]] = self.next_values[0]
        self.verify_mt({self.next_keys[0]: tmp_dict})
        self.verify_dict(new, {self.next_keys[0]: tmp_dict})

    def test__copy__(self):
        self.check_for_skip('copy_func')
        self.verify_dict(dict(copy(self.test_obj)))

    def test__copy__empty(self):
        self.check_for_skip('copy_func')
        self.assertEqual(copy(self.mt), self.mt)

    def test__copy__is_same_class(self):
        self.check_for_skip('copy_func')
        self.assertIsInstance(copy(self.mt), self.mt.__class__)

    def test__copy__moves_refs(self):
        self.check_for_skip('copy_func')
        # set a value to a dict object
        tmp_dict = copy(self.dict)
        self.mt[self.next_keys[0]] = tmp_dict

        # make a copy of the dict
        new = copy(self.mt)
        # lets make sure the are the same so far (just checking)
        self.verify_mt({self.next_keys[0]: tmp_dict})

        # change something in the sub-object
        tmp_dict[self.keys[0]] = self.next_values[0]

        # making sure that the change is reflected in both the old and new object
        self.verify_mt({self.next_keys[0]: tmp_dict})
        self.verify_dict(new, {self.next_keys[0]: tmp_dict})

    def test_deepcopy(self):
        self.check_for_skip('deepcopy')
        self.verify_dict(dict(deepcopy(self.test_obj)))

    def test_deepcopy_empty(self):
        self.check_for_skip('deepcopy')
        self.assertEqual(deepcopy(self.mt), self.mt)

    def test_deepcopy_is_same_class(self):
        self.check_for_skip('deepcopy')
        self.assertIsInstance(deepcopy(self.mt), self.mt.__class__)

    def test_deepcopy_new_values(self):
        self.check_for_skip('deepcopy')
        tmp_dict = self.dict.copy()
        self.mt[self.next_keys[0]] = tmp_dict
        new = deepcopy(self.mt)
        # Both should match
        self.verify_mt({self.next_keys[0]: tmp_dict})
        self.verify_dict(new, {self.next_keys[0]: tmp_dict})

        # change a value in the referenced sub_dict
        tmp_dict[self.keys[0]] = self.next_values[0]

        # now, the old one should match the changed_value
        self.verify_mt({self.next_keys[0]: tmp_dict})

        # and the new one should not have changed
        self.verify_dict(new, {self.next_keys[0]: self.dict})

    @SkipIfPyLower(3, 7)
    def test_ordered(self):
        self.check_for_skip('ordered')
        for i in range(1000):
            self._set_data(__size__=100)
            self.assertEqual(self.keys, list(self.test_obj.keys()))

    def test_clear(self):
        self.check_for_skip('clear')
        # from mapping
        self.test_obj.clear()
        self.verify_td({})

    def test_clear_raise_on_attr(self):
        self.check_for_skip('clear', 'invalid_attr', 'raise')
        self.assertRaises(TypeError, self.test_obj.clear, None)


    def test_get_from_mt_none(self):
        self.check_for_skip('get')
        self.assertTrue(self.mt.get(self.keys[0]) is None)

    def test_get_from_mt_default(self):
        self.check_for_skip('get')
        self.assertEqual(self.mt.get(self.keys[0], self.values[1]), self.values[1])

    def test_get_from_full_none(self):
        self.check_for_skip('get')
        self.assertTrue(self.test_obj.get(self.next_keys[0]) is None)

    def test_get_from_full_default(self):
        self.check_for_skip('get')
        self.assertEqual(self.test_obj.get(self.next_keys[0], self.next_values[1]), self.next_values[1])

    def test_get_from_full_value(self):
        self.check_for_skip('get')
        self.assertEqual(self.test_obj.get(self.keys[0]), self.values[0])

    def test_get_from_full_with_default_value(self):
        self.check_for_skip('get')
        self.assertEqual(self.test_obj.get(self.keys[0], self.next_values[0]), self.values[0])

    def test_get_raise_on_attr(self):
        self.check_for_skip('get', 'invalid_attr', 'raise')
        self.assertRaises(TypeError, self.mt.get)

    def test_get_raise_on_unhashable_key(self):
        self.check_for_skip('get', 'only_hashable_keys')
        self.assertRaises(TypeError, self.mt.get, None, None, None)

    def test_setdefault_full_return_known(self):
        self.check_for_skip('setdefault')
        self.assertEqual(self.test_obj.setdefault(self.keys[0], self.next_values[0]), self.values[0])
        self.verify_td()

    def test_setdefault_mt_return_default(self):
        self.check_for_skip('setdefault')
        self.assertEqual(self.mt.setdefault(self.keys[0], self.next_values[0]), self.next_values[0])
        self.verify_mt({self.keys[0]: self.next_values[0]})

    def test_setdefault_full_return_default(self):
        self.check_for_skip('setdefault')
        self.assertEqual(self.test_obj.setdefault(self.next_keys[0], self.next_values[0]), self.next_values[0])
        tmp_dict = self.dict
        tmp_dict.update({self.next_keys[0]: self.next_values[0]})
        self.verify_td(tmp_dict)

    def test_setdefault_raises_on_attr(self):
        self.check_for_skip('setdefault', 'invalid_attr', 'raise')
        self.assertRaises(TypeError, self.mt.setdefault)

 
    def test_setdefault_raise_on_bad_hash(self):
        self.check_for_skip('setdefault', 'only_hashable_keys')
        d = self._make_obj()
        x = self.bad_hash_on_call()
        d[x] = 42
        x.fail = True
        self.assertRaises(FixtureExc, d.setdefault, x, [])

    @SkipIfPyLower(3, 7)
    def test_popitem_ordered(self):
        self.check_for_skip('popitem', 'scale')

        for i in range(1000):

            self._set_data(__size__=50)
            tmp_keys = []
            tmp_values = []

            self.verify_td()

            while self.test_obj:
                key, value = self.test_obj.popitem()
                tmp_keys.append(key)
                tmp_values.append(value)

            tmp_keys.reverse()
            tmp_values.reverse()

            self.assertEqual(self.keys, tmp_keys)
            self.assertEqual(self.values, tmp_values)


    def test_popitem(self):
        self.check_for_skip('popitem')
        key, value = self.test_obj.popitem()
        self.assertNotIn(key, self.test_obj)
        self.assertIn(value, self.keys)

    def test_popitem_raises_on_mt(self):
        self.check_for_skip('popitem', 'raise', 'keyerror')
        self.assertRaises(KeyError, self.mt.popitem)

    def test_popitem_raises_on_arg(self):
        self.check_for_skip('popitem', 'invalid_attr', 'raise')
        self.assertRaises(TypeError, self.test_obj.popitem, 42)

    def test_popitem_on_copies_large_size(self):
        self.check_for_skip('popitem', 'scale')
        for copymode in -1, +1:
            # -1: b has same structure as a
            # +1: b is a.copy()
            for log2size in range(12):
                # print(log2size)
                size = 2**log2size
                # print('size:', size)
                keys = self._make_value_list(size, allow_numeric=False)
                a = self._make_obj()
                b = self._make_obj()
                for i in range(size):
                    # print('Build Step-%s a: %s, b: %s' % (i, len(a), len(b)))
                    # print('Key: ', keys[i])
                    a[keys[i]] = keys[i]
                    if copymode < 0:
                        b[keys[i]] = keys[i]
                if copymode > 0:
                    b = a.copy()
                # print('Pre-Step:  a: %s, b: %s' % (len(a), len(b)))
                for i in range(size):
                    # print('Step-%s a: %s, b: %s' % (i, len(a), len(b)))
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, ka)
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, kb)
                    self.assertTrue(not(copymode < 0 and ta != tb))
                self.verify_dict(a, {})
                self.verify_dict(b, {})

    def test_pop(self):
        self.check_for_skip('pop')
        self.assertEqual(self.test_obj.pop(self.keys[0]), self.values[0])
        self.assertNotIn(self.keys[0], self.test_obj)

    def test_pop_raises_on_not_found(self):
        self.check_for_skip('pop', 'keyerror', 'raise')
        self.assertRaises(KeyError, self.test_obj.pop, self.next_keys[0])

    def test_pop_with_default_ret_value(self):
        self.check_for_skip('pop')
        default = self.next_values[0]
        self.assertEqual(self.test_obj.pop(self.keys[0], default), self.values[0])
        self.assertNotIn(self.keys[0], self.test_obj)

    def test_pop_with_default_return_default(self):
        self.check_for_skip('pop')
        self.assertEqual(self.test_obj.pop(self.next_keys[0], self.next_values[0]), self.next_values[0])

    def test_pop_with_bad_hash_raises(self):
        self.check_for_skip('pop', 'only_hashable_keys')
        x = self.bad_hash_on_call()
        self.test_obj[x] = 42
        x.fail = True
        self.assertRaises(FixtureExc, self.test_obj.pop, x)

    def test_mutating_iteration(self):
        self.check_for_skip('raise')
        with self.assertRaises(RuntimeError, msg="changing dict size during iteration doesn't raise Error"):
            for i, key in enumerate(self.test_obj):
                self.test_obj[self.next_keys[i]] = self.next_values[i]

    def test_repr_mt(self):
        self.check_for_skip('__repr__')
        exp_repr = self.expected_repr_mt or repr({})
        self.assertEqual(repr(self.mt), exp_repr)

    def test_repr_base(self):
        self.check_for_skip('__repr__')
        exp_repr = self.expected_repr_base or repr(self.dict)
        self.assertEqual(repr(self.test_obj), exp_repr)

    def test_repr_recursive(self):
        self.check_for_skip('__repr__')
        self.mt[self.next_keys[0]] = self.test_obj
        test_d = {}
        test_d[self.next_keys[0]] = self.dict
        exp_repr = repr(test_d)
        self.assertEqual(repr(self.mt), exp_repr)

    def test_repr_inner_obj_raises(self):
        self.check_for_skip('__repr__', 'subfail')
        self.test_obj[self.next_keys[0]] = self.bad_repr()
        self.assertRaises(FixtureExc, repr, self.test_obj)

    def test_repr_deep_recursion(self):
        self.check_for_skip('__repr__', 'scale', 'raise')
        # from hash
        d = self._make_obj()
        for i in range(sys.getrecursionlimit() + 100):
            d0 = d
            d = self._make_obj()
            d[1] = d0
        self.assertRaises(RecursionError, repr, d)

    def test_eq_to_self(self):
        self.check_for_skip('__eq__')
        self.assertEqual(self.test_obj, self.test_obj)

    def test_eq_to_new_self(self):
        self.check_for_skip('__eq__')
        d = self._make_obj(self.dict)
        self.assertEqual(self.test_obj, d)

    def test_eq_to_dict_left(self):
        self.check_for_skip('__eq__')
        self.assertEqual(self.dict, self.test_obj)

    def test_eq_to_dict_right(self):
        self.check_for_skip('__eq__')
        self.assertEqual(self.test_obj, self.dict)

    def test_eq_to_self_mt(self):
        self.check_for_skip('__eq__')
        self.assertEqual(self.mt, self._make_obj())

    def test_eq_raises_bad_comp_in_key(self):
        self.check_for_skip('__eq__', 'subfail')
        bc = self.bad_cmp()
        self.mt[bc] = self.next_values[0]
        d = dict()
        d[1] = self.next_values[0]
        self.assertRaises(FixtureExc, lambda: bc == 1)
        self.assertRaises(FixtureExc, lambda: self.mt == d)

    def test_eq_raises_bad_comp_in_value(self):
        self.check_for_skip('__eq__', 'subfail')
        self.mt[self.next_keys[0]] = self.bad_cmp()
        d = dict()
        d[self.next_keys[0]] = self.next_values[0]
        self.assertRaises(FixtureExc, lambda: self.bad_cmp() == 1)
        self.assertRaises(FixtureExc, lambda: self.mt == d)

    def test_ne_self(self):
        self.check_for_skip('__ne__')
        self.assertNotEqual(self.mt, self.test_obj)

    def test_ne_dict_left(self):
        self.check_for_skip('__ne__')
        self.assertNotEqual(self.dict, self.mt)

    def test_ne_dict_right(self):
        self.check_for_skip('__ne__')
        self.assertNotEqual(self.mt, self.dict)


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
        # return {"one": "two", "key1": "value1", "key2": (1, 2, 3)}
        tmp_td = self.m('aa', 'aa', 'as')
        return tmp_td.dict

    def _empty_mapping(self):
        return self.type2test()


    def _full_mapping(self, *args, **kwargs):
        if kwargs:
            x = self._make_obj()
            for key, value in kwargs.items():
                x[key] = value
            return x
        else: 
            if not args:
                args = ['an', 'an']
            elif isinstance(args[0], dict):
                x = self._make_obj()
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
        p = self._make_obj()
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
        p = self._make_obj()
        #Indexing
        for key, value in self.reference.items():
            p[key] = value
            self.assertEqual(p[key], value)
        for key in self.reference.keys():
            del p[key]
            self.assertRaises(KeyError, lambda:p[key])
        p = self._make_obj()
        #update
        p.update(self.reference)
        self.assertEqual(dict(p), self.reference)
        items = list(p.items())
        p = self._make_obj()
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
        p=self._make_obj()
        self.assertRaises(KeyError, p.popitem)

    def test_constructor(self):
        self.assertEqual(self._make_obj(), self._make_obj())

    def test_bool(self):
        self.assertTrue(not self._make_obj())
        self.assertTrue(self.reference)
        self.assertTrue(bool(self._make_obj()) is False)
        self.assertTrue(bool(self.reference) is True)

    def test_keys(self):
        d = self._make_obj()
        self.assertEqual(list(d.keys()), [])
        d = self.reference
        self.assertIn(list(self.inmapping.keys())[0], d.keys())
        self.assertNotIn(list(self.other.keys())[0], d.keys())
        self.assertRaises(TypeError, d.keys, None)

    def test_values(self):
        d = self._make_obj()
        self.assertEqual(list(d.values()), [])

        self.assertRaises(TypeError, d.values, None)

    def test_items(self):
        d = self._make_obj()
        self.assertEqual(list(d.items()), [])

        self.assertRaises(TypeError, d.items, None)

    def test_len(self):
        d = self._make_obj()
        self.assertEqual(len(d), 0)

    def test_getitem(self):
        d = self.reference
        self.assertEqual(d[list(self.inmapping.keys())[0]],
                         list(self.inmapping.values())[0])

        self.assertRaises(TypeError, d.__getitem__)

    def test_update(self):
        # mapping argument
        d = self._make_obj()
        d.update(self.other)
        self.assertEqual(list(d.items()), list(self.other.items()))

        # No argument
        d = self._make_obj()
        d.update()
        self.assertEqual(d, self._make_obj())

        # item sequence
        d = self._make_obj()
        d.update(self.other.items())
        self.assertEqual(list(d.items()), list(self.other.items()))

        # Iterator
        d = self._make_obj()
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

        class FixtureExc(Exception): pass

        d = self._make_obj()
        class FailingUserDict:
            def keys(self):
                raise FixtureExc
        self.assertRaises(FixtureExc, d.update, FailingUserDict())

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
                        raise FixtureExc
                return BogonIter()
            def __getitem__(self, key):
                return key
        self.assertRaises(FixtureExc, d.update, FailingUserDict())

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
                raise FixtureExc
        self.assertRaises(FixtureExc, d.update, FailingUserDict())

        d = self._make_obj()
        class badseq(object):
            def __iter__(self):
                return self
            def __next__(self):
                raise FixtureExc()

        self.assertRaises(FixtureExc, d.update, badseq())

        self.assertRaises(ValueError, d.update, [(1, 2, 3)])

    # no test_fromkeys or test_copy as both os.environ and selves don't support it

    def test_get(self):
        d = self._make_obj()
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
        d = self._make_obj()
        self.assertRaises(TypeError, d.setdefault)

    def test_popitem(self):
        d = self._make_obj()
        self.assertRaises(KeyError, d.popitem)
        self.assertRaises(TypeError, d.popitem, 42)

    def test_pop(self):
        d = self._make_obj()
        k, v = list(self.inmapping.items())[0]
        d[k] = v
        self.assertRaises(KeyError, d.pop, list(self.other.keys())[0])

        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)

        self.assertRaises(KeyError, d.pop, k)

class TestMappingProtocol(BasicTestMappingProtocol):
    def test_constructor(self):
        BasicTestMappingProtocol.test_constructor(self)
        self.assertTrue(self._make_obj() is not self._make_obj())
        self.assertEqual(self.type2test(**self.dict), self.dict)

    def test_bool(self):
        BasicTestMappingProtocol.test_bool(self)
        self.assertTrue(not self._make_obj())
        self.assertTrue(self.test_obj)
        self.assertTrue(bool(self._make_obj()) is False)
        self.assertTrue(bool(self.test_obj is True)

    def test_keys(self):
        BasicTestMappingProtocol.test_keys(self)
        d = self._make_obj()
        self.assertEqual(list(d.keys()), [])
        d = self.test_obj
        k = d.keys()
        self.assertIn(self.keys[0], k)
        self.assertIn(self.keys[0], k)
        self.assertNotIn('__foobar__', k)

    def test_values(self):
        BasicTestMappingProtocol.test_values(self)
        self.assertEqual(list(self.test_obj.values()), self.values)

    def test_items(self):
        BasicTestMappingProtocol.test_items(self)
        self.assertEqual(list(self.items()), self.items)

    def test_contains(self):
        d = self._make_obj()
        self.assertNotIn('a', d)
        self.assertTrue(not ('a' in d))
        self.assertTrue('a' not in d)
        self.assertIn(self.keys[0], self.test_obj)
        self.assertIn(self.keys[1], self.test_obj)
        self.assertNotIn('__foobar__', d)

        self.assertRaises(TypeError, d.__contains__)

    def test_len(self):
        BasicTestMappingProtocol.test_len(self)
        self.assertEqual(len(self.test_obj), len(self.keys))

    def test_getitem(self):
        BasicTestMappingProtocol.test_getitem(self)

        self.assertEqual(self.test_obj[self.keys[0]], self.values[0])
        self.assertEqual(self.test_obj[self.keys[1]], self.values[1])

        self.test_obj[self.next_keys[0]] = self.next_values[0]
        self.test_obj[self.keys[0]] = self.next_values[1]
        self.assertEqual(self.test_obj[self.next_keys[0]], self.next_values[0])
        self.assertEqual(self.test_obj[self.keys[0]], self.next_values[1])
        del self.test_obj[self.keys[1]]
        self.assertEqual(self.test_obj, {self.keys[0]: self.next_values[1], self.next_keys[0]: self.next_values[0]})

        self.assertRaises(TypeError, self.test_obj.__getitem__)

    def test_clear(self):

        self.test_obj.clear()
        self.assertEqual(self.test_obj, {})

        self.assertRaises(TypeError, self.test_obj.clear, None)

    def test_update(self):
        BasicTestMappingProtocol.test_update(self)
        # mapping argument
        d = self._make_obj()
        self.m(3, 'nn', set=True)
        d.update({self.keys[0]:100})
        d.update({self.keys[1]:20})
        d.update(self.dict)
        self.assertEqual(d, self.dict)

        # no argument
        d.update()
        self.assertEqual(d, self.dict)

        # keyword arguments
        d = self._make_obj()
        self.m(3, 'an', set=True)
        kw1 = {self.keys[0]: 100}
        kw2 = {self.keys[1]: 20}
        d.update(**kw1)
        d.update(**kw2)
        d.update(**self.dict)
        self.assertEqual(d, self.dict)

        # item sequence
        self.m(2, 'an', set=True)
        d = self._make_obj()
        d.update(self.items)
        self.assertEqual(d, self.dict)

        # Both item sequence and keyword arguments
        d = self._make_obj()
        d.update(self.items, **self.dict)
        self.assertEqual(d, self.dict)

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
        d = self._make_obj()
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

        class FixtureExc(Exception): pass

        class baddict1(self.type2test):
            def __init__(self):
                raise FixtureExc()

        self.assertRaises(FixtureExc, baddict1.fromkeys, [1])

        class BadSeq(object):
            def __iter__(self):
                return self
            def __next__(self):
                raise FixtureExc()

        self.assertRaises(FixtureExc, self.type2test.fromkeys, BadSeq())

        class baddict2(self.type2test):
            def __setitem__(self, key, value):
                raise FixtureExc()

        self.assertRaises(FixtureExc, baddict2.fromkeys, [1])

    def test_copy(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        self.assertEqual(d.copy(), {1:1, 2:2, 3:3})
        d = self._make_obj()
        self.assertEqual(d.copy(), d)
        self.assertIsInstance(d.copy(), d.__class__)
        self.assertRaises(TypeError, d.copy, None)

    def test_get(self):
        BasicTestMappingProtocol.test_get(self)
        d = self._make_obj()
        self.assertTrue(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        d = self._full_mapping({'a' : 1, 'b' : 2})
        self.assertTrue(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)

    def test_setdefault(self):
        BasicTestMappingProtocol.test_setdefault(self)
        d = self._make_obj()
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
                a = self._make_obj()
                b = self._make_obj()
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
        d = self._make_obj()
        k, v = 'abc', 'def'

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)


class TestHashMappingProtocol(TestMappingProtocol):

    def test_getitem(self):
        TestMappingProtocol.test_getitem(self)
        class FixtureExc(Exception): pass

        class BadEq(object):
            def __eq__(self, other):
                raise FixtureExc()
            def __hash__(self):
                return 24

        d = self._make_obj()
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise FixtureExc()
                else:
                    return 42

        d = self._make_obj()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(FixtureExc, d.__getitem__, x)

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

        class FixtureExc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise FixtureExc()
                else:
                    return 42

        d = self._make_obj()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(FixtureExc, d.pop, x)

    def test_mutatingiteration(self):
        d = self._make_obj()
        d[1] = 1
        try:
            for i in d:
                d[i+1] = 1
        except RuntimeError:
            pass
        else:
            self.fail("changing dict size during iteration doesn't raise Error")

    def test_repr(self):
        d = self._make_obj()
        self.assertEqual(repr(d), '{}')
        d[1] = 2
        self.assertEqual(repr(d), '{1: 2}')
        d = self._make_obj()
        d[1] = d
        self.assertEqual(repr(d), '{1: {...}}')

        class FixtureExc(Exception): pass

        class BadRepr(object):
            def __repr__(self):
                raise FixtureExc()

        d = self._full_mapping({1: BadRepr()})
        self.assertRaises(FixtureExc, repr, d)

    def test_repr_deep(self):
        d = self._make_obj()
        for i in range(sys.getrecursionlimit() + 100):
            d0 = d
            d = self._make_obj()
            d[1] = d0
        self.assertRaises(RecursionError, repr, d)

    def test_eq(self):
        self.assertEqual(self._make_obj(), self._make_obj())
        self.assertEqual(self._full_mapping({1: 2}),
                         self._full_mapping({1: 2}))

        class FixtureExc(Exception): pass

        class BadCmp(object):
            def __eq__(self, other):
                raise FixtureExc()
            def __hash__(self):
                return 1

        d1 = self._full_mapping({BadCmp(): 1})
        d2 = self._full_mapping({1: 1})
        self.assertRaises(FixtureExc, lambda: BadCmp()==1)
        self.assertRaises(FixtureExc, lambda: d1==d2)

    def test_setdefault(self):
        TestMappingProtocol.test_setdefault(self)

        class FixtureExc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise FixtureExc()
                else:
                    return 42

        d = self._make_obj()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(FixtureExc, d.setdefault, x, [])
    
'''
