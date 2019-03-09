#!/usr/bin/env python

"""
This module provides a tool to help complex testcases to be able to run different tests based on flags set for each
test.


Active flags: (these flags dont rely on setting values in the inc_flags or skip_flags lists)

skip_if_is_os_<xxx>
skip_if_not_os_<xxx>

skip_if_is_pyv_x.x(+-)
skip_if_not_pyv_x.x.x(+-)

skip_if_is_module_xxx[_loaded]
skip_if_not_module_xxx[_loaded]

skip_if_is_test_xxx_[passed/failed/raised/run]
skip_if_not_test_xxx_[passed/failed/raised/run]

skip_if_is_flag_xxx_[all/any/none]_[passed/failed/raised/run]
skip_if_not_flag_xxx_[all/any/none]_[passed/failed/raised/run]


usage options:

(using normal test case)

class TestThing(TestCase):
    def setUpClass(cls):
        test_flagger.setup(cls, flags, etc...)
        -or-
        test_flagger.setup(test_case_name, flags, etc...)

    @check_flag('flag_1' 'flag_2')
    def test_that_item(self):
        self.assertSomething('foo', 'bar')

    @check_flag('flag_1' 'flag_2', test_name='test_case_name.test_name')
    def test_that_item(self):
        self.assertSomething('foo', 'bar')

    def test_that_item(self):
        with check_flag('flag1', 'flag2'):
            self.assertSomething('foo', 'bar')

        with check_flag('flag3', 'flag4', sub_test='foobar part 2'):
            self.assertSomething('foo', 'bar')

    def test_that_item(self):
        for i in range(10):
            with self.subTest(n=i):
                with check_flag('flag_1', 'flag2', sub_test='subtest' + str(i)):

    def FinishClass(cls):
        test_flagger.finish(cls / 'test_case_name', report_options)


(using custom test_case)

class TestAnotherThing(FlaggerTestCase)
    flags={blah, blah, blah)
    inc_flags=[a,b,c]
    report_options='blah'

    @check_flag('flag1', 'flag2', 'flag_4')
    def test_this_item(self):
        pass

    def test_that_item(self):
        with self.check_flags('test_flag1, 'flag2'):
            pass

"""

__author__ = ""
__copyright__ = ""
__credits__ = []
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = ""


import unittest
import sys
import platform
import os
from fnmatch import fnmatch
from PythonUtils.BaseUtils import make_list, format_key_value, indent_str, FORMAT_RETURN_STYLE
from distutils.version import StrictVersion
import re
from collections import OrderedDict



# ******************************************************************************
# Base Flagger Item
# ******************************************************************************


class TestFlaggerBaseItemObj(object):
    metric_info = {}
    all_groups = []
    dump_header = 'Dump'
    dump_inc_summary = True
    stats_in_status = False
    obj_name = 'Objs'
    sub_references = 'Objs'

    def __init__(self, flagger, name, desc='', is_default=True, **kwargs):
        self.flagger = flagger
        self.name = name
        self.desc = desc
        self.is_default = is_default
        self.referenced_obj = []

        if kwargs:
            for key, item in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, item)
                else:
                    raise AttributeError('object %r does not have attribute %r' % (self, key))

    def clear(self):
        self.referenced_obj.clear()

    def __eq__(self, other):
        return other == self.name

    def __str__(self):
        return self.name

    def stats_dict(self, inc_stat=None, exc_stat=None, inc_empty=True, full_field_names=True):
        exc_stat = make_list(exc_stat)
        inc_stat = make_list(inc_stat)
        tmp_ret = {}
        if exc_stat and inc_stat:
            raise AttributeError('Cannot use both inc_stats and exc_stats')
        for metric_attr, metric_name in self.metric_info.items():
            if metric_attr in exc_stat:
                continue
            if inc_stat and metric_attr not in inc_stat:
                continue
            tmp_value = getattr(self, metric_attr)
            if not inc_empty and not tmp_value:
                continue
            if full_field_names:
                tmp_ret[metric_name] = tmp_value
            else:
                tmp_ret[metric_attr] = tmp_value
        return tmp_ret

    @property
    def status(self):
        return ''

    @property
    def status_prefix(self):
        if self.status:
            return self.status[0]
        else:
            return ''

    @property
    def summary_data(self):
        return ''

    @property
    def short_name(self):
        tmp_ret = ''
        if self.status_prefix:
            tmp_ret += '[%s] ' % self.status_prefix
        tmp_ret += self.name
        return tmp_ret

    @property
    def long_name(self):
        tmp_ret = self.short_name
        tmp_ret_2 = self.summary_data
        if tmp_ret_2:
            tmp_ret += ' | ' + tmp_ret_2
        return tmp_ret

    @property
    def status_name(self):
        tmp_status = self.status
        tmp_ret = self.name
        if tmp_status:
            tmp_ret += ' [%s]' % tmp_status
        return tmp_ret

    def _dump_data(self):
        return {}

    @property
    def dump_item(self):
        return self.name

    def _dump_dict(self):
        tmp_ret = OrderedDict()

        if self.desc:
            tmp_ret['Desc'] = self.desc
        tmp_ret.update(self._dump_data())
        if self.referenced_obj:
            tmp_item = []
            for i in self.referenced_obj:
                tmp_item.append(i.dump_item)
            tmp_item = '\n'.join(tmp_item)
            tmp_ret[self.dump_header] = tmp_item
        else:
            tmp_ret[self.dump_header] = '* None *'
        return tmp_ret

    def dump(self, as_dict=False):
        if as_dict:
            tmp_ret = format_key_value(self._dump_dict())
            tmp_ret = {self.status_name: tmp_ret}
        else:
            tmp_ret = format_key_value(self._dump_dict(), indent=4)
            tmp_ret = self.status_name + '\n' + tmp_ret
        return tmp_ret

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        if self.desc:
            return '%s: %s ( %r )' % (self.__class__.__name__, self.long_name, self.desc)
        else:
            return '%s: %s' % (self.__class__.__name__, self.long_name)


