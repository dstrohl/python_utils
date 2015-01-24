__author__ = 'dstrohl'




# ===============================================================================
# Utility counts unique values in a list or dict
#===============================================================================

def count_unique(data_in, dict_key=None):
    """
    :param data_in: list or tuple of items to be counted
    :param dict_key: if data_in is a list of dict's, this is the key for which item to compare
    :return: integer
    """

    tmp_list = []

    if not isinstance(data_in, (list, tuple)):
        raise AttributeError('count_unique: not a list, or tuple')

    tmp_item = data_in[0]
    if dict_key:

        if not isinstance(tmp_item, dict):
            raise AttributeError('count_unique: dict key passed but no dict found')

        for item in data_in:
            tmp_list.append(item[dict_key])

    else:
        tmp_list = data_in

    tmp_count = len(set(tmp_list))

    return tmp_count

