__author__ = 'strohl'

import copy
from .db_dict_comp import default_comparators
from .ordered_set import OrderedSet, is_iterable
from .string_helpers import flatten
from django.utils.text import slugify
from django.db import models
from collections import namedtuple
from common.utils import get_related_values, GenericMeta, get_meta_attrs, getAttrFK

from ppm.settings import ip

# noinspection PyProtectedMember
class ListDBRecord(object):
    _ldb = None

    def __init__(self, db): #, no_initial_fields=False,):

        self._ldb = db
        self._rec = {}
        # self._ldb = db
        #self._rec = {}

        #if not no_initial_fields:
        #    self._rec.update(self._ldb.fieldlist._get_base_dict)


    def __str__(self):
        return self[self._ldb.default_field]


    def __getattr__(self, field):
        if field in self._ldb.fieldlist:
            return self._rec[field]
        else:
            if self._ldb.related_manager is None:
                raise AttributeError('no fields by the name ' + field + ' exist')
            else:
                return self._ldb.related_manager.get_related(field, self._rec)

    def __setattr__(self, field, value):
        if field == '_lbl':
            if field in self._ldb.fieldlist or not self._ldb.strict:
                self.__dict__['_rec'][field] = value
            else:
                self.__dict__[field] = value
        else:
            self.__dict__[field] = value

    def __getitem__(self, field):
        if field in self._ldb.fieldlist:
            try:
                return self._rec[field]
            except KeyError:
                return None
        else:
            if self._ldb.related_manager is None:
                raise KeyError('no fields by the name ' + field + ' exist')
            else:
                return self._ldb.related_manager.get_related(field, self._rec)


    def __setitem__(self, field, value):
        if field in self._ldb.fieldlist:
            self._rec[field] = value
        else:
            raise KeyError(field + ' is not defined in the field list.')


    def __eq__(self, other):
        return self._rec == other

    def __ne__(self, other):
        return self._rec != other

    def __nonzero__(self):
        tmp_ret = False
        for rec in self._rec:
            if rec:
                tmp_ret = True
        return tmp_ret

    def __len__(self):
        return len(self._rec)

    def __repr__(self):
        tmp_str = '[{}]:{}'.format(self._ldb.default_field, str(self))
        return '{} FieldRec / {}'.format(self._ldb._name, tmp_str)


class FieldManager(object):
    listdb = None
    name = None

    def __init__(self, listdb):
        self.listdb = listdb

    def __iter__(self):
        tmp_list = self.listdb.values(self.name)
        for i in tmp_list:
            yield i

    def __contains__(self, item):
        tmp_list = self.listdb.values(self.name)
        if item in tmp_list:
            return True
        else:
            return False

    def __eq__(self, other):
        tmp_list = self.listdb.values(self.name)
        if tmp_list == other:
            return True
        else:
            return False

    def __ne__(self, other):
        tmp_list = self.listdb.values(self.name)
        if tmp_list == other:
            return True
        else:
            return False

    def __repr__(self):
        return '{} FieldManager (Fields:{})'.format(self.listdb._name, str(self.listdb.fieldlist))


# noinspection PyShadowingNames
class FieldList(OrderedSet):
    _verify_list = namedtuple('verify_list', ['in_list', 'not_in_list', 'added', 'not_in_request'])


    # noinspection PyMissingConstructor
    def __init__(self, iterable=None, force_string=True, case_sensitive=True, slugify=True):
        self.case_sensitive = case_sensitive
        self.slugify = slugify
        self.items = []
        self.map = {}

        if case_sensitive or slugify:
            force_string = True
        self.force_string = force_string

        if iterable is not None:
            self.extend(iterable)


    def _fix_iterable(self, iterable):
        tmp_list = []
        if self.force_string or self.case_sensitive or self.slugify:
            for i in iterable:
                tmp_list.append(self._fix_item(i))
            return tmp_list
        else:
            return iterable

    def _fix_item(self, item):
        if self.force_string:
            item = str(item)

        if self.slugify:
            item = slugify(item)
        elif self.case_sensitive:
            item = item.lower()

        return item


    def add(self, key):
        key = self._fix_item(key)
        return super(FieldList, self).add(key)

    def delete(self, *keys):
        tmp_keys = flatten(keys)
        tmp_rec = self._verify_list(tmp_keys)
        return FieldList(tmp_rec.not_in_request, force_string=self.force_string, slugify=self.slugify,
                         case_sensitive=self.case_sensitive)

    def verify(self, fieldlist, add=False):
        """
        Checks to make sure all items in a list are present,

        :param fieldlist: list of fields to test
        :param add: boolean flag allowing to add any new fields
        :return: named tuple of items.
        """
        ret_rec = self._verify_list
        ret_rec.added = []  # fields added (if requested)
        ret_rec.in_list = []  # in list and in request
        ret_rec.not_in_list = []  # in list, not in request
        ret_rec.not_in_request = []  # not in list, in request

        tmp_list = list(self)

        for field in self._fix_iterable(fieldlist):
            if field in self:
                ret_rec.in_list.append(field)
                tmp_list.remove(field)
            elif add:
                self.add(field)
                ret_rec.in_list.append(field)
                ret_rec.added.append(field)
                tmp_list.remove(field)
            else:
                ret_rec.not_in_list.append(field)
        ret_rec.not_in_request = tmp_list

        return ret_rec


    def extend(self, *iterables):
        for iterable in iterables:
            if is_iterable(iterable):
                for item in iterable:
                    self.add(item)
            else:
                self.add(iterable)

    def append(self, *keys):
        for key in keys:
            self.add(key)

    @property
    def _get_base_dict(self):
        tmp_dict = {}
        for item in self:
            tmp_dict[item] = None

        return tmp_dict

    def __str__(self):
        tmp_str = '],['.join(self.items)
        return '[{}]'.format(tmp_str)

    def __repr__(self):
        return 'FieldList: {}'.format(str(self))