class TestFlaggerBaseItemList(object):
    item_class = TestFlaggerBaseItemObj
    item_name = 'Item'

    def __init__(self, flagger, items=None, **kwargs):
        self.flagger = flagger
        self.data = {}
        self.stats_info = self.item_class.metric_info.copy()
        self.stats_info['total'] = 'Total ' + self.item_class.obj_name
        self.stats_headers = {}
        for val in self.stats_info.values():
            self.stats_headers[val] = 0

        if items is not None:
            if isinstance(items, dict):
                for name, desc in items.items():
                    self.add(name, desc, **kwargs)
            elif isinstance(items, (list, tuple)):
                for name in items:
                    self.add(name, **kwargs)
            else:
                raise AttributeError('Unknown items type: %r' % items)

    def clear(self):
        for name in list(self.data.keys()):
            if not self.data[name].is_default:
                del self.data[name]
            else:
                self.data[name].clear()

    def add(self, name, desc=None, **kwargs):
        if name in self.data:
            raise AttributeError('%r already exists and cannot be added twice' % name)
        tmp_item = self.item_class(self, name, desc, **kwargs)
        self.data[tmp_item.name] = tmp_item

    def iter(self, *names, filter_flags=None, **kwargs):
        filter_flags = make_list(filter_flags)
        for i in self.data.values():
            if names and i.name not in names:
                continue
            if not i.match(*filter_flags, **kwargs):
                continue
            yield i

    def __getitem__(self, item):
        return self.data[item]

    def __iter__(self):
        for item in self.data.values():
            yield item

    def __len__(self):
        return len(self.data)

    def __contains__(self, item):
        return item in self.data

    def __bool__(self):
        if self.data:
            return True
        return False

    def get_stat_data(self, *stats, names=None, filter_flags=None, full_field_names=False, **filter_kwargs):

        count = 0
        names = make_list(names)
        tmp_ret = {}
        if full_field_names:
            total_name = 'Total %ss' % self.item_name
        else:
            total_name = 'total'

        for item in self.iter(*names, filter_flags=filter_flags, **filter_kwargs):
            count += 1
            for key, item in item.stats_dict(full_field_names=full_field_names).items():
                if stats and key not in stats:
                    continue
                if key in tmp_ret:
                    tmp_ret[key] += item
                else:
                    tmp_ret[key] = item
        if stats and total_name in stats or not stats:
            tmp_ret[total_name] = count

        return tmp_ret

    def get_stat(self, stat):
        tmp_dict = self.get_stat_data(stat)
        return tmp_dict[stat]

    def summary(self, *names, indent=0, filter_flags=None, **filter_kwargs):
        tmp_ret = self.get_stat_data(names=names, filter_flags=filter_flags, full_field_names=True, **filter_kwargs)
        tmp_ret = format_key_value(tmp_ret)
        if indent:
            tmp_ret = indent_str(tmp_ret, indent)
        return tmp_ret

    def name_list(self, *names, indent=0, filter_flags=None, long_name_kwargs=None, **filter_kwargs):
        tmp_ret = []
        long_name_kwargs = long_name_kwargs or {}
        for i in self.iter(*names, filter_flags=filter_flags, **filter_kwargs):
            tmp_ret.append(i.long_name(**long_name_kwargs))

        tmp_ret = '\n'.join(tmp_ret)

        if indent:
            tmp_ret = indent_str(tmp_ret, indent)
        return tmp_ret

    def _details(self, *names, dump=False, filter_flags=None, detail_kwargs=None, **filter_kwargs):
        tmp_ret = {}
        def_kwargs = dict(inc_stats=True, inc_analysis=True, inc_status=True)
        if detail_kwargs:
            def_kwargs.update(detail_kwargs)
        for i in self.iter(*names, filter_flags=filter_flags, **filter_kwargs):
            tmp_ret[i.short_name(inc_status_prefix=True)] = i.details(dump=dump, inc_name=False, **def_kwargs)


        tmp_ret = format_key_value(tmp_ret)
        return tmp_ret

    def details(self, *names, indent=0, dump=False, inc_summary=True, filter_flags=None, detail_kwargs=None, **filter_kwargs):
        tmp_details = self._details(*names, filter_flags=filter_flags, detail_kwargs=detail_kwargs, **filter_kwargs)
        if inc_summary:
            tmp_ret = [
                'Summary:',
                self.summary(*names, indent=2, filter_flags=filter_flags, **filter_kwargs),
                'Details:',
                indent_str(tmp_details, 2)
            ]
            tmp_ret = '\n'.join(tmp_ret)
        else:
            tmp_ret = tmp_details
        tmp_ret = indent_str(tmp_ret, indent)

        return tmp_ret


