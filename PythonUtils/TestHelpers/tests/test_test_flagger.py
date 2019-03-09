import unittest
from PythonUtils.BaseUtils import iif, init_dict, merge_object
from PythonUtils.TestHelpers.test_flagger import *
from PythonUtils.TestHelpers.test_common import make_exp_act_str, make_msg, TestMsgHelper
import os
import sys
import platform
import re


class TestRegex(unittest.TestCase):

    def test_re_match(self):
        # EXPECT_NAMES = r'machine|node|platform_aliased|platform_terse|processor|python_compiler|python_implementation|python_branch|release|system|version'
        # re_in = r'skip_if_(?P<is_not>is|not)_platform_(?P<platform_name>.+)_(?P<platform_func>%s)_(?P<expect>.+)' % EXPECT_NAMES
        re_in = r'skip_if_(?P<is_not>is|not)_pyv_(?P<pyv_name>[0-9\.]+)(?P<modifier>[+-]?)'
        # re_in = r'skip_if_(?P<is_not>is|not)_os_(?P<os_name>.+)'
        # re_in = r'skip_if_(?P<is_not>is|not)_os_.*'
        tests = [
            # (str_in, Match_TF, Match_dict),
            # ('skip_if_not_platform_machine_AMD64', True, {'platform_name': '', 'is_not': 'not'})
            ('skip_if_not_pyv_1.0+', True, {'pyv_name': '1.0', 'modifier': '+', 'is_not': 'not'})
        ]

        for str_in, match_tf, match_dict in tests:
            with self.subTest(str_in):
                rex = re.compile(re_in)
                tmp_match = rex.fullmatch(str_in)
                if match_tf:
                    self.assertTrue(tmp_match)
                    self.assertEqual(match_dict, tmp_match.groupdict())
                else:
                    self.assertFalse(rex.fullmatch(str_in))


class FixtureTestCase(object):
    """test_desc"""
    def id(self):
        return 'test_module.test_case.test_name'    
ftc = FixtureTestCase()


class FlaggerFixture(object):
    allow_no_flags = False
    skip_on_unknown = False
    allow_unknown = True
    flags = {}
    skip_ids = {}
    tests = {}

flagger_fixture = FlaggerFixture()


