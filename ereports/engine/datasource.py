# -*- coding: utf-8 -*-
from collections import OrderedDict
import copy
import logging
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import curry
from ereports.engine.cache import DatasourceCacheManager, DummyCacheManager
from ereports.engine.columns import Column, get_column_for_attribute, RowValueError
from ereports.engine.utils import get_tables_for_query
from ereports.utils import get_model_field_names

REPR_OUTPUT_SIZE = 20

logger = logging.getLogger(__name__)


class RecordFilteredError(Exception):
    pass


class DatasourceRow(OrderedDict):
    def __getattr__(self, item):
        if item in self:
            return self[item]
        return OrderedDict.__getattr__(self, item)

    def __eq__(self, other):
        return tuple(v.value for k, v in self.items()) == other


class Datasource(object):
    """
        Represent a set of data. Basically act as a queryset,
        but can work with any model attribute and can traverse them.

        Each row is a classnametuple

    :param source can be Model, Manager or Queryset
    """
    model = None
    queryset = None
    columns = None
    extras = None
    order_by = None
    use_cache = False
    dependent_models = None  # used by the cache system
    cache_manager = None

    def __init__(self, **kwargs):
        self.kwfilters = {}
        self.filters = []
        self._result_cache = None
        self._queryset = None
        self._custom_filters = kwargs.pop('custom_filters', [])
        self.extras = kwargs.pop('extras', {})

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        if self.use_cache and self.cache_manager is None:
            self.cache_manager = DatasourceCacheManager()
        elif not self.use_cache:
            self.cache_manager = DummyCacheManager()

    @classmethod
    def as_datasource(cls, **initkwargs):
        for key, value in initkwargs.items():
            if not hasattr(cls, key) and not callable(value):
                raise TypeError(u"%s() received an invalid keyword %r" % (cls.__name__, key))

        queryset = initkwargs.get('queryset', cls.queryset)
        model = initkwargs.get('model', cls.model)
        _columns = initkwargs.get('columns', cls.columns)

        if queryset:
            model = queryset.model
        elif model is None:
            raise ImproperlyConfigured(u"%(cls)s is missing a queryset. Define "
                                       u"%(cls)s.model, %(cls)s.queryset" % {'cls': cls.__name__})

        factory = curry(get_column_for_attribute, model)
        if not _columns:
            initkwargs['columns'] = [factory(name)(name, model=model)
                                     for name in get_model_field_names(model)]
        else:
            columns = list(_columns)
            for idx, colname in enumerate(_columns):
                if isinstance(colname, basestring):
                    columns[idx] = factory(colname)(colname, model=model)
                elif isinstance(colname, Column):
                    colname.model = model
                elif isinstance(colname, (list, tuple)):
                    name, Class = colname
                    columns[idx] = Class(name, model=model)
            initkwargs['columns'] = columns

        initkwargs['RowClass'] = DatasourceRow
        initkwargs['model'] = model

        return cls(**initkwargs)

    def __repr__(self):
        data = list(self.get_data()[:REPR_OUTPUT_SIZE + 1])
        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."
        return repr(data)

    def __len__(self):
        return len(self.get_data())

    def filter_record(self, obj):
        pass

    def add_custom_filter(self, func):
        self._custom_filters.append(func)

    def __iter__(self):
        return iter(self.get_data())

    def __getitem__(self, k):
        ds = self.get_data()
        ret = ds[k]
        return ret

    def add_filters(self, *args, **kwargs):
        for k, v in kwargs.items():
            self.kwfilters[k] = v
        for v in args:
            self.filters.append(v)

    def _create_result_cache(self):
        result_cache = []
        qs = self._get_queryset()
        for obj in qs:
            try:
                self.filter_record(obj)
                row = self._get_values_from_object(obj)
                for func in self._custom_filters:
                    func(row)
                result_cache.append(row)
            except RecordFilteredError:
                pass
            except ValueError as e:
                logger.exception(e)
        return tuple(result_cache)

    def get_data(self):
        if self._result_cache is None:
            cache_key = self.cache_manager.get_key(self)
            cached_data = self.cache_manager.retrieve(cache_key)
            if cached_data is None:
                self._result_cache = self._create_result_cache()
                self.cache_manager.store(cache_key, self._result_cache)
            else:
                self._result_cache = cached_data
        return self._result_cache

    def _get_queryset(self):
        if not bool(self._queryset):
            if self.queryset:
                qs = self.queryset
            else:
                qs = self.model._default_manager.all()
            qs = qs.filter(*self.filters, **self.kwfilters)
            if self.order_by is not None:
                qs = qs.order_by(*self.order_by)
            qs = qs.select_related()
            self._queryset = qs
            self.dependent_tables = get_tables_for_query(qs.query)
        return self._queryset

    def query(self):
        self.get_data()
        return self._queryset.query

    def _get_values_from_object(self, obj):
        """
            process each queryset entry and returns a list of Column()
        :param obj:
        :return:
        """
        row = self.RowClass()
        for col in self.columns:
            try:
                cell = col.get_value(obj, self)
                row[col.name] = col.apply_manipulator(cell)
                row._original = obj
                # values.append(col.apply_manipulator(cell))
            except Exception as e:
                row[col.name] = RowValueError(e)
                # values.append(RowValueError(e))

        # row = self.RowClass(values)
        return row

    def _clone(self, extras=None):
        klass = self.__class__
        kwargs = copy.deepcopy(self.__dict__)
        if extras is not None:
            kwargs["extras"] = extras
        if self.queryset:
            kwargs.update({'queryset': self.queryset._clone()})
        c = klass()
        c.__dict__.update(kwargs)
        return c