# ******************************************************************************
# ID Flagger Item
# ******************************************************************************

class TestFlaggerSkipIDObj(TestFlaggerBaseItemObj):
    """
    [m] id_name

    id_name [matched 2]
        desc  : desc
        tests : test 1
                test 2
                test 3

    """

    metric_info = {'test_count': 'Matched Tests',
                   'not_found': 'Not Found IDs'}
    dump_header = 'Tests'
    _should_skip = True

    def __eq__(self, other):
        if self.name == other:
            return True
        return fnmatch(other, self.name)

    def should_skip(self, **kwargs):
        return self._should_skip

    @property
    def not_found(self):
        if self.tests:
            return 0
        else:
            return 1

    @property
    def tests(self):
        return self.referenced_obj

    @property
    def test_count(self):
        return len(self.tests)

    @property
    def matched(self):
        if self.tests:
            return True
        return False

    @property
    def unmatched(self):
        return not self.matched

    @property
    def summary_data(self):
        return self.status

    @property
    def status(self):
        if self.matched:
            if self.test_count > 1:
                return 'Matched %s times' % self.test_count
            else:
                return 'Matched 1 time'

        else:
            return 'Not Matched'

    @property
    def status_prefix(self):
        tmp_status = self.status
        if tmp_status == 'Not Matched':
            return 'U'
        else:
            return 'M'

    @property
    def long_name(self):
        tmp_status = self.status
        if tmp_status:
            return self.name + ' | ' + tmp_status
        else:
            return self.name

    found = test_count


class TestFlaggerSkipIDList(TestFlaggerBaseItemList):
    item_class = TestFlaggerSkipIDObj
    item_name = 'ID'

    def __contains__(self, item):
        for i in self.data.values():
            if item == i:
                return True
        return False

    def details(self, *names, indent=0, dump=False, inc_summary=True, filter_flags=None, detail_kwargs=None, **filter_kwargs):
        if dump:
            def_kwargs = dict(inc_stats=True, inc_analysis=True, inc_status=True)
        else:
            def_kwargs = dict(inc_stats=False, inc_analysis=False, inc_status=True)
        if detail_kwargs is not None:
            def_kwargs.update(detail_kwargs)

        return super(TestFlaggerSkipIDList, self).details(
            *names,
            indent=indent,
            dump=dump,
            inc_summary=inc_summary,
            filter_flags=filter_flags,
            detail_kwargs=def_kwargs,
            **filter_kwargs
        )

# ******************************************************************************
# Test Flagger Item
# ******************************************************************************


