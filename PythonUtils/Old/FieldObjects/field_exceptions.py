__all__ = ['FieldDoesNotExistException', 'FieldValidationException', 'AddFieldDisallowedException',
           'UnknownFieldException', 'FieldBaseException', 'UnknownDataTypeException', 'MaxListLenException',
           'FieldReadOnlyException', 'UncomparableFieldsException']

from PythonUtils import make_list
from .field_messages import *


class FieldBaseException(Exception):

    def __init__(self, msg=None):
        self.msg = msg or "Field Error"

    def __str__(self):
        return self.msg


# Processing Exceptions


# Validation Exceptions
class FieldValidationException(FieldBaseException):
    def __init__(self, fieldname, message_helper=None, full_msg=None):
        self.fieldname = fieldname
        if full_msg is not None:
            self.msg = full_msg
        else:
            if message_helper is None:
                self.msg = 'Unknown Validation Error'
            else:
                self.msg = message_helper.message(format_as=message_helper.TABLE)


class FieldReadOnlyException(FieldValidationException):
    def __init__(self, fieldname, full_msg=None, **kwargs):
        full_msg = attempt_to_write_to_a_read_only_record
        failed_steps = [read_only_record]

        super().__init__(fieldname=fieldname, full_msg=full_msg)


class FieldDoesNotExistException(FieldBaseException):
    def __init__(self, fieldname, full_msg=None):
        self.fieldname = fieldname
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            tmp_msg = field_does_not_exist % fieldname
        self.msg = tmp_msg


class AddFieldDisallowedException(FieldBaseException):
    def __init__(self, fieldname, full_msg=None):
        self.fieldname = fieldname
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            tmp_msg = record_locked_field_not_added % fieldname
        self.msg = tmp_msg


class UnknownFieldException(FieldBaseException):
    def __init__(self, fieldname, full_msg=None):
        self.fieldname = fieldname
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            tmp_msg = field_is_not_in_this_record % fieldname
        self.msg = tmp_msg


class UnknownDataTypeException(FieldBaseException):
    def __init__(self, value, full_msg=None):
        self.value = value
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            tmp_msg = value_datatype_cannot_be_determined % value
        self.msg = tmp_msg


class MaxListLenException(FieldBaseException):
    def __init__(self, max_len, full_msg=None):
        self.max_len = max_len
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            tmp_msg = the_list_has_reached_the_max_length_of_allowed % max_len
        self.msg = tmp_msg


class UncomparableFieldsException(FieldBaseException):
    def __init__(self, full_msg=None):
        pass
