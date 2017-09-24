


def tags(tag_name):
    def tags_decorator(func):
        def func_wrapper(name):
            return "<{0}>{1}</{0}>".format(tag_name, func(name))
        return func_wrapper
    return tags_decorator


@tags("p")
def get_text(name):
    return "Hello "+name


def p_decorate(func):
   def func_wrapper(*args, **kwargs):
       return "<p>{0}</p>".format(func(*args, **kwargs))
   return func_wrapper

class Person(object):
    def __init__(self):
        self.name = "John"
        self.family = "Doe"

    @p_decorate
    def get_fullname(self):
        return self.name+" "+self.family

my_person = Person()

# print(my_person.get_fullname())


def run_init(init_str='test'):
    print(init_str)

    def parse_decorator(func):
        print('pre_run_init - %s' % init_str)
        func._init(func)
        return func
    return parse_decorator


@run_init('blah')
class TestClass(object):

    def _init(self):
        print('inside init')

# print(get_text("John"))

tc = TestClass()
tc._init()