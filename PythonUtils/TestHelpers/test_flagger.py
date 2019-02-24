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
from PythonUtils.BaseUtils import make_list, format_key_value, indent_str
from distutils.version import StrictVersion

def SkipIfPyLower(major, minor):
    if sys.version_info[0] < major or (sys.version_info[0] == major and sys.version_info[1] < minor):
        return unittest.skip("Python version %s.%s required, running %s.%s" % (major, minor, sys.version_info[0], sys.version_info[0]))
    return lambda func: func




# ******************************************************************************
# Base Flagger Item
# ******************************************************************************


class TestFlaggerBaseItemObj(object):
    metric_info = {}
    dump_header = 'Dump'
    dump_inc_summary = True
    stats_in_status = False
    obj_name = 'Objs'

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

    def match(self, *filter_flags, **filter_kwrgs):
        """
        flags:

            all_<metric_name>
            any_<metric_name> or inc_<metric_name>
            no_<metric_name>

        kwargs:
          inc_<reference_obj>=[test_list]

        :param match_kwargs:
        :return:
        """

        for flag in filter_flags:
            metrics = list(self.metric_info.keys())
            parsed_flag = flag.split('_', maxsplit=1)
            scope_flag = parsed_flag[0]
            metric_flag = parsed_flag[-1]
            if metric_flag not in metrics:
                raise AttributeError('filter flag %r does not reference a valid metric: %r' % (flag, list(self.metric_info.keys())))

            if scope_flag == 'all':
                metrics.remove(metric_flag)
                if not getattr(self, metric_flag):
                    return False
                for other_flag in metrics:
                    if getattr(self, other_flag):
                        return False
            elif scope_flag in ('any', 'inc'):
                if not getattr(self, metric_flag):
                    return False
            elif scope_flag == 'no':
                if getattr(self, metric_flag):
                    return False
            else:
                raise AttributeError('filter flag %s does not reference a valid scope' % flag)

        for key, value in filter_kwrgs.items():
            if key.startswith('inc_'):
                look_in = key[4:]
                look_for = make_list(value)

                look_in_list = getattr(self, look_in)

                for l in look_for:
                    if l not in look_in_list:
                        return False
        return True

    def stats_dict(self, inc_stats=None, exc_stat=None, inc_empty=True, full_field_names=True):
        exc_stat = make_list(exc_stat)
        inc_stats = make_list(inc_stats)
        tmp_ret = {}
        if exc_stat and inc_stats:
            raise AttributeError('Cannot use both inc_stats and exc_stats')
        for metric_attr, metric_name in self.metric_info.items():
            if metric_attr in exc_stat:
                continue
            if inc_stats and metric_attr not in inc_stats:
                continue
            tmp_value = getattr(self, metric_attr)
            if not inc_empty and not tmp_value:
                continue
            if full_field_names:
                tmp_ret[metric_name] = tmp_value
            else:
                tmp_ret[metric_attr] = tmp_value
        return tmp_ret

    def status(self, as_prefix=False):
        return ''

    def summary_data(self, inc_desc=True, inc_status=True, **kwargs):
        tmp_ret = []
        if inc_status and self.status():
            tmp_ret.append('[%s]' % self.status())
        if inc_desc and self.desc:
            tmp_ret.append('(%s)' % self.desc)
        tmp_ret = ' '.join(tmp_ret)
        return tmp_ret

    def short_name(self, inc_status_prefix=True, **kwargs):
        tmp_ret = ''
        if inc_status_prefix and self.status(as_prefix=True):
            tmp_ret += '[%s] ' % self.status(as_prefix=True)
        tmp_ret += self.name
        return tmp_ret

    def long_name(self, inc_desc=True, inc_status=True, inc_status_prefix=False, **kwargs):
        tmp_ret = self.short_name(inc_status_prefix=inc_status_prefix, **kwargs)
        tmp_ret_2 = self.summary_data(inc_desc=inc_desc, inc_status=inc_status, **kwargs)
        if tmp_ret_2:
            tmp_ret += ' ' + tmp_ret_2
        return tmp_ret

    def _dump(self, **kwargs):
        if self.dump_inc_summary:
            tmp_ret = {}
            for item in self.referenced_obj:
                tmp_ret[item.short_name(inc_status_prefix=True, **kwargs)] = item.summary_data(inc_desc=False, **kwargs)
            return format_key_value(tmp_ret)
        else:
            tmp_ret = []
            for item in self.referenced_obj:
                tmp_ret.append(item.short_name(inc_status_prefix=True, **kwargs))
            return '\n'.join(tmp_ret)

    def _analysis(self, **kwargs):
        for metric, name in self.metric_info.items():
            if self.match('all_' + metric):
                tmp_analysis = 'All %s' % name
                return tmp_analysis
        return None

    def details(self, indent=0, dump=False, inc_name=True, inc_stats=True, inc_analysis=True, inc_status=True, **kwargs):
        """
        :param indent:
        :param dump:
        :param inc_stats:
        :param inc_analysis:
        :param kwargs:
        :return:

        [S] name (description)
          status
          analysis
          <stats>: xx
          <stats>: xx
          <stats>: xx
          dump:
            dump data
        """
        if dump:
            inc_stats = True
            inc_analysis = True
            inc_status = True

        if inc_status and inc_name and not (inc_analysis or inc_stats):
            high_status = True
        else:
            high_status = False

        tmp_dict = {}
        if inc_analysis:
            tmp_analy = self._analysis(**kwargs)
            if tmp_analy:
                tmp_dict['Analysis'] = tmp_analy
        if inc_stats:
            tmp_stats = self.stats_dict(**kwargs)
            if tmp_stats:
                tmp_dict.update(tmp_stats)
        if dump:
            tmp_dump = self._dump(**kwargs)
            if tmp_dump:
                tmp_dict[self.dump_header] = tmp_dump

        tmp_data = []
        if inc_status and self.status():
            if not high_status:
                tmp_data.append(self.status(as_prefix=False))

        if tmp_dict:
            tmp_data.append(format_key_value(tmp_dict))

        tmp_data = '\n'.join(tmp_data)
        if inc_name:
            tmp_ret = self.long_name(inc_status=high_status, **kwargs)
            if tmp_data:
                tmp_data = '\n' + indent_str(tmp_data, 2)
                tmp_ret += tmp_data

        else:
            tmp_ret = tmp_data

        if indent:
            tmp_ret = indent_str(tmp_ret, indent)
        return tmp_ret


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

    def status(self, as_prefix=False):
        if as_prefix:
            return ''
        if self.matched:
            if self.test_count > 1:
                return 'Matched %s times' % self.test_count
            else:
                return 'Matched 1 time'

        else:
            return 'Not Matched'

    def details(self, indent=0, dump=False, inc_stats=False, inc_analysis=False, inc_status=True, **kwargs):
        if inc_stats:
            inc_status = False

        return super(TestFlaggerSkipIDObj, self).details(
                    indent=indent,
                    dump=dump,
                    inc_stats=inc_stats,
                    inc_analysis=inc_analysis,
                    inc_status=inc_status,
                    **kwargs
                )


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
    metric_info = {
        'ran': 'Ran',
        'passed': 'Passed',
        'failed': 'Failed',
        'raised': 'Raised',
        'skipped': 'Skipped'
    }
    dump_header = 'Flags'

    def __init__(self, flagger, name, desc=None, is_default=True, flags=None, failed=None, fail_reason=None, **kwargs):
        if not isinstance(name, str):
            desc = desc or name.__doc__
            name = name.id()
            name = name.rsplit('.', maxsplit=1)[1]
        if name.startswith('test_'):
            name = name[:5]
        elif name.startswith('test'):
            name = name[:4]
        self.skip_id_obj = None
        self.skip_reason = None
        self.skipped = None
        self.run = None
        self.passed = None
        self.failed = failed
        self.raised = None
        self.fail_reason = fail_reason

        super(TestFlaggerTestObj, self).__init__(flagger, name, desc, is_default, **kwargs)

        self.check(flags)

    def clear(self):
        super(TestFlaggerTestObj, self).clear()
        self.skip_id_obj = None
        self.skip_reason = None
        self.skipped = None
        self.run = None
        self.passed = None
        self.failed = None
        self.raised = None
        self.fail_reason = None

    def check(self, flags):
        flags = make_list(flags)

        if not flags and not self.flagger.allow_no_flags:
            self.skip_reason = 'Test was missing flags'
            self.failed = True
            raise AttributeError('No flags defined for this test')

        skip_reasons = []

        for a in flags:
            skipped_flags = []
            if a in self.flagger.flags:
                tmp_flag = self.flagger.flags[a]
                tmp_flag.found += 1
                tmp_flag.tests.append(self)
                self.flags.append(tmp_flag)

                if tmp_flag.should_skip:
                    skipped_flags.append(tmp_flag.name)
            if skipped_flags:
                if len(skipped_flags) > 1:
                    skip_reasons.append('Flags: %r' % ', '.join(skipped_flags))
                else:
                    skip_reasons.append('Flag: %r' % skipped_flags[0])

        if self.name in self.flagger.skip_ids:
            self.skip_id_obj = self.flagger.skip_ids[self.name]
            self.skip_id_obj.found += 1
            self.skip_id_obj.tests.append(self)
            skip_reasons.append('ID Match: %r' % self.skip_id_obj)

        if skip_reasons:
            self.skipped = True
            self.skip_reason = 'Skipped due to: %s' % ' '.join(skip_reasons)
            for f in self.flags:
                if f.should_skip:
                    f.self_skip += 1
                else:
                    f.other_skip += 1
                f.skipped += 1
            raise unittest.SkipTest(self.skip_reason)

        else:
            self.run = True
            for f in self.flags:
                f.run += 1

    def set_result(self, exc=None):
        self.passed = False
        self.failed = False
        self.raised = False
        if exc is None:
            self.passed = True
        else:
            self.fail_reason = str(exc)
            if issubclass(exc.__class__, AssertionError):
                self.failed = True
            else:
                self.raised = True

        for f in self.flags:
            f.set_result(passed=self.passed, failed=self.failed, raised=self.raised, exc_str=self.fail_reason)

    @property
    def flags(self):
        return self.referenced_obj

    @property
    def skip_ids(self):
        return [self.skip_id_obj]

    def status(self, as_prefix=False):
        tmp_ret = 'Run'
        if self.skipped:
            tmp_ret = 'Skipped'
        elif self.passed is not None:
            if self.passed:
                tmp_ret = 'Passed'
            elif self.failed:
                tmp_ret = 'Failed'
            elif self.raised:
                tmp_ret = 'Exc Raised'
        if as_prefix:
            tmp_ret = '[%s]' % tmp_ret[0]
        return tmp_ret

    def flag_list(self):
        if not self.flags:
            return None
        tmp_ret = []
        for f in self.flags:
            tmp_ret.append(f.name)
        tmp_ret = ', '.join(tmp_ret)
        tmp_ret = 'Flags: ' + tmp_ret

        return tmp_ret

    def summary_data(self, inc_desc=True, inc_status=True, inc_flags=True, inc_skip_id=True, **kwargs):
        tmp_ret = []
        if inc_status and self.status():
            tmp_ret.append('[%s]' % self.status())
        if inc_flags:
            tmp_flags = self.flag_list()
            if tmp_flags:
                tmp_ret.append(tmp_flags)

        if inc_skip_id and self.skip_id_obj is not None:
            tmp_ret.append('Skip ID Matched: %s' % self.skip_id_obj.name)

        if inc_desc and self.desc:
            tmp_ret.append('(%s)' % self.desc)
        tmp_ret = ' '.join(tmp_ret)
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
    metric_info = {
        'ran': 'Ran',
        'passed': 'Passed',
        'failed': 'Failed',
        'raised': 'Raised',
        'skipped': 'Skipped',
        'self_skipped': 'Skipped(self)',
        'other_skipped': 'Skipped(Other)',
    }
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

    def status(self, as_prefix=False):
        if self.should_skip:
            tmp_ret = 'skip'
        else:
            tmp_ret = 'include'

        if as_prefix:
            return tmp_ret[0]
        return tmp_ret

    def set_result(self, passed=False, failed=False, raised=False, exc_reason=None):
        self.passed += passed
        self.failed += failed
        self.raised += raised
        if exc_reason:
            if exc_reason not in self.fail_reasons:
                self.fail_reasons.append(exc_reason)