class TestTestItemBase(unittest.TestCase):
    maxDiff = None
    skip_build = False
    build_kwargs = None

    def make_msg(self, exp, act, msg):
        if isinstance(msg, TestMsgHelper):
            msg.config = self.get_config_dict()
            msg.other_objs['self.obj_data'] = self.obj_data
            msg = msg.make_msg(exp=exp, act=act)
        return msg

    def assertEqual(self, exp, act, msg=None):
        msg = self.make_msg(exp=exp, act=act, msg=msg)
        super(TestTestItemBase, self).assertEqual(exp, act, msg=msg)

    def assertNotEqual(self, exp, act, msg=None, levels=None, **msg_kwargs):
        msg = self.make_msg(exp=exp, act=act, msg=msg)
        super(TestTestItemBase, self).assertNotEqual(exp, act, msg=msg)

    def assertTrue(self, act, msg=None, levels=None, **msg_kwargs):
        msg = self.make_msg(exp=True, act=act, msg=msg)
        super(TestTestItemBase, self).assertTrue(act, msg=msg)

    def assertFalse(self, act, msg=None, levels=None, **msg_kwargs):
        msg = self.make_msg(exp=False, act=act, msg=msg)
        super(TestTestItemBase, self).assertFalse(act, msg=msg)

    def tearDown(self):
        self.reset_vars()

    def reset_vars(self):
        self.skipped_flags = []
        self.test_obj = None
        self.test_obj_2 = None
        self.flag_obj_1 = None
        self.flag_obj_2 = None
        self.id_obj = None
        self.flag_count = 2
        self.flagger_fixture = FlaggerFixture()

        self.obj_data = dict(
            test_obj=dict(
                obj_class=TestFlaggerTestObj,
                name='my_test_name',
                desc='test_desc',
                stats=dict(passed=None, failed=None, raised=None, run=None, skipped=None),
                eq_names=[],
                ne_names=['foobar'],
                obj=self.test_obj,
                status='Not Tried',
                status_prefix='?',
                summary_data='',
                status_name='{name} {status}',
                short_name='[{status_prefix}] {name}',
                long_name='[{status_prefix}] {name}',
                dump='{name} [{status}]\n'
                     '    Desc          : {desc}\n'
                     '    Skipped Names : * None *\n'
                     '    Flags         : * None *',
            ),
            test_obj_2=dict(
                obj_class=TestFlaggerTestObj,
                name='my_test_name_2',
                desc='test_desc_2',
                stats=dict(passed=None, failed=None, raised=None, run=None, skipped=None),
                eq_names=[],
                ne_names=['foobar'],
                obj=self.test_obj_2,
                status='Not Tried',
                status_prefix='?',
                summary_data='',
                status_name='{name} {status}',
                short_name='[{status_prefix}] {name}',
                long_name='[{status_prefix}] {name}',
                dump='{name} [{status}]\n'
                     '    Desc          : {desc}\n'
                     '    Skipped Names : * None *\n'
                     '    Flags         : * None *',
            ),
            flag_obj_1=dict(
                obj_class=TestFlaggerFlagObj,
                name='flag_name_1',
                desc='flag_desc_1',
                stats=dict(passed=0, failed=0, raised=0, run=0, skipped=0),
                eq_names=[],
                ne_names=['foobar'],
                obj=self.flag_obj_1,
                status='Inc',
                status_prefix='I',
                summary_data='Not Found',
                status_name='{name} {status}',
                short_name='[{status_prefix}] {name}',
                long_name='{name} [{status}] | Not Found',
                dump='{name} [{status}]\n'
                     '    Desc  : {desc}\n'
                     '    Stats : * No Stats *\n'
                     '    Tests : * None *'
            ),
            flag_obj_2=dict(
                obj_class=TestFlaggerFlagObj,
                name='flag_name_2',
                desc=None,
                stats=dict(passed=0, failed=0, raised=0, run=0, skipped=0),
                eq_names=[],
                ne_names=['foobar'],
                obj=self.flag_obj_2,
                status='Inc',
                status_prefix='I',
                summary_data='Not Found',
                status_name='{name} {status}',
                short_name='[{status_prefix}] {name}',
                long_name='{name} [{status}] | Not Found',
                dump='{name} [{status}]\n'
                     '    Stats : * No Stats *\n'
                     '    Tests : * None *'
            ),
            id_obj=dict(
                obj_class=TestFlaggerSkipIDObj,
                name='sip_obj',
                desc='test_skip_desc',
                stats=dict(test_count=0, not_found=1),
                eq_names=['sip_obj', 'sip_objfoobar'],
                ne_names=['foobar', 'no_sip_obj'],
                obj=self.id_obj,
                status='Not Matched',
                status_prefix='U',
                summary_data='{status}',
                status_name='{name} {status}',
                short_name='[{status_prefix}] {name}',
                long_name='{name} | {status}',
                dump='{name} [{status}]\n'
                     '    Desc  : {desc}\n'
                     '    Tests : * None *',
            ),

        )

        self.skip_flag_defs = dict(
            status='Skip',
            status_prefix='S',
        )

        self.inc_flag_defs = dict(
            status='Inc',
            status_prefix='I',
        )

        self.id_obj_match_defs = dict(
            name='*test_name*',
            eq_names=['test_name', 'test_name_foobar', 'my_test_name'],
        )
        self.id_obj_no_match_defs = dict(
            name='sip_obj*',
            eq_names=['sip_obj', 'sip_objfoobar'],
        )

        if self.id_obj_match:
            self.obj_data['id_obj'].update(self.id_obj_match_defs)
        else:
            self.obj_data['id_obj'].update(self.id_obj_no_match_defs)

        if self.skip_flag_1:
            self.obj_data['flag_obj_1'].update(self.skip_flag_defs)
        else:
            self.obj_data['flag_obj_1'].update(self.inc_flag_defs)

        if self.skip_flag_2:
            self.obj_data['flag_obj_2'].update(self.skip_flag_defs)
        else:
            self.obj_data['flag_obj_2'].update(self.inc_flag_defs)

    def get_object_info(self, obj_type, **kwargs):
        tmp_object = dict(self.obj_data[obj_type])
        tmp_object.update(kwargs)
        if self.test_obj is not None:
            tmp_object.update(dict(
                test_name=self.test_obj.name,
                test_status=self.test_obj.status,
                test_desc=self.test_obj.desc,
                test_prefix=self.test_obj.status_prefix,
            ))
        if self.test_obj_2 is not None:
            tmp_object.update(dict(
                test_2_name=self.test_obj_2.name,
                test_2_status=self.test_obj_2.status,
                test_2_desc=self.test_obj_2.desc,
                test_2_prefix=self.test_obj_2.status_prefix,
            ))
        if self.flag_obj_1 is not None:
            tmp_object.update(dict(
                flag1_name=self.flag_obj_1.name,
                flag1_status=self.flag_obj_1.status,
                flag1_desc=self.flag_obj_1.desc,
                flag1_prefix=self.flag_obj_1.status_prefix,
            ))
        if self.flag_obj_2 is not None:
            tmp_object.update(dict(
                flag2_name=self.flag_obj_2.name,
                flag2_status=self.flag_obj_2.status,
                flag2_desc=self.flag_obj_2.desc,
                flag2_prefix=self.flag_obj_2.status_prefix,
            ))
        if self.id_obj is not None:
            tmp_object.update(dict(
                sid_name=self.id_obj.name,
                sid_status=self.id_obj.status,
                sid_desc=self.id_obj.desc,
                sid_prefix=self.id_obj.status_prefix,
            ))

        for key, item in tmp_object.items():
            if isinstance(item, str) and '{' in item:
                tmp_object[key] = item.format(**tmp_object)

        return tmp_object

    def get_config_dict(self, **kwargs):

        config_dict = dict(
            test_obj=self.test_obj,
            test_obj_2=self.test_obj_2,
            flag_obj_1=self.flag_obj_1,
            flag_obj_2=self.flag_obj_2,
            id_obj=self.id_obj,
            flag_count=self.flag_count,
            skip_flag_1=self.skip_flag_1,
            skip_flag_2=self.skip_flag_2,
            id_obj_match=self.id_obj_match,
            match_flag_1=self.match_flag_1,
            match_flag_2=self.match_flag_2,
            set_result_to=self.set_result_to,

        )
        config_dict.update(kwargs)
        return config_dict

    def check_obj(self, obj_in_type, inc_stats_dict=True, msg='', **tests):
        tmp_obj_data = self.get_object_info(obj_in_type, **tests)
        obj = getattr(self, obj_in_type)
        msg = msg + obj_in_type
        msg.other_objs['expected_text'] = tmp_obj_data

        if inc_stats_dict:
            tmp_act = obj.stats_dict(full_field_names=False)
            self.assertEqual(tmp_obj_data['stats'], tmp_act, msg=msg + 'check dict')

        for attr_name in ['status', 'status_prefix', 'summary_data', 'short_name', 'long_name', 'dump']:
            if attr_name in tmp_obj_data:
                exp_value = tmp_obj_data[attr_name]
                if exp_value is None:
                    continue
                with self.subTest('%s.%s' % (obj_in_type, attr_name)):
                    tmp_ret = getattr(obj, attr_name)
                    if attr_name in ['dump']:
                        tmp_ret = tmp_ret()
                    self.assertEqual(exp_value, tmp_ret, msg=msg + attr_name)

    def check_objects(self, inc_test_1=True, inc_test_2=True, inc_flag_1=True, inc_flag_2=True, inc_id=True, inc_stats=True, msg='', text_updates=None):
        text_updates = text_updates or {}
        if inc_test_1:
            self.check_obj('test_obj', inc_stats_dict=inc_stats, msg=msg, **text_updates.get('test_obj', {}))
        if inc_test_2:
            self.check_obj('test_obj_2', inc_stats_dict=inc_stats, msg=msg, **text_updates.get('test_obj_2', {}))
        if inc_flag_1:
            self.check_obj('flag_obj_1', inc_stats_dict=inc_stats, msg=msg, **text_updates.get('flag_obj_1', {}))
        if inc_flag_2:
            self.check_obj('flag_obj_2', inc_stats_dict=inc_stats, msg=msg, **text_updates.get('flag_obj_2', {}))
        if inc_id:
            self.check_obj('id_obj', inc_stats_dict=inc_stats, msg=msg, **text_updates.get('id_obj', {}))

    def build(self, set_result, inc_pf=True, inc_check=True, msg=''):

        self.skip_flag_1 = False
        self.skip_flag_2 = False
        self.id_obj_match = False
        self.match_flag_1 = True
        self.match_flag_2 = True
        self.set_result_to = set_result

        if self.set_result_to == 'skipped':
            if not (self.skip_flag_1 or self.skip_flag_2):
                self.skip_flag_1 = True
        elif self.set_result_to == 'one_flag':
            self.match_flag_2 = False
        elif self.set_result_to == 'no_flags':
            self.match_flag_1 = False
            self.match_flag_2 = False
        elif self.set_result_to == 'id_skipped':
            self.id_obj_match = True
            self.set_result_to = 'skipped'
            if not (self.skip_flag_1 or self.skip_flag_2):
                self.skip_flag_1 = True
        elif self.set_result_to == 'all_skipped':
            self.id_obj_match = True
            self.set_result_to = 'skipped'
            self.skip_flag_1 = True
            self.skip_flag_2 = True

        self.reset_vars()

        msg = TestMsgHelper(levels=[msg, set_result], format_kwargs={'format_type': 'str'})

        self.build_obj(msg=msg + 'build')

        self.check_objects(msg=msg + 'after build')

        if inc_check:
            self.link_objects(msg=msg + 'link')

        if inc_pf:
            self.set_result(msg=msg + 'set_result')

        return msg

    def build_obj(self, obj_kwargs=None, flag_1_kwargs=None, flag_2_kwargs=None, with_id_kwargs=None,
                  skip_flag_1=None, skip_flag_2=None, msg=''):

        def make_obj(obj_in_type, msg='', **kwargs):

            obj_data = self.obj_data[obj_in_type]
            name = obj_data['name']
            desc = obj_data.get('desc', None)
            eq_names = obj_data['eq_names']
            ne_names = obj_data['ne_names']

            obj_kwargs = init_dict({'name': name, 'desc': desc}, kwargs)
            tmp_obj = obj_data['obj_class'](self.flagger_fixture, **obj_kwargs)
            setattr(self, obj_in_type, tmp_obj)

            self.assertEqual(name, tmp_obj.name, msg=msg + 'check name')
            self.assertEqual(name, str(tmp_obj), msg=msg + 'check str(obj)')
            self.assertEqual(name, tmp_obj, msg=msg + 'check eq_name')
            self.assertNotEqual('foobar', tmp_obj, msg=msg + 'check eq_bad_name')
            for n in make_list(eq_names):
                self.assertEqual(n, tmp_obj, msg=msg + 'check check_eq_name: ' + n)
            for n in make_list(ne_names):
                self.assertNotEqual(n, tmp_obj, msg=msg + 'check check_ne_name: ' + n)
            if desc is not None:
                self.assertEqual(desc, tmp_obj.desc, msg=msg + 'check check_desc')

        if skip_flag_1 is None:
            skip_flag_1 = self.skip_flag_1
        if skip_flag_2 is None:
            skip_flag_2 = self.skip_flag_2

        obj_kwargs = obj_kwargs or {}
        make_obj('test_obj', msg=msg + 'test_1', **obj_kwargs)
        self.flagger_fixture.tests[self.test_obj.name] = self.test_obj

        make_obj('test_obj_2', msg=msg + 'test_1')
        self.flagger_fixture.tests[self.test_obj_2.name] = self.test_obj_2

        flag_1_kwargs = flag_1_kwargs or {}
        if skip_flag_1:
            flag_1_kwargs['_should_skip'] = True
        make_obj('flag_obj_1', msg=msg + 'flag_1', **flag_1_kwargs)
        self.flagger_fixture.flags[self.flag_obj_1.name] = self.flag_obj_1

        flag_2_kwargs = flag_2_kwargs or {}
        if skip_flag_2:
            flag_2_kwargs['_should_skip'] = True
        make_obj('flag_obj_2', msg=msg + 'flag_2', **flag_2_kwargs)
        self.flagger_fixture.flags[self.flag_obj_2.name] = self.flag_obj_2

        with_id_kwargs = with_id_kwargs or {}
        make_obj('id_obj', msg=msg + 'id_obj', **with_id_kwargs)
        self.flagger_fixture.skip_ids[self.id_obj.name] = self.id_obj

    def link_objects(self, match_flag_1=None, match_flag_2=None, id_obj_match=None, msg=''):
        flags = []
        is_skipped = False

        if match_flag_1 is None:
            match_flag_1 = self.match_flag_1
        if match_flag_2 is None:
            match_flag_2 = self.match_flag_2
        if id_obj_match is None:
            id_obj_match = self.id_obj_match

        if match_flag_1:
            flags.append(self.flag_obj_1.name)
            if self.flag_obj_1._should_skip:
                self.skipped_flags.append(self.flag_obj_1)
                is_skipped = True

        if match_flag_2:
            flags.append(self.flag_obj_2.name)
            if self.flag_obj_2._should_skip:
                self.skipped_flags.append(self.flag_obj_2)
                is_skipped = True
                with self.assertRaises(unittest.SkipTest, msg=msg + 'test_obj_2 skip check'):
                    self.test_obj_2.check(self.flag_obj_2)
            else:
                self.test_obj_2.check(self.flag_obj_2)

        id_obj_match_obj = None
        if id_obj_match:
            is_skipped = True
            id_obj_match_obj = self.id_obj

        if not match_flag_2 and not match_flag_1:
            self.flagger_fixture.allow_no_flags = True

        if is_skipped:
            with self.assertRaises(unittest.SkipTest, msg=msg + 'test_obj skip check'):
                self.test_obj.check(flags, skip_id_obj=id_obj_match_obj)
        else:
            self.test_obj.check(flags, skip_id_obj=id_obj_match_obj)

    def set_result(self, set_result=None, msg=''):
        set_result = set_result or self.set_result_to
        if set_result == 'failed':
            self.test_obj.set_result(AssertionError('failed'))
        elif set_result == 'passed':
            self.test_obj.set_result()
        elif set_result == 'raised':
            self.test_obj.set_result(AttributeError('raised'))

    def default_run_data(self, **kwargs):
        """
        stats=dict(passed=None, failed=None, raised=None, run=None, skipped=None),
        status='Not Tried',
        status_prefix='?',
        summary_data='',
        status_name='{name} {status}',
        short_name='[{status_prefix}] {name}',
        long_name='[{status_prefix}] {name}',
        dump='{name} [{status}]\n'
            '    Desc          : {desc}\n'
            '    Skipped Names : * None *\n'
            '    Flags         : * None *',

        """

        tmp_ret = {
            'test_obj': {
                'stats': {'run': True, 'passed': None, 'failed': None, 'raised': None, 'skipped': False},
                'status': 'Run',
                'status_prefix': 'R',
                'summary_data': '',
                'status_name': '{name} {status}',
                'short_name': '[{status_prefix}] {name}',
                'long_name': '[{status_prefix}] {name}',
                'dump': '{name} [{status}]\n'
                      '    Desc          : {desc}\n'
                      '    Skipped Names : * None *\n'
                      '    Flags         : flag_name_1\n'
                      '                    flag_name_2',
            },
            'test_obj_2': {
                'stats': {'run': True, 'passed': None, 'failed': None, 'raised': None, 'skipped': False},
                'status': 'Run',
                'status_prefix': 'R',
                'summary_data': '',
                'status_name': '{name} {status}',
                'short_name': '[{status_prefix}] {name}',
                'long_name': '[{status_prefix}] {name}',
                'dump': '{name} [{status}]\n'
                        '    Desc          : {desc}\n'
                        '    Skipped Names : * None *\n'
                        '    Flags         : flag_name_2',

            },
            'flag_obj_1': {
                'stats': {'run': 1, 'passed': 0, 'failed': 0, 'raised': 0, 'skipped': 0},
                'long_name': '{name} [{status}] | R:1 S:0 / P:0 F:0 E:0',
                'summary_data': 'R:1 S:0 / P:0 F:0 E:0',
                'dump': '{name} [{status}]\n'
                        '    Desc               : {desc}\n'
                        '    Skipped Names      : * None *\n'                                                         
                        '    Run/Skipped Stats:\n'
                        '        Run            : 1\n'
                        '        Skipped/Self   : 0\n'
                        '        Skipped/Other  : 0\n'
                        '    Passed/Failed Stats:\n'
                        '        Passed         : 0\n'
                        '        Failed         : 0\n'
                        '        Raised         : 0\n'
                        '    Tests              : my_test_name\n'

            },
            'flag_obj_2': {
                'stats': {'run': 1, 'passed': 0, 'failed': 0, 'raised': 0, 'skipped': 0},
                'long_name': '{name} [{status}] | R:1 S:0 / P:0 F:0 E:0',
                'summary_data': 'R:1 S:0 / P:0 F:0 E:0',
                'dump': '{name} [{status}]\n'
                        '    Desc          : {desc}\n'
                        '    Skipped Names : * None *\n'                                                         
                        '    Flags         : * None *',

            },
            'id_obj': {
            },
        }
        tmp_ret = merge_object(tmp_ret, kwargs)
        return tmp_ret

    def default_passed_data(self, **kwargs):
        tmp_ret = self.default_run_data()
        update = {
            'test_obj': {
                'stats': {'run': True, 'passed': None, 'failed': None, 'raised': None, 'skipped': False},
                'status': 'Run',
                'status_prefix': 'R',
                'summary_data': '',
                'status_name': '{name} {status}',
                'short_name': '[{status_prefix}] {name}',
                'long_name': '[{status_prefix}] {name}',
                'dump': '{name} [{status}]\n'
                      '    Desc          : {desc}\n'
                      '    Skipped Names : * None *\n'                                                         
                        '    Flags         : * None *',
            },
            'test_opj_2': {
                'stats': {'run': True, 'passed': None, 'failed': None, 'raised': None, 'skipped': False},
                'status': 'Run',
                'status_prefix': 'R',
                'summary_data': '',
                'status_name': '{name} {status}',
                'short_name': '[{status_prefix}] {name}',
                'long_name': '[{status_prefix}] {name}',
                'dump': '{name} [{status}]\n'
                        '    Desc          : {desc}\n'
                        '    Skipped Names : * None *\n'                                                         
                        '    Flags         : * None *',

            },
            'flag_obj_1': {
                'stats': {'run': 1, 'passed': None, 'failed': None, 'raised': None, 'skipped': 0},
                'status': 'Run',
                'status_prefix': 'R',
                'summary_data': '',
                'status_name': '{name} {status}',
                'short_name': '[{status_prefix}] {name}',
                'long_name': '[{status_prefix}] {name}',
                'dump': '{name} [{status}]\n'
                        '    Desc          : {desc}\n'
                        '    Skipped Names : * None *\n'                                                         
                        '    Flags         : * None *',

            },
            'flag_obj_2': {
                'stats': {'run': 1, 'passed': None, 'failed': None, 'raised': None, 'skipped': 0},
                'status': 'Run',
                'status_prefix': 'R',
                'summary_data': '',
                'status_name': '{name} {status}',
                'short_name': '[{status_prefix}] {name}',
                'long_name': '[{status_prefix}] {name}',
                'dump': '{name} [{status}]\n'
                        '    Desc          : {desc}\n'
                        '    Skipped Names : * None *\n'                                                         
                        '    Flags         : * None *',

            },
            'id_obj': {
                'stats': {'test_count': 0, 'not_found': 1},
                'status': 'Run',
                'status_prefix': 'R',
                'summary_data': '',
                'status_name': '{name} {status}',
                'short_name': '[{status_prefix}] {name}',
                'long_name': '[{status_prefix}] {name}',
                'dump': '{name} [{status}]\n'
                        '    Desc          : {desc}\n'
                        '    Skipped Names : * None *\n'                                                         
                        '    Flags         : * None *',

            },
        }
        tmp_ret = merge_object(tmp_ret, update, kwargs)
        return tmp_ret

    def test_init_tests(self):
        # run is the default build
        with self.subTest('init_run'):
            self.build('run', msg='init_test_run')
            self.assertEqual('Run', self.test_obj.status)
            self.assertEqual(2, len(self.flag_obj_2.tests))
        # skipped
        with self.subTest('init_skipped'):
            self.build('skipped', msg='init_test_skipped')
            self.assertTrue(self.flag_obj_1._should_skip)
            self.assertFalse(self.flag_obj_2._should_skip)
            self.assertEqual('Skipped', self.test_obj.status)
            self.assertEqual(2, len(self.flag_obj_2.tests))

        with self.subTest('init_one_flag'):
            self.build('one_flag', msg='init_test_one_flag')
            self.assertEqual(1, len(self.test_obj.flags))
            self.assertEqual('Run', self.test_obj.status)
            self.assertEqual(0, len(self.flag_obj_2.tests))

        with self.subTest('no_flags'):
            self.build('no_flags', msg='init_test_no_flags')
            self.assertEqual(0, len(self.test_obj.flags))
            self.assertEqual('Run', self.test_obj.status)
            self.assertEqual(0, len(self.flag_obj_2.tests))

        # skipped
        with self.subTest('init_ID_skipped'):
            self.build('id_skipped', msg='init_test_id_skipped')
            self.assertEqual('Skipped', self.test_obj.status)
            self.assertTrue(self.flag_obj_1._should_skip)
            self.assertFalse(self.flag_obj_2._should_skip)
            self.assertIsNotNone(self.test_obj.skip_id_obj)

        # skipped
        with self.subTest('init_all_skipped'):
            self.build('all_skipped', msg='init_test_all_skipped')
            self.assertEqual('Skipped', self.test_obj.status)
            self.assertTrue(self.flag_obj_1._should_skip)
            self.assertTrue(self.flag_obj_2._should_skip)
            self.assertIsNotNone(self.test_obj.skip_id_obj)

        # passed
        with self.subTest('init_passed'):
            self.build('passed', msg='init_test_passed')
            self.assertEqual('Passed', self.test_obj.status)

        # failed
        with self.subTest('init_failed'):
            self.build('failed', msg='init_test_failed')
            self.assertEqual('Failed', self.test_obj.status)

        # raised
        with self.subTest('init_raised'):
            self.build('raised', msg='init_test_raised')
            self.assertEqual('Raised', self.test_obj.status)



        """
        # skipped - passed
        with self.subTest('init_skipped_passed'):
            with self.assertRaises(AttributeError):
                self.build_obj('passed', skip_flag_1=True)

        # skipped - failed
        with self.subTest('init_skipped_failed'):
            with self.assertRaises(AttributeError):
                self.build_obj('failed', skip_flag_1=True)

        # skipped - raised
        with self.subTest('init_skipped_raised'):
            with self.assertRaises(AttributeError):
                self.build_obj(set_result='raised', skip_flag_1=True)
        """

    def test_text_run(self):
        """
        stats=dict(passed=None, failed=None, raised=None, run=None, skipped=None),
        status='Not Tried',
        status_prefix='?',
        summary_data='',
        status_name='{name} {status}',
        short_name='[{status_prefix}] {name}',
        long_name='[{status_prefix}] {name}',
        dump='{name} [{status}]\n'
            '    Desc          : {desc}\n'
            '    Skipped Names : * None *\n'
            '    Flags         : * None *',

        """
        msg = self.build('run', msg='test_text_run', inc_pf=False)

        updates = self.default_run_data()

        self.check_objects(msg=msg + 'after build', text_updates=updates)


    def test_text_skip(self):
        msg = self.build('skipped', msg='test_text_skipped', inc_pf=False)
        updates = {
            'test_pbj': {},
            'test_opj_2': {},
            'flag_obj_1': {},
            'flag_obj_2': {},
            'id_obj': {},
        }

        updates = self.default_run_data(**updates)

        self.check_objects(msg=msg + 'after build', text_updates=updates)

    def test_text_one_flag(self):
        msg = self.build('one_flag', msg='test_text_one_flag', inc_pf=False)
        updates = {
            'test_pbj': {},
            'test_opj_2': {},
            'flag_obj_1': {},
            'flag_obj_2': {},
            'id_obj': {},
        }

        self.check_objects(msg=msg + 'after build', text_updates=updates)

    def test_text_no_flags(self):
        msg = self.build('no_flags', msg='test_text_no_flags', inc_pf=False)
        updates = {
            'test_pbj': {},
            'test_opj_2': {},
            'flag_obj_1': {},
            'flag_obj_2': {},
            'id_obj': {},
        }
        updates = self.default_run_data(**updates)

        self.check_objects(msg=msg + 'after build', text_updates=updates)

    def test_text_all_skipped(self):
        msg = self.build('all_skipped', msg='test_text_all_skipped', inc_pf=False)
        updates = {
            'test_pbj': {},
            'test_opj_2': {},
            'flag_obj_1': {},
            'flag_obj_2': {},
            'id_obj': {},
        }
        updates = self.default_run_data(**updates)

        self.check_objects(msg=msg + 'after build', text_updates=updates)

    def test_text_id_skipped(self):
        msg = self.build('id_skipped', msg='test_text_id_skipped', inc_pf=False)
        updates = {
            'test_pbj': {},
            'test_opj_2': {},
            'flag_obj_1': {},
            'flag_obj_2': {},
            'id_obj': {},
        }
        updates = self.default_run_data(**updates)

        self.check_objects(msg=msg + 'after build', text_updates=updates)

    def test_text_passed(self):
        msg = self.build('passed', msg='test_text_passed')
        updates = {
            'test_pbj': {},
            'test_opj_2': {},
            'flag_obj_1': {},
            'flag_obj_2': {},
            'id_obj': {},
        }
        updates = self.default_passed_data(**updates)

        self.check_objects(msg=msg + 'after pf', text_updates=updates)

    def test_text_failed(self):
        msg = self.build('failed', msg='test_text_failed')
        updates = {
            'test_pbj': {},
            'test_opj_2': {},
            'flag_obj_1': {},
            'flag_obj_2': {},
            'id_obj': {},
        }
        updates = self.default_passed_data(**updates)

        self.check_objects(msg=msg + 'after pf', text_updates=updates)

    def test_text_raised(self):
        msg = self.build('raised', msg='test_text_raised')
        updates = {
            'test_pbj': {},
            'test_opj_2': {},
            'flag_obj_1': {},
            'flag_obj_2': {},
            'id_obj': {},
        }
        updates = self.default_passed_data(**updates)

        self.check_objects(msg=msg + 'after pf', text_updates=updates)


