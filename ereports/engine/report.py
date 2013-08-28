# -*- coding: utf-8 -*-
from collections import defaultdict
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_unicode
from ereports.engine.config import ConfigurationForm
from ereports.engine.datasource import Datasource, DatasourceRow
from ereports.engine.renderer import BaseHtmlRender
from ereports.utils import get_attr, fqn


class Group(list):
    pass


class BaseGrouper(object):
    def __init__(self, report, group_by, internal_order):
        super(BaseGrouper, self).__init__()
        self.report = report
        self.group_by = group_by
        self.internal_order = internal_order  # field name to use for group order
        self._dict = defaultdict(Group)
        self._processed = False

    def _process(self):
        if self._processed:
            return
        ds = self.report.datasource
        # record is a DatasourceRow instance
        for datasourcerow in ds:
            if callable(self.group_by):
                group_name = self.group_by(datasourcerow._original)
            elif isinstance(self.group_by, basestring):
                try:
                    col = self.report.get_column_by_name(self.group_by)
                    group_name = col.get_value(datasourcerow._original, self.report.datasource).value
                except KeyError:
                    group_name = get_attr(datasourcerow._original, self.group_by)
            else:
                group_name = get_attr(datasourcerow._original, self.group_by)

            #datasourcerow._sort_func = self.report._order_columns
            orderedrow = DatasourceRow([(name, datasourcerow[name]) for name in self.report.display_order()])
            orderedrow._original = datasourcerow._original
            self._dict[group_name].append(orderedrow)

        self._processed = True

    def values(self):
        self._process()
        return self._dict.values()

    def keys(self):
        self._process()
        return self._dict.keys()

    groups = keys

    def items(self):
        self._process()

        # order internal group elements
        for group_name, rows in self._dict.items():
            rows.sort(key=lambda x: get_attr(x._original, self.internal_order))

        #returns groups ordered
        sorted_groups = zip(self._dict.keys(), self._dict.values())
        sorted_groups.sort(key=lambda x: smart_unicode(x[0]))

        return sorted_groups


class BaseReport(object):
    title = None
    description = None
    datasource = None
    model = None
    config_form_class = ConfigurationForm  # search form base class
    list_display = None  # columns and order to display
    list_filter = ()  # field names to use in the search_form
    formats = [('html', BaseHtmlRender)]
    use_cache = False
    order_by = None

    group_by = None  # (group, internal order)
    grouper = BaseGrouper
    extras = None
    column_totals = None  # columns to sum the values

    def __init__(self, **kwargs):
        self.extras = kwargs.pop('extras', {})
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self.title = self.title or fqn(self)

    def __repr__(self):
        return "<%s: on `%s`>" % (self.__class__.__name__, self.datasource.model.__name__)

    def has_subtotals(self):
        return bool(self.column_totals)

    @classmethod
    def as_report(cls, **initkwargs):
        for key, value in initkwargs.items():
            if not hasattr(cls, key) and not callable(value):
                raise TypeError(u"%s() received an invalid keyword %r" % (cls.__name__, key))

        model = initkwargs.get('model', cls.model)
        datasource = initkwargs.get('datasource', cls.datasource)
        use_cache = initkwargs.get('use_cache', cls.use_cache)
        extras = initkwargs.get('extras', cls.extras)

        if datasource is not None:
            initkwargs['model'] = datasource.model
            initkwargs['datasource'] = datasource._clone(extras=extras)
        elif model is not None:
            initkwargs['datasource'] = Datasource.as_datasource(model=model, use_cache=use_cache)
        else:
            raise ImproperlyConfigured(u"%(cls)s is missing a datasource. Define "
                                       u"%(cls)s.model, %(cls)s.datasource" % {'cls': cls.__name__})

        return cls(**initkwargs)

    def display_order(self):
        """
            returns the order and the column names to display
        :return: list
        """
        if self.list_display is not None:
            return self.list_display
        else:
            return [c.name for c in self.datasource.columns if not c.sys_only]

    def _order_columns(self, row):
        """
            orders the columns of the passed row to reflect the `list_display` attribute
        :param row:
        :return:
        """
        if self.list_display:
            return DatasourceRow([(name, row[name]) for name in self.list_display])
        return row

    def __iter__(self):
        self.datasource.order_by = self.order_by
        if self.group_by:
            g = self.get_groups()
            for group, rows in g:
                for row in rows:
                    yield self._order_columns(row)
        else:
            for row in self.datasource:
                yield self._order_columns(row)

    def __getitem__(self, item):
        rows = self.datasource[item]
        if isinstance(rows, (slice, list, tuple)):
            return tuple([self._order_columns(r) for r in rows])
        return self._order_columns(rows)

    def get_column_by_name(self, name):
        """
            return the Column instance for the given column's name
        :param name: string
        :return:
        """
        return self.columns_dict[name]

    @property
    def columns_dict(self):
        return dict([(c.name, c) for c in self.datasource.columns])

    def get_column_values(self, column_name):
        """
            returns all the values for the given column's name
        :param column_name:
        :return:
        """
        ds = self.datasource
        return [row[column_name].value for row in ds]

    @property
    def headers(self):
        if self.list_display:
            return [self.get_column_by_name(c).title for c in self.list_display
                    if not self.get_column_by_name(c).sys_only]
        else:
            return [c.title for c in self.datasource.columns if not c.sys_only]

    def get_format_labels(self):
        return self.formats_dict.keys()

    @property
    def formats_dict(self):
        return dict(self.formats)

    def get_renderer_class_for_format(self, render_format):
        return self.formats_dict[render_format]

    def get_renderer_for_format(self, render_format):
        return self.formats_dict[render_format](self)

    def get_groups(self):
        if not self.group_by:
            raise ImproperlyConfigured('Cannot use get_group() without set group_by')

        assert len(self.group_by) == 2, "Invalid GroupBy `%s`" % self.group_by
        groups = self.grouper(self, *self.group_by)
        return groups.items()