"""
skip_if_is_os_<xxx>

skip_if_is_pyv_x.x(+-)

skip_if_is_module_xxx[_loaded]

skip_if_is_test_xxx_[passed/failed/raised/run]

skip_if_is_flag_xxx_[all/any/none]_[passed/failed/raised/run]

skip_if_is_platform_[xxx]_xxx
    [machine|node|platform_aliased|platform_terse|processor|python_compiler|python_implementation|python_branch|release|system|version|java_ver|win32_ver|mac_ver|dist|linux_distribution]

skip_if_is_environ_

"""

class TestFlaggerTestSkipOS(TestFlaggerFlagObj):
    flag_prefix = ('skip_if_is_os_', 'skip_if_not_os_')
    desc = 'Skip this test if {is_not}the OS is {os_name}'
    active = True
    check_params = None

    def __init__(self, flagger, name, desc=None, is_default=True, flags=None, failed=None, fail_reason=None, **kwargs):
        for flag_prefix in make_list(self.flag_prefix):
            if name.startswith(flag_prefix):
                rem_name = name[:len(flag_prefix)]
                if flag_prefix.startswith('skip_if_not'):
                    self.check_for_not = True
                self.check_params = self.parse_params(rem_name)
        if self.check_for_not:
            is_not = "not "
        else:
            is_not = ''

        desc = self.desc.format(is_not=is_not, **self.check_params)

        super(TestFlaggerTestSkipOS, self).__init__(flagger=flagger,
                                                 name=name,
                                                 desc=desc,
                                                 is_default=is_default,
                                                 flags=flags,
                                                 failed=failed,
                                                 fail_reason=fail_reason,
                                                 **kwargs)

    def parse_params(self, check_name_in):
        return {'os_name': check_name_in}

    def check_skip(self, **kwargs):
        return self.check_params['os_name'] != os.name

    def should_skip(self, **kwargs):
        if self.check_for_not:
            return not self.check_skip(**kwargs)
        else:
            return self.check_skip(**kwargs)