class TestTestFlaggerIDItem(TestTestItemBase):

    @property
    def oit(self):
        return self.id_obj

    def test_matched_run(self):
        true_args = ['no_test_count', 'all_not_found', 'any_not_found']
        false_args = ['any_test_count', 'no_not_found', 'all_test_count', {'inc_tests': 'foobar'}]
        self._test_matched('run', true_args=true_args, false_args=false_args)

    def test_matched_id_matched(self):
        true_args = ['any_test_count', 'no_not_found', 'all_test_count', {'inc_tests': 'my_test_name'}]
        false_args = ['no_test_count', 'all_not_found', 'any_not_found', {'inc_tests': 'foobar'}]
        self._test_matched('id_skipped', true_args=true_args, false_args=false_args)

    def test_text_id_matched(self):
        exp_details = '{name} [{status}] ({desc})'

        exp_detail_dump = '{name} ({desc})\n' \
                          '  Matched Tests : 1\n' \
                          '  Analysis      : {status}\n' \
                          '  Tests         : [{test_prefix}] {test_name} : {test_status}'

        exp_detail_no_status = '{name} ({desc})'

        exp_detail_analysis = '{name} ({desc})\n' \
                              '  {status}\n' \
                              '  Analysis : {status}'

        exp_detail_stats = '{name} [{status}] ({desc})'

        tests = {
            'details': exp_details,
            'details.dump': exp_detail_dump,
            'details.-inc_status': exp_detail_no_status,
            'details.inc_analysis': exp_detail_analysis,
            'details.inc_stats': exp_detail_stats,
        }
        self._test_text('id_matched', **tests)

    def test_text_run(self):
        exp_details = '{name} [{status}] ({desc})'

        exp_detail_dump = '{name} ({desc})\n' \
                          '  Matched Tests : 2\n' \
                          '  Analysis      : {status}\n' \
                          '  Tests         : * None *'

        exp_detail_no_status = '{name} ({desc})'

        exp_detail_analysis = '{name} ({desc})\n' \
                              '  {status}\n' \
                              '  Analysis : {status}'

        exp_detail_stats = '{name} [{status}] ({desc})'

        tests = {
            'details': exp_details,
            'details.dump': exp_detail_dump,
            'details.-inc_status': exp_detail_no_status,
            'details.inc_analysis': exp_detail_analysis,
            'details.-inc_stats': exp_detail_stats,
        }
        self._test_text('run', **tests)


