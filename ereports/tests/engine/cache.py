import pickle
from django.contrib.contenttypes.models import ContentType
from django_dynamic_fixture import G
import mock
from django.core import cache
from django.contrib.auth.models import Permission
from django.test.testcases import TestCase, _AssertNumQueriesContext
from ereports.engine.cache import monitor_model, reset, DatasourceCacheManager
from ereports.engine.datasource import Datasource
from django.db import connections
from ereports.engine.report import BaseReport
from ereports.tests.app.models import SimpleDemoModel

locmem_cache = cache.get_cache('django.core.cache.backends.locmem.LocMemCache')
dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')


class TestDatasourceCacheManager(TestCase):
    def test_get_key(self):
        manager = DatasourceCacheManager()
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        dummy_cache.clear()
        with mock.patch('ereports.engine.cache._cache', dummy_cache):
            monitor_model(Permission)
            reset(Permission)

            TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission,
                                                                    'dependent_models': [ContentType],
                                                                    'use_cache': True,
                                                                    'columns': ['id', 'name']})
            ds1 = TestDatasource.as_datasource()
            k = manager.get_key(ds1)
            self.assertTrue(k.startswith('ereports/1/django.contrib.auth.models.Permission/0'
                                         '/django.contrib.contenttypes.models.ContentType/0/'), k)

    def test_generation(self):
        locmem_cache = cache.get_cache('django.core.cache.backends.locmem.LocMemCache')
        manager = DatasourceCacheManager()
        with mock.patch('ereports.engine.cache._cache', locmem_cache):
            monitor_model(Permission)
            reset(Permission)

            TestDatasource = type('TestDatasource', (Datasource,),
                                  {'model': Permission,
                                   'dependent_models': [ContentType],
                                   'use_cache': True,
                                   'columns': ['id', 'name']})

            ds1 = TestDatasource.as_datasource()
            k1 = manager.get_key(ds1)
            self.assertTrue(k1.startswith('ereports/1/django.contrib.auth.models.Permission/0'
                                          '/django.contrib.contenttypes.models.ContentType/0/'), k1)
            Permission.objects.filter(pk=1).delete()
            k2 = manager.get_key(ds1)
            self.assertTrue(k2.startswith('ereports/1/django.contrib.auth.models.Permission/1'
                                          '/django.contrib.contenttypes.models.ContentType/0/'), k2)


class TestCacheDatasource(TestCase):
    def test_queryset_no_hit_db(self):
        TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission,
                                                                'use_cache': False,
                                                                'columns': ['id', 'name']})
        ds = TestDatasource.as_datasource()
        with _AssertNumQueriesContext(self, 0, connections['default']):
            ds._get_queryset()

    def test_queryset_cache(self):
        with mock.patch('ereports.engine.cache._cache', locmem_cache):
            locmem_cache.clear()

            TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission,
                                                                    'use_cache': True,
                                                                    'columns': ['id', 'name']})
            ds = TestDatasource.as_datasource()
            with _AssertNumQueriesContext(self, 1, connections['default']):
                i1 = list(ds)
            with _AssertNumQueriesContext(self, 0, connections['default']):
                i2 = list(ds)
            self.assertSequenceEqual(i1, i2)

    def test_pickle(self):
        TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission,
                                                                'use_cache': True,
                                                                'columns': ['id', 'name']})
        ds1 = TestDatasource.as_datasource()
        self.assertTrue(pickle.dumps(ds1.get_data()))

    def test_base_cache(self):
        with mock.patch('ereports.engine.cache._cache', locmem_cache):
            locmem_cache.clear()
            TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission,
                                                                    'use_cache': True,
                                                                    'columns': ['id', 'name']})
            from ereports.engine.cache import _cache

            _cache.set('aa', 1)
            assert _cache.get('aa') == 1

            ds1 = TestDatasource.as_datasource()
            ds2 = TestDatasource.as_datasource()

            with _AssertNumQueriesContext(self, 1, connections['default']):
                i1 = list(ds1)
                self.assertSequenceEqual(i1, list(ds2))

        with mock.patch('ereports.engine.cache._cache', dummy_cache):
            TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission,
                                                                    'use_cache': True,
                                                                    'columns': ['id', 'name']})
            ds1 = TestDatasource.as_datasource()
            ds2 = TestDatasource.as_datasource()

            with _AssertNumQueriesContext(self, 2, connections['default']):
                i1 = list(ds1)
                self.assertSequenceEqual(i1, list(ds2))

    def test_cache_different_columns(self):
        with mock.patch('ereports.engine.cache._cache', locmem_cache):
            locmem_cache.clear()

            TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission, 'use_cache': True})
            ds1 = TestDatasource.as_datasource(columns=['id', 'name'])
            ds2 = TestDatasource.as_datasource(columns=['id'])

            with _AssertNumQueriesContext(self, 2, connections['default']):
                list(ds1)
                list(ds2)

    def test_cache_different_filters(self):
        with mock.patch('ereports.engine.cache._cache', locmem_cache):
            locmem_cache.clear()

            TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission,
                                                                    'use_cache': True,
                                                                    'columns': ['id', 'name']})
            ds1 = TestDatasource.as_datasource()
            ds1.add_filters(id__gt=0)
            ds2 = TestDatasource.as_datasource()

            with _AssertNumQueriesContext(self, 2, connections['default']):
                i1 = list(ds1)
                i2 = list(ds2)
                self.assertSequenceEqual(i1, i2)

    def test_cache_invalidate_on_update(self):
        with mock.patch('ereports.engine.cache._cache', locmem_cache):
            locmem_cache.clear()
            monitor_model(Permission)
            reset(Permission)
            TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission,
                                                                    'use_cache': True,
                                                                    'columns': ['id', 'name']})
            ds1 = TestDatasource.as_datasource()
            list(ds1)
            p = Permission.objects.get(pk=1)
            p.name = 'aaaaaa'
            p.save()
            ds2 = TestDatasource.as_datasource()
            with _AssertNumQueriesContext(self, 1, connections['default']):
                list(ds2)

    def test_cache_invalidate_on_delete(self):
        with mock.patch('ereports.engine.cache._cache', locmem_cache):
            locmem_cache.clear()
            monitor_model(Permission)
            reset(Permission)

            TestDatasource = type('TestDatasource', (Datasource,), {'model': Permission,
                                                                    'use_cache': True,
                                                                    'columns': ['id', 'name']})
            ds1 = TestDatasource.as_datasource()
            list(ds1)
            Permission.objects.filter(pk=1).delete()
            ds2 = TestDatasource.as_datasource()
            with _AssertNumQueriesContext(self, 1, connections['default']):
                list(ds2)


class TestCacheReport(TestCase):
    def test_cache(self):
        locmem_cache = cache.get_cache('django.core.cache.backends.locmem.LocMemCache')
        # dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        locmem_cache.clear()
        with mock.patch('ereports.engine.cache._cache', locmem_cache):
            G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20, boolean=True)
            r1 = BaseReport.as_report(model=SimpleDemoModel, use_cache=True)
            r2 = BaseReport.as_report(model=SimpleDemoModel, use_cache=True)

            with _AssertNumQueriesContext(self, 1, connections['default']):
                i1 = list(r1)
                self.assertSequenceEqual(i1, list(r2))