class TestFlaggerTestObj(TestFlaggerBaseItemObj):
    """

    short_name | summary_data = long name
    [s] Test_name | Flags: xxx  name_match = xxx

    dump
    status_name
    test_name [skipped]
        desc     : desc
        flags    :  flag_name
                    flag_name
        is_match : test_name*


    """

    metric_info = {
        'run': 'Run',
        'passed': 'Passed',
        'failed': 'Failed',
        'raised': 'Raised',
        'skipped': 'Skipped'
    }
    dump_header = 'Flags'
    all_groups = [('run', 'skipped'), ('passed', 'failed', 'raised')]

    def __init__(self, flagger, name, desc=None, is_default=True, flags=None, **kwargs):
        if not isinstance(name, str):
            desc = desc or name.__doc__
            name = name.id()
            name = name.rsplit('.', maxsplit=1)[1]
        if name.startswith('test_'):
            name = name[5:]
        elif name.startswith('test'):
            name = name[4:]
        self.skip_id_obj = None
        self.skipped = None
        self.skipped_flags = []
        self.run = None
        self.passed = None
        self.failed = None
        self.raised = None
        self.fail_reason = None

        super(TestFlaggerTestObj, self).__init__(flagger, name, desc, is_default, **kwargs)

        if flags:
            self.check(flags)

    def clear(self):
        super(TestFlaggerTestObj, self).clear()
        self.skip_id_obj = None
        self.skipped_flags.clear()
        self.skipped = None
        self.run = None
        self.passed = None
        self.failed = None
        self.raised = None
        self.fail_reason = None

    def skip_reasons(self):
        if self.skipped is None:
            return ''
        elif not self.skipped:
            return ''
        else:
            tmp_ret = []
            tmp_flags = []
            for f in self.skipped_flags:
                if isinstance(f, str):
                    tmp_flags.append(f)
                else:
                    tmp_flags.append(f.name)
            if tmp_flags:
                if len(tmp_flags) > 1:
                    tmp_flags = 'Flags: %s' % ', '.join(tmp_flags)
                else:
                    tmp_flags = 'Flag: %s' % tmp_flags[0]
                tmp_ret.append(tmp_flags)

            if self.skip_id_obj is not None:
                tmp_ret.append('Skip Test IDs: %s' % self.skip_id_obj.name)

            if tmp_ret:
                tmp_ret = 'Due To: %s' % ' / '.join(tmp_ret)

        return tmp_ret

    def check(self, flags=None, skip_id_obj=None):
        flags = make_list(flags)

        if not flags and not self.flagger.allow_no_flags:
            self.fail_reason = 'Test was missing flags'
            raise AttributeError('No flags defined for this test')

        for index in range(len(flags)):
            if isinstance(flags[index], TestFlaggerFlagObj):
                continue
            elif flags[index] in self.flagger.flags:
                flags[index] = self.flagger.flags[flags[index]]
            else:
                if self.flagger.allow_unknown:
                    if self.flagger.skip_on_unknown:
                        flags[index] = 'Unknown Flag: ' + flags[index]
                    else:
                        flags[index] = self.flagger.add_flag(flags[index])
                else:
                    raise AttributeError('%s not defined as a flag' % flags[index])

        if self.name in self.flagger.skip_ids or skip_id_obj is not None:
            if skip_id_obj is not None:
                self.skip_id_obj = skip_id_obj
            else:
                self.skip_id_obj = self.flagger.skip_ids[self.name]
            self.skip_id_obj.tests.append(self)

        for flag in flags:
            if isinstance(flag, str):
                self.skipped_flags.append(flag)
            else:
                flag.link_test(self)
                self.flags.append(flag)

                if flag.should_skip():
                    self.skipped_flags.append(flag)

        if self.skipped_flags or self.skip_id_obj is not None:
            self._set_result(state='skipped')
            raise unittest.SkipTest(self.skip_reasons())

        else:
            self._set_result(state='run')

    def set_result(self, exc=None):
        if exc is not None:
            self.fail_reason = str(exc)
            if issubclass(exc.__class__, AssertionError):
                self._set_result('failed')
            else:
                self._set_result('raised')
        else:
            self._set_result('passed')

    def _set_result(self, state):

        if state in ('passed', 'failed', 'raised'):
            if self.skipped:
                raise AttributeError('Test marked as skipped, cannot set result')
            self.passed = False
            self.failed = False
            self.raised = False
            self.run = True
            self.skipped = False
            if state == 'passed':
                self.passed = True
            elif state == 'failed':
                self.failed = True
            else:
                self.raised = True
        elif state in ('run', 'skipped'):
            self.passed = None
            self.failed = None
            self.raised = None
            self.run = False
            self.skipped = False
            if state == 'skipped':
                self.skipped = True
            elif state == 'run':
                self.run = True
        else:
            self.passed = None
            self.failed = None
            self.raised = None
            self.run = False
            self.skipped = False

        for f in self.flags:
            f.set_result()

    @property
    def flags(self):
        return self.referenced_obj

    @property
    def skip_ids(self):
        return [self.skip_id_obj]

    @property
    def status(self):
        if not self.run and not self.skipped:
            tmp_ret = 'Not Tried'
        else:
            tmp_ret = 'Run'
            if self.skipped:
                tmp_ret = 'Skipped'
            elif self.passed is not None:
                if self.passed:
                    tmp_ret = 'Passed'
                elif self.failed:
                    tmp_ret = 'Failed'
                elif self.raised:
                    tmp_ret = 'Raised'

        return tmp_ret

    @property
    def summary_data(self):
        return self.skip_reasons()

    @property
    def status_prefix(self):
        tmp_ret = self.status
        if tmp_ret == 'Raised':
            tmp_ret = 'E'
        elif tmp_ret == 'Not Tried':
            tmp_ret = '?'
        else:
            tmp_ret = tmp_ret[0]
        return tmp_ret

    def _dump_data(self):
        tmp_ret = {}
        if self.skip_id_obj is not None:
            tmp_ret['Skipped Names'] = self.skip_id_obj.name
        else:
            tmp_ret['Skipped Names'] = '* None *'
        tmp_sr = self.skip_reasons()
        if tmp_sr:
            tmp_ret['Reasons'] = tmp_sr
        return tmp_ret


class TestFlaggerTestList(TestFlaggerBaseItemList):
    item_class = TestFlaggerTestObj
    item_name = 'Test'

    def add(self, name, desc=None, **kwargs):
        if not isinstance(name, str):
            desc = desc or name.__doc__
            name = self.parse_name(name)

        super(TestFlaggerTestList, self).add(name, desc=desc, **kwargs)

    def parse_name(self, name):
        if not isinstance(name, str):
            name = name.id()
        if '.' in name:
            name = name.rsplit('.', maxsplit=1)[1]
        if name.startswith('test_'):
            name = name[:5]
        elif name.startswith('test'):
            name = name[:4]
        return name


# ******************************************************************************
# Flag Flagger Item
# ******************************************************************************

def pass_fail_run_skip_analysis(passed=0, failed=0, raised=0, skipped=0, run=0, **kwargs):
    if sum((passed, failed, raised, skipped, run)) == 0:
        return 'Not Found'
    if sum((passed, failed, raised)) == 0:
        tmp_pf = 'No PF Info'
    elif sum((failed, raised)) == 0:
        tmp_pf = 'All Passed'
    elif sum((passed, raised)) == 0:
        tmp_pf = 'All Failed'
    elif sum((passed, failed)) == 0:
        tmp_pf = 'All Raised'
    elif passed == 0:
        tmp_pf = 'All Failed or Raised'
    elif failed == 0:
        tmp_pf = 'All Passed or Raised'
    elif raised == 0:
        tmp_pf = 'All Passed or Failed'
    else:
        tmp_pf = 'All Passed, Failed, or Raised'

    if sum((skipped, run)) == 0:
        raise AttributeError('skipped and run are 0, should not get here')
    elif skipped == 0:
        tmp_sr = 'All Run'
    elif run == 0:
        tmp_sr = 'All Skipped'
    else:
        tmp_sr = 'Some Skipped'

    return tmp_sr + ', ' + tmp_pf


