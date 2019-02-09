
#!/usr/bin/env python


from unittest import TestCase
from PythonUtils.BaseUtils import _UNSET


class TestUnset(TestCase):
    def test_unset(self):
        t = _UNSET

        self.assertEqual(_UNSET, t)
        self.assertFalse(bool(t))
        self.assertIs(t, _UNSET)