class RelationManager(object):
    class RelClass(object):
        rel_db = None
        foreign_key = None
        remote_id_field = None
        remote_proxy_field_name = None
        local_proxy_field_name = None
        reverse = False

        def __init__(self,
                     rel_db=None,
                     foreign_key=None,
                     remote_id_field=None,
                     remote_proxy_field_name=None,
                     local_proxy_field_name=None,
                     reverse=False, ):
            self.rel_db = rel_db
            self.foreign_key = foreign_key
            self.remote_id_field = remote_id_field
            self.remote_proxy_field_name = remote_proxy_field_name
            self.local_proxy_field_name = local_proxy_field_name
            self.reverse = reverse


    # rel_rec = namedtuple('_rel_class', ['rel_db', 'foreign_key', 'remote_id_field', 'remote_proxy_field_name', 'local_proxy_field_name','reverse'],)


    def __init__(self, ldb):
        self._ldb = ldb
        self._related_dict = {}


    def setup_relations(self, rel_rec):


        if rel_rec.remote_id_field is None:
            if rel_rec.rel_db.default_field_autoconfigured:
                raise AttributeError('Auto-remote id only works with manually set default_field on db')
            else:
                rel_rec.remote_id_field = rel_rec.rel_db.default_field

        if rel_rec.remote_proxy_field_name is None:
            if self._ldb.name is None:
                raise AttributeError('No remote proxy name given AND no remote db name set')

            tmp_name = self._ldb.name + '_set'
            rel_rec.remote_proxy_field_name = tmp_name

        '''
        if rel_rec.local_proxy_field_name is None:
            if rel_rec.rel_db.name is None:
                raise AttributeError('no local proxy name given AND no local db name set')
            rel_rec.local_proxy_field_name = rel_rec.rel_db.name
        '''

        tmp_remote_field_name = rel_rec.rel_db.related_manager.setup_reverse_relations(self._ldb, rel_rec)
        rel_rec.local_proxy_field_name = tmp_remote_field_name

        if rel_rec.local_proxy_field_name in self._related_dict:
            raise AttributeError('local proxy field name (' + rel_rec.local_proxy_field_name + ') already registered')
        rel_rec.reverse = False
        self._related_dict[rel_rec.local_proxy_field_name] = rel_rec


    def setup_reverse_relations(self, from_db, rel_rec):

        rev_rel_rec = self.RelClass()

        rev_rel_rec.rel_db = from_db
        rev_rel_rec.foreign_key = rel_rec.remote_id_field
        rev_rel_rec.remote_id_field = rel_rec.foreign_key

        rev_rel_rec.local_proxy_field_name = rel_rec.remote_proxy_field_name

        '''
        if rel_rec.remote_proxy_field_name is None:
            if self._ldb.name is None:
                raise AttributeError('No remote proxy name given AND no remote db name set')

            tmp_name = self._ldb.name + '_set'
            rel_rec.remote_proxy_field_name = tmp_name
        '''

        if rel_rec.local_proxy_field_name is None:
            if self._ldb.name is None:
                raise AttributeError('no local proxy name given AND no local db name set')
            rev_rel_rec.remote_proxy_field_name = self._ldb.name
        else:
            rev_rel_rec.remote_proxy_field_name = rel_rec.local_proxy_field_name

        if rev_rel_rec.local_proxy_field_name in self._related_dict:
            raise AttributeError('remote proxy field name (' + rel_rec.local_proxy_field_name + ') already registered')

        rev_rel_rec.reverse = True
        self._related_dict[rev_rel_rec.local_proxy_field_name] = rev_rel_rec

        return rev_rel_rec.remote_proxy_field_name

    def get_related(self, field, rel_dict):

        try:
            rev_rec = self._related_dict[field]
        except KeyError:
            raise KeyError('no fields by the name ' + field + ' exist')

        try:
            loc_key = rel_dict[rev_rec.foreign_key]
        except KeyError:
            return None

        tmp_db = rev_rec.rel_db
        filter_set = (rev_rec.remote_id_field, loc_key)

        if rev_rec.reverse:
            return tmp_db.filter(filter_set)
        else:
            return tmp_db.get(filter_set)

    def __repr__(self):
        tmp_str = '],['.join(iter(self._related_dict.keys()))
        tmp_str = '[{}]'.format(tmp_str)
        return "{} RelationManager (managed fields: {} )".format(self._ldb.name, tmp_str)