class TestFlaggerFlagObj(TestFlaggerBaseItemObj):
    """
    skip_if_is_os_<xxx>
    skip_if_not_os_<xxx>

    skip_if_is_pyv_x.x(+-)
    skip_if_not_pyv_x.x(+-)

    skip_if_is_module_xxx[_loaded]
    skip_if_not_module_xxx[_loaded]

    skip_if_is_test_xxx_[passed/failed/raised/run]
    skip_if_not_test_xxx_[passed/failed/raised/run]

    skip_if_is_flag_xxx_[all/any/none]_[passed/failed/raised/run]
    skip_if_not_flag_xxx_[all/any/none]_[passed/failed/raised/run]

    skip_if_is_platform_[xxx]_xxx
        [machine|node|platform_aliased|platform_terse|processor|python_compiler|python_implementation|python_branch|release|system|version|java_ver|win32_ver|mac_ver|dist|linux_distribution]
    skip_if_is_environ_

    """

    """
    [s] flag_name [Skip] | sk:(s-2/o-3) rn:3 ps:3 fa:4 ex:4


    flag_name [skip]
        desc          : desc
        run/skipped:
            skipped other : 1
            skipped self  : 1
            run           : 2
        pass/fail:
            passed        : 7
            failed        : 3
            raised        : 3
        tests         : test 1
                        test 2
                        test 3

    """
    metric_info = {
        'run': 'Run',
        'passed': 'Passed',
        'failed': 'Failed',
        'raised': 'Raised',
        'skipped': 'Skipped',
    }
    all_groups = [('run', 'skipped'), ('passed', 'failed', 'raised')]
    dump_header = 'Tests'
    dump_inc_summary = True

    def __init__(self, flagger, name, desc=None, is_default=True, **kwargs):
        self._should_skip = False
        self.should_include = True
        self.found = 0
        self.skipped = 0
        self.other_skipped = 0
        self.self_skipped = 0
        self.run = 0
        self.passed = 0
        self.failed = 0
        self.raised = 0
        self.fail_reasons = []
        self._check_func = None
        self._check_func_kwargs = {}

        self.active_check = False

        super(TestFlaggerFlagObj, self).__init__(flagger, name, desc, is_default, **kwargs)

    @property
    def tests(self):
        return self.referenced_obj

    def should_skip(self, **kwargs):
        return self._should_skip

    def clear(self):
        super(TestFlaggerFlagObj, self).clear()
        self.fail_reasons.clear()

    def _analysis(self):
        return pass_fail_run_skip_analysis(**self.stats_dict(full_field_names=False))

    @property
    def status(self):
        if self.should_skip():
            return 'Skip'
        else:
            return 'Inc'

    @property
    def summary_data(self):
        if self.run + self.skipped == 0:
            return 'Not Found'
        elif self.passed is None:
            return 'R:%s S:%s' % (self.run, self.skipped)
        else:
            return 'R:%s S:%s / P:%s F:%s E:%s' % (self.run, self.skipped, self.passed, self.failed, self.raised)

    def _dump_data(self):
        """
        run/skipped:
            skipped other : 1
            skipped self  : 1
            run           : 2
        pass/fail:
            passed        : 7
            failed        : 3
            raised        : 3

        :return:
        """
        if self.run + self.skipped == 0:
            return {'Stats': '* No Stats *'}
        tmp_ret = OrderedDict()
        tmp_ret['Run/Skipped Stats:'] = '__header__'
        tmp_ret['Run'] = self.run
        tmp_ret['Skipped/Self'] = self.self_skipped
        tmp_ret['Skipped/Other'] = self.other_skipped
        if self.passed is not None:
            tmp_ret['Passed/Failed Stats:'] = '__header__'
            tmp_ret['Passed'] = self.passed
            tmp_ret['Failed'] = self.failed
            tmp_ret['Raised'] = self.raised
        if self.fail_reasons:
            tmp_ret['Reasons:'] = '__header__'
            tmp_ret[''] = '\n'.join(self.fail_reasons)
        return tmp_ret

    def link_test(self, test_in):
        self.tests.append(test_in)
        self.set_result()

    def set_result(self):
        self.found = len(self.tests)
        self.skipped = 0
        self.other_skipped = 0
        self.self_skipped = 0
        self.run = 0
        self.passed = 0
        self.failed = 0
        self.raised = 0

        for t in self.tests:
            status = t.status
            if status == 'Skipped':
                if self.should_skip():
                    self.self_skipped += 1
                else:
                    self.other_skipped += 1
                self.skipped += 1
            else:
                self.run += 1
                if status == 'Passed':
                    self.passed += 1
                elif status == 'Failed':
                    self.failed += 1
                    self.fail_reasons.append(t.fail_reason)
                elif status == 'Raised':
                    self.raised += 1
                    self.fail_reasons.append(t.fail_reason)

    @property
    def long_name(self):
        return '%s [%s] | %s' % (self.name, self.status, self.summary_data)


