from django.contrib.auth.models import Permission
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django_dynamic_fixture import G
import itertools
import mock
from ereports.engine.cache import DummyCacheManager, DatasourceCacheManager
from ereports.engine.columns import Column, CalcColumn, ColumnCallable, BooleanColumn, OptionalColumn
from ereports.engine.datasource import Datasource, RecordFilteredError
from ereports.tests import app
from ereports.tests.app.models import SimpleDemoModel, DemoOptionalModel
from ereports.utils import get_verbose_name


def test_get_verbose_name():
    l = get_verbose_name(SimpleDemoModel, 'char')
    assert l == 'Character'


class TestDatasource(TestCase):
    def test_inherit(self):
        TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission, 'columns': ['id']})
        ds = TestDatasource.as_datasource()
        self.assertIsInstance(list(ds), list)

    def test_inherit_exception(self):
        TestDatasource = type('TestDatasource', (Datasource, ), {'model': Permission, 'columns': ['id']})
        with self.assertRaises(TypeError):
            kwargs = dict(wrong='oops')
            TestDatasource.as_datasource(**kwargs)

    def test_inherit_improperlyconfigured(self):
        TestDatasource = type('TestDatasource', (Datasource, ), {'columns': ['id']})
        with self.assertRaises(ImproperlyConfigured):
            kwargs = dict(model=None)
            TestDatasource.as_datasource(**kwargs)

    def test_create_from_model(self):
        instances = G(SimpleDemoModel, n=2, char='1', integer1=1, integer2=2, boolean=True)

        self.assertEquals(len(instances), 2)

        ds = Datasource.as_datasource(model=SimpleDemoModel)

        self.assertSequenceEqual([c.name for c in ds.columns], ['id', 'char', 'integer1', 'integer2', 'boolean'])
        self.assertSequenceEqual([c.title for c in ds.columns],
                                 ['ID', 'Character', 'Integer #1', 'Integer #2', 'Boolean'])
        self.assertSequenceEqual(ds, [(instances[0].pk, u'1', 1, 2, True), (instances[1].pk, u'1', 1, 2, True)])

    def test_columns(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=1)
        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      columns=[Column('char', 'AAA'), Column('integer1')])

        self.assertSequenceEqual([c.name for c in ds.columns], ['char', 'integer1'])
        self.assertSequenceEqual([c.title for c in ds.columns], ['AAA', 'Integer #1'])
        self.assertSequenceEqual(ds, [(u'abc', 1), (u'abc', 1)])

    def test_list_columns(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=1, integer2=3)
        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      columns=[('char', Column), ('integer1', Column)])
        self.assertSequenceEqual([c.name for c in ds.columns], ['char', 'integer1'])
        self.assertSequenceEqual([c.title for c in ds.columns], ['Character', 'Integer #1'])
        self.assertSequenceEqual(ds, [(u'abc', 1), (u'abc', 1)])

    def test_manipulator(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=1)
        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      columns=[Column('char', manipulator=lambda v: v.upper())])
        self.assertSequenceEqual(ds, [(u'ABC', ), (u'ABC', )])

    def test_custom_column_from_string(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=1, integer2=3)
        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      extra_column=lambda obj: 'extra_value',
                                      columns=[Column('integer1'),
                                               'integer2',
                                               CalcColumn(['integer1', 'integer2'])])
        self.assertSequenceEqual(ds, [(1, 3, 4), (1, 3, 4)])

    def test_create_from_queryset(self):
        instances = G(SimpleDemoModel, n=2, char='abc')

        self.assertEquals(len(instances), 2)

        ds = Datasource.as_datasource(queryset=SimpleDemoModel.objects.all(),
                                      columns=['id', 'char'])

        self.assertSequenceEqual([c.name for c in ds.columns], ['id', 'char'])
        self.assertSequenceEqual([c.title for c in ds.columns], ['ID', 'Character'])
        self.assertSequenceEqual(ds, [(instances[0].pk, u'abc'), (instances[1].pk, u'abc')])

    def test_get_col_by_name(self):
        G(SimpleDemoModel, n=2, char='abc')
        ds = Datasource.as_datasource(queryset=SimpleDemoModel.objects.all())
        self.assertSequenceEqual([u'abc', u'abc'], [row.char for row in ds])
        self.assertSequenceEqual([u'abc', u'abc'], [row['char'] for row in ds])

    def test_filter_queryset(self):
        instances = G(SimpleDemoModel, n=5, char='abc')

        self.assertEquals(len(instances), 5)

        ds = Datasource.as_datasource(queryset=SimpleDemoModel.objects.all(),
                                      columns=['id', 'char'])
        ds.add_filters(id__gt=instances[2].pk)
        self.assertSequenceEqual(ds, [(instances[3].pk, u'abc'), (instances[4].pk, u'abc')])

    def test_post_filter(self):
        instances = G(SimpleDemoModel, n=5, char='abc')
        ds = Datasource.as_datasource(queryset=SimpleDemoModel.objects.all(),
                                      columns=['id', 'char'])
        ds.add_filters(id__gt=instances[2].pk)
        self.assertSequenceEqual(ds, [(instances[3].pk, u'abc'), (instances[4].pk, u'abc')])

    def test_cachemanager(self):
        ds = Datasource.as_datasource(model=SimpleDemoModel, use_cache=False)
        self.assertIsInstance(ds.cache_manager, DummyCacheManager)

        ds = Datasource.as_datasource(model=SimpleDemoModel, use_cache=True)
        self.assertIsInstance(ds.cache_manager, DatasourceCacheManager)

    # def test_internal_cache(self):
    #     G(SimpleDemoModel, n=10, char='abc')
    #     ds = Datasource.as_datasource(model=SimpleDemoModel, columns=[Column('filter_source')])

    def test_custom_filter(self):
        G(SimpleDemoModel, n=10, char='abc')
        app.models.counter = itertools.count()
        ds = Datasource.as_datasource(model=SimpleDemoModel, columns=[Column('filter_source')])
        ds._get_queryset = mock.Mock(wraps=ds._get_queryset)
        ds._create_result_cache = mock.Mock(wraps=ds._create_result_cache)

        def filter_odd(row):
            if not row.filter_source.value % 2:
                raise RecordFilteredError

        ds.add_custom_filter(filter_odd)
        list(ds)
        list(ds)
        self.assertSequenceEqual(ds, [(1,), (3,), (5,), (7,), (9,)])
        assert ds._get_queryset.call_count == 1
        assert ds._create_result_cache.call_count == 1


