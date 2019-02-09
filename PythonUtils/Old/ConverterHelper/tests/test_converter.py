from unittest import TestCase
from PythonUtils.Old.ConverterHelper import ConverterHelper, NoConverterError, ConversionError, \
    DuplicateTermError, UnableToDetectTypeError
from PythonUtils import UnSet
from decimal import Decimal
from datetime import datetime, time, date, timezone, timedelta

_UNSET = UnSet()

'''

converters_def = [
    {'to': 'int',
     'fr': ['str', 'dec', 'custom1'],
     'func': int},
    {'to': 'str',
     'fr': ['str', 'dec', 'custom1'],
     'func': str},
    {'to': 'custom1',
     'fr': ['str', 'int', 'decimal'],
     'func': custom_fr_function},
    {'to': 'str',
     'fr': ['custom1'],
     'func': custom_to_func}
]
config = [
    {'name': 'ini', 'default': 'str', 'mappings': {
        'str': ['int', 'float', 'decimal', 'date']
    }},
    {'name': 'mongo', 'default': 'passthrough'}
]
'''
'''
ConverterHelper.add_converter(to='int', fr=['str', 'float', 'decimal'], func=int, datatype=int)
ConverterHelper.add_system(system='ini', sys_format='str', local_format=['int', 'float', 'dec', 'date'])
ConverterHelper.add_system(system='mongo', passthrough=['str', 'int', 'float'])
ConverterHelper.add_system(system='mongo', sys_format='str', local_format='custom1')
'''

# ch = ConverterHelper()


def dt2_to_str(dt):
    return dt.strftime('%m/%d/%Y')


def str_to_dt2(str_in):
    return datetime.strptime(str_in, '%m/%d/%Y')


NEW_CONVERTERS = [
    {
        'to': 'date2',
        'converters': {'fr': 'str', 'func': str_to_dt2}},
    {
        'to': 'str',
        'converters': {'fr': 'date2', 'func': dt2_to_str},
    }
]


NEW_SYSTEM = dict(
    name='mongo',
    default='passthrough',
    mappings={'str': ['date2', 'int'], 'decimal': 'float'})

TESTDATE2 = datetime(year=2015, month=1, day=1)
TESTDATE = date(year=2015, month=1, day=1)
TESTDATE_STR = '2015-01-01'
TESTTIME = time(hour=12, minute=12, second=12, microsecond=12)
TESTTIME_STR = '12:12:12.000012'
TESTDT = datetime(year=2015, month=1, day=1, hour=12, minute=12, second=12, microsecond=12)
TESTDT_STR = TESTDATE_STR+"T"+TESTTIME_STR
TESTDT_TZ = datetime(year=2015, month=1, day=1, 
                     hour=12, minute=12, second=12, microsecond=12, 
                     tzinfo=timezone(timedelta(hours=-8)))
TESTDT_TZ_STR = TESTDT_STR+'-0800'


