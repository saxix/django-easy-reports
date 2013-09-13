# -*- coding: utf-8 -*-
from decimal import Decimal
import re
import operator
import logging
import datetime
from django.utils.encoding import smart_str
from ereports.engine.widgets import ColumnWidget, CurrencyWidget, YesNoWidget, DateWidget, TimeWidget
from django.db import models
from ereports.utils import get_verbose_name, get_field_from_path, get_attr


__all__ = ['Column', 'DecimalColumn', 'DateColumn', 'DateTimeColumn', 'TimeColumn', 'IntegerColumn', 'BooleanColumn']

NOTFOUND = object()
rex = re.compile(r'^(\d|_)+')
logger = logging.getLogger(__name__)


def normalize_name(attr):
    attr = "".join(attr).replace(".", "_")
    return rex.sub("", attr)


class RowValueError(Exception):
    pass


class RowValue(object):
    def __init__(self, value, column=None):
        self.value = value
        self.column = column

    def __str__(self):
        return smart_str(self.value)

    def __repr__(self):
        return repr(self.value)

    def __unicode__(self):
        return unicode(self.value)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getstate__(self):
        obj_dict = self.__dict__.copy()
        obj_dict['column'] = None
        return obj_dict


class Column(object):
    widget = ColumnWidget
    wraps = basestring
    default_format = None

    def __init__(self, attr, title=None, manipulator=None, model=None, widget=None, sys_only=False, format=None,
                 name=None, **kwargs):
        self.attr = attr
        self.sys_only = sys_only
        self.name = name or normalize_name(attr)
        self._title = title
        self.format = format or self.default_format
        self._manipulator = manipulator or (lambda x: x)
        self.model = model
        if widget:
            self.widget = widget

    def __repr__(self):
        return repr(self.attr)

    def __str__(self):
        return str(self.attr)

    def get_value(self, obj, datasource):
        value = self._get_value_from_attr(obj, self.attr, datasource)
        return RowValue(value, self)

    def _get_value_from_attr(self, obj, attr_name, datasource):
        try:
            notfound = object()
            attr = get_attr(obj, attr_name, notfound)
            if attr is notfound:
                attr = getattr(datasource, attr_name, None)
                if attr:
                    if callable(attr):
                        return attr(obj)
                    else:
                        return attr
            else:
                if callable(attr):
                    return attr()
                return attr
        except Exception as e:
            logger.exception(e)
            raise ValueError("Unable to get value from `%s`: `%s` `%s`" % (attr_name, type(e), e))
        raise ValueError(attr_name)

    @property
    def title(self):
        if self._title is not None:
            return self._title
        try:
            return get_verbose_name(self.model, self.attr)
        except AttributeError:
            return self.attr.split(".")[-1].replace("_", " ").title()

    def apply_manipulator(self, cell):
        cell.value = self._manipulator(cell.value)
        return cell


class CalcColumn(Column):
    op = operator.add
    initial = 0
    wraps = int

    def __init__(self, attrs, **kwargs):
        self.attrs = attrs
        super(CalcColumn, self).__init__(attrs, **kwargs)

    def get_value(self, obj, datasource):
        result = self.initial
        for el in self.attrs:
            value = self._get_value_from_attr(obj, el, datasource)
            result = self.op(value, result)
        return RowValue(result, self)


class ColumnCallable(Column):
    """
        wraps a callable as Column.

        callable will be invoked passing the current object and the Datasoource instance.
        the Column header can be customized with ``callable.title = 'Title'``

        >>> def get_custom_format(obj, ds):
        ...     return obj.field.upper()
        >>> get_custom_format.title = 'Field'
        >>> c = ColumnCallable(get_custom_format)

    """

    def __init__(self, attr, **kwargs):
        name = kwargs.pop('name', None) or normalize_name(attr.__name__)
        title = kwargs.pop('title', None) or getattr(attr, 'title', name)
        super(ColumnCallable, self).__init__(attr, title=title, name=name, **kwargs)

    def get_value(self, obj, datasource):
        try:
            value = self.attr(obj, datasource)
            return RowValue(value, self)
        except Exception as e:
            logger.exception(e)
            raise ValueError("ColumnCallable: Unable to get value from `%s`: `%s`" % (self.attr, e))


class StringFormatColumn(Column):
    def __init__(self, attr, title=None, manipulator=None, model=None, widget=None, sys_only=False, format='{0}',
                 name=None, **kwargs):
        super(StringFormatColumn, self).__init__(attr, title, manipulator, model, widget, sys_only, format, name,
                                                 **kwargs)

    def get_value(self, obj, datasource):
        result = self.format.format(obj)
        return RowValue(result, self)


class DecimalColumn(Column):
    wraps = Decimal

    def get_value(self, obj, datasource):
        value = self._get_value_from_attr(obj, self.attr, datasource)
        return RowValue(self.wraps(value), self)


class DateColumn(Column):
    wraps = datetime.date
    widget = DateWidget
    default_format = '%d %b %Y'


class DateTimeColumn(Column):
    wraps = datetime.datetime


class TimeColumn(Column):
    wraps = datetime.time
    widget = TimeWidget
    default_format = '%H %M'


class IntegerColumn(Column):
    wraps = int
    pass


class CharColumn(Column):
    pass


class TextColumn(Column):
    pass


class CurrencyColumn(Column):
    widget = CurrencyWidget


class BooleanColumn(Column):
    wraps = bool
    widget = YesNoWidget


class OptionalColumn(Column):
    def get_value(self, obj, datasource):
        try:
            value = self._get_value_from_attr(obj, self.attr, datasource)
        except ValueError as e:
            logger.exception(e)
            value = ""
        return RowValue(value, self)


def get_column_for_attribute(model, fieldpath):
    """
        returns the more suitable Column class for `attr`.

    :param: can be a Django Field, attribute or callable
    :return:
    """
    attr = get_field_from_path(model, fieldpath)
    mapping = {
        models.IntegerField: IntegerColumn,
        models.DecimalField: DecimalColumn,
        models.DateField: DateColumn,
        models.CharField: CharColumn,
        models.BooleanField: BooleanColumn,
    }
    return mapping.get(type(attr), Column)
