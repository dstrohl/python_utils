#!/usr/bin/env python

"""
"""

__author__ = ""
__copyright__ = ""
__credits__ = []
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = ""

from PythonUtils.TestHelpers.test_common import make_exp_act_str, TestMsgHelper
from unittest import TestCase


class TestMakeExpActStr(TestCase):

    def test_make_exp_act_str(self):
        te = dict(passed=True, failed=False, run=True, skipped=False, raised=False)
        ta = dict(failed=True, run=True, raised=False, passed=False, skipped=False)

        tmp_act = make_exp_act_str(te, ta)

        tmp_exp = 'Expected: {"failed": false, "passed": true, "raised": false, "run": true, "skipped": false}\n' \
                  'Actual  : {"failed": true, "passed": false, "raised": false, "run": true, "skipped": false}'

        self.assertEqual(tmp_exp, tmp_act)

"""
class TestTestMsgHelper(TestCase):
    def test_init(self):
        msg = TestMsgHelper()
        
    def test_add(self):

    def test_sub(self):

    def test_radd(self):

    def test_rsub(self):
"""
