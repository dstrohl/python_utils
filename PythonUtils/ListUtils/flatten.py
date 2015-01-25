__author__ = 'dstrohl'


def flatten(l, ltypes=(list, tuple)):
    """
    Will flatten lists and tuples to a single level

    from: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html

    :param l: list or tuple to be flattened
    :param ltypes: the types of items allowed to be flattened, default = (list, tuple)
    :return: single level list or tuple (same as what went in)
    """
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

def unpack_class_method(class_object_list, method, ret_type=str, *args, **kwargs):
    """
    This will iterate through a list of objects and pull a value from each one, even if the items are functions.

    :param class_object_list: A list of objects
    :param method: the method to pull from (string)
    :param return_type: what type of data is expected to be returned. this should be a function/class that will convert to the type desired.
        for example, the default is str, but int, float are also options.
    :param args: if the method is a function, what arguments to pass
    :param kwargs: if the method is a function, what keyword arguments to pass.
    :return:
    """
    tmpretset = []
    class_object_list = flatten(class_object_list)
    for obj in class_object_list:
        func = getattr(obj, method, None)
        if callable(func):
            tmpret = ret_type(func(*args, **kwargs))
        else:
            tmpret = ret_type(func)
        tmpretset.append(tmpret)
    return tmpretset

