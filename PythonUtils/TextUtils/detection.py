__author__ = 'strohl'

def is_string(in_obj):
    return isinstance(in_obj, str )

def make_list(in_obj):
    if is_string(in_obj):
        return [in_obj]
    else:
        return in_obj