class TestFlaggerTestSkipPyVer(TestFlaggerTestSkipOS):
    flag_prefix = ('skip_if_is_pyv_', 'skip_if_not_pyv_')
    desc = 'Skip this test is {is_not}the Python Version {modifier} {version}'

    def parse_params(self, check_name_in):
        if check_name_in[-1] == '+':
            modifier = '<='
            check_name_in = check_name_in[:-1]
        elif check_name_in[-1] == '-':
            modifier = '>='
            check_name_in = check_name_in[:-1]
        else:
            modifier = '=='

        return {'version': StrictVersion(check_name_in),
                'modifier': modifier}

    def check_skip(self, **kwargs):
        if self.check_params['modifier'] == '<=':
            return self.check_params['version'] <= platform.python_version()
        if self.check_params['modifier'] == '>=':
            return self.check_params['version'] >= platform.python_version()
        if self.check_params['modifier'] == '==':
            return self.check_params['version'] == platform.python_version()


class TestFlaggerTestSkipTestRun(TestFlaggerTestSkipOS):
    """skip_if_is_test_xxx_[passed/failed/raised/run"""
    flag_prefix = ('skip_if_is_test_', 'skip_if_not_test_')
    desc = 'Skip this test if test {name} was {is_not}{action}'

    def parse_params(self, check_name_in):
        broken_out = check_name_in.rsplit('_', maxsplit=1)
        tmp_ret = {
            'test_name': broken_out[0],
            'action': broken_out[1]
        }
        return tmp_ret

    def check_skip(self, **kwargs):
        pass


