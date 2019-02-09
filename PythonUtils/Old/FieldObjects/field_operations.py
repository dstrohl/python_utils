from .field_exceptions import *

__all__ = ['raise_on_read_only', 'default_to_unset', 'unset_to_default', 'validate_from_user', 'convert_from_db',
           'convert_from_user', 'convert_to_db', 'convert_to_user', 'none_to_empty']


def raise_on_read_only(value, field_rec, **kwargs):
    raise FieldReadOnlyException(field_rec._fieldname)


def default_to_unset(value, field_rec, **kwargs):
    if value == field_rec._default:
        return field_rec._empty_value
    else:
        return value


def unset_to_default(value, field_rec, **kwargs):
    if value == field_rec._empty_value:
        return field_rec._default
    else:
        return value


def validate_from_user(value, field_rec, **kwargs):
    if field_rec._validator(value):
        return value
    else:
        raise FieldValidationException(field_rec._fieldname, field_rec._validator.msgs)


def convert_to_user(value, field_rec, **kwargs):
    to = kwargs.get('system', field_rec._user_system)
    value = field_rec._converter(value, fr=field_rec._local_format, to=to)
    return value


def convert_to_db(value, field_rec, **kwargs):
    to = kwargs.get('system', field_rec._db_system)
    value = field_rec._converter(value, fr=field_rec._local_format, to=to)
    return value


def convert_from_user(value, field_rec, **kwargs):
    fr = kwargs.get('system', field_rec._user_system)
    value = field_rec._converter(value, to=field_rec._local_format, fr=fr)
    return value


def convert_from_db(value, field_rec, **kwargs):
    fr = kwargs.get('system', field_rec._db_system)
    return field_rec._converter(value, to=field_rec._local_format, fr=fr)


def none_to_empty(value, field_rec, **kwargs):
    if value is None:
        return field_rec._empty_value
    return value
