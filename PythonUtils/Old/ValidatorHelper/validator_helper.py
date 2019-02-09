from collections import OrderedDict
from .validator_formatters import *


class ValidationException(Exception):
    pass


class InvalidValidatorError(ValidationException):
    pass


class DuplicateValidatorNameError(ValidationException):
    pass

FORMATTERS = dict(
    table=validator_format_table,
    list=validator_format_list,
    line=validator_format_line,
    lines=validator_format_lines)

class ValidateMessageHandler(object):

    TABLE = 'table'
    LIST = 'list'
    LINE = 'line'
    LINES = 'lines'

    def __init__(self, value, passed, fieldname='Field'):
        self._results = OrderedDict()
        self.fieldname = fieldname
        self.passed = passed
        self.failed = not passed
        self.value = value
        self.passed_validations = []
        self.failed_validations = []

    def add_message(self, validator, msg, passed, args, kwargs):
        self._results[validator] = dict(
            validator=validator,
            passed=passed,
            message=msg,
            args=args,
            kwargs=kwargs,
        )
        if passed:
            self.passed_validations.append(validator)
        else:
            self.failed_validations.append(validator)

    def get_results(self, passed=True, failed=True):
        for key, value in self._results.items():
            if value['failed'] and failed:
                yield value
            elif not value['failed'] and passed:
                yield value

    def message(self, fieldname=None, format_as=None, passed=True, failed=True):
        format_as = format_as or self.TABLE
        format_func = FORMATTERS[format_as]
        fieldname = fieldname or self.fieldname
        return format_func(
            value=self.value,
            results=self._results,
            pf=self.passed,
            failed=failed,
            passed=passed,
            fieldname=fieldname)

    def fail_messages(self, format_as=LIST):
        return self.message(format_as=format_as, passed=False)

    def pass_messages(self, format_as=LIST):
        return self.message(format_as=format_as, failed=False)

    def __iter__(self):
        for value in self._results.values():
            yield value

    def __getitem__(self, item):
        return self._results[item]

    def __bool__(self):
        return self.passed

    def __len__(self):
        return len(self._results)

    __call__ = message


class Validator(object):
    
    def __init__(self, *validators, fieldname=None):
        self._validators = []
        self._fieldname = fieldname or 'Field'
        self._validator_names = {}
        self._passed = []
        self._failed = []
        self._was_run = False
        self._pass_message_list = None
        self._fail_message_list = None
        self._last_pf = None
        self._msgs_helper = None

        self.add_validators(*validators)

    def add_validators(self, *validators):
        for validator in validators:
            if validator.name in self._validator_names:
                validator.name += str(len(self._validators)+2)
            self._validator_names[validator.name] = validator
            self._validators.append(validator.name)

    def _run_check(self):
        if not self._was_run:
            raise AttributeError('Validation has not been run yet')

    def get_passed(self):
        self._run_check()
        return self._passed

    def get_failed(self):
        self._run_check()
        return self._failed

    @property
    def msgs(self):
        self._run_check()
        if self._msgs_helper is None:
            self._msgs_helper = ValidateMessageHandler(
                value=self._value, fieldname=self._fieldname, passed=self._last_pf)
            for v in self:
                self._msgs_helper.add_message(**self[v].msg_dict())
        return self._msgs_helper

    def messages(self, passed=True, failed=True, fieldname=None, format_as='list'):
        self._fieldname = fieldname or self._fieldname
        return self.msgs(passed=passed, failed=failed, format_as=format_as)

    '''
    def messages(self, join=None, passed=True, failed=True, fieldname=None):
        self._fieldname = fieldname or self._fieldname
        self._run_check()
        tmp_ret = []
        if passed:
            if self._pass_message_list is None:
                self._pass_message_list = []
                for v in self._passed:
                    self._pass_message_list.append(self[v].message())
            tmp_ret.extend(self._pass_message_list)
        if failed:
            if self._fail_message_list is None:
                self._fail_message_list = []
                for v in self._failed:
                    self._fail_message_list.append(self[v].message())
            tmp_ret.extend(self._fail_message_list)
        if join is None:
            return tmp_ret
        else:
            return join.join(tmp_ret)
    '''
    def pass_messages(self, format_as='list'):
        return self.messages(failed=False, format_as=format_as)

    def fail_messages(self, format_as='list'):
        return self.messages(passed=False, format_as=format_as)

    def _clear(self):
        self._msgs_helper = None
        self._value = None
        # self._passed = []
        # self._failed = []
        # self._pass_message_list = None
        # self._fail_message_list = None

    def validate(self, value, validators=None, fieldname=None, stop_on_fail=False, **kwargs):
        self._clear()
        self._value = value
        self._fieldname = fieldname or self._fieldname
        self._was_run = True
        self._last_pf = True
        if validators is not None and isinstance(validators, str):
            validators = [validators]
        validators = validators or self
        for v in validators:
            tmp_args = []
            tmp_kwargs = {}
            if v in kwargs:
                tmp_ka = kwargs[v]
                if isinstance(tmp_ka, dict):
                    tmp_kwargs = tmp_ka
                elif isinstance(tmp_ka, (list, tuple)):
                    tmp_args = tmp_ka
                else:
                    tmp_args = [tmp_ka]
            if self[v](value, *tmp_args, fieldname=self._fieldname, **tmp_kwargs):
                self._passed.append(v)
            else:
                self._failed.append(v)
                self._last_pf = False
                if stop_on_fail:
                    break
        return self._last_pf

    __call__ = validate

    def __getitem__(self, item):
        try:
            return self._validator_names[item]
        except KeyError:
            raise InvalidValidatorError

    def __contains__(self, item):
        return item in self._validator_names

    def __len__(self):
        return len(self._validators)

    def __iter__(self):
        for v in self._validators:
            yield v