class TestColumns(TestCase):
    def test_custom_column_callable(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20)

        def _custom_callable(obj, ds):
            return obj.integer1 + 100

        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      columns=[Column('integer1'),
                                               Column('integer2'),
                                               ColumnCallable(_custom_callable)])

        self.assertSequenceEqual(ds, [(10, 20, 110), (10, 20, 110)])

    def test_custom_column(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=1, integer2=3)
        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      columns=[Column('integer1'), Column('integer2'),
                                               CalcColumn(['integer1', 'integer2'])])
        self.assertSequenceEqual(ds, [(1, 3, 4), (1, 3, 4)])

    def test_custom_column_from_datasource_method(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=1, integer2=3)
        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      extra_column=lambda obj: 'extra_value',
                                      columns=[Column('integer1'),
                                               Column('integer2'),
                                               Column('extra_column'),
                                               CalcColumn(['integer1', 'integer2'])])
        self.assertSequenceEqual(ds, [(1, 3, 'extra_value', 4), (1, 3, 'extra_value', 4)])

    def test_boolean_column_no(self):
        G(SimpleDemoModel, n=2, boolean=False)
        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      columns=[BooleanColumn('boolean')])
        self.assertSequenceEqual([c.title for c in ds.columns], ['Boolean'])
        self.assertSequenceEqual(ds, [(False,), (False,)])

    def test_booleanyesno_column_yes(self):
        G(SimpleDemoModel, n=2, boolean=True)
        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      columns=[BooleanColumn('boolean')])
        self.assertSequenceEqual([c.title for c in ds.columns], ['Boolean'])
        self.assertSequenceEqual(ds, [(True,), (True,)])

    def test_optional_column(self):
        G(DemoOptionalModel, n=2, name='abc', user=G(User, n=1, first_name='user1'))
        ds = Datasource.as_datasource(model=DemoOptionalModel,
                                      columns=[Column('name'), OptionalColumn('user.first_name')])
        self.assertSequenceEqual([c.title for c in ds.columns], ['name', 'first name'])
        self.assertSequenceEqual(ds, [('abc', 'user1',), ('abc', 'user1')])

    def test_optional_column_optional(self):
        G(DemoOptionalModel, n=2, name='abc', user=None)
        ds = Datasource.as_datasource(model=DemoOptionalModel,
                                      columns=[Column('name'), OptionalColumn('user.first_name')])
        self.assertSequenceEqual([c.title for c in ds.columns], ['name', 'first name'])
        self.assertSequenceEqual(ds, [('abc', '',), ('abc', '')])
