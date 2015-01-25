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

    def __init__(self, *args, **kwargs):
        super(AdvDict,self).__init__(*args, **kwargs)
        self.k = DictKey2Method(self)


