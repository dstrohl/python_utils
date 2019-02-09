#!/usr/bin/env python

from unittest import TestCase
from PythonUtils.BaseUtils import Path


def path_validate_func(path_in):
    if 'p3' not in path_in:
        raise ValueError


class PathTests(TestCase):

    def test_new_create(self):
        p = Path('p1/p2', key_sep='/')
        self.assertEqual(['p1', 'p2'], list(p))

    def test_create_from_path(self):
        p = Path('p1/p2', key_sep='/')
        q = Path(p)
        self.assertEqual(list(q), ['p1', 'p2'])

    def test_cd(self):
        p = Path('p1/p2', key_sep='/')
        self.assertEqual('/p1', str(p.cd('//')))
        self.assertEqual(p[-1], 'p1')

        self.assertEqual('/p3', str(p.cd('//p3')))
        self.assertEqual(p[-1], 'p3', p)

        self.assertEqual('/p3/p4', str(p.cd('p4')))
        self.assertEqual('/p3/p4/p4/p5', str(p.cd('p4/p5')))
        self.assertEqual('/', str(p.cd('/')))
        self.assertEqual('/p1/p2/p3/p4', str(p.cd('p1/p2/p3/p4')))
        self.assertEqual('/p5/p6', str(p.cd('/p5/p6')))

    def test_cd_up_2(self):
        p = Path('p1.p2.p3.p4.')
        self.assertEqual(p.cd('...')._path, ['p1', 'p2'])
        self.assertEqual(p[-1], 'p2')

    def test_cd_to_root(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(p.cd('.')._path, [])

    def test_addition_1(self):
        print('--- making p1 ----')
        p1 = Path('p1/p2', key_sep='/')
        print('--- making p2 ----')
        p2 = Path('p3.p4')
        print('--- making p ----')
        p = p1 + p2

        self.assertEqual('p1/p2', p1)
        self.assertEqual('p3.p4', p2)

        self.assertEqual('/p1/p2/p3/p4', p)

    def test_addition_2(self):
        p1 = Path('p1.p2')
        p = p1 + 'p3.p4'

        self.assertEqual('.p1.p2.p3.p4', p)
        self.assertEqual('p1.p2', p1)

    def test_addition_3(self):
        p1 = Path('p1.p2')
        p1 += 'p3.p4'

        self.assertEqual('p1.p2.p3.p4', p1)

    def test_merge_1(self):
        p1 = Path('p1.p2')
        p2 = Path('p3.p4')
        p1 &= p2

        self.assertEqual('p1.p2.p3.p4', p1)
        self.assertEqual('p3.p4', p2)

    def test_merge_2(self):
        p1 = Path('p1.p2.p3')
        p2 = Path('p3.p4')
        p = p1 & p2

        self.assertEqual('p1.p2.p3', p1)
        self.assertEqual('p3.p4', p2)
        self.assertEqual('p1.p2.p3.p4', p)

    def test_merge_3(self):
        p1 = Path('p1.p2.p3')
        p2 = Path('p2.p3.p4')
        p = p1 & p2

        self.assertEqual('p1.p2.p3', p1)
        self.assertEqual('p2.p3.p4', p2)
        self.assertEqual('p1.p2.p3.p4', p)

    def test_merge_4(self):
        p1 = Path('p1.p2.p3')
        p2 = Path('p1.p3.p4')
        p = p1 & p2

        self.assertEqual('p1.p2.p3', p1)
        self.assertEqual('p1.p3.p4', p2)
        self.assertEqual('p1.p2.p3.p1.p3.p4', p)

    def test_str(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(str(p), '.p1.p2.p3.p4')

    def test_str_2(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual('/p1/p2/p3/p4', p.to_string('/'))

    def test_str_3(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(p.to_string('/', leading=False), 'p1/p2/p3/p4')

    def test_str_4(self):
        p = Path('p1.p2.p3.p4', key_xform=str.upper)
        self.assertEqual(p.to_string('/', trailing=True), '/P1/P2/P3/P4/')

    def test_index(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(p[2], 'p3')

    def test_index_2(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(p[2:], 'p3.p4')

    def test_index_3(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(len(p), 4)
        p2 = p[:2]
        self.assertEqual(p2, '.p1.p2')
        self.assertEqual(len(p2), 2)
        self.assertEqual(len(p), 4)

    def test_len(self):
        p = Path('p1.p2.p3.p4')
        self.assertEqual(len(p), 4)

    def test_find(self):
        p = Path('p1.p2.p3.p4', key_xform=str.upper)
        self.assertEqual(p.find('p2'), 1)
        self.assertEqual(p.find('P2'), 1)

    def test_no_find(self):
        p = Path('p1.p2.p3.p4')
        with self.assertRaises(ValueError):
            p.find('p6')

    def test_in(self):
        p = Path('p1.p2.p3.p4')
        self.assertTrue('p2' in p)

    def test_not_in(self):
        p = Path('p1.p2.p3.p4')
        self.assertFalse('p6' in p)

    def test_from(self):
        p = Path('p1.p2.p3.p4')
        p2 = p.path_from('p2')
        self.assertEqual(p2, 'p2.p3.p4')
        self.assertEqual(len(p2), 3)
        self.assertEqual(len(p), 4)

    def test_to(self):
        p = Path('p1.p2.p3.p4')
        p2 = p.path_to('p3')
        self.assertEqual('p1.p2.p3', p2)
        self.assertEqual(len(p2), 3)
        self.assertEqual(len(p), 4)

    def test_no_from(self):
        p = Path('p1.p2.p3.p4')
        with self.assertRaises(ValueError):
            p2 = p.path_from('p6')

    def test_no_to(self):
        p = Path('p1.p2.p3.p4')
        with self.assertRaises(ValueError):
            p2 = p.path_to('p6')

    def test_compare(self):
        test_items = [

            ('lt_1', ('<', '<=', '!='), 5),
            ('lt_2', ('<', '<=', '!='), 'p1.p2.p3.p4'),
            ('lt_4', ('<', '<=', '!='), Path('p1.p2.p3.p4', key_sep='/')),
            ('lt_5', ('<', '<=', '!='), ['p1', 'p2', 'p3', 'p4']),

            ('eq_1', ('==', '<=', '>='), 3),
            ('eq_2', ('==', '<=', '>='), 'p1.p2.p3'),
            ('eq_3', ('==', '<=', '>='), Path('p1.p2.p3')),
            ('eq_4', ('==', '<=', '>='), ['p1', 'p2', 'p3']),

            ('gt_1', ('>', '>=', '!='), 1),
            ('gt_2', ('>', '>=', '!='), 'p1.p2'),
            ('gt_3', ('>', '>=', '!='), Path('p1.p2', key_sep='/')),
            ('gt_4', ('>', '>=', '!='), ['p1', 'p2']),

            ('ne_3', ('!=',), 'p6.p2.p3'),
            ('ne_4', ('!=',), Path('p6.p2.p3')),
            ('ne_5', ('!=',), ['p6', 'p2', 'p3']),
        ]

        all_test_types = (
            ('==', self.assertEqual),
            ('>', self.assertGreater),
            ('<', self.assertLess),
            ('<=', self.assertLessEqual),
            ('>=', self.assertGreaterEqual),
            ('!=', self.assertNotEqual)
        )
        base_item = Path('p1.p2.p3')

        TEST_ITEM_CODE = None
        TEST_TYPE = None
        # TEST_ITEM_CODE = 'lt_2'
        # TEST_TYPE = '<'

        for name, test_types, test_value in test_items:
            for cur_test_type, cur_test_assert in all_test_types:
                if TEST_ITEM_CODE is None or TEST_ITEM_CODE == name:
                    if TEST_TYPE is None or TEST_TYPE == cur_test_type:
                        if cur_test_type in test_types:
                            with self.subTest(f'{name} {cur_test_type} (good)'):
                                cur_test_assert(base_item, test_value)
                        else:
                            with self.subTest(f'{name} {cur_test_type} (bad)'):
                                with self.assertRaises(AssertionError):
                                    cur_test_assert(base_item, test_value)

    def test_bool(self):
        p = Path('p1.p2.p3.p4')
        self.assertTrue(p)

    def test_not_bool(self):
        p = Path('p1.p2.p3.p4')
        p.cd('.')
        self.assertEqual(p, '')
        self.assertFalse(p)

    def test_validate_ok(self):
        p = Path('p1.p2.p3.p4', validate_func=path_validate_func)
        self.assertEqual(p, 'p1.p2.p3.p4')

    def test_validate_ok_2(self):
        p = Path('p1.p2.p3.p4', validate_func=path_validate_func)
        p.cd('..')
        self.assertEqual(p, 'p1.p2.p3')

    def test_validate_bad(self):
        with self.assertRaises(ValueError):
            p = Path('p1.p2.p4', validate_func=path_validate_func)
            self.assertEqual(p, 'p1.p2.p3.p4')

    def test_validate_bad_2(self):
        p = Path('p1.p2.p3.p4', validate_func=path_validate_func)
        p.cd('..')
        self.assertEqual(p, 'p1.p2.p3')
        with self.assertRaises(ValueError):
            p.cd('..')

        self.assertEqual(p, 'p1.p2.p3')
        with self.assertRaises(ValueError):
            p.cd('.')

        self.assertEqual(p, 'p1.p2.p3')