class ListDB(object):
    default_default_field_name = 'default_field'
    comparators = default_comparators
    name = None
    default_name = '_list_db_'
    default_field = None
    default_field_autoconfigured = False

    def __init__(self, *iterables, **kwargs):
        """
        :param fieldlist: field list, can also be auto-generated from iterables passed in init
            if no fields are passed, strict is overridden for any importing records.
        :param default_field: default field name if no info is found or if a str is requested
        :param strict: boolean flag to allow adding new fields when found (defaults to True)
        :param *iterables: any number of iterables to be added to the listDB
        :param name: string name of db
        """

        self.fieldlist = FieldList()

        self.base_list = kwargs.pop('_base_list', [])
        self.fieldlist.extend(kwargs.pop('fieldlist', []))
        self.strict = kwargs.pop('strict', True)
        self.default_field = kwargs.pop('default_field', None)
        self.name = kwargs.pop('name', None)

        if self.default_field is None:
            self.default_field_autoconfigured = True
            try:
                self.default_field = self.fieldlist[0]
            except (IndexError, TypeError):
                pass

        if iterables:
            tmp_strict = self.strict
            if not self.fieldlist and self.strict:
                self.strict = False
            self.extend(*iterables)
            self.strict = tmp_strict

        if not self.default_field:
            try:
                self.default_field = self.fieldlist[0]
            except (IndexError, TypeError):
                self.default_field = self.default_default_field_name

        self.comparator_dict = {}
        self.field_manager = None
        self._related_manager = None

        # self.field_manager = FieldManager(self)

    def __repr__(self):

        if self.name is not None:
            tmp_name = self.name
        else:
            tmp_name = '<unnamed_db>'

        return '{} ListDB (fields: {})'.format(tmp_name, '')


    @property
    def related_manager(self):
        if self._related_manager is None:
            self._related_manager = RelationManager(self)
        return self._related_manager

    @property
    def _name(self):
        if self.name is not None:
            return self.name
        else:
            return '<unnamed_db>'

    def relate(self, rel_db, foreign_key, remote_id_field=None, remote_proxy_field_name=None,
               local_proxy_field_name=None):
        """
        Sets up a one to many relationship with another table.
        :param rel_db:  the other table
        :param foreign_key: the local ID field
        :param remote_id_field: the remote ID field that will be matched to
        :param local_proxy_field_name: the local field that will be added to relate the other table
        :param remote_proxy_field_name: the remote field that willb e added to relate to this table
        :return:
        """

        tmp_rec = self.related_manager.RelClass(rel_db=rel_db,
                                                foreign_key=foreign_key,
                                                remote_id_field=remote_id_field,
                                                remote_proxy_field_name=remote_proxy_field_name,
                                                local_proxy_field_name=local_proxy_field_name,
                                                reverse=False)

        self.related_manager.setup_relations(tmp_rec)

        return self

    def _setup_comparators(self):
        for c in self.comparators:
            self.comparator_dict[c.comparison_flag] = c

    def _cf(self, field):
        if field not in self.fieldlist:
            raise AttributeError(field, ': not in list of fields')
        return field

    def _new_obj(self, new_list, fieldlist=None):
        if not fieldlist:
            fieldlist = self.fieldlist
        default_field = self.default_field
        strict = self.strict

        return ListDB(_base_list=new_list,
                      fieldlist=fieldlist,
                      default_field=default_field,
                      strict=strict)


    def get_dict(self, *filterparams, default=None):
        tmp_ret = self.get(*filterparams, default=default)
        return tmp_ret._rec

    def get(self, *filterparams, default=None):
        tmp_list = self._get_filtered_list(filterparams)
        if len(tmp_list) > 1:
            if not default:
                raise ValueError('Too many objects returned')
            else:
                return default
        return tmp_list[0]

    def first(self):
        return self.base_list[0]

    def last(self):
        return self.base_list[len(self.base_list) - 1]

    def values(self, field=None):
        """
        Returns a list of items in one field
        :param field: string field name
        :return: list
        """
        if not field:
            field = self.default_field

        tmp_list = []
        for item in self.base_list:
            tmp_list.append(item[self._cf(field)])
        return tmp_list


    def values_list(self, fields=None):
        """
        Returns a list of dictionaries with fields matching the ones requested
        :param fields: list of fields to be returned
        :return: a list of dictionary entries.
        """
        if not fields:
            return self.base_list
        else:
            tmp_list, tmp_fields = self._filter_fields(fields)
            return tmp_list


    # def _test_in_out(self, test_str, in_list, out_list):
    #     if not in_list:
    #         in_list = []
    #     elif isinstance(in_list, str):
    #         in_list = [in_list, ]
    #
    #     if not out_list:
    #         out_list = []
    #     elif isinstance(out_list, str):
    #         out_list = [out_list, ]
    #
    #     if test_str in in_list:
    #         if test_str not in out_list:
    #             return True
    #
    #     return False

    def _fix_fields(self, fields, reverse=False):
        tmp_rec = self.fieldlist.verify(fields)

        if tmp_rec.not_in_list:
            raise AttributeError(tmp_rec.not_in_list, ': not valid fields')

        if reverse:
            return tmp_rec.not_in_request
        else:
            return tmp_rec.in_list


    def _filter_fields(self, fields, reverse=False):
        fields = self._fix_fields(fields, reverse)
        tmp_list = []

        for rec in self.base_list:
            tmp_dict = self._start_rec() #no_initial_fields=True)
            for field in fields:
                tmp_dict[field] = rec[field]
            tmp_list.append(tmp_dict)
        return tmp_list, fields

    def slice_fields(self, fields=None):
        return self._new_obj(*self._filter_fields(fields))


    def remove_fields(self, fields=None):
        return self._new_obj(*self._filter_fields(fields, reverse=True))


    def __getitem__(self, item):
        return self.base_list[item]

    def __setitem__(self, key, value):
        self.base_list[key] = self._make_rec(value)

    def exists(self, *filterparams):
        for rec in self.base_list:
            if self._filter_list_check(rec, filterparams):
                return True
        return False

    def __getattr__(self, item):
        if not self.field_manager:
            self.field_manager = FieldManager(self)

        self.field_manager.name = self._cf(item)

        return self.field_manager

    def __delitem__(self, key):
        del self.base_list[key]

    def _filter_check(self, rec, *args):
        if not self.comparator_dict:
            self._setup_comparators()
        if len(args) == 2:
            field = args[0]
            comparison = self.comparator_dict['eq']
            compare_to = args[1]
        elif len(args) == 3:
            field = args[0]
            comparison = self.comparator_dict[args[1]]
            compare_to = args[2]
        elif len(args) == 1:
            if rec[args[0]]:
                return True
            else:
                return False
        else:
            raise AttributeError('too many arguments passed')

        try:
            return comparison.compare(rec[field], compare_to)
        except KeyError:
            return False

    def unique(self, field):
        if field in self.fieldlist:
            tmp_match_list = []
            tmp_rec_list = []
            for rec in self.base_list:
                if rec[field] not in tmp_match_list:
                    tmp_rec_list.append(rec)
                    tmp_match_list.append(rec[field])

            return self._new_obj(tmp_rec_list)

        else:
            raise AttributeError(field, ' : not in field list')


    def _filter_list_check(self, rec, filter_list):
        found = False
        for filter in filter_list:
            if self._filter_check(rec, *filter):
                found = True
        return found

    def _get_filtered_list(self, filterparams):

        if len(filterparams) > 0:
            tmp_list = []
            for rec in self.base_list:
                if self._filter_list_check(rec, filterparams):
                    tmp_list.append(rec)

            return tmp_list
        else:
            return self

    def filter(self, *filterparams):
        """

        :param filterset: pass a tuple for the filter.
                ('fieldname', ['comparison',] compare_to')
                valid comparisons are:
                 'eq' : Equals  <-- default if not given
                 'in' : In
                 'not' : Does not equal
                 'nin' : not in
                 'starts' : starts with
                 'ends' : ends with
        :return:
        """

        tmp_list = self._get_filtered_list(filterparams)
        if len(tmp_list) > 0:
            return self._new_obj(tmp_list)
        else:
            return None


    def __len__(self):
        return len(self.base_list)

    def extend(self, *args):
        for arg in args:
            for item in arg:
                self.append(item)
        return self

    def append(self, *args, **kwargs):
        self.base_list.append(self._make_rec(*args, **kwargs))
        return self

    def __iter__(self):
        for i in self.base_list:
            yield i

    def _start_rec(self):
        rec = ListDBRecord(self)
        return rec


    def _make_rec(self, *args, **kwargs):


        tmp_dict = self._start_rec()

        # if there is just one argument
        if len(args) == 1 and not kwargs:
            tmp_arg = copy.deepcopy(args[0])
            args = []

            # try adding info as if from a dict
            found_field = False
            if self.fieldlist:
                for f in self.fieldlist:
                    try:
                        tmp_dict[f] = tmp_arg.pop(f)
                        found_field = True
                    except KeyError:
                        pass

            # try adding the dict fields to the dict
            if tmp_arg and not self.strict:
                try:
                    for key, item in tmp_arg.items():
                        self.fieldlist.append(key)
                        tmp_dict[key] = item
                    found_field = True
                except KeyError:
                    pass

            if not found_field:
                if not self.default_field:
                    self.default_field = self.default_default_field_name
                self.fieldlist.append(self.default_field)
                tmp_dict[self.default_field] = tmp_arg

        if self.fieldlist and args:
            for item in zip(self.fieldlist, args):
                tmp_dict[item[0]] = item[0]

        for key, item in kwargs.items():
            if key in self.fieldlist:
                tmp_dict[key] = item
            elif not self.strict:
                tmp_dict[key] = item
                self.fieldlist.append(key)

        return tmp_dict

    def __eq__(self, other):
        return self.base_list == other

    def __ne__(self, other):
        return other != self.base_list


