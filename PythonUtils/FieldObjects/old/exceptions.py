__all__ = ['FieldDoesNotExistException', 'FieldValidationException', 'AddFieldDisallowedException',
           'UnknownFieldException', 'CI_BaseException', 'UnknownDataTypeException', 'MaxListLenException',
           'FieldReadOnlyException']

from PythonUtils import make_list


class CI_BaseException(Exception):

    def __init__(self, msg=None):
        self.msg = msg or "CI Error"

    def __str__(self):
        return self.msg


class FieldValidationException(CI_BaseException):
    def __init__(self, fieldname, failed_steps=None, value=None, full_msg=None):
        self.fieldname = fieldname
        if failed_steps is None:
            self.failed_steps = [_('Unknown')]
        else:
            self.failed_steps = make_list(failed_steps)
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            if value is not None:
                try:
                    value = ' [%s]' % value
                except:
                    value = ' [%r]' % value
            else:
                value = ''
            if len(self.failed_steps) == 1:
                msg = _('Field failed validation step: ')+self.failed_steps[0]
            else:
                msg = _('Field failed multiple validations: %r') % self.failed_steps
            tmp_msg = _('%s field validation error%s: %s') % (fieldname, value, msg)
        self.msg = tmp_msg


class FieldReadOnlyException(FieldValidationException):
    def __init__(self, fieldname, failed_steps=None, value=None, full_msg=None):
        full_msg = _('Attempt to write to a read only record')
        failed_steps = [_('Read only record')]

        super().__init__(fieldname=fieldname, value=value, failed_steps=failed_steps, full_msg=full_msg)


class FieldDoesNotExistException(CI_BaseException):
    def __init__(self, fieldname, full_msg=None):
        self.fieldname = fieldname
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            tmp_msg = _('%s field does not exist') % fieldname
        self.msg = tmp_msg


class AddFieldDisallowedException(CI_BaseException):
    def __init__(self, fieldname, full_msg=None):
        self.fieldname = fieldname
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            tmp_msg = _('record locked, field %s not added') % fieldname
        self.msg = tmp_msg


class UnknownFieldException(CI_BaseException):
    def __init__(self, fieldname, full_msg=None):
        self.fieldname = fieldname
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            tmp_msg = _('field %s is not in this record') % fieldname
        self.msg = tmp_msg


class UnknownDataTypeException(CI_BaseException):
    def __init__(self, value, full_msg=None):
        self.value = value
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            tmp_msg = _('value %r datatype cannot be determined or there is no registered field type') % value
        self.msg = tmp_msg


class MaxListLenException(CI_BaseException):
    def __init__(self, max_len, full_msg=None):
        self.max_len = max_len
        if full_msg is not None:
            tmp_msg = full_msg
        else:
            tmp_msg = _('The list has reached the max length of %s allowed') % max_len
        self.msg = tmp_msg
