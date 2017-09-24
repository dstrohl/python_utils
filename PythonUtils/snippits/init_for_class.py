
class MetaTest(type):
    def __new__(cls, name, bases, dct):
        tmp_ret = type.__new__(cls, name, bases, dct)
        tmp_ret._init(tmp_ret)
        return tmp_ret


class TestClassInit(metaclass=MetaTest):
    test_var_1 = 't1.1'
    test_var_2 = 't1.2'
    __test_var_4 = 'goodby'

    def _init(cls, t=''):
        print('within_init', t)
        cls.test_var_1 = [cls.test_var_1]
        cls.test_var_2 = [cls.test_var_2]

    # _init()
    def __foo(self):
        pass

    print(repr(test_var_2))

class T2(TestClassInit):
    test_var_1 = 't2.1'

    def _init(cls):
        print('within init_t2')
        cls.test_var_1 = 'foobar.' + cls.test_var_1
        TestClassInit._init(cls)

    def __foo(self):
        pass



class T3(TestClassInit):
    test_var_1 = 't3.1'

    def __foo(self):
        pass

class T4(T2):
    test_var_1 = 't4.1'
    __test_var_4 = 'helo'

    def __foo(self):
        pass


class T5(object):
    def __new__(cls, *args, **kwargs):
        print('new for T5')

print(repr(TestClassInit.test_var_1))
print(repr(T2.test_var_1))
print(repr(T3.test_var_1))
print(repr(T4.test_var_1))

print(dir(TestClassInit))
print(dir(T4))
