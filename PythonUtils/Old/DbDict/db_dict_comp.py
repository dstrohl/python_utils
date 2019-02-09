__author__ = 'strohl'


class BaseComparator(object):
    comparison_flag = ''

    @staticmethod
    def compare(field, comparison):
        return True


class CompEQ(object):
    comparison_flag = 'eq'

    @staticmethod
    def compare(field, comparison):
        if field == comparison:
            return True
        else:
            return False


class CompIN(object):
    comparison_flag = 'in'

    @staticmethod
    def compare(field, comparison):
        if field in comparison:
            return True
        else:
            return False


class CompNOT(object):
    comparison_flag = 'not'

    @staticmethod
    def compare(field, comparison):
        if field != comparison:
            return True
        else:
            return False


class CompNIN(object):
    comparison_flag = 'nin'

    @staticmethod
    def compare(field, comparison):
        if field not in comparison:
            return True
        else:
            return False


class CompStarts(object):
    comparison_flag = 'starts'

    @staticmethod
    def compare(field, comparison):
        tmp_str = str(field)
        if tmp_str.startswith(comparison):
            return True
        else:
            return False


class CompEnds(object):
    comparison_flag = 'ends'

    @staticmethod
    def compare(field, comparison):
        tmp_str = str(field)
        if tmp_str.endswith(comparison):
            return True
        else:
            return False


# CASE INSENSITIVE COMPARATORS

def _fixcase(field, comparison):
    try:
        f = str(field).lower()
        c = str(comparison).lower()
    except TypeError:
        f = field
        c = comparison
    return f, c


class CompEQ_I(object):
    comparison_flag = 'i_eq'

    @staticmethod
    def compare(field, comparison):
        field, comparison = _fixcase(field, comparison)
        if field == comparison:
            return True
        else:
            return False


class CompIN_I(object):
    comparison_flag = 'i_in'

    @staticmethod
    def compare(field, comparison):
        field, comparison = _fixcase(field, comparison)
        if field in comparison:
            return True
        else:
            return False


class CompNOT_I(object):
    comparison_flag = 'i_not'

    @staticmethod
    def compare(field, comparison):
        field, comparison = _fixcase(field, comparison)
        if field != comparison:
            return True
        else:
            return False


class CompNIN_I(object):
    comparison_flag = 'i_nin'

    @staticmethod
    def compare(field, comparison):
        field, comparison = _fixcase(field, comparison)
        if field not in comparison:
            return True
        else:
            return False


class CompStarts_I(object):
    comparison_flag = 'i_starts'

    @staticmethod
    def compare(field, comparison):
        field, comparison = _fixcase(field, comparison)
        tmp_str = str(field)
        if tmp_str.startswith(comparison):
            return True
        else:
            return False


class CompEnds_I(object):
    comparison_flag = 'i_ends'

    @staticmethod
    def compare(field, comparison):
        field, comparison = _fixcase(field, comparison)
        tmp_str = str(field)
        if tmp_str.endswith(comparison):
            return True
        else:
            return False


default_comparators = (
    BaseComparator,
    CompEQ,
    CompIN,
    CompNOT,
    CompNIN,
    CompStarts,
    CompEnds,
    CompEQ_I,
    CompIN_I,
    CompNOT_I,
    CompNIN_I,
    CompStarts_I,
    CompEnds_I,
)
