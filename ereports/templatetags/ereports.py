from __future__ import absolute_import
from decimal import Decimal, InvalidOperation
from django import template
from ereports.engine.columns import RowValue, RowValueError
from ereports.utils import currencyformat, fqn

register = template.Library()


def isNumeric(s):
    try:
        return int(s) or True
    except (ValueError, TypeError):
        pass
    try:
        Decimal(s) or True
    except (ValueError, TypeError, InvalidOperation):
        pass
    try:
        return float(s) or True
    except (ValueError, TypeError):
        pass
    return False

register.filter(currencyformat)


@register.filter
def col_to_css_class(row_value):
    if isinstance(row_value, RowValue):
        return fqn(row_value.column).lower().replace('.', '_')
    elif isinstance(row_value, RowValueError):
        return str(row_value)
    else:
        raise ValueError('wrong value for `col_to_css_class` ({0}, {1})'.format(row_value, type(row_value)))


@register.filter
def with_widget(row_value, format=None):
    if isinstance(row_value, RowValue):
        widget = row_value.column.widget
        render = getattr(widget, 'render_{}'.format(format), widget.render)
        return render(row_value)
    elif isinstance(row_value, RowValueError):
        return str(row_value)
    else:
        raise ValueError('wrong value for `with_widget` ({0})'.format(type(row_value)))


@register.filter
def humanize_filters(filters):
    LOOKUP_MAPPING = [
        'exact',
        'iexact',
        'contains',
        'icontains',
        'in',
        'gt',
        'gte',
        'lt',
        'lte',
        'startswith',
        'istartswith',
        'endswith',
        'iendswith',
        'range',
        'year',
        'month',
        'day',
        'week_day',
        'isnull',
        'search',
        'regex',
        'iregex',
    ]

    def get_label(parts):
        if parts[-1] in LOOKUP_MAPPING:
            return " ".join(parts[-2:])
        return parts[-1]

    ret = []
    if filters:
        for k, v in filters.items():
            if k:
                parts = k.lower().split('__')
                label = get_label(parts)
                last = parts[-1]
                # if not k.lower().endswith('office'):
                if last != 'office':
                    ret.append((label.replace('_', ' ').title(), str(v)))
    return sorted(ret)


@register.filter
def format_raw_value(row_value):
    if isinstance(row_value.value, Decimal):
        return currencyformat(row_value.value)
    return row_value.value


@register.simple_tag()
def subtotal(report, rows, col):
    try:
        if isinstance(col, basestring):
            col = report.get_column_by_name(col)
        tot = sum(r[col.name].value or 0 for r in rows)
        return format_raw_value(RowValue(tot, col))
    except TypeError:
        return 0


@register.simple_tag()
def total(report, col):
    try:
        if isinstance(col, basestring):
            col = report.get_column_by_name(col)
        values = report.get_column_values(col.name)
        return format_raw_value(RowValue(sum(values), col))
    except TypeError:
        return 0


@register.filter
def div_mod(dividend, divisor):
    quotient, remainder = divmod(dividend, divisor)
    return quotient, remainder
