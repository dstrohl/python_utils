from unittest import TestCase
from PythonUtils.Old.ValidatorHelper import ValidateMessageHandler
from PythonUtils.Old.ValidatorHelper import *
from PythonUtils import UnSet

_UNSET = UnSet()

VR1_PASSED = [
    dict(
        validator='v1',
        passed=True,
        msg='v1 msg',
        args=[str],
        kwargs={},
    ),
    dict(
        validator='v2',
        passed=True,
        msg='v2 msg, foo bar foo bar',
        args=[str],
        kwargs={},
    )
]

VR2_FAILED = [
    dict(
        validator='v3',
        passed=False,
        msg='v3 msg',
        args=[str],
        kwargs={},
    ),
    dict(
        validator='v4',
        passed=False,
        msg='v4 msg, foo bar foo bar',
        args=[str],
        kwargs={},
    )
]

VR3_MIXED = [
    dict(
        validator='v5',
        passed=False,
        msg='v5 msg',
        args=[str],
        kwargs={},
    ),
    dict(
        validator='v6',
        passed=True,
        msg='v6 msg, foo bar foo bar',
        args=[str],
        kwargs={},
    )
]


class TestValidatorFormatter(TestCase):

    maxDiff = None

    def _make_vr(self, value, passed, *results):
        vr = ValidateMessageHandler(value, passed)
        for result_set in results:
            for r in result_set:
                vr.add_message(**r)
        return vr

    def test_format_line(self): 
        vr = self._make_vr('foo', True, VR3_MIXED)
        tmp_ret = vr.message(format_as=vr.LINE)

        exp_ret = 'Field [PASSED]: v5 msg, v6 msg, foo bar foo bar'

        print(tmp_ret)

        self.assertEqual(exp_ret, tmp_ret)

    def test_format_lines(self):
        vr = self._make_vr('foo', False, VR3_MIXED)
        tmp_ret = vr.message(format_as=vr.LINES)

        exp_ret = 'Field [FAILED]:\n\n    v5 msg\n    v6 msg, foo bar foo bar'

        print(tmp_ret)

        self.assertEqual(exp_ret, tmp_ret)

    def test_format_list(self):
        vr = self._make_vr('foo', True, VR3_MIXED)
        tmp_ret = vr.message(format_as=vr.LIST)

        exp_ret = ['v5 msg', 'v6 msg, foo bar foo bar']

        print(tmp_ret)

        self.assertEqual(exp_ret, tmp_ret)

    def test_format_table(self):
        vr = self._make_vr('foo', False, VR3_MIXED)
        tmp_ret = vr.message(format_as=vr.TABLE)

        exp_ret = 'Field [FAILED]\n' \
            '\n' \
            '+----+-----------+-------------------------+\n' \
            '| PF | Validator | Message                 |\n' \
            '+====+===========+=========================+\n' \
            '|  P | v5        | v5 msg                  |\n' \
            '+----+-----------+-------------------------+\n' \
            '| *F | v6        | v6 msg, foo bar foo bar |\n' \
            '+----+-----------+-------------------------+'

        print(tmp_ret)

        self.assertEqual(exp_ret, tmp_ret)

    def test_passed_list(self):
        vr = self._make_vr('foo', True, VR3_MIXED)
        tmp_ret = vr.message(format_as=vr.LINE, failed=False)

        exp_ret = 'Field [PASSED]: v6 msg, foo bar foo bar'

        print(tmp_ret)

        self.assertEqual(exp_ret, tmp_ret)

    def test_failed_list(self):
        vr = self._make_vr('foo', False, VR3_MIXED)
        tmp_ret = vr.message(format_as=vr.LINE, passed=False)

        exp_ret = 'Field [FAILED]: v5 msg'

        print(tmp_ret)

        self.assertEqual(exp_ret, tmp_ret)





