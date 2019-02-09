#!/usr/bin/env python


from datetime import datetime, timedelta

from unittest import TestCase
from PythonUtils.BaseUtils import quartiles, PercCounter, make_percentage, perc_bar, scaled_perc, \
    format_percentage, PERC_RET, est_total_timedelta, est_finish_time, est_finish_timedelta, MathList, SimpleDataClass
import statistics
from decimal import Decimal


class TestQuartileCalc(TestCase):

    def test_qu_calc(self):
        test_list = [71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69]
        q1, q2, q3 = quartiles(test_list)
        self.assertEqual(q1, 70)
        self.assertEqual(q2, 70.5)
        self.assertEqual(q3, 71.5)

    def test_qu_calc_2(self):
        test_list = [2, 5, 6, 9, 12]
        q1, q2, q3 = quartiles(test_list)
        self.assertEqual(q1, 3.5)
        self.assertEqual(q2, 6)
        self.assertEqual(q3, 10.5)

    def test_qu_calc_3(self):
        test_list = [3, 10, 14, 22, 19, 29, 70, 49, 36, 32]
        q1, q2, q3 = quartiles(test_list)
        self.assertEqual(q1, 14)
        self.assertEqual(q2, 25.5)
        self.assertEqual(q3, 36)


class TestPercCalcs(TestCase):
    def test_basic_function(self):
        pc = PercCounter(total=10)
        self.assertEqual(0, pc())
        self.assertEqual(10, pc(1))
        self.assertEqual(20, pc(2))
        self.assertEqual(30, pc(delta=1))
        self.assertEqual(110, pc(11))

    def test_iadd_isub_function(self):
        pc = PercCounter(total=10)
        self.assertEqual(0, pc())
        pc += 1
        self.assertEqual('10%', str(pc))
        pc += 1
        self.assertEqual(0.2, float(pc))
        pc -= 1
        self.assertEqual(10, int(pc))

    def test_format_perc_float(self):
        pc = PercCounter(total=10, perc_format=PERC_RET.AS_FLOAT)
        self.assertEqual(0.0, pc())
        self.assertEqual(0.1, pc(1))
        self.assertEqual(0.2, pc(2))
        self.assertEqual(0.3, pc(delta=1))
        self.assertEqual(1.1, pc(11))

    def test_format_str(self):
        pc = PercCounter(total=10, perc_format=PERC_RET.AS_STR_INT)
        self.assertEqual('0%', pc())
        self.assertEqual('10%', pc(1))
        self.assertEqual('20%', pc(2))
        self.assertEqual('30%', pc(delta=1))
        self.assertEqual('110%', pc(11))

    def test_make_perc_min_max(self):
        pc = PercCounter(total=10, min_perc=0.2, max_perc=0.75)
        self.assertEqual(20, pc())
        self.assertEqual(20, pc(1))
        self.assertEqual(20, pc(2))
        self.assertEqual(30, pc(delta=1))
        self.assertEqual(75, pc(11))

    def test_make_perc_raise(self):
        with self.assertRaises(ZeroDivisionError):
            pc = PercCounter(total=0)

    def test_scaled_perc(self):
        pc = PercCounter(total=100, current=10)
        self.assertEqual(5, pc.scaled(50, as_int=True))
        self.assertEqual(5.5, pc.scaled(55, as_int=False))

    def test_perc_bar_left(self):
        pc = PercCounter(total=50, current=5, perc_bar_length=20)
        tmp_ret = pc.perc_bar()
        exp_ret = '##..................'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_right(self):
        pc = PercCounter(total=50, current=5, perc_bar_length=20)
        tmp_ret = pc.perc_bar(bar_format='{right_bar}')
        exp_ret = '..................##'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_center(self):
        pc = PercCounter(total=50, current=22, perc_bar_length=20)
        tmp_ret = pc.perc_bar(bar_format='{center_bar}')
        exp_ret = '.......#............'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_with_perc(self):
        pc = PercCounter(total=50, perc_bar_length=20)
        tmp_ret = pc.perc_bar(5, bar_format='{left_bar} {perc:.0%}')
        exp_ret = '##.................. 10%'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_with_spinner(self):
        pc = PercCounter(total=50, perc_bar_length=20)
        tmp_ret = pc.perc_bar(5, bar_format='[{spinner}] {left_bar}')
        exp_ret = '[/] ##..................'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_complex(self):
        pc = PercCounter(total=50, current=40, perc_bar_length=20)
        tmp_ret = pc.perc_bar(5, bar_format='{perc} {foobar} snafu', foobar='FOOBAR')
        exp_ret = '0.1 FOOBAR snafu'
        self.assertEqual(exp_ret, tmp_ret)

    def test_est_total_timedelta(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        pc = PercCounter(total=100, time_start=start_time)

        exp_time = timedelta(seconds=40)

        tmp_ret = pc.est_total_timedelta(current=25, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)

    def test_est_finish_timedelta(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        exp_time = timedelta(seconds=30)

        pc = PercCounter(total=100, time_start=start_time)

        tmp_ret = pc.est_finish_timedelta(current=25, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)

    def test_est_finish_time(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        exp_time = time_now + timedelta(seconds=40)

        pc = PercCounter(total=100, time_start=start_time)

        tmp_ret = pc.est_finish_time(current=25, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)

    def test_format(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)

        pc = PercCounter(total=100, current=25, time_start=start_time)

        tmp_ret = repr(pc)
        tmp_exp = 'PercCounter: Perc: 25.00% Current: 25 / Total: 100 Started: {start_time} Est_Fininh In: 0:00:30'.format(start_time=start_time)

        self.assertEqual(tmp_exp, tmp_ret)


class TestPercCounter(TestCase):
    def test_format_perc(self):
        self.assertEqual(0.1234, format_percentage(0.1234, perc_format=PERC_RET.AS_FLOAT))
        self.assertEqual(12, format_percentage(0.1234, perc_format=PERC_RET.AS_INT))
        self.assertEqual('12%', format_percentage(0.1234, perc_format=PERC_RET.AS_STR_INT))
        self.assertEqual('12.34%', format_percentage(0.1234, perc_format=PERC_RET.AS_STR_DOT_2))
        self.assertEqual('12.3%', format_percentage(0.1234, perc_format=PERC_RET.AS_STR_DOT_1))
        self.assertEqual(12.34, format_percentage(0.1234, perc_format=PERC_RET.AS_FLOAT_PERC))
        self.assertEqual('perc=0.1234', format_percentage(0.1234, perc_format='perc={perc}'))

    def test_make_perc(self):
        self.assertEqual(0.10, make_percentage(10, 100))

    def test_make_perc_format(self):
        self.assertEqual(10, make_percentage(10, 100, perc_format=PERC_RET.AS_INT))

    def test_make_perc_min_max(self):
        self.assertEqual(0.1, make_percentage(9, 100, min_perc=0.1, max_perc=1))
        self.assertEqual(1.0, make_percentage(110, 100, min_perc=0.1, max_perc=1))
        self.assertEqual(0.2, make_percentage(20, 100, min_perc=0.1, max_perc=1))

    def test_make_perc_raise_good(self):
        with self.assertRaises(ZeroDivisionError):
            make_percentage(10, 0, raise_on_div_zero=True)

    def test_make_perc_raise_bad(self):
        self.assertEqual(0, make_percentage(110, 0, raise_on_div_zero=False))

    def test_scaled_perc(self):
        self.assertEqual(5, scaled_perc(0.1, 50, as_int=True))
        self.assertEqual(5.25, scaled_perc(0.105, 50, as_int=False))

    def test_perc_bar_left(self):
        tmp_ret = perc_bar(0.1, length=20)
        exp_ret = '##..................'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_right(self):
        tmp_ret = perc_bar(0.1, length=20, bar_format='{right_bar}')
        exp_ret = '..................##'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_center(self):
        tmp_ret = perc_bar(0.22, length=20, bar_format='{center_bar}')
        exp_ret = '...#................'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_with_perc(self):
        tmp_ret = perc_bar(0.1, length=20, bar_format='{left_bar} {perc:.0%}')
        exp_ret = '##.................. 10%'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_with_spinner(self):
        tmp_ret = perc_bar(0.1, length=20, bar_format='[{spinner}] {left_bar}', spin_state=0)
        exp_ret = '[|] ##..................'
        self.assertEqual(exp_ret, tmp_ret)

    def test_perc_bar_complex(self):
        tmp_ret = perc_bar(0.1, length=20, bar_format='{perc} {foobar} snafu', foobar='FOOBAR')
        exp_ret = '0.1 FOOBAR snafu'
        self.assertEqual(exp_ret, tmp_ret)

    def test_est_total_timedelta(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        exp_time = timedelta(seconds=40)

        tmp_ret = est_total_timedelta(perc=0.25, start_time=start_time, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)

    def test_est_finish_timedelta(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        exp_time = timedelta(seconds=30)

        tmp_ret = est_finish_timedelta(perc=0.25, start_time=start_time, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)

    def test_est_finish_time(self):
        time_now = datetime.now()
        start_time = time_now - timedelta(seconds=10)
        exp_time = time_now + timedelta(seconds=40)

        tmp_ret = est_finish_time(perc=0.25, start_time=start_time, time_now=time_now)

        self.assertEqual(exp_time, tmp_ret)


def math_list_test_func(value, **kwargs):
    return value * 2


class TestMathList(TestCase):

    def test_list_like_behaivior(self):

        ml = MathList()
        self.assertFalse(ml)
        self.assertEqual(len(ml), 0)
        ml.append(1)
        self.assertTrue(ml == [1])
        ml.extend([2, 3, 4])
        self.assertTrue([1, 2, 3, 4] == ml)
        self.assertTrue(3 == ml[2])
        ml[2] = 5
        self.assertTrue([1, 2, 5, 4] == ml)
        ml.reverse()
        self.assertFalse([1, 2, 5, 4] == ml)
        self.assertTrue([4, 5, 2, 1] == ml)

    def test_item_in_list(self):

        ml = MathList([1, 2, 3, 4])
        self.assertTrue(1 in ml)

    def test_sum(self):
        ml = MathList([1, 2, 3, 4])
        self.assertEqual(ml.sum, 10)
        self.assertFalse(ml.has_float)
        self.assertTrue(ml.has_int)
        self.assertFalse(ml.has_dec)

    def test_fsum(self):
        td = [1, 1e100, 1, -1e100] * 10000
        # print(sum(td))
        # print(fsum(td))
        ml = MathList(td)
        self.assertTrue(ml.has_float)
        self.assertTrue(ml.has_int)
        self.assertFalse(ml.has_dec)
        self.assertEqual(ml.sum, 20000.0)

    def test_min(self):
        ml = MathList([1, 2, 3, 4])
        self.assertEqual(ml.min, 1)

    def test_max(self):
        ml = MathList([1, 2, 3, 4])
        self.assertEqual(ml.max, 4)

    def test_mean(self):
        ml = MathList([1, 2, 3, 4])
        self.assertEqual(ml.mean, 2.5)

    def test_harmonic_mean(self):
        ml = MathList([2.5, 3, 10])
        self.assertEqual(ml.harmonic_mean, 3.6)

    def test_median(self):
        ml = MathList([1, 3, 5])
        self.assertEqual(ml.median, 3)
        ml.append(7)
        self.assertEqual(ml._cache_, {})
        self.assertEqual(ml.median, 4.0)

    def test_median_low(self):
        ml = MathList([1, 3, 5])
        self.assertEqual(ml.median_low, 3)
        ml.append(7)
        self.assertEqual(ml._cache_, {})
        self.assertEqual(ml.median_low, 3)

    def test_median_high(self):
        ml = MathList([1, 3, 5])
        self.assertEqual(ml.median_high, 3)
        ml.append(7)
        self.assertEqual(ml._cache_, {})
        self.assertEqual(ml.median_high, 5)

    def test_median_grouped(self):
        ml = MathList([52, 52, 53, 54])
        self.assertEqual(ml.median_grouped(), 52.5)

        ml = MathList([1, 2, 2, 3, 4, 4, 4, 4, 4, 5])
        self.assertEqual(ml.median_grouped(), 3.7)

        ml = MathList([1, 3, 3, 5, 7])
        self.assertEqual(ml.median_grouped(interval=1), 3.25)

        ml = MathList([1, 3, 3, 5, 7])
        self.assertEqual(ml.median_grouped(interval=2), 3.5)

    def test_mode(self):
        ml = MathList([1, 1, 2, 3, 3, 3, 3, 4])
        self.assertEqual(ml.mode, 3)

        ml = MathList([1, 2, 3, 4, 5])
        with self.assertRaises(statistics.StatisticsError):
            x = ml.mode

    def test_pstdev(self):
        ml = MathList([1.5, 2.5, 2.5, 2.75, 3.25, 4.75])
        self.assertEqual(ml.pstdev, 0.986893273527251)
        self.assertTrue(ml.has_float)
        self.assertFalse(ml.has_int)
        self.assertFalse(ml.has_dec)

    def test_pvariance(self):
        ml = MathList([0.0, 0.25, 0.25, 1.25, 1.5, 1.75, 2.75, 3.25])
        self.assertEqual(ml.pvariance, 1.25)

        ml = MathList([Decimal("27.5"), Decimal("30.25"), Decimal("30.25"), Decimal("34.5"), Decimal("41.75")])
        self.assertEqual(ml.pvariance, Decimal('24.815'))
        self.assertFalse(ml.has_float)
        self.assertFalse(ml.has_int)
        self.assertTrue(ml.has_dec)

    def test_stdev(self):
        ml = MathList([1.5, 2.5, 2.5, 2.75, 3.25, 4.75])
        self.assertEqual(ml.stdev, 1.0810874155219827)

    def test_variance(self):
        ml = MathList([2.75, 1.75, 1.25, 0.25, 0.5, 1.25, 3.5])
        self.assertEqual(ml.variance, 1.3720238095238095)

    def test_find_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61])
        self.assertEqual([300, 1, 78, 61], ml.list_outliers(include_outliers=ml.OUTLIERS.ALL_OUTLIERS))
        self.assertEqual([78, 61], ml.list_outliers(include_outliers=ml.OUTLIERS.MINOR_OUTLIERS))
        self.assertEqual([300, 1], ml.list_outliers(include_outliers=ml.OUTLIERS.MAJOR_OUTLIERS))
        self.assertEqual([], ml.list_outliers(include_outliers=ml.OUTLIERS.NO_OUTLIERS))
        self.assertEqual(ml.list_outliers(), [])
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=ml.OUTLIERS.ALL_OUTLIERS)
        self.assertEqual(ml.list_outliers(), [300, 1, 78, 61])

    def test_filter_all_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.ALL_OUTLIERS)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.sum, 776)
        self.assertEqual(len(ml), 11)
        self.assertEqual(ml.list_outliers(), [300, 1, 78, 61])

    def test_filter_no_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.NO_OUTLIERS)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.sum, 1216)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.list_outliers(), [])

    def test_filter_major_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.MAJOR_OUTLIERS)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.sum, 915)
        self.assertEqual(len(ml), 13)
        self.assertEqual(ml.list_outliers(), [300, 1])

        self.assertEqual(ml.list_outliers(include_outliers=ml.OUTLIERS.MINOR_OUTLIERS), [78, 61])
        self.assertEqual(ml.list_outliers(include_outliers=ml.OUTLIERS.MAJOR_OUTLIERS), [300, 1])
        self.assertEqual(ml.list_outliers(include_outliers=ml.OUTLIERS.ALL_OUTLIERS), [300, 1, 78, 61])
        self.assertEqual(ml.list_outliers(include_outliers=ml.OUTLIERS.NO_OUTLIERS), [])

        self.assertEqual(ml.sum, 915)
        self.assertEqual(len(ml), 13)
        self.assertEqual(ml.list_outliers(), [300, 1])

    def test_filter_minor_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.MINOR_OUTLIERS)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.sum, 776)
        self.assertEqual(len(ml), 11)
        self.assertEqual(ml.list_outliers(), [300, 1, 78, 61])

    def test_remove_outliers(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.ALL_OUTLIERS)
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.list_outliers(), [300, 1, 78, 61])
        self.assertEqual(len(ml), 15)
        self.assertEqual(ml.sum, 776)
        self.assertEqual(len(ml), 11)
        self.assertEqual(len(ml._data), 15)
        ml.rem_outliers()
        self.assertEqual(len(ml), 11)
        self.assertEqual(len(ml._data), 11)
        self.assertEqual(ml.list_outliers(), [73])
        self.assertEqual(ml.sum, 703)
        self.assertEqual(len(ml), 10)
        self.assertEqual(len(ml._data), 11)

    def test_calc_list_basic(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.ALL_OUTLIERS)
        tmp_list = ml.calc_list()
        exp_list = [71, 70, 73, 70, 70, 69, 70, 72, 71, 71, 69]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_return_as_list(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(return_row_as='list')
        exp_list = [[1], [2], [3], [4]]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_return_as_list_auto(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['row_num', 'value'], return_row_as='list')
        exp_list = [[0, 1], [1, 2], [2, 3], [3, 4]]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_return_as_dict(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['row_num', 'value'], return_row_as='dict')
        exp_list = [{'row_num': 0, 'value': 1},
                    {'row_num': 1, 'value': 2},
                    {'row_num': 2, 'value': 3},
                    {'row_num': 3, 'value': 4}]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_return_as_object(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['row_num', 'value'], return_row_as=SimpleDataClass)
        self.assertEqual(0, tmp_list[0].row_num)
        self.assertEqual(1, tmp_list[0].value)

        self.assertEqual(1, tmp_list[1].row_num)
        self.assertEqual(2, tmp_list[1].value)

        self.assertEqual(2, tmp_list[2].row_num)
        self.assertEqual(3, tmp_list[2].value)

        self.assertEqual(3, tmp_list[3].row_num)
        self.assertEqual(4, tmp_list[3].value)

    def test_calc_list_return_as_named(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['row_num', 'value'], return_row_as='named')
        self.assertEqual(0, tmp_list[0].row_num)
        self.assertEqual(1, tmp_list[0].value)

        self.assertEqual(1, tmp_list[1].row_num)
        self.assertEqual(2, tmp_list[1].value)

        self.assertEqual(2, tmp_list[2].row_num)
        self.assertEqual(3, tmp_list[2].value)

        self.assertEqual(3, tmp_list[3].row_num)
        self.assertEqual(4, tmp_list[3].value)

    def test_calc_list_format_dict(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_sum'], format_dict={'running_sum': '{}'})
        exp_list = ['1', '3', '6', '10']
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_func_dict(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_sum'], format_dict={'running_sum': '{}'}, func_dict={'running_sum': math_list_test_func})
        exp_list = ['2', '6', '12', '20']
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_row_offset(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['row_num', 'value'], row_num_offset=1)
        exp_list = [[1, 1], [2, 2], [3, 3], [4, 4]]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_start_end(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_sum'], start_at=1, end_at=3)
        exp_list = [3, 6]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_force_total(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], force_total=20)
        exp_list = [5, 15, 30, 50]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_int(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'])
        exp_list = [10, 30, 60, 100]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_float(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], perc_return=PERC_RET.AS_FLOAT)
        exp_list = [0.1, 0.3, 0.6, 1.0]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_float_perc(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], perc_return=PERC_RET.AS_FLOAT_PERC)
        exp_list = [10.0, 30.0, 60.0, 100.0]
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_str(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], perc_return=PERC_RET.AS_STR_INT)
        exp_list = ['10%', '30%', '60%', '100%']
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_str_2(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], perc_return=PERC_RET.AS_STR_DOT_2)
        exp_list = ['10.00%', '30.00%', '60.00%', '100.00%']
        self.assertListEqual(exp_list, tmp_list)

    def test_calc_list_running_perc_value_done_format(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_value_done'], perc_return={'running_perc_value_done':'perc: {0:.1f}'})
        exp_list = ['perc: 0.1','perc: 0.3','perc: 0.6','perc: 1.0']
        self.assertListEqual(exp_list, tmp_list)

    def test_running_perc_rows_done_headers(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['value', 'perc_rows_done', 'running_perc_value_done'], perc_return={'running_perc_value_done':'perc: {0:.1f}'}, inc_header=True)
        exp_list = [['value', 'perc_rows_done', 'running_perc_value_done'],[1, 25, 'perc: 0.1'],[2, 50, 'perc: 0.3'],[3, 75, 'perc: 0.6'],[4, 100, 'perc: 1.0']]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_perc_rows_done(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list('perc_rows_done')
        exp_list = [25, 50, 75, 100]
        self.assertListEqual(exp_list, tmp_list)

    def test_perc_of_total(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['perc_of_total'])
        exp_list = [10, 20, 30, 40]
        self.assertListEqual(exp_list, tmp_list)

    def test_difference_from_mean(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['difference_from_mean'])
        exp_list = [-1.5, -0.5, .5, 1.5]
        self.assertListEqual(exp_list, tmp_list)

    def test_difference_from_median(self):
        ml = MathList([1, 2, 5, 3, 4])
        tmp_list = ml.calc_list(['difference_from_median'])
        exp_list = [-2, -1, 2, 0, 1]
        self.assertListEqual(exp_list, tmp_list)

    def test_outlier_flag(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61], filter_outliers=MathList.OUTLIERS.NO_OUTLIERS)
        tmp_list = ml.calc_list(['outlier_flag'])
        exp_list = ['', '', '', '', '', '', '', '', '', 'major', '', '', 'major', 'minor', 'minor']
        self.assertListEqual(exp_list, tmp_list)

    def test_running_mean(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_mean'])
        exp_list = [1.0, 1.5, 2, 2.5]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_median(self):
        ml = MathList([1, 2, 3, 4, 5])
        tmp_list = ml.calc_list(['running_median'])
        exp_list = [1.0, 1.5, 2.0, 2.5, 3]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_max(self):
        ml = MathList([1, 3, 2, 4])
        tmp_list = ml.calc_list(['running_max'])
        exp_list = [1, 3, 3, 4]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_min(self):
        ml = MathList([3, 2, 4, 1])
        tmp_list = ml.calc_list(['running_min'])
        exp_list = [3, 2, 2, 1]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_change(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_change'])
        exp_list = [1, 1, 1, 1]
        self.assertListEqual(exp_list, tmp_list)

    def test_running_perc_change(self):
        ml = MathList([1, 2, 3, 4])
        tmp_list = ml.calc_list(['running_perc_change'])
        exp_list = [100, 100, 50, 33]
        self.assertListEqual(exp_list, tmp_list)

    def test_interval(self):
        ml = MathList([71, 70, 73, 70, 70, 69, 70, 72, 71, 300, 71, 69, 1, 78, 61])
        tmp_list = ml.calc_list(interval=4)
        exp_list = [70, 72, 69]
        self.assertListEqual(exp_list, tmp_list)