class TestFlaggerTestSkipOS(TestFlaggerFlagObj):
    """
    os.name
    'nt'
    """
    skip_name = 'os'
    re_match = re.compile(r'skip_if_(?P<is_not>is|not)_os_(?P<os_name>.+)')
    desc = 'Skip this test if the OS is {is_not}{os_name!r}'
    active = True
    check_params = None

    def __init__(self, flagger, name, desc=None, **kwargs):
        tmp_match = self.re_match.fullmatch(name)
        if not tmp_match:
            raise AttributeError('invalid name: %r for %r' % (name, self.re_match))
        self.check_for_not = tmp_match['is_not'] == 'not'
        self.check_params = tmp_match.groupdict()
        if self.check_params['is_not'] == 'is':
            self.check_params['is_not'] = ''
        else:
            self.check_params['is_not'] = 'not '
        self.update_params()
        desc = self.desc.format(**self.check_params)

        super(TestFlaggerTestSkipOS, self).__init__(flagger=flagger,
                                                 name=name,
                                                 desc=desc,
                                                 **kwargs)

    def update_params(self):
        pass

    def check_skip(self, **kwargs):
        return self.check_params['os_name'] == os.name

    def should_skip(self, **kwargs):
        if self.check_for_not:
            return not self.check_skip(**kwargs)
        else:
            return self.check_skip(**kwargs)


class TestFlaggerTestSkipPyVer(TestFlaggerTestSkipOS):
    """skip_if_is_pyv_x.x.x[+|-]"""
    skip_name = 'pyv'
    desc = 'Skip this test if the Python Version is {is_not}{modifier} {pyv_name!r}'
    re_match = re.compile(r'skip_if_(?P<is_not>is|not)_pyv_(?P<pyv_name>[0-9\.]+)(?P<modifier>[+-]?)')

    def update_params(self):
        if 'modifier' not in self.check_params or self.check_params['modifier'] == '':
            self.check_params['modifier'] = '=='
        elif self.check_params['modifier'] == '-':
            self.check_params['modifier'] = '<='
        else:
            self.check_params['modifier'] = '>='
        if self.check_params['pyv_name'].isdigit():
            self.check_params['pyv_name'] += '.0'

    def check_skip(self, **kwargs):
        check_version = StrictVersion(self.check_params['pyv_name'])
        plat_version = StrictVersion(platform.python_version())

        # print('%s (%s):  %s %s %s' % (self.name, self.desc, check_version, self.check_params['modifier'], plat_version))

        if self.check_params['modifier'] == '<=':
            return  plat_version <= check_version
        if self.check_params['modifier'] == '>=':
            return plat_version >= check_version
        if self.check_params['modifier'] == '==':
            return check_version == plat_version


class TestFlaggerTestSkipTestRun(TestFlaggerTestSkipOS):
    """skip_if_is_test_xxx_[passed/failed/raised/run"""
    skip_name = 'test'
    desc = 'Skip this test if the test {test_name!r} {is_not}{action}'
    re_match = re.compile(r'skip_if_(?P<is_not>is|not)_test_(?P<test_name>.+)_(?P<action>passed|failed|raised|run)')

    def check_skip(self, **kwargs):
        tmp_test = self.flagger.tests[self.check_params['test_name']]
        return bool(getattr(tmp_test, self.check_params['action']))


class TestFlaggerTestSkipModule(TestFlaggerTestSkipOS):
    """skip_if_is_module_xxx"""
    skip_name = 'module'
    desc = 'Skip this test if the module {module_name!r} was {is_not}loaded'
    re_match = re.compile(r'skip_if_(?P<is_not>is|not)_module_(?P<module_name>.+)')
    # re_match = MODULE_MATCH_RE

    def parse_params(self, check_name_in):
        tmp_ret = {'module': check_name_in}
        return tmp_ret

    def check_skip(self, **kwargs):
        return self.check_params['module_name'] in sys.modules


class TestFlaggerTestSkipFlag(TestFlaggerTestSkipOS):
    """skip_if_is_flag_xxx_[all/any/no]_[passed/failed/raised/run"""
    skip_name = 'flag'
    re_match = re.compile(r'skip_if_(?P<is_not>is|not)_flag_(?P<flag_name>.+)_(?P<scope>all|any|no)_(?P<action>passed|failed|raised|run)')
    # re_match = FLAG_MATCH_RE
    desc = 'Skip this test if the other tests for flag {flag_name!r} {is_not}{scope} {action}'

    def check_skip(self, **kwargs):
        tmp_flag = self.flagger.flags[self.check_params['flag_name']]
        return tmp_flag.match(self.check_params['match'])


EXPECT_NAMES = r'machine|node|platform_full|platform_aliased|platform_terse|processor|python_compiler|python_implementation|python_branch|release|system|version'
PLAT_RE = r'skip_if_(?P<is_not>is|not)_platform_(?P<platform_name>%s)_(?P<expect>.+)' % EXPECT_NAMES


