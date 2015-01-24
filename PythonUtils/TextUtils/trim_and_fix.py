__author__ = 'strohl'


def elipse_trim(instr, trim_length, elipse_string='...'):
    instr = str(instr)
    str_len = trim_length-len(elipse_string)
    if len(instr) > trim_length:
        return '{}{}'.format(instr[:str_len], elipse_string)
    else:
        return instr