class TestTestFlaggerTestObj(TestTestItemBase):
    run_statuses = ['id_skipped', 'skipped', 'no_flags', 'one_flag', 'all_skipped', 'run', 'passed', 'raised','failed']

    @property
    def oit(self):
        return self.test_obj

    def test_matched(self):
        def make_sets(scopes, metrics, f1_l, f2_l, id_l):
            scopes = make_list(scopes)
            metrics = make_list(metrics)
            tmp_ret = [ s + '_' + m for s in scopes for m in metrics ]
            tmp_d = {}
            if f1_l and f2_l:
                tmp_d['inc_flag'] = [self.flag_obj_1.name, self.flag_obj_2.name]
            elif f1_l:
                tmp_d['inc_flag'] = self.flag_obj_1.name
            elif f2_l:
                tmp_d['inc_flag'] = self.flag_obj_1.name
            if id_l:
                tmp_d['inc_id'] = self.id_obj.name
            if tmp_d:
                tmp_ret.append(tmp_d)
            return tmp_ret

        def make_metrics(exc=None):
            all_metrics = ['run', 'skipped', 'passed', 'failed', 'raised']
            tmp_ret = all_metrics.copy()
            for x in make_list(exc):
                tmp_ret.remove(x)
            return tmp_ret

        aa_scopes = ['all', 'any']
        no_scopes = 'no'

        for run_status in self.run_statuses:

            flag1_linked = True
            flag2_linked = True
            has_id = False
            false_metrics = None
            true_metrics = run_status

            if run_status == 'id_skipped':
                has_id = True
                true_metrics = 'skipped'

            elif run_status == 'all_skipped':
                has_id = True
                true_metrics = 'skipped'

            elif run_status == 'passed':
                true_metrics = ['passed', 'run']

            elif run_status == 'raised':
                true_metrics = ['raised', 'run']

            elif run_status == 'failed':
                true_metrics = ['failed', 'run']

            if false_metrics is None:
                false_metrics = true_metrics

            true_matches = make_sets(scopes=aa_scopes, metrics=true_metrics, f1_l=flag1_linked, f2_l=flag2_linked, id_l=has_id)
            false_matches = make_sets(scopes=no_scopes, metrics=make_metrics(false_metrics), f1_l=flag1_linked, f2_l=flag2_linked, id_l=has_id)

            self._test_matched('run', true_args=true_matches, false_args=false_matches)


    """
    def test_text(self):
        tests = {
            'status': '{status}',
            'status.as_prefix': '{prefix}',
            'short_name': '{name}',
            'short_name.inc_prefix': '{name}',
            'long_name': '{name} [{status}] ({desc})',
            'long_name.-inc_desc': '{name} [{status}]',
            'long_name.-inc_status': '{name} ({desc})',
            'long_name.inc_prefix': '{prefix}{name} [{status}] ({desc})',
            'summary_data': '[{status}] [{desc}]',
            'summary_data.inc_status': '[{status}] [{desc}]',
            'summary_data.inc_desc': '[{status}]',
            'details': '',
            'details.dump': '',
            'details.inc_status': '',
            'details.inc_analysis': '',
            'details.inc_name': '',
            'details.inc_stats': '',
            'details.add_indent': '',
        }

        self._test_text(**tests)
    """

    def base_text_dict(self, with_id=False):
        nsd = '{name} [{status}] ({desc})'
        nd = '{name} ({desc})'
        f1 = '[{flag1_prefix}] {flag1_name}'
        f2 = '[{flag2_prefix}] {flag2_name}'

        if with_id:
            sid_count = '1'
        else:
            sid_count = '0'

        exp_details = nsd + ' Flags: %s, %s' % (f1, f2)
        if with_id:
            exp_details += ' / Skip ID: {sid_name}'

        exp_detail_no_status = nd

        exp_detail_analysis = nd + '\n' \
                                   '  Analysis : {status}'

        exp_detail_stats = '{name} [{status}] ({desc})\n' \
                           '  Flags    : 2\n' \
                           '  Skip IDs : ' + sid_count

        if with_id:
            exp_detail_dump = nd + '\n' \
                                   '  Analysis   : {status}\n' \
                                   '  Flags      : 2\n' \
                                   '  Skip IDs   : 1\n' \
                                   '  Flags      : %s\n' \
                                   '               %a\n' \
                                   '  Skipped ID : {sid_name}' % (f1, f2)
        else:
            exp_detail_dump = nd + '\n' \
                                   '  Analysis : {status}\n' \
                                   '  Flags    : 2\n' \
                                   '  Skip IDs : 0\n' \
                                   '  Flags    : %s\n' \
                                   '             %a' % (f1, f2)

        tests = {
            'details': exp_details,
            'details.dump': exp_detail_dump,
            'details.-inc_status': exp_detail_no_status,
            'details.inc_analysis': exp_detail_analysis,
            'details.-inc_stats': exp_detail_stats,
        }
        return tests

    def test_text_sets(self):

        for run_status in self.run_statuses:
            if run_status in ['id_skipped', 'all_skipped']:
                has_id = True
            else:
                has_id = False
            self._test_text(run_status, **self.base_text_dict(has_id))


class TestTestFlaggerFlag1Obj(TestTestFlaggerTestObj):

    @property
    def oit(self):
        return self.flag_obj_1

    """
    def test_matched(self):
        def make_sets(scopes, metrics, f1_l, f2_l, id_l):
            scopes = make_list(scopes)
            metrics = make_list(metrics)
            tmp_ret = [s + '_' + m for s in scopes for m in metrics]
            tmp_d = {}
            if f1_l and f2_l:
                tmp_d['inc_flag'] = [self.flag_obj_1.name, self.flag_obj_2.name]
            elif f1_l:
                tmp_d['inc_flag'] = self.flag_obj_1.name
            elif f2_l:
                tmp_d['inc_flag'] = self.flag_obj_1.name
            if id_l:
                tmp_d['inc_id'] = self.id_obj.name
            if tmp_d:
                tmp_ret.append(tmp_d)
            return tmp_ret

        def make_metrics(exc=None):
            all_metrics = ['run', 'skipped', 'passed', 'failed', 'raised']
            tmp_ret = all_metrics.copy()
            for x in make_list(exc):
                tmp_ret.remove(x)
            return tmp_ret

        aa_scopes = ['all', 'any']
        no_scopes = 'no'

        for run_status in ['id_skipped', 'skipped', 'all_skipped', 'run', 'passed', 'raised', 'failed']:

            flag1_linked = True
            flag2_linked = True
            has_id = False
            false_metrics = None
            true_metrics = run_status

            if run_status == 'id_skipped':
                has_id = True
                true_metrics = 'skipped'

            elif run_status == 'all_skipped':
                has_id = True
                true_metrics = 'skipped'

            elif run_status == 'passed':
                true_metrics = ['passed', 'run']

            elif run_status == 'raised':
                true_metrics = ['raised', 'run']

            elif run_status == 'failed':
                true_metrics = ['failed', 'run']

            if false_metrics is None:
                false_metrics = true_metrics

            true_matches = make_sets(scopes=aa_scopes, metrics=true_metrics, f1_l=flag1_linked, f2_l=flag2_linked,
                                     id_l=has_id)
            false_matches = make_sets(scopes=no_scopes, metrics=make_metrics(false_metrics), f1_l=flag1_linked,
                                      f2_l=flag2_linked, id_l=has_id)

            self._test_matched('run', true_args=true_matches, false_args=false_matches)
    """

    def base_text_dict(self, with_id=False):
        nsd = '{name} [{status}] ({desc})'
        nd = '{name} ({desc})'
        f1 = '[{flag1_prefix}] {flag1_name}'
        f2 = '[{flag2_prefix}] {flag2_name}'

        if with_id:
            sid_count = '1'
        else:
            sid_count = '0'

        exp_details = nsd + ' Flags: %s, %s' % (f1, f2)
        if with_id:
            exp_details += ' / Skip ID: {sid_name}'

        exp_detail_no_status = nd

        exp_detail_analysis = nd + '\n' \
                                   '  Analysis : {status}'

        exp_detail_stats = '{name} [{status}] ({desc})\n' \
                           '  Flags    : 2\n' \
                           '  Skip IDs : ' + sid_count

        if with_id:
            exp_detail_dump = nd + '\n' \
                                   '  Analysis   : {status}\n' \
                                   '  Flags      : 2\n' \
                                   '  Skip IDs   : 1\n' \
                                   '  Flags      : %s\n' \
                                   '               %a\n' \
                                   '  Skipped ID : {sid_name}' % (f1, f2)
        else:
            exp_detail_dump = nd + '\n' \
                                   '  Analysis : {status}\n' \
                                   '  Flags    : 2\n' \
                                   '  Skip IDs : 0\n' \
                                   '  Flags    : %s\n' \
                                   '             %a' % (f1, f2)

        tests = {
            'details': exp_details,
            'details.dump': exp_detail_dump,
            'details.-inc_status': exp_detail_no_status,
            'details.inc_analysis': exp_detail_analysis,
            'details.-inc_stats': exp_detail_stats,
        }
        return tests

    def test_text_sets(self):

        for run_status in ['id_skipped', 'skipped', 'all_skipped', 'run', 'passed', 'raised', 'failed']:
            if run_status in ['id_skipped', 'all_skipped']:
                has_id = True
            else:
                has_id = False
            self._test_text(run_status, **self.base_text_dict(has_id))


