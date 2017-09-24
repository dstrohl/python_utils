from unittest import TestCase

"""
class MetaBaseParser(type):

    def __new__(cls, name, bases, dct):
        tmp_ret = type.__new__(cls, name, bases, dct)

        def _update_obj(field_name):

            if hasattr(tmp_ret, field_name):
                _counter = 0
                while True:
                    tmp_name = '%s__%s' % (field_name, _counter)
                    if not hasattr(tmp_ret, tmp_name):
                        setattr(tmp_ret, tmp_name, getattr(tmp_ret, field_name))
                        delattr(tmp_ret, field_name)
                        break
                    _counter += 1
                    if _counter > 100:
                        break

        if hasattr(tmp_ret, '_meta_keys'):
            for key in tmp_ret._meta_keys:
                _update_obj(key)
        return tmp_ret


class TestWithMeta(metaclass=MetaBaseParser):
    _meta_keys = ['test_attr_1', 'test_attr_2', 'test_attr_3']
    test_attr_1 = ['t1']
    test_attr_2 = ['t2']
    test_attr_3 = ['t3']

    def __init__(self):
        self._cleanup()

    def _cleanup(self):
        if hasattr(self, '_meta_keys'):
            for field in self._meta_keys:
                tmp_data = None
                is_dict = False
                counter = 0
                while True:
                    tmp_name = '%s__%s' % (field, counter)
                    counter += 1
                    if not hasattr(self, tmp_name):
                        break

                    tmp_field = getattr(self, tmp_name)
                    if tmp_data is None:
                        if isinstance(tmp_field, dict):
                            tmp_data = {}
                            is_dict = True
                        else:
                            tmp_data = []
                            is_dict = False
                    if is_dict:
                        tmp_data.update(tmp_field)
                    else:
                        tmp_data.extend(tmp_field)
                setattr(self, field, tmp_data)
"""

class MetaBaseParser(type):
    def __init__(self, o: object):
        super().__init__(o)


class TestWithMeta(metaclass=MetaBaseParser):
    _meta_keys = ['test_attr_1', 'test_attr_2', 'test_attr_3']
    test_attr_1 = ['t1']
    test_attr_2 = ['t2']
    test_attr_3 = ['t3']



class TestSubMeta(TestWithMeta):
    test_attr_2 = ['s2']
    test_attr_3 = ['s3']


class TestSubSubMeta(TestSubMeta):
    test_attr_2 = ['u2']
    test_attr_3 = ['u3']

class TestSubMeta2(TestWithMeta):
    test_attr_2 = ['v2']
    test_attr_3 = ['v3']

print('\nt1\n')
t1 = TestSubSubMeta()
print(dir(t1))
print('\nt2\n')
t2 = TestSubMeta2()
print('\nt3\n')
t3 = TestWithMeta()


"""

class TestConfigObject(TestCase):
    def test_init_empty(self):
        tsm = TestSubMeta()
        self.assertEqual(tsm.c['test_attr_1'], 't1')
        self.assertEqual(tsm.c['test_attr_2'], 's2')
        self.assertEqual(tsm.c['test_attr_3'], 's3')

    def test_change_change(self):
        tsm = TestSubMeta(test_attr_2='w2')
        self.assertEqual(tsm.c['test_attr_1'], 't1')
        self.assertEqual(tsm.c['test_attr_2'], 'w2')
        self.assertEqual(tsm.c['test_attr_3'], 's3')


    def test_make_sure_different(self):
        tsm = TestSubMeta(test_attr_1='k1')
        self.assertEqual(tsm.c['test_attr_1'], 'k1')
        self.assertEqual(tsm.c['test_attr_2'], 's2')
        self.assertEqual(tsm.c['test_attr_3'], 's3')

        tsm2 = TestSubMeta(test_attr_1='j1')
        self.assertEqual(tsm2.c['test_attr_1'], 'j1')
        self.assertEqual(tsm2.c['test_attr_2'], 's2')
        self.assertEqual(tsm2.c['test_attr_3'], 's3')

        self.assertEqual(tsm.c['test_attr_1'], 'k1')
        self.assertEqual(tsm.c['test_attr_2'], 's2')
        self.assertEqual(tsm.c['test_attr_3'], 's3')


    def test_init2(self):
        tsm = TestSubSubMeta()
        self.assertEqual(tsm._get_attr_2_list(), ['t1', 's2', 'u2'])
        # self.assertEqual(tsm.c['test_attr_1'], 't1')
        # self.assertEqual(tsm.c['test_attr_2'], 's2')
        # self.assertEqual(tsm.c['test_attr_3'], 's3')

"""