class TableDbDjangoModelDefinition(object):
    """
    name = ''  # will default to the actual model name
    fields = ('field','field','field',{'fieldname':another_def_class})
    rename_fields = {'field':'new_name','field':'new_name'}
    pk_field_name = 'pk'  # will default to 'pk'
    default_field = 'pk'  # will default to 'pk'
    fk_fields = [{ 'fk_field':'fieldname',
                   'local_proxy_name':'fieldname',
                   'remote_proxy_name':'fieldname',
                   'remote_id':'fieldname',
                   'remote_db':another_def_class,},
    }]

    """
    pk_field_name_format = '__{}_pk__'
    fk_field_name_format = '__{}{}_fk__'
    remote_proxy_field_name_format = '{}{}_set'
    local_proxy_field_name_format = '{}{}'
    current_pk = 0
    select_related_prefix = ''

    class Meta:
        name = None
        pk_field_name = 'pk'
        default_field = 'pk'
        fields = None
        rename_fields = None
        fk_field_defs = None



    class DataFieldRec():
        rec_type = 'Field'
        name = None
        list_db_name = None
        db_rec = None
        key = None
        proxy_field = None
        model_def = None
        select_related_list_name = ''


        def __init__(self, fieldname):
            # self.db_rec = db_rec
            self.name = fieldname
            # self.list_name = self.db_rec.field_prefix + fieldname



    def __init__(self, factory):


        self.name = None
        self.factory = factory
        self.pk_field_name = 'pk'
        self.default_field = 'pk'
        self.fields = []
        self.rename_fields = []
        self.fk_field_defs = {}
        self.list_db = None

        self._meta = copy.deepcopy(self.Meta())
        get_meta_attrs(self._meta,self)
        #self._meta.get_meta_attrs(self)
        self.fk_fields = {}
        self.set_fields = {}
        self.relations_list = []
        self.fieldrec_def = {}

        ip.pl('finished init list_db: ',self.name).a()


    '''
    def fill_in_blanks(self,qs):
        if self.name is None:
            self.name = qs._meta.model_name
    '''
    '''
    def make_relations(self):

        for rel in self.fk_field_defs:
            remote_db =  rel['remote_db']

            rel_rec = RelationManager.RelClass(
                rel_db = remote_db.list_db,
                foreign_key = rel['fk_field'],
                remote_id_field=rel['remote_id'],
                remote_proxy_field_name=rel['remote_proxy_name'],
                local_proxy_field_name=rel['local_proxy_name'],
                reverse=False)

            self.relations_list.append(rel_rec)
            self.fk_fields[rel_rec.local_proxy_field_name] = rel_rec
            rel_rec.rel_db.set_fields[rel_rec.remote_proxy_field_name] = rel_rec

    '''
    def make_list_db(self):

        ip.pl('make list_db: ',self.name)

        # make database
        self.list_db = ListDB(fieldlist=self.list_db_fieldlist, default_field=self.default_field, name=self.name)

    def make_related(self):

        ip.pl('relate lists',self.name)

        # make relationships
        for rel in self.relations_list:

            rel.rel_db = self.list_db

            self.list_db.related_manager.setup_relations(rel)

    @property
    def list_db_fieldlist(self):
        tmp_list = []
        for rec in iter(self.fieldrec_def.values()):
            if rec.rec_type == 'field':
                tmp_list.append(rec.list_db_name)
        return tmp_list

    @property
    def select_related_fields(self):
        tmp_list = []

        for rec in iter(self.fieldrec_def.values()):
            if rec.rec_type in ('fk', 'set'):
                tmp_list.extend(rec.model_def.select_related_fields)
            elif rec.rec_type == 'field':
                if not self.select_related_prefix == '':
                    tmp_list.append(rec.select_related_list_name)
        return tmp_list


    def setup(self, select_related_prefix = ''):
        self.select_related_prefix = select_related_prefix

        ip.pl('setup list_dbs: ',self.name)

        # read fk_field dictionaries
        if self.fk_field_defs:
            for fieldname, rel in iter(self.fk_field_defs.items()):

                #fk_field = rel

                rel_rec = RelationManager.RelClass(
                    rel_db = self.factory[rel['remote_db']].list_db,
                    foreign_key = rel.get('fk_field',fieldname+'_id'),
                    remote_id_field=rel.get('remote_id','pk'),
                    remote_proxy_field_name=rel.get('remote_proxy_name',fieldname+'_set'),
                    local_proxy_field_name=rel.get('local_proxy_name',fieldname),
                    reverse=False)
                rel_rec.remote_db_def = self.factory[rel['remote_db']]

                self.relations_list.append(rel_rec)
                self.fk_fields[rel_rec.local_proxy_field_name] = rel_rec
                rel_rec.remote_db_def.set_fields[rel_rec.remote_proxy_field_name] = rel_rec


        # create pk field
        if self.pk_field_name not in self.fields:
            tmp_fieldrec = self.DataFieldRec(self.pk_field_name)
            tmp_fieldrec.list_db_name = self.pk_field_name
            tmp_fieldrec.rec_type='field'

            self.fieldrec_def[self.pk_field_name] = tmp_fieldrec

        # iter through fields and create them.
        for field in self.fields:
            tmp_fieldrec = self.DataFieldRec(field)
            tmp_select_related_prefix = self.select_related_prefix+"__"+field

            if field in self.rename_fields:
                tmp_fieldrec.list_db_name = self.rename_fields[field]
            else:
                tmp_fieldrec.list_db_name = field

            tmp_fieldrec.select_related_list_name =self.select_related_prefix+field


            if field in self.set_fields:
                tmp_fieldrec.rec_type='set'
                tmp_fieldrec.model_def = self.set_fields[field].rel_db
                tmp_fieldrec.related_rec = self.set_fields[field]
                # self.set_fields[field].remote_db_def.setup(tmp_select_related_prefix)
            elif field in self.fk_fields:
                tmp_fieldrec.rec_type = 'fk'
                tmp_fieldrec.model_def = self.fk_fields[field].rel_db
                tmp_fieldrec.related_rec = self.fk_fields[field]
                # self.set_fields[field].remote_db_def.setup(tmp_select_related_prefix)
            else:
                tmp_fieldrec.rec_type = 'field'

            self.fieldrec_def[field] = tmp_fieldrec


        #self.make_list_db()

        #self.make_related()


    def generate(self, qs):
        self.setup()
        tmp_ret = self.get_data(qs)

        return tmp_ret

    def get_data(self,qs):

        ip.pl('get_data_for lists: ', self.name)

        tmp_all_lists_dict = {}
        #rec_pk = None

        for rec in qs:

            tmp_rec_dict = {}

            for field, fieldrec in iter(self.fieldrec_def.items()):
                tmp_field_data = getAttrFK(rec, field)

                if fieldrec.rec_type == 'field':
                    tmp_rec_dict[field] = tmp_field_data
                elif fieldrec.rec_type == 'fk':
                    tmp_fieldname = fieldrec.name+'_id'
                    tmp_rec_dict[fieldrec.related_rec.remote_proxy_field_name] = getAttrFK(rec,tmp_fieldname)

                    tmp_all_lists_dict[self.name] = fieldrec.rel_db.get_data(rec)

            self.list_db.append(tmp_rec_dict)
        return tmp_all_lists_dict


