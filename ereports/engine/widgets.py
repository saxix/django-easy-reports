# -*- coding: utf-8 -*-

from django.utils.translation import gettext as _
from ereports.utils import currencyformat


class ColumnWidget(object):
    @classmethod
    def render(cls, raw_value):
        ret = raw_value.value
        if ret is None:
            return ""
        return ret


class YesNoWidget(ColumnWidget):
    @classmethod
    def render(cls, raw_value):
        return _("Yes") if raw_value.value else _("No")


class CurrencyWidget(ColumnWidget):
    thousand_sep = ','
    decimal_sep = '.'

    @classmethod
    def render(cls, raw_value):
        return currencyformat(raw_value.value)


class PercentWidget(ColumnWidget):
    @classmethod
    def render(cls, raw_value):
        return "%s %%" % raw_value.value


class DateWidget(ColumnWidget):
    @classmethod
    def render(cls, raw_value):
        if raw_value.value is not None:
            return raw_value.value.strftime(raw_value.column.format)
        return ""

    @classmethod
    def render_xls(cls, raw_value):
        if raw_value.value is not None:
            return raw_value.value
        return ""


class TimeWidget(ColumnWidget):
    @classmethod
    def render(cls, raw_value):
        if raw_value.value is not None:
            return raw_value.value.strftime(raw_value.column.format)
        return ""