class TestFlaggerTestSkipModule(TestFlaggerTestSkipOS):
    """skip_if_is_module_xxx"""
    flag_prefix = ('skip_if_is_module_', 'skip_if_not_module_')
    desc = 'Skip this test if the module {module} was {is_not}loaded'

    def parse_params(self, check_name_in):
        tmp_ret = {'module': check_name_in}
        return tmp_ret

    def check_skip(self, **kwargs):
        return self.check_params['module'] in sys.modules


class TestFlaggerTestSkipFlag(TestFlaggerTestSkipOS):
    """skip_if_is_flag_xxx_[all/any/none]_[passed/failed/raised/run"""
    flag_prefix = ('skip_if_is_flag_', 'skip_if_not_flag_')
    desc = 'Skip this test if the flag {flag_name} was {is_not}{action}'

    def parse_params(self, check_name_in):
        broken_out = check_name_in.rsplit('_', maxsplit=1)
        tmp_ret = {
            'flag_name': broken_out[0],
            'action': broken_out[1]
        }
        return tmp_ret

    def check_skip(self, **kwargs):
        pass

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
    flag_prefix = ('skip_if_is_module_xxx[_loaded_', '')
    desc = 'Skip this test if the Python Version is'
    check_funcs = {
        'machine': platform.machine,
        'node': platform.node,
        'platform': platform.platform,
        'platform-aliased': platform.platform,
        'platform-terse': platform.platform,
        'processor': platform.processor,
        'python-compiler': platform.python_compiler,
        'python-implementation': platform.python_implementation,
        'python-branch': platform.python_branch,
        'release': platform.release,
        'system': platform.system,
        'version': platform.version,
    }

    def parse_params(self, check_name_in):
        broken_out = check_name_in.rsplit('_', maxsplit=1)
        tmp_ret = {
            'platform_func': broken_out[0],
            'expect': broken_out[1]
        }
        return tmp_ret

    def check_skip(self, **kwargs):
        if self.check_params['platform_func'] == 'platform-aliased':
            return self.check_params['expect'] == platform.platform(aliased=True)
        elif self.check_params['platform_func'] == 'platform-terse':
            return self.check_params['expect'] == platform.platform(terse=True)
        else:
            return self.check_params['expect'] == self.check_funcs[self.check_params['platform_func']]()