class django_listdb_factory():


    def __init__(self,
                 def_set,
                 query_set,
                 root_def,
                 select_related=True,
                 prefetch_related=False):
        self.model_defs = {}
        for mod in def_set:

            ip.push().pl('factory - loading defs')

            tmp_mod = mod(self)
            #mod.setup()
            self.model_defs[tmp_mod.name] = tmp_mod

            if select_related:
                self.initial_queryset = query_set.select_related(*tmp_mod.select_related_fields)

            elif prefetch_related:
                self.initial_queryset = query_set.prefetch_related(*tmp_mod.select_related_fields)

            else:
                self.initial_queryset = query_set

            ip.pop()

        self.root_def = self[root_def]

        self.make_db()

    def make_db(self):

        ip.pl('factory-make-db')

        for db_name, db in iter(self.model_defs.items()):
            db.setup()

        for db_name, db in iter(self.model_defs.items()):
            db.make_list_db()

        for db_name, db in iter(self.model_defs.items()):
            db.make_related()


        self.root_def.get_data(self.initial_queryset)

    def __getattr__(self, item):
        try:
            return self.model_defs[item].list_db
        except KeyError:
            return AttributeError('No List DB by the name '+item)

    def __getitem__(self, item):
        return self.model_defs[item]



'''

# noinspection PyPep8Naming
class Django_ListDB_Factory(object):
    max_recursive_depth = 4


    class FieldRec(object):
        rec_type = 'Field'
        name = None
        list_name = None
        db_rec = None

        def __init__(self, db_rec, fieldname):
            self.db_rec = db_rec
            self.name = fieldname
            self.list_name = self.db_rec.field_prefix + fieldname

    class DBMaster(object):

        pk_field_name_format = '__{}_pk__'
        fk_field_name_format = '__{}{}_fk__'
        remote_proxy_field_name_format = '{}{}_set'
        local_proxy_field_name_format = '{}{}'
        current_pk = 0


        def __init__(self, dbrec):
            self.name = dbrec.name
            self.factory = dbrec.factory
            self.related_dict = {}
            self.pk_field = self.pk_field_name_format.format(self.name)
            self.local_fieldlist = dbrec.local_fieldslist

            if dbrec.parent is not None:
                self.add_relation(dbrec)

        @property
        def get_db_list_dict(self):
            return {self.name:self.list_db}

        @property
        def get_pk(self):
            self.current_pk += 1
            return self.current_pk

        def _get_rel_field_suffix(self, db_name):
            for cnt in range(100):
                tmp_field_name = self.local_proxy_field_name_format.format(db_name, cnt)
                if tmp_field_name not in self.related_dict:
                    return cnt

            raise AttributeError('field naming inf loop problem')


        def add_relation(self, dbrec):
            rel_rec = RelationManager.RelClass()

            if dbrec.name != self.name:
                raise AttributeError('names do not match')

            if not dbrec.set:
                remote_db_rec = dbrec.parent
                # local_db_rec = dbrec
            else:
                remote_db_rec = dbrec
                # local_db_rec = dbrec.parent

            rel_rec.rel_db = remote_db_rec

            remote_db_name = remote_db_rec.name
            tmp_suffix = self._get_rel_field_suffix(remote_db_name)

            rel_rec.foreign_key = self.fk_field_name_format.format(remote_db_name, tmp_suffix)

            rel_rec.local_proxy_field_name = self.local_proxy_field_name_format.format(remote_db_name, tmp_suffix)
            rel_rec.remote_id_field = remote_db_rec.pk_field
            rel_rec.remote_proxy_field_name = self.remote_proxy_field_name_format.format(remote_db_name, tmp_suffix)
            rel_rec.reverse = False

            remote_db_rec.master.related_dict[dbrec.name] = rel_rec

            return remote_db_rec.master


    # noinspection PyAttributeOutsideInit,PyProtectedMember
    class DBRec(object):
        factory = None
        rec_type = 'DB'
        field_name = None
        name = None
        list_name = None
        parent_obj = None
        field_prefix = ''
        set = True
        master = None


        def __init__(self, factory, fieldlist, obj, parent=None, fieldname=None, field_prefix=''):
            self.fieldlist = fieldlist
            self.parent = parent
            self.obj = obj
            self.name = obj._meta.model_name
            self.field_dict = {}
            self.fieldname = fieldname
            self.field_prefix = field_prefix
            self.factory = factory
            self.local_fieldslist = []
            self.relation_manager = None

            if isinstance(obj, models.QuerySet):
                self.set = True
                tmp_obj = obj[0]
            else:
                self.set = False
                tmp_obj = obj

            self.add_to_db_dict()

            for field in fieldlist:

                if isinstance(field, str):
                    self.field_dict[field] = self.factory.FieldRec(self, field)
                    self.local_fieldslist.append(field)
                elif isinstance(field, dict):
                    fld_name, sub_fields_list = field.popitem()
                    self.local_fieldslist.append(fld_name)

                    sub_obj = getattr(tmp_obj, fld_name)

                    tmp_prefix = self.field_prefix + fld_name + '__'

                    self.field_dict[field] = self.factory.DBRec(self.factory, sub_fields_list, sub_obj, self, fld_name, tmp_prefix)

        def add_to_db_dict(self):

            self.master = self.factory.db_dict[self.name]
            if self.name in self.factory.db_dict:
                self.factory.db_dict[self.name].add_relation(self)
                self.relation_master = None
            else:
                self.relation_master = self.factory.db_dict[self.name] = self.factory.DBMaster(self)


        @property
        def pk_field(self):
            return self.master.pk_field

        @property
        def pk(self):
            return self.master.get_pk

        @property
        def fk_field(self):
            if self.relation_master == self.master:
                return self.relation_master.related_dict[self.name].foreign_key
            else:
                return None

    def __init__(self, query_set=None, field_list=None, select_related=True, prefetch_related=False):
        """
        :param query_set:
        :param field_list: example:
                ('fieldname','fieldname','fieldname',{'fieldname':('fieldname',),{'fieldname':('fieldname','fieldname'}},'fieldname')
        :param select_related:
        :param prefetch_related:
        :return: [list of ListDB's] or ListDB
        """
        self.initial_qs = query_set
        self.initial_field_list = field_list
        self.select_related = select_related
        self.prefetch_related = prefetch_related
        self.full_field_list = None
        self.db_dict = {}
        self.root_db_rec = None


    def extract_fields_list(self, fieldlist, field_prefix=''):
        tmp_full_field_list = []
        for field in fieldlist:
            if isinstance(field, str):
                tmp_full_field_list.append(field_prefix+field)
            elif isinstance(field, dict):
                fld_name, sub_fields_list = field.popitem()
                tmp_full_field_list.append(fld_name)
                tmp_prefix = field_prefix + fld_name + '__'
                tmp_full_field_list.extend(self.extract_fields_list(sub_fields_list,field_prefix = tmp_prefix ) )

        return tmp_full_field_list

    def make_databases(self):

        # make databases
        for db_name, db_rec in iter(self.db_dict.items()):
            tmp_db = ListDB(fieldlist=db_rec.local_fieldlist, default_field=db_rec.pk_field, name=db_rec.name)
            self.db_dict[db_name].list_db = tmp_db

        # make relationships
        for db_name, db_rec in iter(self.db_dict.items()):
            for rel in iter(db_rec.related_dict.values()):
                rel.db_rec = self.db_dict[rel.db_rec].list_db
                self.db_dict[db_name].list_db.related_manager.setup_relations(rel.db_rec)


    def _load_set(self, qs=None, db_rec=None, rec_fk=None):
        rec_pk = None
        if qs is None:
            qs = get_related_values(self.initial_qs,
                                    self.full_field_list,
                                    self.select_related,
                                    self.prefetch_related)
        if db_rec is None:
            db_rec = self.root_db_rec

        list_db = db_rec.master.list_db

        for rec in qs:
            # self._load_rec(rec, list_db, db_rec, rec_pk)

            tmp_rec_dict = {}
            rec_pk = db_rec.pk
            tmp_rec_dict[db_rec.pk_field] = rec_pk

            for field in db_rec.field_list:
                tmp_field_data = getattr(rec, field)

                if field.rec_type == 'Field':
                    tmp_rec_dict[field] = tmp_field_data
                elif field.rec_type == 'DB':
                    if db_rec.set:
                        rec_fk = self._load_set(tmp_field_data, field, None)
                    else:
                        rec_fk = self._load_set(tmp_field_data, field, rec_pk)

            if rec_fk:
                tmp_rec_dict[db_rec.fk_field] = rec_fk


            list_db.add(tmp_rec_dict)

        return rec_pk


    def generate(self, query_set=None, field_list=None, select_related=True, prefetch_related=False):
        if query_set:
            self.initial_qs = query_set
        if field_list:
            self.initial_field_list = field_list
        if select_related:
            self.select_related = select_related
        if prefetch_related:
            self.prefetch_related = prefetch_related

        if self.initial_field_list:
            self.full_field_list = self.extract_fields_list(self.initial_field_list)

        else:
            raise AttributeError("no field list defined")
            # TODO: work on auto field list generator

        self.root_db_rec = self.DBRec(self, self.full_field_list, query_set)

        self.make_databases()

        self._load_set()

        tmp_ret_dict = {}
        for db in iter(self.db_dict.values()):
            tmp_ret_dict.update(db.list_db)

        return tmp_ret_dict
'''
