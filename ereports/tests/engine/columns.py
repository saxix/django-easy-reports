# -*- coding: utf-8 -*-
from decimal import Decimal
from unittest import TestCase

from ereports.engine.columns import Column, normalize_name, get_column_for_attribute, CharColumn, \
    IntegerColumn, DateColumn, DecimalColumn, RowValue, BooleanColumn, CalcColumn, ColumnCallable, OptionalColumn, \
    StringFormatColumn
from ereports.tests.app.models import DemoModel, DemoModelGroup, SimpleDemoModel
from ereports.tests.app.reports import SimpleDemoModelSource


class FakeCallable():
    title = 'Callable'

    def __init__(self, obj, ds):
        if ds is not None:
            raise Exception


def F(obj=None):
    if obj is None:
        return 'called without obj'
    return 'called with obj'


def test_normalize():
    attr_norm_list = [
        ("char", "char"),
        (".hello", "hello"),
        ("one.two..three", "one_two__three"),
        ("1_2.3.hello.world", "hello_world"),
    ]

    for attr, norm in attr_norm_list:
        n = normalize_name(attr)
        assert n == norm


def test_get_column_for_attribute():
    c = get_column_for_attribute(DemoModel, 'char')
    assert c == CharColumn

    c = get_column_for_attribute(DemoModel, 'integer')
    assert c == IntegerColumn

    c = get_column_for_attribute(DemoModel, 'date')
    assert c == DateColumn

    c = get_column_for_attribute(DemoModel, 'decimal')
    assert c == DecimalColumn

    c = get_column_for_attribute(DemoModel, 'logic')
    assert c == BooleanColumn


class TestColumns(TestCase):
    def test_init(self):
        attr = 'char'
        c = Column(attr)
        self.assertEqual(c.attr, attr)
        self.assertEqual(str(c), attr)
        self.assertEqual(repr(c), "'%s'" % attr)

        c = Column(attr, widget='Widget')
        self.assertEqual(c.widget, 'Widget')

    def test_title(self):
        title = 'AAA'
        c = Column('char', title=title)
        self.assertEqual(c.title, title)

        c = Column('char')
        self.assertEqual(c.title, "Char")

        c = Column('char', title="")
        self.assertEqual(c.title, "")

        c = Column('char', model="AAA")
        self.assertEqual(c.title, "Char")

        c = Column('char', model="AAA", title="")
        self.assertEqual(c.title, "")

        c = Column('name', model=DemoModel)
        self.assertEqual(c.title, 'Name')

        c = Column('user.first_name', model=DemoModelGroup)
        self.assertEqual(c.title, 'first name')

    def test_get_value(self):
        o = SimpleDemoModel()
        ds = SimpleDemoModelSource.as_datasource()

        # model found return attr
        c = Column('char')
        v = c.get_value(o, ds)
        self.assertIsInstance(v, RowValue)

        # raise last ValueError
        c = Column('nonexistant')
        with self.assertRaises(ValueError):
            c.get_value(o, ds)

        # Exception with raise ValueError
        c = Column(FakeCallable, name='fake')
        with self.assertRaises(ValueError):
            c.get_value(o, ds)

    def test_get_value_model_attr_callable(self):
        o = SimpleDemoModel()
        ds = SimpleDemoModelSource.as_datasource()
        o.fake = F
        c = Column('fake')
        v = c.get_value(o, ds)
        self.assertIsInstance(v, RowValue)
        self.assertEqual(v, 'called without obj')

    def test_get_value_attr_on_ds(self):
        """Test get value where attr not found on model, but on ds"""
        o = SimpleDemoModel()
        ds = SimpleDemoModelSource.as_datasource()

        ds.fake = 'Hello'
        c = Column('fake')
        v = c.get_value(o, ds)
        self.assertIsInstance(v, RowValue)
        self.assertEqual(v, 'Hello')

    def test_get_value_attr_callable_on_ds(self):
        """Test get value where attr is not found on model and is callable
        attr on ds
        """
        o = SimpleDemoModel()
        ds = SimpleDemoModelSource.as_datasource()

        ds.fake = F
        c = Column('fake')
        v = c.get_value(o, ds)
        self.assertIsInstance(v, RowValue)
        self.assertEqual(v, 'called with obj')

    def test_apply_manipulator(self):
        class FakeCell():
            value = 'low'

        def upper(v):
            return v.upper()

        c = Column('char', manipulator=upper)
        v = c.apply_manipulator(FakeCell())
        self.assertEqual(v.value, 'LOW')


class TestRowValue(TestCase):
    def test_init(self):
        value = 'val'
        r = RowValue(value)
        self.assertEqual(r.value, value)
        self.assertEqual(str(r), str(value))
        self.assertEqual(repr(r), repr(value))
        self.assertEqual(unicode(r), unicode(value))
        self.assertEqual(r, r)
        self.assertEqual(r, value)
        self.assertNotEqual(r, 'wrong')

    def test_pickle(self):
        import pickle
        value = 'val'
        c = Column('char')
        r = RowValue(value, column=c)

        p = pickle.dumps(r)
        up = pickle.loads(p)
        self.assertEqual(up.column, None)


class TestCalcColumn(TestCase):
    def test_init(self):
        col = CalcColumn('char')
        self.assertEqual(col.attrs, 'char')

    def test_get_value(self):
        ds = SimpleDemoModelSource.as_datasource()
        col = CalcColumn(['integer1'])

        self.assertEqual(col.get_value(SimpleDemoModel(integer1=5), ds), 5)

        col.initial = 10
        self.assertEqual(col.get_value(SimpleDemoModel(integer1=5), ds), 15)


class TestColumnCallable(TestCase):
    def test_init(self):
        col = ColumnCallable(FakeCallable)
        self.assertEqual(col.title, 'Callable')

    def test_get_value(self):
        col = ColumnCallable(FakeCallable)
        v = col.get_value(None, None)
        self.assertIsInstance(v, RowValue)

    def test_get_value_exception(self):
        o = SimpleDemoModel()
        ds = SimpleDemoModelSource.as_datasource()

        col = ColumnCallable(FakeCallable)
        with self.assertRaises(ValueError):
            col.get_value(o, ds)


class TestStringFormatColumn(TestCase):
    def test_init(self):
        col = StringFormatColumn('simple')
        self.assertEqual(col.format, '{0}')

    def test_get_value(self):
        col = StringFormatColumn('simple')
        self.assertEqual(col.get_value('data', None), RowValue('data'))


class TestDecimalColumn(TestCase):
    def test_get_value(self):
        col = DecimalColumn('integer1')
        ds = SimpleDemoModelSource.as_datasource()
        v = col.get_value(SimpleDemoModel(integer1=5), ds)
        self.assertEqual(v, Decimal(5.00))


class TestOptionalColumn(TestCase):
    def test_get_value(self):
        ds = SimpleDemoModelSource.as_datasource()

        col = OptionalColumn('nonexistant')
        v = col.get_value(SimpleDemoModel(), ds)
        self.assertEqual(v, "")

        col = OptionalColumn('integer1')
        v = col.get_value(SimpleDemoModel(integer1=5), ds)
        self.assertEqual(v, 5)
