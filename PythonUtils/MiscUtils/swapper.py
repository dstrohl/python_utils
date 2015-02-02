__author__ = 'dstrohl'


def swap(item, opt1=True, opt2=False):
    if item == opt1:
        return opt2
    elif item == opt2:
        return opt1
    else:
        raise AttributeError(str(item)+' not in available options')
