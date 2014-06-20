# -*- coding: utf-8 -*-
import datetime

from ereports.engine.columns import Column, RowValue
from ereports.engine.widgets import ColumnWidget, YesNoWidget, CurrencyWidget, PercentWidget, DateWidget, TimeWidget


def test_columnwidget():
    c = Column('normal')
    r = RowValue('abc', column=c)
    assert ColumnWidget.render(r) == 'abc'

    r = RowValue(None, column=c)
    assert ColumnWidget.render(r) == ''


def test_yesnowidget():
    c = Column('normal')
    r = RowValue(True, column=c)
    assert YesNoWidget.render(r) == 'Yes'

    r = RowValue('abc', column=c)
    assert YesNoWidget.render(r) == 'Yes'

    r = RowValue(False, column=c)
    assert YesNoWidget.render(r) == 'No'


def test_currencywidget():
    c = Column('normal')
    r = RowValue(1000.00, column=c)
    assert CurrencyWidget.render(r) == "1,000.00"

    r = RowValue(1000, column=c)
    assert CurrencyWidget.render(r) == "1,000.00"


def test_percentwidget():
    c = Column('normal')
    r = RowValue("10", column=c)
    assert PercentWidget.render(r) == "10 %"

    r = RowValue(10, column=c)
    assert PercentWidget.render(r) == "10 %"

    r = RowValue(10.0, column=c)
    assert PercentWidget.render(r) == "10.0 %"

    r = RowValue(10.01, column=c)
    assert PercentWidget.render(r) == "10.01 %"


def test_datewidget():
    c = Column('normal', format="%Y-%m-%d")
    r = RowValue(datetime.date(2000, 1, 1), column=c)
    assert DateWidget.render(r) == "2000-01-01"
    assert DateWidget.render_xls(r) == datetime.date(2000, 1, 1)

    r = RowValue(None, column=c)
    assert DateWidget.render(r) == ""


def test_timewidget():
    c = Column('normal', format="%H:%M")
    r = RowValue(datetime.time(16, 20, 10), column=c)
    assert TimeWidget.render(r) == "16:20"

    r = RowValue(None, column=c)
    assert TimeWidget.render(r) == ""
