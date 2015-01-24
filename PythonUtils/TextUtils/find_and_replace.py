__author__ = 'strohl'



def replace_between(instring, start_key, end_key, replace, keep_keys=False, offset_count=1, count=9999):
    """
    :param instring: The string to search
    :param start_key: The starting boundary key
    :param end_key: The ending boundary key
    :param replace: The string to replace the text between the boundary keys.
    :param keep_keys: True/False: include the key strings in the replacement
    :param count: replace up to this many instances
    :param offset_count: start replacing after this many instances
    :return: String
    """
    instring = str(instring)

    if start_key not in instring:
        return instring

    start_pos = 0
    curs_pos = 0
    found = 0
    start_key_len = len(start_key)
    end_key_len = len(end_key)
    outstring = ''

    start_pos = index_of_count(instring, find=start_key, offset_count=offset_count, start=0)

    while True:

        if count <= found or start_pos == -1:
            break

        end_pos = instring.find(end_key, start_pos+start_key_len)

        if end_pos == -1:
            break

        if keep_keys:
            suffix = instring[end_pos:end_pos+end_key_len]
            outstring = outstring + instring[curs_pos:start_pos+start_key_len] + replace + suffix
            curs_pos = end_pos+end_key_len

        else:
            outstring = outstring + instring[curs_pos:start_pos] + replace
            curs_pos = end_pos+end_key_len

        found = found+1

        start_pos = instring.find(start_key, curs_pos)

    return outstring+instring[curs_pos:]

def index_of_count(instring, find, offset_count=1, start=0):
    if instring:
        offset_loc = start
        current_off = 0
        for i in range(offset_count):
            offset_loc = instring.find(find, current_off)
            if offset_loc > -1:
                if i == offset_count-1:
                    return offset_loc
                current_off = offset_loc+1
            else:
                return current_off
        return offset_loc
    return -1


def get_before(instring, find, offset_count=1):
    offset_loc = index_of_count(instring, find, offset_count)

    if offset_loc != -1:
        return instring[:offset_loc]
    return instring


def get_after(instring, find, offset_count=1):
    offset_len = len(find)
    offset_loc = index_of_count(instring, find, offset_count)

    if offset_loc != -1:
        return_size = offset_loc+offset_len
        return instring[return_size:]
    return instring


def get_between(instring, start_key, end_key):
    return get_after(get_before(instring, end_key), start_key)