class TestTestFlaggerFlag2Obj(TestTestFlaggerTestObj):

    @property
    def oit(self):
        return self.flag_obj_2

    """
    def test_matched(self):
        def make_sets(scopes, metrics, f1_l, f2_l, id_l):
            scopes = make_list(scopes)
            metrics = make_list(metrics)
            tmp_ret = [s + '_' + m for s in scopes for m in metrics]
            tmp_d = {}
            if f1_l and f2_l:
                tmp_d['inc_flag'] = [self.flag_obj_1.name, self.flag_obj_2.name]
            elif f1_l:
                tmp_d['inc_flag'] = self.flag_obj_1.name
            elif f2_l:
                tmp_d['inc_flag'] = self.flag_obj_1.name
            if id_l:
                tmp_d['inc_id'] = self.id_obj.name
            if tmp_d:
                tmp_ret.append(tmp_d)
            return tmp_ret

        def make_metrics(exc=None):
            all_metrics = ['run', 'skipped', 'passed', 'failed', 'raised']
            tmp_ret = all_metrics.copy()
            for x in make_list(exc):
                tmp_ret.remove(x)
            return tmp_ret

        aa_scopes = ['all', 'any']
        no_scopes = 'no'

        for run_status in ['id_skipped', 'skipped', 'all_skipped', 'run', 'passed', 'raised', 'failed']:

            flag1_linked = True
            flag2_linked = True
            has_id = False
            false_metrics = None
            true_metrics = run_status

            if run_status == 'id_skipped':
                has_id = True
                true_metrics = 'skipped'

            elif run_status == 'all_skipped':
                has_id = True
                true_metrics = 'skipped'

            elif run_status == 'passed':
                true_metrics = ['passed', 'run']

            elif run_status == 'raised':
                true_metrics = ['raised', 'run']

            elif run_status == 'failed':
                true_metrics = ['failed', 'run']

            if false_metrics is None:
                false_metrics = true_metrics

            true_matches = make_sets(scopes=aa_scopes, metrics=true_metrics, f1_l=flag1_linked, f2_l=flag2_linked,
                                     id_l=has_id)
            false_matches = make_sets(scopes=no_scopes, metrics=make_metrics(false_metrics), f1_l=flag1_linked,
                                      f2_l=flag2_linked, id_l=has_id)

            self._test_matched('run', true_args=true_matches, false_args=false_matches)
    """

    def base_text_dict(self, with_id=False):
        nsd = '{name} [{status}] ({desc})'
        nd = '{name} ({desc})'
        f1 = '[{flag1_prefix}] {flag1_name}'
        f2 = '[{flag2_prefix}] {flag2_name}'

        if with_id:
            sid_count = '1'
        else:
            sid_count = '0'

        exp_details = nsd + ' Flags: %s, %s' % (f1, f2)
        if with_id:
            exp_details += ' / Skip ID: {sid_name}'

        exp_detail_no_status = nd

        exp_detail_analysis = nd + '\n' \
                                   '  Analysis : {status}'

        exp_detail_stats = '{name} [{status}] ({desc})\n' \
                           '  Flags    : 2\n' \
                           '  Skip IDs : ' + sid_count

        if with_id:
            exp_detail_dump = nd + '\n' \
                                   '  Analysis   : {status}\n' \
                                   '  Flags      : 2\n' \
                                   '  Skip IDs   : 1\n' \
                                   '  Flags      : %s\n' \
                                   '               %a\n' \
                                   '  Skipped ID : {sid_name}' % (f1, f2)
        else:
            exp_detail_dump = nd + '\n' \
                                   '  Analysis : {status}\n' \
                                   '  Flags    : 2\n' \
                                   '  Skip IDs : 0\n' \
                                   '  Flags    : %s\n' \
                                   '             %a' % (f1, f2)

        tests = {
            'details': exp_details,
            'details.dump': exp_detail_dump,
            'details.-inc_status': exp_detail_no_status,
            'details.inc_analysis': exp_detail_analysis,
            'details.-inc_stats': exp_detail_stats,
        }
        return tests

    def test_text_sets(self):

        for run_status in ['id_skipped', 'skipped', 'all_skipped', 'run', 'passed', 'raised', 'failed']:
            if run_status in ['id_skipped', 'all_skipped']:
                has_id = True
            else:
                has_id = False
            self._test_text(run_status, **self.base_text_dict(has_id))


# *******************************************************************************************
#    Test lists
# *******************************************************************************************


