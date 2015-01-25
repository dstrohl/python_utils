__author__ = 'dstrohl'


class DictKey2Method(object):

    def __init__(self, mydict):
        self.mydict = mydict

    def __getattr__(self, item):
        try:
            return self.mydict[item]
        except KeyError:
            raise KeyError(item, ' is not a valid key for this dictionary')

    def __setattr__(self, key, value):
        if key in ('mydict',):
            self.__dict__[key] = value
        else:
            self.mydict[key] = value


class AdvDict(dict):
    """
    A dictionary that allows you to access contents as if they were methods.

    :param property_name: The name of the property to use to access the fields.
        Default = 'key'

    Example:

    >>> d = AdvDict()
    >>> d['one'] = 1
    >>> d['two'] = 2
    >>> d['three'] = 3
    >>> d.key.one
    1

    >>> d = AdvDict(property_name='number')
    >>> d['one'] = 1
    >>> d['two'] = 2
    >>> d['three'] = 3
    >>> d.number.two
    2
    """
    def __init__(self, *args, **kwargs):
        property_name = kwargs.pop('property_name', 'key')
        super(AdvDict, self).__init__(*args, **kwargs)
        setattr(self, property_name, DictKey2Method(self))