class TestFlaggerTestSkipPlatform(TestFlaggerTestSkipOS):
    """skip_if_is_platform_[xxx]_xxx
    [machine|node|platform-aliased|platform_terse|processor|python-compiler|python-implementation|python-branch|release|system|version]

    platform.platform()
    'Windows-10-10.0.17763-SP0'
    platform.platform(terse=True)
    'Windows-10'
    platform.platform(aliased=True)
    'Windows-10-10.0.17763-SP0'
    platform.processor()
    'Intel64 Family 6 Model 63 Stepping 2, GenuineIntel'
    platform.machine()
    'AMD64'
    platform.node()
    'WHITE-PC'
    platform.python_compiler()
    'MSC v.1915 64 bit (AMD64)'
    platform.python_implementation()
    'CPython'
    platform.python_branch()
    'v3.7.1'
    platform.release()
    '10'
    platform.version()
    '10.0.17763'

    """
    skip_name = 'platform'
    # re_match = PLAT_MATCH_RE
    re_match = re.compile(PLAT_RE)
    desc = 'Skip this test if the platform.{platform_name}() is {is_not}{expect!r}'
    check_funcs = {
        'machine': platform.machine,
        'node': platform.node,
        'platform_full': platform.platform,
        'platform_aliased': platform.platform,
        'platform_terse': platform.platform,
        'processor': platform.processor,
        'python_compiler': platform.python_compiler,
        'python_implementation': platform.python_implementation,
        'python_branch': platform.python_branch,
        'release': platform.release,
        'system': platform.system,
        'version': platform.version,
    }

    def check_skip(self, **kwargs):
        if self.check_params['platform_name'] == 'platform_aliased':
            return self.check_params['expect'] == platform.platform(aliased=True)
        elif self.check_params['platform_name'] == 'platform_terse':
            # print('%s (%s): %s == %s' % (self.name, self.desc, self.check_params['expect'], platform.platform(terse=True)))
            return self.check_params['expect'] == platform.platform(terse=True)
        else:
            return self.check_params['expect'] == self.check_funcs[self.check_params['platform_name']]()


class TestFlaggerTestSkipEnvironBase(TestFlaggerTestSkipOS):
    """skip_if_is_environ_

    This is an example of how to build a custom skip check

    """
    skip_name = 'env_var'
    # re_match = ENV_MATCH_RE
    re_match = re.compile(r'skip_if_(?P<is_not>is|not)_env_var_(?P<env_var_name>.+)_(?P<expect>.+)')

    desc = 'Skip this test if the environment var {env_var_name!r} is {is_not}{expect!r}'

    def check_skip(self, **kwargs):
        try:
            return os.environ[self.check_params['env_var_name']] == self.check_params['expect']
        except KeyError:
            return self.check_for_not


class TestFlaggerFlagList(TestFlaggerBaseItemList):
    item_class = TestFlaggerFlagObj
    item_name = 'Flag'

    def add_flags(self, *flags, should_skip=True):
        for flag in flags:
            if flag in self:
                self[flag].found += 1
            else:
                if self.flagger.allow_unknown:
                    self.add(flag, _should_skip=should_skip, is_default=False, found=1)
                else:
                    raise AttributeError('Invalid Skip Key Found: %r' % flag)


# ******************************************************************************
# Test Flagger Oject
# ******************************************************************************