class TestConverter(TestCase):
    ch = ConverterHelper()
    ch.add_converters(*NEW_CONVERTERS)
    ch.add_systems(NEW_SYSTEM)

    def test_standard_built_in_conversions(self):
        test_sets = [

            (1, 'str', '1', 'int', 1),
            (2, 'decimal', Decimal('1.0'), 'int', 1),
            (3, 'float', 1.0, 'int', 1),
            (4, 'int', 1, 'int', 1),
    

            (10, 'str', '1.0', 'float', 1.0),
            (11, 'decimal', Decimal(1), 'float', 1.0),
            (12, 'float', 1.0, 'float', 1.0),
            (14, 'int', 1, 'float', 1.0),
            (15, 'float', 1.0, 'float', 1.0),
    

            (20, 'int', 1, 'str', '1'),
            (21, 'decimal', Decimal('1'), 'str', '1'),
            (22, 'float', 1.0, 'str', '1.0'),
            (23, 'list', ['foo', 'bar'], 'str', "['foo', 'bar']"),
            (24, 'dict', {'foo': 'bar'}, 'str', "{'foo': 'bar'}"),
            (25, 'bool', True, 'str', 'True'),
            (26, 'complex', complex(1), 'str', '(1+0j)'),
            (27, 'yesno', 'Yes', 'str', 'Yes'),
            (28, 'str', 'Yes', 'str', 'Yes'),

            (30, 'str', "{'foo': 'bar'}", 'dict', {'foo': 'bar'}),
            (31, 'dict', {'foo': 'bar'}, 'dict', {'foo': 'bar'}),

            (40, 'str', "['foo', 'bar']", 'list', ['foo', 'bar']),
            (41, 'list', ['foo', 'bar'], 'list', ['foo', 'bar']),
        
            (50, 'int', 1, 'decimal', Decimal('1')),
            (51, 'float', 1.0, 'decimal', Decimal('1.0')),
            (52, 'str', '1', 'decimal', Decimal('1')),
            (54, 'decimal', Decimal(1), 'decimal', Decimal('1')),

            (60, 'int', 0, 'bool', False),
            (61, 'decimal', Decimal(0.0), 'bool', False),
            (62, 'float', float(0), 'bool', False),
            (63, 'complex', complex(0), 'bool', False),
            (64, 'str', 'False', 'bool', False),
            (65, 'str', 'false', 'bool', False),
            (66, 'str', 'no', 'bool', False),
            (67, 'yesno', 'No', 'bool', False),

            (70, 'int', 1, 'bool', True),
            (71, 'decimal', Decimal(1.0), 'bool', True),
            (72, 'float', float(1), 'bool', True),
            (73, 'complex', complex(1), 'bool', True),
            (74, 'str', 'True', 'bool', True),
            (75, 'str', 'True', 'bool', True),
            (76, 'str', 'yes', 'bool', True),
            (77, 'yesno', 'Yes', 'bool', True),
            (78, 'bool', True, 'bool', True),

            (80, 'int', 1, 'complex', complex(1)),
            (81, 'float', 1.0, 'complex', complex(1)),
            (82, 'decimal', Decimal(1), 'complex', complex(1)),
            (83, 'str', '1', 'complex', complex(1)),
            (84, 'complex', complex(1), 'complex', complex(1)),

            (90, 'bool', True, 'yesno', 'Yes'),
            (91, 'str', 'Yes', 'yesno', 'Yes'),
            (92, 'yesno', 'Yes', 'yesno', 'Yes'),

            (100, 'str', '01/01/2015', 'date2', TESTDATE2),
            (101, 'date2', TESTDATE2, 'date2', TESTDATE2),

            (110, 'str', TESTTIME_STR, 'time', TESTTIME),
            (111, 'time', TESTTIME, 'str', TESTTIME_STR),        
            (112, 'time', TESTTIME, 'time', TESTTIME),

            (120, 'str', TESTDATE_STR, 'date', TESTDATE),
            (121, 'date', TESTDATE, 'str', TESTDATE_STR),
            (122, 'date', TESTDATE, 'date', TESTDATE),

            (130, 'str', TESTDT_STR, 'datetime', TESTDT),
            (131, 'datetime', TESTDT, 'str', TESTDT_STR),
            (132, 'datetime', TESTDT, 'datetime', TESTDT),

            (140, 'str', TESTDT_TZ_STR, 'datetime_tz', TESTDT_TZ),
            (141, 'datetime_tz', TESTDT_TZ, 'str', TESTDT_TZ_STR),
            (142, 'datetime_tz', TESTDT_TZ, 'datetime_tz', TESTDT_TZ),
        ]

        for ts in test_sets:
            tmp_name = '#%s: From(%s): %s => To(%s): %s' % (ts[0], ts[1], ts[2], ts[3], ts[4])
            with self.subTest(tmp_name):
                tmp_ret = self.ch(ts[2], fr=ts[1], to=ts[3])
                # print(tmp_name)
                self.assertEqual(ts[4], tmp_ret)

    def test_auto_detection(self):
        test_sets = [
            (20, 'int', 1, 'str', '1'),
            (21, 'decimal', Decimal('1'), 'str', '1'),
            (22, 'float', 1.0, 'str', '1.0'),
            (23, 'list', ['foo', 'bar'], 'str', "['foo', 'bar']"),
            (24, 'dict', {'foo': 'bar'}, 'str', "{'foo': 'bar'}"),
            (25, 'bool', True, 'str', 'True'),
            (26, 'complex', complex(1), 'str', '(1+0j)'),
            (27, 'yesno', 'Yes', 'str', 'Yes'),
            (28, 'str', 'foo', 'str', 'foo'),
            (29, 'time', TESTTIME, 'str', TESTTIME_STR),
            (30, 'date', TESTDATE, 'str', TESTDATE_STR),
            (31, 'datetime', TESTDT, 'str', TESTDT_STR),
            (32, 'datetime_tz', TESTDT_TZ, 'str', TESTDT_TZ_STR),

        ]

        for ts in test_sets:
            tmp_name = '#%s: From(%s): %s => To(%s): %s' % (ts[0], 'auto', ts[2], ts[3], ts[4])
            with self.subTest(tmp_name):
                tmp_ret = self.ch(ts[2], fr='auto', to=ts[3])
                # print(tmp_name)
                self.assertEqual(ts[4], tmp_ret)

    def test_built_in_systems(self):
        test_sets = [
            (0, 'int', 1, 'to', 'sys_str', '1'),
            (1, 'int', '1', 'fr', 'sys_str', 1),

            (0, 'float', 1.0, 'to', 'sys_str', '1.0'),
            (1, 'float', '1', 'fr', 'sys_str', 1.0),

            (0, 'bool', True, 'to', 'sys_str', 'True'),
            (1, 'bool', 'True', 'fr', 'sys_str', True),

            (0, 'str', 'foo', 'to', 'sys_str', 'foo'),
            (1, 'str', 'bar', 'fr', 'sys_str', 'bar'),

            (0, 'list', [1, 2, 'test'], 'to', 'sys_str', "[1, 2, 'test']"),
            (1, 'list', "[1, 2, 'test']", 'fr', 'sys_str', [1, 2, 'test']),

            (0, 'int', 1, 'to', 'sys_dict', 1),
            (1, 'int', 1, 'fr', 'sys_dict', 1),

            (0, 'float', 1.0, 'to', 'sys_dict', 1.0),
            (1, 'float', 1.0, 'fr', 'sys_dict', 1.0),

            (0, 'bool', True, 'to', 'sys_dict', True),
            (1, 'bool', True, 'fr', 'sys_dict', True),

            (0, 'str', 'foo', 'to', 'sys_dict', 'foo'),
            (1, 'str', 'bar', 'fr', 'sys_dict', 'bar'),

            (0, 'list', [1, 2, 'test'], 'to', 'sys_dict', [1, 2, 'test']),
            (1, 'list', [1, 2, 'test'], 'fr', 'sys_dict', [1, 2, 'test']),


            (0, 'int', 1, 'to', 'mongo', '1'),
            (1, 'int', '1', 'fr', 'mongo', 1),

            (0, 'float', 1.0, 'to', 'mongo', Decimal(1.0)),
            (1, 'float', Decimal(1.0), 'fr', 'mongo', 1.0),

            (0, 'bool', True, 'to', 'mongo', True),
            (1, 'bool', True, 'fr', 'mongo', True),

            (0, 'str', 'foo', 'to', 'mongo', 'foo'),
            (1, 'str', 'bar', 'fr', 'mongo', 'bar'),

            (0, 'list', [1, 2, 'test'], 'to', 'mongo', [1, 2, 'test']),
            (1, 'list', [1, 2, 'test'], 'fr', 'mongo', [1, 2, 'test']),

            (0, 'date2', TESTDATE2, 'to', 'mongo', '01/01/2015'),
            (1, 'date2', '01/01/2015', 'fr', 'mongo', TESTDATE2),
        ]

        for ts in test_sets:
            tmp_name = str(ts)
            with self.subTest(tmp_name):
                if ts[3] == 'to':
                    lc = 'fr'
                else:
                    lc = 'to'
                tmp_dict = {
                    ts[3]: ts[4],
                    lc: ts[1],
                    'value': ts[2]
                }
                tmp_ret = self.ch(**tmp_dict)
                # print(tmp_name)
                self.assertEqual(ts[5], tmp_ret)

    def test_none_converters(self):
        self.assertEqual(None, self.ch(None, fr='int', to='str', return_none_as=None))
        self.assertEqual(_UNSET, self.ch(None, fr='int', to='str', return_none_as=_UNSET))
        self.assertEqual('None', self.ch(None, fr='int', to='str'))
        self.assertEqual(None, self.ch('<__None__>', fr='sys_str', to='str'))
        self.assertEqual('<__None__>', self.ch(None, fr='str', to='sys_str'))

        self.assertEqual(None, self.ch(None, fr='sys_dict', to='str'))
        self.assertEqual(None, self.ch(None, fr='str', to='sys_dict'))

        with self.assertRaises(ConversionError):
            self.assertNotEqual(_UNSET, self.ch(None, fr='str', to='int'))

    def test_no_converter_error(self):
        with self.assertRaises(NoConverterError):
            foo = self.ch(1, fr='foo', to='int')

    def test_conversion_error(self):
        with self.assertRaises(ConversionError):
            foo = self.ch('foo', fr='int', to='complex')

    def test_duplicate_term_error(self):
        with self.assertRaises(DuplicateTermError):
            self.ch.add_systems({'name': 'str', 'default': 'passthrough'})

        with self.assertRaises(DuplicateTermError):
            tmp_conv = {
                'to': 'sys_dict',
                'converters': {
                    'fr': 'str', 'func': str}}

            self.ch.add_converters(tmp_conv)

    def test_detection_error(self):
        with self.assertRaises(UnableToDetectTypeError):
            foo = self.ch(self, fr='auto', to='str')
