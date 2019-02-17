#!/usr/bin/env python

from unittest import TestCase
from PythonUtils.TestHelpers.test_mapping import TestDictLikeObject


class TestHashingTest(TestDictLikeObject):
    type2test = dict

    def check_for_skip(self, *args):

        for arg in args:
            if arg not in TestDictLikeObject.options_to_test:
                raise self.fail('invalid skip key set:  %s' % arg)