class TestValidatorHelper(TestCase):
    
    def test_str_type(self):
        v = Validator(fieldname='test1')
        v.add_validators(ValidateInstance(str))        
        self.assertTrue(v('test'))
        self.assertFalse(v(1))
        
    def test_mult_validators(self):
        v = Validator(fieldname='test1')
        v.add_validators(ValidateInstance(str))        
        v.add_validators(ValidateEq('test'))
        self.assertTrue(v('test'))
        self.assertFalse(v(1))
        self.assertFalse(v('test2'))

    def test_mult_validator_get_failed_passed(self):
        v = Validator(fieldname='test1')
        v.add_validators(ValidateInstance(str, name='ty'))        
        v.add_validators(ValidateStartsWith('foo', name='fo'))
        v.add_validators(ValidateEndsWith('bar', name='ba'))
        self.assertTrue(v('foobar'))
        tmp_passed = v.get_passed()
        self.assertIn('ty', tmp_passed)
        self.assertIn('fo', tmp_passed)
        self.assertIn('ba', tmp_passed)
        
        self.assertFalse(v('foo_man_chu'))
        tmp_passed = v.get_passed()
        self.assertIn('ty', tmp_passed)
        self.assertIn('fo', tmp_passed)
        
        self.assertFalse(v('test2'))
        tmp_passed = v.get_failed()
        self.assertIn('fo', tmp_passed)
        self.assertIn('ba', tmp_passed)

    def test_pass_messages(self):
        v = Validator(ValidateInstance(str), ValidateEq('test'), fieldname='test1')

        self.assertTrue(v('test'))
        self.assertListEqual(['test1 PASSED: str is an instance of str', 'test1 PASSED: test equals test'], v.pass_messages())
        self.assertEqual('test1 PASSED: str is an instance of str\ntest1 PASSED: test equals test', v.pass_messages(join='\n'))

    def test_fail_messages(self):
        v = Validator(ValidateInstance(str), ValidateEq('test'), fieldname='test1')
        self.assertFalse(v(1))
        self.assertListEqual(['test1 FAILED: int is not an instance of str', 'test1 FAILED: 1 does not equal test'], v.fail_messages())
        self.assertEqual('test1 FAILED: int is not an instance of str\ntest1 FAILED: 1 does not equal test', v.fail_messages(join='\n'))

    def test_mixed_pass_messages(self):
        v = Validator(ValidateInstance(str), ValidateEq('test'))
        self.assertFalse(v('test3'))
        self.assertListEqual(['Field PASSED: str is an instance of str'], v.pass_messages())
        self.assertEqual('Field PASSED: str is an instance of str', v.pass_messages(join='\n'))

    def test_mixed_fail_messages(self):
        v = Validator(ValidateInstance(str), ValidateEq('test'), fieldname='test1')
        self.assertFalse(v('test3'))
        self.assertListEqual(['test1 FAILED: test3 does not equal test'], v.fail_messages())
        self.assertEqual('test1 FAILED: test3 does not equal test', v.fail_messages(join='\n'))

    def test_mixed_both_messages(self):
        v = Validator(ValidateInstance(str), ValidateEq('test'), fieldname='test1')
        self.assertFalse(v('test3'))
        self.assertListEqual(['test1 PASSED: str is an instance of str', 'test1 FAILED: test3 does not equal test'], v.messages())
        self.assertEqual('test1 PASSED: str is an instance of str\ntest1 FAILED: test3 does not equal test', v.messages(join='\n'))
                    
    def test_extra_info(self):
        v = Validator(fieldname='test1')
        v.add_validators(ValidateInstance())        
        v.add_validators(ValidateEq(name='eq'))
        self.assertTrue(v('test', instance=str, eq='test'))
        self.assertFalse(v(1, instance=str, eq='test'))
        self.assertFalse(v('test2', instance=str, eq='test'))

    def test_called_validator(self):
        v = Validator(fieldname='test1')
        v.add_validators(ValidateInstance())        
        v.add_validators(ValidateEq())
        self.assertTrue(v('test', validators='instance', instance=str))
        self.assertTrue(v('test2', validators='instance', instance=str))
        self.assertFalse(v(1, instance=str, eq=1))
        self.assertFalse(v('test2', eq='test', instance=str))

    def test_no_validators(self):
        v = Validator(fieldname='test1')
        self.assertTrue(v('test'))
        self.assertTrue(v('test2'))
        self.assertTrue(v(1))
        self.assertTrue(v('test2'))

    '''
    def test_validator_groups(self):
        v = Validator(fieldname='test1')
        v.add_validators(ValidateEq(150), group='eq1_test')
        v.add_validators(ValidateEq(50), group='eq2_test')
        v.add_validators(ValidateLT(100))
        v.add_validators(ValidateCompare(gt=1), group=['eq1_test', 'eq2_test'])        
        self.assertFalse(v(150, group='eq1_test'))
        self.assertEqual(1, v.fail_count('eqi_test'))
        self.assertTrue(v(2))
        self.assertEqual(0, v.fail_count())

        self.assertTrue(v(50, group='eq2_test'))
        self.assertEqual(0, v.fail_count('eq2_test'))

        self.assertFalse(v(-1, group='eq2_test'))
        self.assertEqual(2, v.fail_count('eq2_test'))
        
    def test_groups_getattr(self):
        v = Validator(fieldname='test1')
        v.eq1_test.add_validators(ValidateEq(150))
        v.eq2_test.add_validators(ValidateEq(50))
        v.add_validators(ValidateLT(100))
        v.add_validators(ValidateCompare(gt=1), group=['eq1_test', 'eq2_test'])        
        self.assertFalse(v.eq1_test(150))
        self.assertEqual(1, v.eq1_test.fail_count())
        self.assertTrue(v(2))
        self.assertEqual(0, v.fail_count())

        self.assertTrue(v.eq2_test(50))
        self.assertEqual(0, v.fail_count('eq2_test'))

        self.assertFalse(v(-1, group='eq2_test'))
        self.assertEqual(2, v.fail_count('eq2_test'))
        
        self.assertEqual(1, len(v))
        self.assertEqual(3, len(v.eq1_test))
        self.assertEqual(3, len(v.eq2_test))
    '''
    def test_invalid_validator_error(self):
        v = Validator(ValidateEq('test'))
        with self.assertRaises(InvalidValidatorError):
            v('test2', validators='foo')        
        
    def test_not_a_validator_error(self):
        with self.assertRaises(AttributeError):
            v = Validator(self)
    '''
    def test_duplicate_validator_name_error(self):
        v = Validator()
        v.add_validators(ValidateInstance(str, name='foo'))
        with self.assertRaises(DuplicateValidatorNameError):
            v.add_validators(ValidateInstance(int, name='foo'))
    '''

