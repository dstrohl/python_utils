from unittest import TestCase
import pprint

p=pprint.PrettyPrinter()

from PythonUtils.Old.DbDict import ListDB
__author__ = 'strohl'



class RelatedTestFields():
        # extra fields:
        #   db2
        #   db2_set
        #   cst_db3_set
        db1 = [
            {'1f1':'test1',
             'id':'1',
             'db2_id':'1',
             '1f2':'test2',
             '1f3':'test3',
             '1f4':'test4',},
            {'1f1':'test11',
             'id':'2',
             'db2_id':'1',
             '1f2':'test12',
             '1f3':'test13',
             '1f4':'test14',},
            {'1f1':'test21',
             'id':'3',
             'db2_id':'5',
             '1f2':'test22',
             '1f3':'test23',
             '1f4':'test24',},
            {'1f1':'test31',
             'id':'4',
             'db2_id':'5',
             '1f2':'test32',
             '1f3':'test33',
             '1f4':'test34',},
            {'1f1':'test1',
             'id':'5',
             'db2_id':'5',
             '1f2':'test42',
             '1f3':'test43',
             '1f4':'test44',},]

        # extra fields:
        #   db1
        #   db1_set
        #   cst_db3_set
        db2 = [
            {'2f1':'2test1',
             'id':'1',
             'db1_id':'1',
             '2f2':'2test2',
             '2f3':'2test3',
             '2f4':'2test4',},
            {'2f1':'2test11',
             'id':'2',
             'db1_id':'1',
             '2f2':'2test12',
             '2f3':'2test13',
             '2f4':'2test14',},
            {'2f1':'2test21',
             'id':'3',
             'db1_id':'1',
             '2f2':'2test22',
             '2f3':'2test23',
             '2f4':'2test24',},
            {'2f1':'2test31',
             'id':'4',
             'db1_id':'1',
             '2f2':'2test32',
             '2f3':'2test33',
             '2f4':'2test34',},
            {'2f1':'2test1',
             'id':'5',
             'db1_id':'5',
             '2f2':'2test42',
             '2f3':'2test43',
             '2f4':'2test44',},]
        # extra fields:
        #   cst_db1
        #   cst_db2

        db3 = [
            {'3f1':'2test1',
             'id':'1',
             'db2_id':'1',
             'db1_id':'5',
             '3f2':'2test2',
             '3f3':'2test3',
             '3f4':'2test4',},
            {'3f1':'2test11',
             'id':'2',
             'db2_id':'1',
             'db1_id':'5',
             '3f2':'2test12',
             '3f3':'2test13',
             '3f4':'2test14',},
            {'3f1':'2test21',
             'id':'3',
             'db2_id':'5',
             'db1_id':'5',
             '3f2':'2test22',
             '3f3':'2test23',
             '3f4':'2test24',},
            {'3f1':'2test31',
             'id':'4',
             'db2_id':'5',
             '3f2':'2test32',
             '3f3':'2test33',
             '3f4':'2test34',},
            {'3f1':'2test1',
             'id':'5',
             'db2_id':'5',
             '3f2':'2test42',
             '3f3':'2test43',
             '3f4':'2test44',},]




        test1_resp_db1_id_1_fld_db2 = {'2f1':'2test1',
                                         'id':'1',
                                         'db1_id':'1',
                                         '2f2':'2test2',
                                         '2f3':'2test3',
                                         '2f4':'2test4',}


        # no related
        test2_resp_db1_id_1_fld_db2_set = [
            {'2f1':'2test1',
             'id':'1',
             'db1_id':'1',
             '2f2':'2test2',
             '2f3':'2test3',
             '2f4':'2test4',},
            {'2f1':'2test11',
             'id':'2',
             'db1_id':'1',
             '2f2':'2test12',
             '2f3':'2test13',
             '2f4':'2test14',},
            {'2f1':'2test21',
             'id':'3',
             'db1_id':'1',
             '2f2':'2test22',
             '2f3':'2test23',
             '2f4':'2test24',},
            {'2f1':'2test31',
             'id':'4',
             'db1_id':'1',
             '2f2':'2test32',
             '2f3':'2test33',
             '2f4':'2test34',},
        ]

        test3_resp_db1_id_1_fld_cst_db3_set = None

        test4_resp_db2_id_5_fld_db1 = {'1f1':'test1',
                                         'id':'5',
                                         'db2_id':'5',
                                         '1f2':'test42',
                                         '1f3':'test43',
                                         '1f4':'test44',}

        test5_resp_db2_id_5_fld_db1_set = [
            {'1f1':'test21',
             'id':'3',
             'db2_id':'5',
             '1f2':'test22',
             '1f3':'test23',
             '1f4':'test24',},
            {'1f1':'test31',
             'id':'4',
             'db2_id':'5',
             '1f2':'test32',
             '1f3':'test33',
             '1f4':'test34',},
            {'1f1':'test1',
             'id':'5',
             'db2_id':'5',
             '1f2':'test42',
             '1f3':'test43',
             '1f4':'test44',},]

        test6_resp_db2_id_1_fld_cst_db3_set = [
            {'3f1':'2test1',
             'id':'1',
             'db2_id':'1',
             'db1_id':'5',
             '3f2':'2test2',
             '3f3':'2test3',
             '3f4':'2test4',},
            {'3f1':'2test11',
             'id':'2',
             'db2_id':'1',
             'db1_id':'5',
             '3f2':'2test12',
             '3f3':'2test13',
             '3f4':'2test14',},

        ]

        test7_resp_db3_id_5_fld_cst_db1 = None
        test8_resp_db3_id_1_fld_cst_db2_fld_db1 = {'1f1':'test1',
                                                     'id':'1',
                                                     'db2_id':'1',
                                                     '1f2':'test2',
                                                     '1f3':'test3',
                                                     '1f4':'test4',}



