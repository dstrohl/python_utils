from decimal import Decimal
from ast import literal_eval
from .converters import *

"""
Base formats supported:
int
float
str
dict
list
Decimal
bool
complex
date
time
datetime
datetime_tz
"""

DEFAULT_CONVERTERS = [
    {
        'to': 'int',
        'converters': {
            'fr': ['str', 'decimal', 'float'], 'func': int}},
    {
        'to': 'float',
        'converters': {
            'fr': ['int', 'str', 'decimal', 'float'], 'func': float}},
    {
        'to': 'str',
        'converters': [
            {'fr': ['int', 'decimal', 'float', 'list', 'dict', 'bool', 'complex'], 'func': str},
            {'fr': 'yesno', 'func': None},
            {'fr': 'time', 'func': time_to_str},
            {'fr': 'date', 'func': date_to_str},
            {'fr': 'datetime', 'func': datetime_to_str},
            {'fr': 'datetime_tz', 'func': datetime_tz_to_str}]},
    {
        'to': 'dict',
        'converters': {
            'fr': 'str', 'func': literal_eval}},
    {
        'to': 'list',
        'converters': {
            'fr': ['str', 'decimal', 'float'], 'func': literal_eval}},
    {
        'to': 'decimal',
        'converters': {
            'fr': ['str', 'float', 'int'], 'func': Decimal},
        'detect': 'Decimal'},
    {
        'to': 'bool',
        'converters': [
            {'fr': ['decimal', 'float', 'int', 'complex'], 'func': bool},
            {'fr': 'str', 'func': str_to_bool},
            {'fr': ['yesno'], 'func': str_to_bool}]},
    {
        'to': 'complex',
        'converters': {
            'fr': ['str', 'decimal', 'float', 'int'], 'func': complex}},
    {
        'to': 'time',
        'converters': {
            'fr': 'str', 'func': str_to_time}},
    {
        'to': 'date',
        'converters': {
            'fr': 'str', 'func': str_to_date}},
    {
        'to': 'datetime',
        'converters': {
            'fr': 'str', 'func': str_to_datetime}},
    {
        'to': 'datetime_tz',
        'converters': {
            'fr': 'str', 'func': str_to_datetime_tz},
        'detect': is_datetime_tz,
        'detect_pri': 10},
    {
        'to': 'yesno',
        'converters': [
            {'fr': 'str', 'func': None},
            {'fr': 'bool', 'func': bool_to_yn}],
        'detect': is_yn,
        'detect_pri': 10},
    ]

DEFAULT_SYSTEMS = [
        {'name': 'sys_dict', 'default': 'passthrough'},
        {'name': 'sys_str', 'default': 'str'}]


class NoConverterError(Exception):
    pass


class ConversionError(Exception):
    pass


class DuplicateTermError(Exception):
    pass


class UnableToDetectTypeError(Exception):
    pass