class JunkClassGood(object):
    test_prop = True

    def good_if_test(self, str_in):
        return str_in == 'test'

    def test_meth(self):
        return True

junk_class_good = JunkClassGood()


class JunkClassBad(object):
    test_prop = False

    def good_if_test(self, str_in):
        return str_in != 'test'

    def test_meth(self):
        return False

junk_class_bad = JunkClassBad()


class TestValidators(TestCase):
    
    """
    ValidateInstance
    ValidateSubType
    ValidateEmpty
    ValidateIs
    ValidateIn
    ValidateComp
        ValidateEq
        ValidateLt
        ValidateGt
        ValidateGte
        ValidateLte
        ValidateBetween
    ValidateStartsWith
    ValidateEndsWith
    ValidateTrue
    ValidateFalse
    ValidateOr
    ValidateAnd
    ValidateFuncWrapper
    ValidateMethod
    """
    
    def test_validators(self):
        
        test_set = [
            (0, ValidateInstance, str, 'foo', 1),
            (1, ValidateSubClass, TestCase, self, junk_class_good),
            (2, ValidateEmpty, [None, _UNSET], _UNSET, 'str'),
            (3, ValidateIs, None, None, 'test'),
            (4, ValidateIn, ['foo', 'bar'], 'foo', 'blah'),

            (6, ValidateComp, {'eq': 'foobar'}, 'foobar', 'foo'),
            (7, ValidateComp, {'lt': 10}, 1, 100),
            (8, ValidateComp, {'gt': 10}, 100, 1),
            (9, ValidateComp, {'gte': 100}, 100, 1),
            (10, ValidateComp, {'gte': 100}, 101, 1),
            (11, ValidateComp, {'lte': 100}, 100, 200),
            (12, ValidateComp, {'lte': 100}, 99, 200),
            (13, ValidateComp, {'gt': 20, 'lt': 100}, 24, 200),
            (14, ValidateComp, {'gt': 20, 'lt': 100}, 40, 1),

            (15, ValidateEq, 'foobar', 'foobar', 'foo'),
            (16, ValidateLt, 10, 1, 100),
            (17, ValidateGt, 100, 101, 20),
            (18, ValidateGte, 100, 100, 1),
            (19, ValidateGte, 100, 101, 1),
            (20, ValidateLte, 100, 100, 200),
            (21, ValidateLte, 100, 99, 200),
            (22, ValidateBetween, [20, 100], 24, 200),
            (23, ValidateBetween, [20, 100], 40, 1),

            (24, ValidateStartsWith, 'foo', 'foobar', 'barfoo'),
            (25, ValidateEndsWith, 'bar', 'foobar', 'barfoo'),
            (26, ValidateTrue, [], True, False),
            (27, ValidateFalse, [], False, True),
            (28, ValidateFuncWrapper, junk_class_good.good_if_test, 'test', 'blah'),
            (29, ValidateMethod, 'test_meth', junk_class_good, junk_class_bad),
            (30, ValidateMethod, 'test_prop', junk_class_good, junk_class_bad),
            (31, ValidateOr, (ValidateInstance(str), ValidateInstance(int)), 'test', {'foo': 'bar'}),
            (32, ValidateOr, (ValidateInstance(str), ValidateInstance(int)), 1, {'foo': 'bar'}),
            (33, ValidateAnd, (ValidateInstance(str), ValidateEq('test')), 'test', 'test2'),
        ]

        for test in test_set:
            # print(test)
            msg = '%s' % str(test)
            with self.subTest(msg):
                args = []
                kwargs = {}
                if isinstance(test[2], dict):
                    kwargs = test[2]
                elif isinstance(test[2], (list,tuple)):
                    args = test[2]
                else:
                    args = [test[2]]

                vt = test[1](*args, **kwargs)

                v = Validator(vt)
                msg2 = msg+' [PASS]'
                with self.subTest(msg2):
                    self.assertTrue(v(test[3]))
                msg2 = msg+' [FAIL]'
                with self.subTest(msg2):
                    self.assertFalse(v(test[4]))

                kwargs['invert'] = True
                vt2 = test[1](*args, **kwargs)

                v2 = Validator(vt2)
                msg2 = msg+'[INVERTED] [PASS]'
                with self.subTest(msg2):
                    self.assertTrue(v2(test[4]))
                msg2 = msg+'[INVERTED] [FAIL]'
                with self.subTest(msg2):
                    self.assertFalse(v2(test[3]))
