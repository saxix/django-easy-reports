from __future__ import absolute_import
import datetime
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django_dynamic_fixture import G

from ereports.engine.columns import Column, DecimalColumn, RowValue, RowValueError
from ereports.engine.datasource import Datasource
from ereports.tests.engine.fixtures import FakeQuerySet
from ereports.engine.report import BaseReport
from ereports.templatetags.ereports import isNumeric, col_to_css_class, with_widget, format_raw_value, \
    subtotal, total, div_mod, humanize_filters
from ereports.tests.app.models import SimpleDemoModel


def test_isnumeric():
    assert isNumeric(1) == 1
    assert isNumeric("1") == 1
    assert isNumeric(1.0) == 1
    assert isNumeric("1.0") == 1

    assert not isNumeric("wrong")


def test_col_to_css_class():
    c = Column('user.first_name')
    r = RowValue('Test', column=c)
    assert col_to_css_class(r) == 'ereports_engine_columns_column'

    e = RowValueError('Test')
    assert col_to_css_class(e) == 'Test'

    with pytest.raises(ValueError):
        col_to_css_class('Wrong')

    ds = Datasource.as_datasource(model=User,
                                  queryset=FakeQuerySet(model=User, items=[User(username='username1'),
                                                                           User(username='username2')]))

    TestReport = type('TestReport', (BaseReport,), {'model': User, 'datasource': ds})
    report = TestReport.as_report()

    assert col_to_css_class(report[0].username) == 'ereports_engine_columns_charcolumn'
    assert col_to_css_class(report[0]['username']) == 'ereports_engine_columns_charcolumn'


def test_with_widget():
    c = Column('user.first_name')
    r = RowValue('Test', column=c)
    assert with_widget(r) == 'Test'
    assert with_widget(r, format='foo') == 'Test'

    c = Column('normal', format="%Y-%m-%d")
    r = RowValue(datetime.date(2000, 1, 1), column=c)
    assert with_widget(r, format='xls') == datetime.date(2000, 1, 1)

    e = RowValueError('Test')
    assert with_widget(e) == 'Test'

    with pytest.raises(ValueError):
        with_widget('Wrong')


def test_format_raw_value():
    c = DecimalColumn('salary.currency')
    r = RowValue(Decimal("1000"), column=c)
    assert format_raw_value(r) == "1,000.00"

    r = RowValue("1000", column=c)
    assert format_raw_value(r) == "1000"

    ds = Datasource.as_datasource(model=User,
                                  queryset=FakeQuerySet(model=User, items=[User(username='username1'),
                                                                           User(username='username2')]))

    TestReport = type('TestReport', (BaseReport,), {'model': User, 'datasource': ds})
    report = TestReport.as_report()

    assert format_raw_value(report[0].username) == 'username1'
    assert format_raw_value(report[0]['username']) == 'username1'


@pytest.mark.django_db
def test_subtotal():
    G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20)
    ds = Datasource.as_datasource(model=SimpleDemoModel)
    r = BaseReport.as_report(datasource=ds)

    assert subtotal(r, r, 'integer1') == 20
    assert subtotal(r, int, 'integer1') == 0


@pytest.mark.django_db
def test_total():
    G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20)
    ds = Datasource.as_datasource(model=SimpleDemoModel)
    r = BaseReport.as_report(datasource=ds)

    assert total(r, 'integer2') == 40
    assert total(r, 'char') == 0


def test_div_mod():
    assert div_mod(5, 2) == divmod(5, 2)


def test_humanize_filters():
    f = {
        'eod__lt': datetime.date(2013, 5, 31),
        'nte__gt': datetime.date(2012, 11, 1),
        'eod__gt': datetime.date(2011, 9, 1),
        u'office': 'Testing',
        'admin_duty_station': 'Bangkok'
    }
    r = humanize_filters(f)
    assert r == [
        ('Admin Duty Station', 'Bangkok'),
        ('Eod Gt', '2011-09-01'),
        ('Eod Lt', '2013-05-31'),
        ('Nte Gt', '2012-11-01'),
    ]