class ConverterHelper(object):

    """
    internal structures:

    _converters = {
        <to_type>: {
            '<from_tyoe>': {
                'func': <conversion_function>,
                'exception': <conversion exception to catch>}}}
    }

    _detectors = [
        (<type_name>, <detector func or class name>, pri),
        ...
    ]

    _systems = {
        '<name>': {
            'default': 'default type_name' or None,
            'mappings': {
                    '<local_type_name>': '<system_type_name>',
                    ...}
        }
    }

    """
    _local_system = None
    _local_format = None

    def __init__(self, converters=None, systems=None, local_format=None):
        self._converters = {}
        self._systems = {}
        self._detectors = []

        self.add_converters(*DEFAULT_CONVERTERS)
        if converters is not None:
            self.add_converters(*converters)

        self.add_systems(*DEFAULT_SYSTEMS)
        if systems is not None:
            self.add_systems(*systems)

        self.set_local_format(local_format)

    def add_systems(self, *systems, clear=False):
        for syst in systems:

            mappings = syst.get('mappings', {})
            name = syst.get('name')

            if name in self._converters:
                raise DuplicateTermError('%s is already used as a type' % name)

            default = syst.get('default')

            if clear:
                self._systems[name] = {
                    'default': default,
                    'mappings': {}}
                sys_rec = self._systems[name]
            else:
                try:
                    sys_rec = self._systems[name]
                except KeyError:
                    self._systems[name] = {
                        'default': default,
                        'mappings': {}}
                    sys_rec = self._systems[name]
                else:
                    if default is not None:
                        sys_rec['default'] = default

            for sys_type, local_list in mappings.items():
                if sys_type not in self._converters:
                    raise NoConverterError('converter %s defined in the system %s does not exist' % (sys_type, name))
                if not isinstance(local_list, (list, tuple)):
                    local_list = [local_list]
                for local_type in local_list:
                    if local_type not in self._converters:
                        print(local_type)
                        raise NoConverterError('converter %s defined in the system %s does not exist' % (local_type, name))
                    sys_rec['mappings'][local_type] = sys_type

    def add_converters(self, *converters):
        for conv in converters:
            tmp_conv_list = conv.pop('converters', [])
            if not isinstance(tmp_conv_list, (list, tuple)):
                tmp_conv_list = [tmp_conv_list]
            to = conv.pop('to')

            if to in self._systems:
                raise DuplicateTermError('%s is already used as a system' % to)

            if to not in self._converters:
                self._converters[to] = {
                    'converters': {},
                    'detect': to,
                    'detect_pri': 100}
            to_rec = self._converters[to]
            to_rec.update(conv)
            for c in tmp_conv_list:
                fr_list = c.get('fr', [])
                if not isinstance(fr_list, (list, tuple)):
                    fr_list = [fr_list]
                func = c.get('func')
                exception = c.get('exception', ValueError)
                for fr in fr_list:
                    to_rec['converters'][fr] = {
                        'func': func,
                        'exception': exception}

        self._detectors.clear()
        for key, item in self._converters.items():
            self._detectors.append((key, item['detect'], item['detect_pri']))
        self._detectors.sort(key=lambda func: func[2])

    def set_local_format(self, local_format):
        self._local_format = local_format

    def _conv(self, value, to, fr):
        if to == fr:
            return value
        try:
            converter = self._converters[to]['converters'][fr]['func']
            exception = self._converters[to]['converters'][fr]['exception']
        except KeyError as err:
            if str(err) == to:
                raise NoConverterError('unable to convert to type: %s' % to)
            else:
                raise NoConverterError('unable to convert from type: %s' % fr)
        if converter is None:
            return value
        try:
            return converter(value)
        except Exception:
            raise ConversionError('error converting %s from %s to %s' % (value, fr, to))

    def _convert(self, value, to=None, fr=None, via=None, local_format=None):
        if to == fr and via is None:
            return value

        if local_format is not None:
            self.set_local_format(local_format)

        if to is None:
            if self._local_format is None:
                raise AttributeError('local format must be set in order to use system')

            to = self._local_format
            try:
                fr = self._systems[fr]['mappings'][to]
            except KeyError as err:
                if str(err) == fr:
                    raise NoConverterError('%s system not defined' % fr)
                tmp_type = self._systems[fr]['default']
                if tmp_type is None:
                    raise NoConverterError('no converter configured for local type %s in system %s' % (to, fr))
                if tmp_type == 'passthrough':
                    return value
                fr = tmp_type

        elif fr is None:
            if self._local_format is None:
                raise AttributeError('local format must be set in order to use system')

            fr = self._local_format
            try:
                to = self._systems[to]['mappings'][fr]
            except KeyError as err:
                if str(err) == to:
                    raise NoConverterError('%s system not defined' % to)
                tmp_type = self._systems[to]['default']
                if tmp_type is None:
                    raise NoConverterError('no converter configured for local type %s in system %s' % (fr, to))
                if tmp_type == 'passthrough':
                    return value
                to = tmp_type

        elif fr == 'auto':
            for det in self._detectors:
                if isinstance(det[1], str):
                    if value.__class__.__name__ == det[1]:
                        fr = det[0]
                        break
                else:
                    if det[1](value):
                        fr = det[0]
                        break
            if fr == 'auto':
                raise UnableToDetectTypeError('unable to detect the type of object for: %r' % value)

        elif via is not None:
            tmp_val = self._conv(value, to=via, fr=fr)
            return self._conv(tmp_val, to=to, fr=via)

        print('converting "%r" from: %s to %s' % (value, fr, to))
        return self._conv(value, to=to, fr=fr)

    __call__ = _convert

