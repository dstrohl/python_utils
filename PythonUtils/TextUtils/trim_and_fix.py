__author__ = 'strohl'



def is_string(in_obj):
    return isinstance(in_obj, str )


def elipse_trim(instr, trim_length, elipse_string='...'):
    """
    Makes sure strings are less than a specified length, and adds an elipse if it needed to trim them.

    :param instr: The String to trim
    :param trim_length: The max length, INCLUDING the elipse
    :param elipse_string: the string used for the elipse.  Default: '...'
    :return: Trimmed string
    """
    instr = str(instr)
    str_len = trim_length-len(elipse_string)
    if len(instr) > trim_length:
        return '{}{}'.format(instr[:str_len], elipse_string)
    else:
        return instr

def concat(*args, separator=' ', trim_items=True):
    """
    Concatenates strings or lists of strings

    :param args: strings or lists / sets of strings
    :param separator: the string that will be used between strings.  Default: ' '
    :param trim: True/False, trim strings before concatenating.
    :return: string created from contents passed
    """
    tmp_str = ""



    for arg in args:
        if is_string(arg):
            if trim_items:
                arg = arg.strip()
            tmp_str = tmp_str + separator + str(arg)
            tmp_str = tmp_str.strip()
        else:
            try:
                for x in range(len(arg)):
                    tmp_str = tmp_str + separator + str(arg[x])
                    tmp_str = tmp_str.strip()

            except TypeError:
                tmp_str = str(arg)

    return tmp_str
