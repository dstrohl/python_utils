__author__ = 'dstrohl'


# Below from: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
def flatten(l, ltypes=( list, tuple )):
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



def unpackClassMethod(ClassObjectList, method, *args, **kwargs):
    tmpRetSet = []
    ClassObjectList = flatten(ClassObjectList)
    for obj in ClassObjectList:
        func = getattr(obj, method, None)
        if callable(func):
            tmpRet = str(func(*args, **kwargs))
        else:
            tmpRet = str(func)
        tmpRetSet.append(tmpRet)
    return tmpRetSet