class TestFlaggerTestSkipEnviron(TestFlaggerTestSkipOS):
    """skip_if_is_environ_

    This is an example of how to build a custom skip check

    """
    flag_prefix = ('skip_if_is_module_xxx[_loaded_', '')
    desc = 'Skip this test if the Python Version is'

    def __init__(self, *args, env_check_args=None, **kwargs):
        super(TestFlaggerTestSkipEnviron, self).__init__(*args, **kwargs)
        self.check_params = env_check_args

    def parse_params(self, check_name_in):
        return check_name_in

    def check_skip(self, **kwargs):
        for key, value in self.check_params.items():
            if os.environ[key] != value:
                return False
        return True

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
                i.should_skip = True

            for i in make_list(inc_flags):
                if i not in self.flags:
                    if has_flags:
                        raise AttributeError('Unknown flag %r in inc_flags' % i)
                    self.flags.add(i, is_default=True, should_skip=False)
                else:
                    self.flags[i].should_skip = False
        if skip_flags:
            self.skip_on_unknown = False
            for i in make_list(skip_flags):
                if i not in self.flags:
                    if has_flags:
                        raise AttributeError('Unknown flag %r in skip_flags' % i)
                    self.flags.add(i, is_default=True, should_skip=True)
                self.flags[i].should_skip = True

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

