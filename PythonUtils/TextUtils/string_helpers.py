__author__ = 'strohl'

from collections import UserDict

# Below from: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
def flatten(l, ltypes=( list, tuple ), force_string_to_list = True):
    if isinstance(l,str) and force_string_to_list:
        l = [l,]
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




def slugifySentence(strIn, KeepWords=False):
    strIn = str(strIn)
    tmpString = u""
    tmpArray = []
    if KeepWords:
        tmpArray = strIn.split()
        for wrd in tmpArray:
            tmpString = tmpString + " " + slugify(str(wrd))
    else:
        tmpString = slugify(strIn)

    return tmpString.strip()


def concatStr(*args, **kwargs):
    tmpString = ""

    sep = kwargs.get("sep", " ")
    slugify = kwargs.get("slugify", False)
    slugifyWords = kwargs.get("slugifyWords", False)


    # numArgs = len(*args)
    # rangen = range(len(*args))
    for arg in args:
        if isinstance(arg, str):
            tmpString = tmpString + sep + str(arg)
            tmpString = tmpString.strip()

        else:
            try:
                for x in range(len(arg)):
                    tmpString = tmpString + sep + str(arg[x])
                    tmpString = tmpString.strip()

            except TypeError:
                tmpString = str(arg)

    if slugify or slugifyWords:
        tmpString = slugifySentence(tmpString, slugifyWords)

    return tmpString