class TestFlagger(object):

    def __init__(self,
                 testcase,
                 flag_data=None,
                 inc_flags=None,
                 skip_flags=None,
                 skip_test_ids=None,
                 verify_all=False,
                 allow_unknown=False,
                 skip_on_unknown=False,
                 allow_no_flag=False):

        self.testcase = testcase
        self.allow_unknown = allow_unknown
        self.skip_on_unknown = skip_on_unknown
        # if not isinstance(skip_test_ids, (tuple, list)):
        #     self.skip_test_ids = [skip_test_ids]
        # else:
        self.skip_test_ids = make_list(skip_test_ids)
        self.verify_all = verify_all
        self.allow_no_flags = allow_no_flag
        if allow_unknown:
            self.no_flag_default = 'inc'
        else:
            self.no_flag_default = 'skip'

        self.skip_ids = TestFlaggerSkipIDList(self, items=skip_test_ids, is_default=True)
        self.tests = TestFlaggerTestList(self)
        self.flags = TestFlaggerFlagList(self, items=flag_data, is_default=True)

        if inc_flags and skip_flags:
            raise AttributeError('Either skip_flags OR inc_flags can be used, not both')

        if self.flags:
            has_flags = True
        else:
            has_flags = False

        if inc_flags:
            self.skip_on_unknown = True
            for i in self.flags:
                i._should_skip = True

            for i in make_list(inc_flags):
                if i not in self.flags:
                    if has_flags:
                        raise AttributeError('Unknown flag %r in inc_flags' % i)
                    self.flags.add(i, is_default=True, should_skip=False)
                else:
                    self.flags[i]._should_skip = False
        if skip_flags:
            self.skip_on_unknown = False
            for i in make_list(skip_flags):
                if i not in self.flags:
                    if has_flags:
                        raise AttributeError('Unknown flag %r in skip_flags' % i)
                    self.flags.add(i, is_default=True, should_skip=True)
                self.flags[i]._should_skip = True

    def reset(self):
        self.skip_ids.clear()
        self.flags.clear()
        self.tests.clear()

    def check(self, test_self, *flags):
        try:
            self.flags.add_flags(*flags, should_skip=self.skip_on_unknown)
        except AttributeError as err:
            self.tests.add(test_self, failed=True, flags=flags, fail_reason=str(err))
            raise

        self.tests.add(test_self, flags=flags)

    def set_passed(self, test_obj):
        try:
            tmp_test = self.tests[test_obj.id()]
        except KeyError:
            raise KeyError('Invalid Test ID Found: %r' % test_obj.id())
        tmp_test.passed = True
        tmp_test.failed = False
        for f in tmp_test.flags:
            f.passed += 1

    def set_failed(self, test_obj, reason):
        try:
            tmp_test = self.tests[test_obj.id()]
        except KeyError:
            raise KeyError('Invalid Test ID Found: %r' % test_obj.id())
        tmp_test.failed = True
        tmp_test.passed = False
        tmp_test.fail_reason = str(reason)
        for f in tmp_test.flags:
            f.failed += 1
            f.fail_reasons.append(str(reason))

    def test_report(self, *filters, summary=True, details=False, dump=False, inc_flags=True, inc_skip_ids=True):
        """
        :param filters:
        :param summary:
        :param details:
        :param dump:
        :return:

        Tests:
            Total : 120
            Ran: 100
            Paassed: 80
            Failed:  20
            Exceptions: 20
            Skipped: 20

        Detail:
            [S] Test_a [Passed/Failed/Skipped/Run/Raised] Flags: x, y, z  Skip_ID_Matched: a
            [F] Test_b [Passed/Failed/Skipped/Run]

        Dump:
            [S] Test_a [Passed/Failed/Skipped/Run]:
                Flags: x, y, z
                    <skip / fail reason>
            [F] Test_b [Passed/Failed/Skipped/Run]:
                Flags: x, y, z
                    <skip / fail reason>


        """

    def flag_report(self, *filters, summary=True, details=False, dump=False):
        """

        :param filters:
        :param summary:
        :param details:
        :param dump:
        :return:

        Flags:
            Total : 20
            Skip_flags: 10
            Include Flags: 10
            Paassed_Tests: 80
            Failed_tests:  20
            Skipped_tests: 20
            Raised: 10

        Detail:
            flag_1
                Skipped (other): 10
                Skipped (self): 10
                Passed: 10
                Failed: 10
                Run: 10
                Found: 10

        Dump:
            flag_1
                Skipped (other): 10
                Skipped (self): 10
                Passed: 10
                Failed: 10
                Run: 10
                Found: 10
                tests:
                    test1 (skipped) Skipped_ID: xxx
                    test2 (passed)





        """

    def skip_id_report(self, *filters, summary=True, details=False, dump=False):
        """
        :param filters:
        :param summary:
        :param details:
        :param dump:
        :return:

        Skip IDs:
            Total IDs: 10
            Skipped Tests: 20
            not_Found: 10

        Detail:
            Skip_ID_1 (not found) / (Skipped: 10)
            Skip_ID_1 (not found) / (Skipped: 10)

        Dump:
            Skip_ID_1 (not found) / (Skipped: 10)
                Tests Skipped:
                    test_1 [status] flags: a, b, c
                    test_2 [status]
                    Test_3 [status]
            Skip_ID_1 (not found) / (Skipped: 10)
                Tests Skipped:
                    test_1
                    test_2
                    Test_3


        """

    def flag_analysis(self):
        """

        summary:

        Analysis:

            all flags failed [test_qty/flag_qty]
            all flags raised
            all flags passed
            Any flags passed

        detail (by_test):

            all flags failed [test_qty/flag_qty]
                test (flags)
                test (flags)
                test (flags)

            all flags raised
            all flags passed
            Any flags passed
            All flags skipped
            Some flags skipped


        dump (by_flag)
            all flags failed [test_qty/flag_qty]
                flag:
                    test
                    test
                    test

            all flags raised
            all flags passed
            Any flags passed


        :return:
        """


class TestFlaggerManager(object):
    def __init__(self):
        self.flaggers = {}

    def parse_test_case_name(self, name):
        if not isinstance(name, str):
            try:
                name = name.id()
                if '.' in name:
                    name = name.rsplit('.', maxsplit=1)[0]
            except AttributeError:
                name = name.__name__
        if name.startswith('test_'):
            name = name[:5]
        elif name.startswith('test'):
            name = name[:4]
        return name

    def setup(self, test_case_name, *args, **kwargs):
        test_case_name = self.parse_test_case_name(test_case_name)
        if test_case_name not in self.flaggers:
            tmp_flagger = TestFlagger(*args, **kwargs)
            self.flaggers[test_case_name] = tmp_flagger

    def finished(self, test_case_name, *args, **kwargs):
        test_case_name = self.parse_test_case_name(test_case_name)
        self.flaggers[test_case_name].finish(*args, **kwargs)

    def __getitem__(self, item):
        test_case_name = self.parse_test_case_name(item)
        return self.flaggers[test_case_name]

    def __call__(self, func):
        def func_wrapper(*flags, name=None, sub_test=None):
            if name is None:
                test_case_name = self.parse_test_case_name(func)
            else:
                test_case_name = self.parse_test_case_name(name)

            if name is None:
                name = func

            tmp_test_obj = self[test_case_name][name]
            tmp_test_obj.check(name, *flags, sub_test=sub_test, )
            try:
                tmp_ret = func()
            except Exception as err:
                tmp_test_obj.set_result(err)
                raise
            tmp_test_obj.set_result()
            return tmp_ret
        return func_wrapper

    def cm(self, name, *flags, sub_test=None):
        test_obj = self[name][sub_test]
        return FlaggerContextManager(test_obj, flags=flags)


class FlaggerContextManager(object):
    def __init__(self, test_obj, flags):
        self.test_obj = test_obj
        self.flags = flags

    def __enter__(self):
        self.test_obj.check(*self.flags)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.test_obj.set_result(exc_type(exc_type))

