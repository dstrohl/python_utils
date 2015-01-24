__author__ = 'strohl'

def get_same(l1, l2):
    tmp_list = []
    for li in l1:
        if li in l2:
            tmp_list.append(li)
    return tmp_list

def get_not_in(check_for, check_in):
    tmp_list = []
    for li in check_for:
        if li not in check_in:
            tmp_list.append(li)
    return tmp_list

def get_different(l1, l2):
    tmp_set = set()
    for li in l1:
        if li in l2:
            tmp_set.append(li)

    for li in l2:
        if li in l1:
            tmp_set.append(li)
    return list(tmp_set)

def remove_dupes(l1):
    return list(set(l1))