class TestFlaggerIDList(unittest.TestCase):

    def test_base(self):
        fl = TestFlaggerSkipIDList(flagger_fixture)
        self.assertFalse(fl)

    def test_base_load_list(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        self.assertTrue(fl)
        self.assertEqual(3, len(fl))

    def test_base_load_dict(self):
        load_items = {'test_1':'td1', 'test_2': 'td2', 'test_3': 'td3'}
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        self.assertTrue(fl)
        self.assertEqual(3, len(fl))

    def test_clear(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        self.assertEqual(1, fl.get_stat('test_count'))

        fl.clear()

        exp_ret = 'Matched Tests : 0\n' \
                  'Not Found IDs : 3\n' \
                  'Total IDs     : 3'

        self.assertEqual(exp_ret, fl.summary())

    def test_add(self):
        fl = TestFlaggerSkipIDList(flagger_fixture)
        fl.add('t1', 'td1')
        fl.add('t2', 'td2')
        self.assertEqual(2, len(fl))

    def test_add_raise(self):
        fl = TestFlaggerSkipIDList(flagger_fixture)
        fl.add('t1', 'td1')
        fl.add('t2', 'td2')
        self.assertEqual(2, len(fl))
        with self.assertRaises(AttributeError):
            fl.add('t2')

    def test__iter__(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        for i in fl:
            # print(i.name)
            load_items.remove(i.name)
        self.assertEqual([], load_items)

    def test_get_item(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)

        self.assertEqual('test_1', fl['test_1'].name)

    def test_iter(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        load_expect = ['test_2', 'test_3']

        for i in fl.iter('test_2', 'test_3'):
            self.assertIn(i.name, load_expect)
            load_expect.remove(i.name)
        self.assertEqual([], load_expect)

    def test_contains(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        self.assertIn('test_2', fl)
        self.assertNotIn('test_4', fl)

    def test_summary(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        exp_ret = 'Matched Tests : 1\n' \
                  'Not Found IDs : 2\n' \
                  'Total IDs     : 3'

        self.assertEqual(exp_ret, fl.summary())

    def test_name_list(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)

        exp_ret = 'test_1 [Not Matched]\n' \
                  'test_2 [Not Matched]\n' \
                  'test_3 [Not Matched]'

        self.assertEqual(exp_ret, fl.name_list())

    def test_details(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        exp_ret = 'Summary:\n' \
                  '  Matched Tests : 1\n' \
                  '  Not Found IDs : 2\n' \
                  '  Total IDs     : 3\n' \
                  'Details:\n' \
                  '  test_1 : Matched 1 time\n' \
                  '  test_2 : Not Matched\n' \
                  '  test_3 : Not Matched' \

        self.assertEqual(exp_ret, fl.details())

    def test_details_w_dump(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        exp_ret = 'Summary:\n' \
                  '  Matched Tests : 1\n' \
                  '  Not Found IDs : 2\n' \
                  '  Total IDs     : 3\n' \
                  'Details:\n' \
                  '  test_1 : Analysis      : All Matched Tests\n' \
                  '           Matched Tests : 1\n' \
                  '           Not Found IDs : 0\n' \
                  '  test_2 : Analysis      : All Not Found IDs\n' \
                  '           Matched Tests : 0\n' \
                  '           Not Found IDs : 1\n' \
                  '  test_3 : Analysis      : All Not Found IDs\n' \
                  '           Matched Tests : 0\n' \
                  '           Not Found IDs : 1'

        self.assertEqual(exp_ret, fl.details(dump=True))

    def test_details_no_summary(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        exp_ret = 'test_1 : Matched 1 time\n' \
                  'test_2 : Not Matched\n' \
                  'test_3 : Not Matched' \

        self.assertEqual(exp_ret, fl.details(inc_summary=False))

    def test_details_filtered(self):
        load_items = ['test_1', 'test_2', 'test_3']
        fl = TestFlaggerSkipIDList(flagger_fixture, items=load_items)
        tmp_sub_1 = TestFlaggerSkipIDObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        fl['test_1'].tests.append(tmp_sub_1)

        exp_ret = 'Summary:\n' \
                  '  Matched Tests : 1\n' \
                  '  Not Found IDs : 1\n' \
                  '  Total IDs     : 2\n' \
                  'Details:\n' \
                  '  test_1 : Matched 1 time\n' \
                  '  test_2 : Not Matched' \

        self.assertEqual(exp_ret, fl.details('test_1', 'test_2'))


'''
class TestTestFlaggerTestObj_old(unittest.TestCase):
    maxDiff = None
    """
    skip_build = False
    obj_kwargs = None
    flag_count = 2
    flag_1_kwargs = None
    flag_2_kwargs = None
    with_id_kwargs = False
    skip_flag_1 = False
    skip_flag_2 = False
    set_result = None # 'failed', 'passed', 'raised'

    test_obj = None
    flag_obj_1 = None
    flag_obj_2 = None
    id_obj = None
    base_obj_dict = None
    base_flag_1_dict = None
    base_flag_2_dict = None
    skipped_flags = None

    def tearDown(self):
        self.reset_vars()

    def reset_vars(self, input=True, output=True):
        if input:
            self.skip_build = False
            self.obj_kwargs = None
            self.flag_count = 2
            self.flag_1_kwargs = None
            self.flag_2_kwargs = None
            self.with_id_kwargs = None
            self.skip_flag_1 = False
            self.skip_flag_2 = False
            self.set_result = None  # 'failed', 'passed', 'raised'

        if output:
            self.skipped_flags = []
            self.test_obj = None
            self.flag_obj_1 = None
            self.flag_obj_2 = None
            self.id_obj = None
            self.base_obj_dict = None
            self.base_flag_1_dict = None
            self.base_flag_2_dict = None
            self.exp_status = 'Not Tried'
            self.base_obj_dict = dict(passed=None, failed=None, raised=None, run=None, skipped=None)
            self.base_flag_1_dict = dict(passed=0, failed=0, raised=0, run=0, skipped=0, self_skipped=0, other_skipped=0)
            self.base_flag_2_dict = dict(passed=0, failed=0, raised=0, run=0, skipped=0, self_skipped=0, other_skipped=0)

    def setUp(self):
        self.reset_vars()

    def check_dict(self, check_obj, exp_dict):
        tmp_act = check_obj.stats_dict(full_field_names=False)
        msg = make_exp_act_str(exp_dict, tmp_act, header='\n\n', footer='\n\n')
        self.assertEqual(exp_dict, tmp_act, msg=msg)

    def check_obj_dicts(self, inc_base=True, inc_flag_1=True, inc_flag_2=True):
        if inc_base:
            self.exp_status = self.exp_status.title()
            self.check_dict(self.test_obj, self.base_obj_dict)
            print('Checking for a status of ', self.exp_status)
            self.assertEqual(self.exp_status, self.test_obj.status())
        if inc_flag_1 and self.flag_count > 0:
            self.check_dict(self.flag_obj_1, self.base_flag_1_dict)
        if inc_flag_2 and self.flag_count > 1:
            self.check_dict(self.flag_obj_2, self.base_flag_2_dict)

    def build_obj(self, set_result=None, reset=False, **kwargs):
        if reset:
            self.reset_vars()
        else:
            self.reset_vars(input=False)

        if set_result is not None:
            self.set_result = set_result
            if set_result == 'skipped':
                if not (self.skip_flag_1 or self.skip_flag_2):
                    self.skip_flag_1 = True

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        flags = []
        obj_kwargs = init_dict({'name': 'my_test_name', 'desc': 'test_desc'}, self.obj_kwargs)
        self.test_obj = TestFlaggerTestObj(flagger_fixture, **obj_kwargs)
        self.skipped_flags = []

        self.check_obj_dicts(inc_flag_1=False, inc_flag_2=False)

        self.exp_status = 'run'
        self.base_obj_dict.update({'run': False, 'skipped': False})
        if self.flag_count > 0:
            self.flag_1_kwargs = self.flag_1_kwargs or {}
            if self.skip_flag_1:
                self.exp_status = 'skipped'
                self.flag_1_kwargs['_should_skip'] = True
            obj_sub_1 = init_dict({'name': 'flag_name_1', 'desc': 'test_desc_1'}, self.flag_1_kwargs)
            self.flag_obj_1 = TestFlaggerFlagObj(flagger_fixture, **obj_sub_1)
            if self.skip_flag_1:
                self.skipped_flags.append(obj_sub_1)
            flags.append(self.flag_obj_1)

        if self.flag_count > 1:
            self.flag_2_kwargs = self.flag_2_kwargs or {}
            if self.skip_flag_2:
                self.exp_status = 'Skipped'
                self.flag_2_kwargs['_should_skip'] = True
            obj_sub_2 = init_dict({'name': 'flag_name_2'}, self.flag_2_kwargs)
            self.flag_obj_2 = TestFlaggerFlagObj(flagger_fixture, **obj_sub_2)
            if self.skip_flag_2:
                self.skipped_flags.append(obj_sub_2)
            flags.append(self.flag_obj_2)

        if self.with_id_kwargs is not None:
            self.exp_status = 'Skipped'
            obj_sub_id = init_dict({'name': 'sip_obj', 'desc': 'test_skip_desc'}, self.with_id_kwargs)
            self.id_obj = TestFlaggerSkipIDObj(flagger_fixture, obj_sub_id)

        if self.skipped_flags or self.id_obj is not None:
            self.base_obj_dict['skipped'] = True
            self.base_flag_1_dict['skipped'] = 1
            self.base_flag_2_dict['skipped'] = 1
            if self.skip_flag_1:
                self.base_flag_1_dict['self_skipped'] = 1
            else:
                self.base_flag_1_dict['other_skipped'] = 1
            if self.skip_flag_2:
                self.base_flag_2_dict['self_skipped'] = 1
            else:
                self.base_flag_2_dict['other_skipped'] = 1

            with self.assertRaises(unittest.SkipTest):
                self.test_obj.check(flags, skip_id_obj=self.id_obj)

            self.assertEqual('Skipped', self.test_obj.status())

        else:
            self.base_obj_dict['run'] = True
            self.base_flag_1_dict['run'] = 1
            self.base_flag_2_dict['run'] = 1
            self.test_obj.check(flags, skip_id_obj=self.id_obj)
            self.assertEqual('Run', self.test_obj.status())

        self.check_obj_dicts()

        if self.set_result is not None and self.set_result in ('passed', 'failed', 'raised'):
            self.exp_status = self.set_result
            try:
                if self.set_result == 'failed':
                    self.test_obj.set_result(AssertionError('failed'))
                    self.base_obj_dict.update({'failed': True, 'passed': False, 'raised': False})
                    self.base_flag_1_dict.update({'failed': 1, 'passed': 0, 'raised': 0})
                    self.base_flag_2_dict.update({'failed': 1, 'passed': 0, 'raised': 0})

                if self.set_result == 'passed':
                    self.test_obj.set_result()
                    self.base_obj_dict.update({'failed': False, 'passed': True, 'raised': False})
                    self.base_flag_1_dict.update({'failed': 0, 'passed': 1, 'raised': 0})
                    self.base_flag_2_dict.update({'failed': 0, 'passed': 1, 'raised': 0})

                if self.set_result == 'raised':
                    self.test_obj.set_result(AttributeError('raised'))
                    self.base_obj_dict.update({'failed': False, 'passed': False, 'raised': True})
                    self.base_flag_1_dict.update({'failed': 0, 'passed': 0, 'raised': 1})
                    self.base_flag_2_dict.update({'failed': 0, 'passed': 0, 'raised': 1})

                self.check_obj_dicts()

            except AttributeError as err:
                if self.skipped_flags:
                    if str(err) != 'Test marked as skipped, cannot set result':
                        raise
                else:
                    raise

    def _test_create_obj(self):
        self.flag_1_kwargs = {}
        self.flag_2_kwargs = {}
        self.num_flags = 2
        self.with_id_obj = False
        self.skip_flags = 0

        # output

        self.test_obj = None
        self.flag_obj_1 = None
        self.flag_obj_2 = None
        self.id_obj = None
        self.skipped_flags = []
        self.base_obj_dict = {}
        self.base_flag_1_dict = {}
        self.base_flag_2_dict = {}
    """

    def test_base_obj(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, ftc, passed=True, run=True)
        self.assertEqual('name', tmp_obj.name)
        self.assertEqual('test_desc', tmp_obj.desc)
        self.assertTrue(tmp_obj.passed)
        self.assertFalse(tmp_obj.skipped)

    def test_base_test_start(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'test_name', 'test_desc', passed=True, run=True)
        self.assertEqual('name', tmp_obj.name)
        self.assertTrue(tmp_obj.passed)
        self.assertFalse(tmp_obj.skipped)

    def test_base_test__start(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'testof_name', 'test_desc', passed=True, run=True)
        self.assertEqual('of_name', tmp_obj.name)
        self.assertTrue(tmp_obj.passed)
        self.assertFalse(tmp_obj.skipped)

    def test_base_no_test_start(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'of_test_name', 'test_desc', passed=True, run=True)
        self.assertEqual('of_test_name', tmp_obj.name)
        self.assertTrue(tmp_obj.passed)
        self.assertFalse(tmp_obj.skipped)

    def test_eq(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        self.assertEqual('my_test_name', tmp_obj)
        self.assertNotEqual('test_name_is_me', tmp_obj)
        self.assertNotEqual('foobar test_name', tmp_obj)

    def test_str(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        self.assertEqual('my_test_name', str(tmp_obj))

    def test_match_set_result(self):
        tests = [
            ('passed', dict(passed=True, failed=False, raised=False, run=True, skipped=False)),
            ('failed', dict(passed=False, failed=True, raised=False, run=True, skipped=False)),
            ('raised', dict(passed=False, failed=False, raised=True, run=True, skipped=False)),
            ('run', dict(passed=None, failed=None, raised=None, run=True, skipped=False)),
            ('skipped', dict(passed=None, failed=None, raised=None, run=False, skipped=True)),
        ]
        match_keys = {
            True: ['all_', 'any_'],
            False: ['no_'],
            None: ['no_']
        }

        for test_set, test_result in tests:
            with self.subTest(test_set):
                self.build_obj(test_set, reset=True)
                # tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
                with self.subTest(test_set + ': dict'):
                    # self.test_obj._set_result(state=test_set)
                    tmp_act = self.test_obj.stats_dict(full_field_names=False)
                    rep_str = '\nObject: ' + repr(self.test_obj)
                    tmp_msg = make_exp_act_str(exp=test_result, act=tmp_act, header=rep_str)
                    self.assertEqual(test_result, tmp_act, tmp_msg)

                    for field, value in test_result.items():
                        for mk in match_keys[value]:
                            match_str = mk + field
                            with self.subTest(test_set + ': match ' + match_str):
                                self.assertTrue(self.test_obj.match(match_str), tmp_msg)
                        for mk in match_keys[not value]:
                            match_str = mk + field
                            with self.subTest(test_set + ': match ' + match_str):
                                self.assertFalse(self.test_obj.match(match_str), tmp_msg)

    def test_match_inc_ref_item(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_obj.referenced_obj.append('foobar3')
        tmp_obj.referenced_obj.append('snafu3')
        self.assertTrue(tmp_obj.match(inc_flags=['foobar3', 'snafu3']))
        self.assertTrue(tmp_obj.match(inc_flags='foobar3'))
        self.assertFalse(tmp_obj.match(inc_flags='not there'))

    def test_init_tests(self):
        # run is the default build
        with self.subTest('init_run'):
            self.build_obj()

        # skipped
        with self.subTest('init_skipped'):
            self.build_obj('skipped', reset=True)

        # passed
        with self.subTest('init_passed'):
            self.build_obj('passed', reset=True)

        # failed
        with self.subTest('init_failed'):
            self.build_obj('failed', reset=True)

        # raised
        with self.subTest('init_raised'):
            self.build_obj('raised', reset=True)

        # skipped - passed
        with self.subTest('init_skipped_passed'):
            self.build_obj('passed', reset=True, skip_flag_1=True)

        # skipped - failed
        with self.subTest('init_skipped_failed'):
            self.build_obj('failed', reset=True, skip_flag_1=True)

        # skipped - raised
        with self.subTest('init_skipped_raised'):
            self.build_obj(reset=True, set_result='raised', skip_flag_1=True)

    def test_summary_data(self):
        self.build_obj()
        self.assertEqual('[Passed] (test_desc)', self.test_obj.summary_data())
        self.assertEqual('[Passed]', self.test_obj.summary_data(inc_desc=False))
        self.assertEqual('[?] my_test_name', self.test_obj.short_name())

    def test_short_name_no_prefix(self):
        self.build_obj()
        # tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        self.assertEqual('my_test_name', self.test_obj.short_name(inc_status_prefix=False))

    def test_long_name(self):
        self.build_obj('failed')
        # tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        self.assertEqual('my_test_name [Failed] (test_desc)', self.test_obj.long_name())
        self.assertEqual('my_test_name [Failed]', self.test_obj.long_name(inc_desc=False))
        self.assertEqual('[?] my_test_name [Failed]', self.test_obj.long_name(inc_desc=False, inc_status_prefix=True))

    def test_dump_w_summary(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc', passed=1, failed=2, raised=0, run=1, skipped=1)
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'test_desc')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)
        exp_ret = 'test_name_2 : [Not Matched]\n' \
                  'test_name_3 : [Not Matched]'

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_w_summary_empty(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')

        exp_ret = ''

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_no_summary(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_obj.dump_inc_summary = False
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_dest_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name_2\n' \
                  'test_name_3'

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_no_summary_empty(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_obj.dump_inc_summary = False

        exp_ret = ''

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_analysis(self):
        tests = [
            (dict(passed=None, failed=None, raised=None, run=False, skipped=False), 'Not Tried'),
            (dict(passed=None, failed=None, raised=None, run=True, skipped=False), 'Run'),
            (dict(passed=None, failed=None, raised=None, run=False, skipped=True), 'Skipped'),
            (dict(passed=True, failed=False, raised=False, run=True, skipped=False), 'Passed'),
            (dict(passed=False, failed=True, raised=False, run=True, skipped=False), 'Failed'),
            (dict(passed=False, failed=False, raised=True, run=True, skipped=False), 'Raised'),
        ]
        for test_args, analysis in tests:
            with self.subTest(analysis):    
                tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc', **test_args)
                self.assertEqual(analysis, tmp_obj.status())

    def test_details(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)
        tmp_obj.set_result('passed')
        exp_ret = 'test_name [Passed] (test_desc) Flags: [test_name_2, test_name_3]'

        self.assertEqual(exp_ret, tmp_obj.details())

    def test_details_w_skip_id(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3', _should_skip=True)
        tmp_sid = TestFlaggerSkipIDObj(flagger_fixture, 'test_skip')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)
        tmp_obj.skip_id_obj = tmp_sid
        tmp_obj.set_result('skipped')

        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        exp_ret = 'test_name [Skipped] (test_desc) Reason: Flags: Test_name_2, test_name_3, SkipID: test_skip'

        self.assertEqual(exp_ret, tmp_obj.details())

    def test_details_w_dump(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Matched 2 times\n' \
                  '  Analysis      : All Matched Tests\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0\n' \
                  '  Tests         : test_name_2 : [Not Matched]\n' \
                  '                  test_name_3 : [Not Matched]'

        self.assertEqual(exp_ret, tmp_obj.details(dump=True))

    def test_details_no_status(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)'

        self.assertEqual(exp_ret, tmp_obj.details(inc_status=False))

    def test_details_w_analysis(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Analysis      : All Matched Tests\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(inc_analysis=True, inc_stats=True))

    def test_details_w_stats(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(inc_stats=True, inc_status=False))

    def test_details_indent(self):
        tmp_obj = TestFlaggerTestObj(flagger_fixture, 'my_test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerTestObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerTestObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = '  test_name (test_desc)\n' \
                  '    Analysis      : All Matched Tests\n' \
                  '    Matched Tests : 2\n' \
                  '    Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(indent=2, inc_analysis=True, inc_stats=True))

'''
'''
class TestTestFlaggerFlagObj(unittest.TestCase):

    def test_base(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=2)
        self.assertEqual('test_name', tmp_obj.name)
        self.assertEqual(2, tmp_obj.passed)

    def test_eq(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('test_name', tmp_obj)
        self.assertNotEqual('test_name_is_me', tmp_obj)
        self.assertNotEqual('foobar test_name', tmp_obj)

    def test_str(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('test_name', str(tmp_obj))

    def test_match_any_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=2, run=2, found=3)

        self.assertTrue(tmp_obj.match('any_passed'))
        self.assertTrue(tmp_obj.match('inc_passed'))
        self.assertFalse(tmp_obj.match('any_failed'))

    def test_match_all_pfr_yes_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=0, raised=0, run=1,
                                     skipped=1)

        self.assertTrue(tmp_obj.match('all_passed'))
        self.assertFalse(tmp_obj.match('all_failed'))

    def test_match_all_pfr_no_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=0,
                                     skipped=0)

        self.assertFalse(tmp_obj.match('all_passed'))
        self.assertFalse(tmp_obj.match('all_failed'))

    def test_match_all_rs_yes_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=0, raised=0, run=0,
                                     skipped=1)

        self.assertTrue(tmp_obj.match('all_skipped'))
        self.assertFalse(tmp_obj.match('all_run'))

    def test_match_all_rs_no_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=0,
                                     skipped=0)

        self.assertFalse(tmp_obj.match('all_skipped'))
        self.assertFalse(tmp_obj.match('all_run'))

    def test_match_all_rs_no_metric_2(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=1,
                                     skipped=1)

        self.assertFalse(tmp_obj.match('all_skipped'))
        self.assertFalse(tmp_obj.match('all_run'))

    def test_match_no_good_metric(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=1,
                                     skipped=1)

        self.assertTrue(tmp_obj.match('no_raised'))
        self.assertFalse(tmp_obj.match('no_run'))
        self.assertFalse(tmp_obj.match('no_passed'))
        self.assertFalse(tmp_obj.match('no_skipped'))

    def test_match_inc_ref_item(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_obj.referenced_obj.append('foobar2')
        tmp_obj.referenced_obj.append('snafu2')
        self.assertTrue(tmp_obj.match(inc_tests=['foobar2', 'snafu2']))
        self.assertTrue(tmp_obj.match(inc_tests='foobar2'))
        self.assertFalse(tmp_obj.match(inc_tests='not there'))

    def test_stats_dict(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=1,
                                     skipped=1)
        exp_ret = {'Run': 1,
                   'Passed': 1,
                   'Failed': 2,
                   'Raised': 0,
                   'Skipped': 1,
                   'Skipped(self)': 0,
                   'Skipped(other)': 0
                   }
        self.assertEqual(exp_ret, tmp_obj.stats_dict())

        exp_ret = {'run': 1,
                   'passed': 1,
                   'failed': 2,
                   'raised': 0,
                   'skipped': 1,
                   'self_skipped': 0,
                   'other_skipped': 0
                   }
        self.assertEqual(exp_ret, tmp_obj.stats_dict(full_field_names=False))

    def test_summary_data(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('[Included] (test_desc)', tmp_obj.summary_data())
        self.assertEqual('[Included]', tmp_obj.summary_data(inc_desc=False))

    def test_short_name_prefix(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('[I] test_name', tmp_obj.short_name())

    def test_short_name_no_prefix(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        self.assertEqual('test_name', tmp_obj.short_name(inc_status_prefix=False))

    def test_long_name(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', _should_skip=True)
        self.assertEqual('test_name [Skipped] (test_desc)', tmp_obj.long_name())
        self.assertEqual('test_name [Skipped]', tmp_obj.long_name(inc_desc=False))
        self.assertEqual('[S] test_name [Skipped]', tmp_obj.long_name(inc_desc=False, inc_status_prefix=True))

    def test_dump_w_summary(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', passed=1, failed=2, raised=0, run=1,
                                     skipped=1)
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'test_desc')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)
        exp_ret = 'test_name_2 : [Not Matched]\n' \
                  'test_name_3 : [Not Matched]'

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_w_summary_empty(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')

        exp_ret = ''

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_no_summary(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_obj.dump_inc_summary = False
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_dest_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name_2\n' \
                  'test_name_3'

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_dump_no_summary_empty(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_obj.dump_inc_summary = False

        exp_ret = ''

        self.assertEqual(exp_ret, tmp_obj._dump())

    def test_analysis(self):
        tests = [
            (dict(passed=0, failed=0, raised=0, run=0, skipped=0, found=0), 'Not Found'),

            (dict(passed=0, failed=0, raised=0, run=2, skipped=2, found=4), 'Some Skipped, No PF Info'),
            (dict(passed=0, failed=0, raised=0, run=2, skipped=0, found=2), 'All Run, No PF Info'),
            (dict(passed=0, failed=0, raised=0, run=0, skipped=2, found=2), 'All Skipped, No PF Info'),

            (dict(passed=1, failed=0, raised=0, run=2, skipped=2, found=4), 'Some Skipped, All Passed'),
            (dict(passed=1, failed=0, raised=0, run=2, skipped=0, found=2), 'All Run, All Passed'),
            (dict(passed=1, failed=0, raised=0, run=0, skipped=2, found=2), 'All Skipped, All Passed'),

            (dict(passed=0, failed=1, raised=0, run=2, skipped=2, found=4), 'Some Skipped, All Failed'),
            (dict(passed=0, failed=1, raised=0, run=2, skipped=0, found=2), 'All Run, All Failed'),
            (dict(passed=0, failed=1, raised=0, run=0, skipped=2, found=2), 'All Skipped, All Failed'),

            (dict(passed=0, failed=0, raised=1, run=2, skipped=2, found=4), 'Some Skipped, All Raised'),
            (dict(passed=0, failed=0, raised=1, run=2, skipped=0, found=2), 'All Run, All Raised'),
            (dict(passed=0, failed=0, raised=1, run=0, skipped=2, found=2), 'All Skipped, All Raised'),

            (dict(passed=0, failed=1, raised=1, run=2, skipped=2, found=4), 'Some Skipped, All Failed or Raised'),
            (dict(passed=0, failed=1, raised=1, run=2, skipped=0, found=2), 'All Run, All Failed or Raised'),
            (dict(passed=0, failed=1, raised=1, run=0, skipped=2, found=2), 'All Skipped, All Failed or Raised'),

            (dict(passed=1, failed=0, raised=1, run=2, skipped=2, found=4), 'Some Skipped, All Passed or Raised'),
            (dict(passed=1, failed=0, raised=1, run=2, skipped=0, found=2), 'All Run, All Passed or Raised'),
            (dict(passed=1, failed=0, raised=1, run=0, skipped=2, found=2), 'All Skipped, All Passed or Raised'),

            (dict(passed=1, failed=1, raised=0, run=2, skipped=2, found=4), 'Some Skipped, All Passed or Failed'),
            (dict(passed=1, failed=1, raised=0, run=2, skipped=0, found=2), 'All Run, All Passed or Failed'),
            (dict(passed=1, failed=1, raised=0, run=0, skipped=2, found=2), 'All Skipped, All Passed or Failed'),

            (dict(passed=1, failed=1, raised=1, run=2, skipped=2, found=4),
             'Some Skipped, All Passed, Failed, or Raised'),
            (dict(passed=1, failed=1, raised=1, run=2, skipped=0, found=2), 'All Run, All Passed, Failed, or Raised'),
            (dict(passed=1, failed=1, raised=1, run=0, skipped=2, found=2),
             'All Skipped, All Passed, Failed, or Raised'),
        ]
        for test_args, analysis in tests:
            with self.subTest(analysis):
                tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc', **test_args)
                self.assertEqual(analysis, tmp_obj._analysis())

    def test_details(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name [Matched 2 times] (test_desc)'

        self.assertEqual(exp_ret, tmp_obj.details())

    def test_details_w_dump(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Matched 2 times\n' \
                  '  Analysis      : All Matched Tests\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0\n' \
                  '  Tests         : test_name_2 : [Not Matched]\n' \
                  '                  test_name_3 : [Not Matched]'

        self.assertEqual(exp_ret, tmp_obj.details(dump=True))

    def test_details_no_status(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)'

        self.assertEqual(exp_ret, tmp_obj.details(inc_status=False))

    def test_details_w_analysis(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Analysis      : All Matched Tests\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(inc_analysis=True, inc_stats=True))

    def test_details_w_stats(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = 'test_name (test_desc)\n' \
                  '  Matched Tests : 2\n' \
                  '  Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(inc_stats=True, inc_status=False))

    def test_details_indent(self):
        tmp_obj = TestFlaggerFlagObj(flagger_fixture, 'test_name', 'test_desc')
        tmp_sub_1 = TestFlaggerFlagObj(flagger_fixture, 'test_name_2', 'tmp_desc_2')
        tmp_sub_2 = TestFlaggerFlagObj(flagger_fixture, 'test_name_3')
        tmp_obj.referenced_obj.append(tmp_sub_1)
        tmp_obj.referenced_obj.append(tmp_sub_2)

        exp_ret = '  test_name (test_desc)\n' \
                  '    Analysis      : All Matched Tests\n' \
                  '    Matched Tests : 2\n' \
                  '    Not Found IDs : 0'

        self.assertEqual(exp_ret, tmp_obj.details(indent=2, inc_analysis=True, inc_stats=True))
'''

s_os = TestFlaggerTestSkipOS
s_mod = TestFlaggerTestSkipModule
s_py = TestFlaggerTestSkipPyVer
s_tst = TestFlaggerTestSkipTestRun
s_flg = TestFlaggerTestSkipFlag
s_pla = TestFlaggerTestSkipPlatform
s_env = TestFlaggerTestSkipEnvironBase


class TestFlaggerSkipActiveObjects(unittest.TestCase):

    def test_common_skips(self):

        os_name = os.name
        pyv = platform.python_version()

        platform_full = platform.platform()
        platform_terse = platform.platform(terse=True)
        platform_aliased = platform.platform(aliased=True)
        processor = platform.processor()
        machine = platform.machine()
        node = platform.node()
        python_compiler = platform.python_compiler()
        python_implementation = platform.python_implementation()
        python_branch = platform.python_branch()
        release = platform.release()
        version = platform.version()
        env_var = 'windir'
        env_value = os.environ[env_var]

        # print(repr(os_name))
        # print(repr(platform_full))
        # print(repr(platform_terse))
        # print(repr(platform_aliased))
        # print(repr(processor))
        # print(repr(machine))
        # print(repr(node))
        # print(repr(python_compiler))
        # print(repr(python_implementation))
        # print(repr(python_branch))
        # print(repr(release))
        # print(repr(version))

        tests = [
            {"obj": s_os,
             "is": {True: [(os_name, "Skip this test if the OS is {is_not}'%s'" % os_name)],
                    False: [("foobar", "Skip this test if the OS is {is_not}'foobar'")]},
             },
            {"obj": s_mod,
             "is": {True: [("unittest", "Skip this test if the module 'unittest' was {is_not}loaded")],
                    False: [("foobar", "Skip this test if the module 'foobar' was {is_not}loaded")]},
             },
            {"obj": s_env,
             "is": {True: [(env_var + "_" + env_value, "Skip this test if the environment var %r is %r" % (env_var, env_value))],
                    False: [(env_var + "_foobar", "Skip this test if the environment var %r is 'foobar'" % env_var),
                            ("snafu_foobar", "Skip this test if the environment var 'snafu' is 'foobar'")
                            ]
                    },
             "not": {False: [(env_var + "_" + env_value, "Skip this test if the environment var %r is not %r" % (env_var, env_value)),
                             ("snafu_foobar", "Skip this test if the environment var 'snafu' is not 'foobar'"),
                             ],
                     True: [(env_var + "_foobar", "Skip this test if the environment var %r is not 'foobar'" % env_var)]
                    },
             },
            {"obj": s_py,
             "is": {True: [
                        (pyv, "Skip this test if the Python Version is {is_not}== '%s'" % pyv),
                        (pyv + "+", "Skip this test if the Python Version is {is_not}>= '%s'" % pyv),
                        (pyv + "-", "Skip this test if the Python Version is {is_not}<= '%s'" % pyv),
                        ("1.0+", "Skip this test if the Python Version is {is_not}>= '1.0'"),
                        ("10-", "Skip this test if the Python Version is {is_not}<= '10.0'"),
                    ],
                    False: [
                        ("10.0", "Skip this test if the Python Version is {is_not}== '10.0'"),
                        ("1.0", "Skip this test if the Python Version is {is_not}== '1.0'"),
                        ("1.0-", "Skip this test if the Python Version is {is_not}<= '1.0'"),
                        ("10+", "Skip this test if the Python Version is {is_not}>= '10.0'"),
                    ],
             }},
            {"obj": s_pla,
             "is": {True: [
                        ("platform_full_" + platform_full, "Skip this test if the platform.%s() is {is_not}%r" % ("platform_full", platform_full)),
                        ("platform_terse_" + platform_terse, "Skip this test if the platform.%s() is {is_not}%r" % ("platform_terse", platform_terse)),
                        ("platform_aliased_" + platform_aliased, "Skip this test if the platform.%s() is {is_not}%r" % ("platform_aliased", platform_aliased)),
                        ("processor_" + processor, "Skip this test if the platform.%s() is {is_not}%r" % ("processor", processor)),
                        ("machine_" + machine, "Skip this test if the platform.%s() is {is_not}%r" % ("machine", machine)),
                        ("node_" + node, "Skip this test if the platform.%s() is {is_not}%r" % ("node", node)),
                        ("python_compiler_" + python_compiler, "Skip this test if the platform.%s() is {is_not}%r" % ("python_compiler", python_compiler)),
                        ("python_implementation_" + python_implementation, "Skip this test if the platform.%s() is {is_not}%r" % ("python_implementation", python_implementation)),
                        ("python_branch_" + python_branch, "Skip this test if the platform.%s() is {is_not}%r" % ("python_branch", python_branch)),
                        ("version_" + version, "Skip this test if the platform.%s() is {is_not}%r" % ("version", version)),
                        ("release_" + release, "Skip this test if the platform.%s() is {is_not}%r" % ("release", release)),
             ],
                    False: [
                        ("platform_full_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("platform_full", "foobar")),
                        ("platform_terse_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("platform_terse", "foobar")),
                        ("platform_aliased_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("platform_aliased", "foobar")),
                        ("processor_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("processor", "foobar")),
                        ("machine_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("machine", "foobar")),
                        ("node_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("node", "foobar")),
                        ("python_compiler_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("python_compiler", "foobar")),
                        ("python_implementation_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("python_implementation", "foobar")),
                        ("python_branch_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("python_branch", "foobar")),
                        ("version_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("version", "foobar")),
                        ("release_foobar", "Skip this test if the platform.%s() is {is_not}%r" % ("release", "foobar")),
                    ]
             },
             },
            {"obj": s_flg,
             "is": {'no_test': [
                 ('this_is_a_test_flag_all_passed', "Skip this test if the other tests for flag 'this_is_a_test_flag' {is_not}all passed"),
                 ('this_is_a_test_flag_no_raised', "Skip this test if the other tests for flag 'this_is_a_test_flag' {is_not}no raised"),
                 ('testflag_any_failed', "Skip this test if the other tests for flag 'testflag' {is_not}any failed"),
                 ('this_is_a_test_flag_no_run', "Skip this test if the other tests for flag 'this_is_a_test_flag' {is_not}no run"),
             ],
             }},
            {"obj": s_tst,
             "is": {'no_test': [
                 ('this_is_a_test_def_passed',
                  "Skip this test if the test 'this_is_a_test_def' {is_not}passed"),
                 ('_this_test__failed',
                  "Skip this test if the test '_this_test_' {is_not}failed"),
                 ('__this___run',
                  "Skip this test if the test '__this__' {is_not}run"),
             ],
             }},

        ]

        def test_item(obj_in, local_is_not, tf, tf_list):
            name_str = 'assertion test for: %r' % obj_in
            with self.subTest(name_str):
                with self.assertRaises(AttributeError):
                    tmp_obj = obj_in(flagger_fixture, 'foobar')

            for rem_str, desc in tf_list:
                match_str = 'skip_if_%s_%s_%s' % (local_is_not, obj_in.skip_name, rem_str)
                name_str = match_str
                with self.subTest(match_str):
                    tmp_obj = obj_in(flagger_fixture, match_str)

                    if tf != 'no_test':
                        if tf:
                            name_str = 'TRUE: ' + match_str
                            with self.subTest(name_str):
                                self.assertTrue(tmp_obj.should_skip())
                        else:
                            name_str = 'FALSE: ' + match_str
                            with self.subTest(name_str):
                                self.assertFalse(tmp_obj.should_skip())
                    name_str = 'DESC: ' + name_str
                    with self.subTest(name_str):
                        desc = desc.format(is_not=iif(local_is_not == 'is', '', 'not '))
                        self.assertEqual(desc, tmp_obj.desc)

        for test_obj_set in tests:
            test_obj = test_obj_set['obj']
            test_is = test_obj_set['is']
            if 'no_test' in test_is:
                test_item(test_obj, 'is', 'no_test', test_is['no_test'])
                test_item(test_obj, 'not', 'no_test', test_is['no_test'])
            else:

                if 'not' in test_obj_set:
                    test_not = test_obj_set['not']
                else:
                    test_not = {
                        True: test_is[False],
                        False: test_is[True]
                    }
                test_item(test_obj, 'is', True, test_is[True])
                test_item(test_obj, 'is', False, test_is[False])

                test_item(test_obj, 'not', True, test_not[True])
                test_item(test_obj, 'not', False, test_not[False])