class TestFieldManager(TestCase):

    field_name_format = 'field{}'
    field_string_format = 'this is the string - {}-{}'
    field_cnt = 4
    rec_count = 10
    cur_rec = 0

    def _create_test_dict(self, rec_num = None, field_cnt = None):
        tmp_fn_list = []
        tmp_dict = {}
        if not field_cnt:
            field_cnt = self.field_cnt

        for i in range(field_cnt):
            field_name = self._getfn(i)
            field_string = self._getfs(rec_num, i)
            tmp_fn_list.append(field_name)
            tmp_dict[field_name] = field_string
        # print('create rec fn list = ',tmp_fn_list)
        # print('create rec rex = ', tmp_dict)
        return tmp_fn_list, tmp_dict

    def _create_fn_list(self,start=None,end=None):
        tmp_list = []
        if not start:
            start = self.field_cnt

        # print('fn count = ',self.field_cnt)

        if not end:
            for i in range(start):
                tmp_list.append(self._getfn(i))
        else:
            for i in range(start = start, stop= end):
                tmp_list.append(self.getfn(i))
        return tmp_list

    def _getfn(self,counter):
        return self.field_name_format.format(counter)

    def _getfs(self,rec,fld):
        return self.field_string_format.format(rec, fld)

    def _checkfn(self,fn,counter):
        self.assertEqual(fn, self._getfn(counter))

    def _checkfs(self, fs, rec, fld):
        self.assertEqual(fs, self._getfs(rec, fld))



    def _create_dict_list(self, rec_count = 10 , field_count = 4):
        tmp_list = []
        for i in range(rec_count):
            tmp_fn_list, tmp_dict = self._create_test_dict(i, field_count)
            tmp_list.append(tmp_dict)
        return tmp_fn_list, tmp_list

    def _create_empty_ldb(self, fn_list = None):
        if not fn_list:
            fn_list = self._create_fn_list()
        return ListDB( fieldlist = fn_list)

    def _create_ldb(self):
        tmp_fn_list, tmp_list = self._create_dict_list()
        ldb = self._create_empty_ldb(tmp_fn_list)
        ldb.extend(tmp_list)
        return ldb

    def test_count(self):
        ldb = self._create_ldb()
        self.assertEqual(len(ldb), 10)

    def test_init(self):
        ldb = self._create_ldb()
        # print('base list')
        #p.pprint(ldb.base_list)
        # print('')
        # print('fields list')
        #p.pprint(ldb.fieldlist)
        self.assertEqual(self._create_fn_list(),ldb.fieldlist)

    # functions:

    def test_get(self):
        test_rec_num = 5
        test_field_num = 3
        test_fn = self._getfn(test_field_num)
        test_fs = self._getfs(test_rec_num,test_field_num)
        test_fn_list, test_rec = self._create_test_dict(rec_num=test_rec_num)
        ldb = self._create_ldb()
        test_ret = ldb.get( (test_fn,test_fs))
        self.assertEqual(test_ret, test_rec)

    def test_get_rec(self):
        test_rec_num = 5
        test_field_num = 3
        test_fn = self._getfn(test_field_num)
        test_fs = self._getfs(test_rec_num,test_field_num)
        test_fn_list, test_rec = self._create_test_dict(rec_num=test_rec_num)
        ldb = self._create_ldb()
        test_ret = ldb.get( (test_fn,test_fs))

        self.assertEqual(test_ret.field1, test_rec['field1'])

        test_ret = ldb.get( (test_fn,test_fs)).field1

        self.assertEqual(test_ret, test_rec['field1'])


    def test_first(self):

        test_rec_num = 0
        test_fn_list, test_rec = self._create_test_dict(rec_num=test_rec_num)

        ldb = self._create_ldb()

        test_ret = ldb.first()
        self.assertEqual(test_ret, test_rec)


    def test_last(self):

        test_rec_num = 9
        test_fn_list, test_rec = self._create_test_dict(rec_num=test_rec_num)

        ldb = self._create_ldb()

        test_ret = ldb.last()
        self.assertEqual(test_ret, test_rec)

    def test_values(self):
        ldb = self._create_ldb()
        field_num = 2
        tmp_field_name = self._getfn(field_num)
        tmp_list = []
        for i in range(self.rec_count):
            tmp_list.append(self._getfs(i,field_num))

        tmp_ret = ldb.values(tmp_field_name)

        self.assertEqual(tmp_ret, tmp_list)


    def test_values_list(self):

        ldb = self._create_ldb()

        field_cnt = 2
        tmp_field_filter = []
        for i in range(field_cnt):
            tmp_field_filter.append(self._getfn(i))

        tmp_fn, tmp_list = self._create_dict_list(field_count=field_cnt)

        tmp_ret = ldb.values_list(tmp_field_filter)

        self.assertEqual(tmp_ret, tmp_list)


    def test_slice_fields(self):
        ldb = self._create_ldb()

        ldb2 = ldb.slice_fields(['field1',])

        self.assertEqual(len(ldb2.fieldlist), 1)
        self.assertEqual(len(ldb.fieldlist), 4)



    def test_remove_fields(self):
        ldb = self._create_ldb()

        ldb2 = ldb.remove_fields(['field1',])

        self.assertEqual(len(ldb2.fieldlist), 3)
        self.assertEqual(len(ldb.fieldlist), 4)

    def test_exists(self):

        test_rec_num = 5
        test_field_num = 3

        test_fn = self._getfn(test_field_num)
        test_fs = self._getfs(test_rec_num,test_field_num)

        #test_fn_list, test_rec = self._create_test_dict(rec_num=test_rec_num)

        ldb = self._create_ldb()
        test_ret = ldb.exists( (test_fn,test_fs))

        self.assertEqual(test_ret, True)


        test_field_num = 34

        test_fn = self._getfn(test_field_num)
        test_fs = self._getfs(test_rec_num,test_field_num)


        test_ret = ldb.exists( (test_fn,test_fs))
        self.assertEqual(test_ret, False)



    def test_getattr(self):

        ldb = self._create_ldb()

        field_num = 2
        tmp_field_name = self._getfn(field_num)
        tmp_list = []

        for i in range(self.rec_count):
            tmp_list.append(self._getfs(i,field_num))

        tmp_ret = ldb.field2

        self.assertEqual(tmp_ret, tmp_list)


    def test_del_item(self):
        #del item[index]
        ldb = self._create_ldb()
        del ldb[2]
        self.assertEqual(len(ldb), 9)




    def test_filter(self):
        ldb = self._create_ldb()
        self.assertEqual(len(ldb), 10)
        pass

    def test_extend(self):

        ldb = self._create_ldb()

        tmp_fn, tmp_list = self._create_dict_list()

        ldb.extend(tmp_list)

        self.assertEqual(len(ldb), 20)
        pass


    def test_append(self):


        test_rec_num = 9
        test_fn_list, test_rec = self._create_test_dict(rec_num=test_rec_num)

        ldb = self._create_ldb()

        ldb.append(test_rec)
        ldb.append(test_rec)
        ldb.append(**test_rec)

        self.assertEqual(len(ldb), 13)
        pass


    def test_iter(self):

        ldb = self._create_ldb()

        for i, item in enumerate(ldb):

            tmp_fn, tmp_dict = self._create_test_dict(rec_num=i)


            self.assertEqual(item, tmp_dict)

    def test_unique(self):

        test_db = [
            {'f1':'test1',
             'f2':'test2',
             'f3':'test3',
             'f4':'test4',},
            {'f1':'test11',
             'f2':'test12',
             'f3':'test13',
             'f4':'test14',},
            {'f1':'test21',
             'f2':'test22',
             'f3':'test23',
             'f4':'test24',},
            {'f1':'test31',
             'f2':'test32',
             'f3':'test33',
             'f4':'test34',},
            {'f1':'test1',
             'f2':'test42',
             'f3':'test43',
             'f4':'test44',},]

        ldb = ListDB(test_db)
        test_ret = ldb.unique('f1')

        self.assertEqual(len(test_ret), 4)

    def test_no_names_assert(self):
        rtf = RelatedTestFields()

        ldb1 = ListDB(rtf.db1, default_field='id')

        with self.assertRaises(AttributeError):
            ldb2 = ListDB(rtf.db2).relate(ldb1,foreign_key='db1_id')


    def _create_related_dbs(self):
        rtf = RelatedTestFields()

        ldb1 = ListDB(rtf.db1, default_field='id', name='db1')

        ldb2 = ListDB(rtf.db2, name='db2').relate(ldb1,foreign_key='db1_id')


        ldb1 = ldb1.relate(ldb2,foreign_key='db2_id',remote_id_field='id')

        tmp_ldb3 = ListDB(rtf.db3,name='db3').relate(ldb1,foreign_key='db1_id',remote_proxy_field_name='cst_db3_set',local_proxy_field_name='cst_db1')
        ldb3 = tmp_ldb3.relate(ldb2,foreign_key='db2_id',remote_id_field='id',remote_proxy_field_name='cst_db3_set',local_proxy_field_name='cst_db2')

        return ldb1, ldb2, ldb3, rtf

    def test_relate_test1(self):

        ldb1, ldb2, ldb3, rtf = self._create_related_dbs()
        test1_ret = ldb1.get(('id','in',('2','abc','def'))).db2

        self.assertEqual(rtf.test1_resp_db1_id_1_fld_db2, test1_ret)


    def test_relate_test2(self):

        ldb1, ldb2, ldb3, rtf = self._create_related_dbs()
        test2_ret_tmp = ldb1.get(('id','nin',('5','2','3','4')))
        test2_ret = test2_ret_tmp['db2_set']

        self.assertEqual(rtf.test2_resp_db1_id_1_fld_db2_set, test2_ret)

    def test_relate_test3(self):

        ldb1, ldb2, ldb3, rtf = self._create_related_dbs()
        test3_ret = ldb1.get(('id','1')).cst_db3_set
        self.assertEqual(rtf.test3_resp_db1_id_1_fld_cst_db3_set, test3_ret)


    def test_relate_test4(self):

        ldb1, ldb2, ldb3, rtf = self._create_related_dbs()
        test4_ret_tmp = ldb2.filter(('id','5')).get()
        test4_ret = test4_ret_tmp['db1']

        self.assertEqual(rtf.test4_resp_db2_id_5_fld_db1, test4_ret)


    def test_relate_test5(self):

        ldb1, ldb2, ldb3, rtf = self._create_related_dbs()
        test5_ret = ldb2.get(('id','5')).db1_set
        self.assertEqual(rtf.test5_resp_db2_id_5_fld_db1_set, test5_ret)


    def test_relate_test6(self):

        ldb1, ldb2, ldb3, rtf = self._create_related_dbs()
        test6_ret = ldb2.get(('id','1')).cst_db3_set
        self.assertEqual(rtf.test6_resp_db2_id_1_fld_cst_db3_set, test6_ret)


    def test_relate_test7(self):

        ldb1, ldb2, ldb3, rtf = self._create_related_dbs()

        test7_ret = ldb3.get(('id','5')).cst_db1
        self.assertEqual(rtf.test7_resp_db3_id_5_fld_cst_db1, test7_ret)


    def test_relate_test8(self):

        ldb1, ldb2, ldb3, rtf = self._create_related_dbs()
        test8_ret = ldb3.get(('id','1')).cst_db2.db1
        self.assertEqual(rtf.test8_resp_db3_id_1_fld_cst_db2_fld_db1, test8_ret)


