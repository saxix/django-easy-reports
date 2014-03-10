import datetime
from django.contrib.auth.models import Permission
from django_dynamic_fixture import G
from django_webtest import WebTest
from itertools import count
from ereports.engine.config import reportform_factory
from ereports.engine.datasource import Datasource
from ereports.engine.renderer import BaseHtmlRender, BaseXlsRender
from ereports.engine.report import BaseReport, BaseGrouper, ImproperlyConfigured
from ereports.tests.app.models import SimpleDemoModel, SimpleDateModel
from ereports.tests.app.reports import SimpleDemoReport, SimpleDateReport, SimpleDateModelSource


class SequentialDataFixture(object):
    def __init__(self, start_from):
        super(SequentialDataFixture, self).__init__()
        self.gen = count(start_from)

    def generate_data(self, field):
        return self.gen.next()


def fake_callable(orig):
    return u'cba'


class TestBaseGroup(WebTest):
    def test_init(self):
        g = BaseGrouper(SimpleDemoReport, 'char', 'Character')
        self.assertEqual(g.report, SimpleDemoReport)
        self.assertEqual(g.group_by, 'char')
        self.assertEqual(g.internal_order, 'Character')
        self.assertFalse(g._processed)

    def test_items_basestring(self):
        G(SimpleDateModel, char='abc', date=datetime.date.today(), date_range=datetime.date.today())
        r = SimpleDateReport.as_report()
        g = BaseGrouper(r, 'char', 'Character')
        self.assertEqual(list(g.items()), [(u'abc', list(r))])
        self.assertTrue(g._processed)

        # call again to ensure _processed param handled properly and no error
        g._process()
        self.assertTrue(g._processed)

    def test_items_callable(self):
        G(SimpleDateModel, char='abc', date=datetime.date.today(), date_range=datetime.date.today())
        r = SimpleDateReport.as_report()
        g = BaseGrouper(r, fake_callable, 'Groups')
        self.assertEqual(list(g.items()), [(u'cba', list(r))])

    def test_items_other(self):
        G(SimpleDemoModel, char='abc')
        r = SimpleDemoReport.as_report()
        r.list_display = ['char', 'integer1']
        g = BaseGrouper(r, 'wrong', 'wrong')
        self.assertEqual(list(g.items()), [(None, list(r))])

    def test_items_sorted(self):
        G(SimpleDateModel, char='cba', date=datetime.date.today(), date_range=datetime.date.today())
        G(SimpleDateModel, char='bac', date=datetime.date.today(), date_range=datetime.date.today())
        G(SimpleDateModel, char='abc', date=datetime.date.today(), date_range=datetime.date.today())
        r = SimpleDateReport.as_report()
        g = BaseGrouper(r, 'char', 'Groups')
        expected = [(u'abc', [r[2]]),
                    (u'bac', [r[1]]),
                    (u'cba', [r[0]])]

        self.assertEqual(list(g.items()), expected)

    def test_values(self):
        G(SimpleDateModel, char='abc', date=datetime.date.today(), date_range=datetime.date.today())
        r = SimpleDateReport.as_report()
        g = BaseGrouper(r, 'char', 'Groups')
        self.assertEqual(g.values(), [list(r)])

    def test_keys(self):
        G(SimpleDateModel, char='abc', date=datetime.date.today(), date_range=datetime.date.today())
        r = SimpleDateReport.as_report()
        g = BaseGrouper(r, 'char', 'Groups')
        self.assertEqual(g.keys(), [u'abc'])


class TestBaseReport(WebTest):
    def test_inherit(self):
        TestReport = type('TestReport', (BaseReport,), {'model': Permission})
        r = TestReport.as_report()
        self.assertIsInstance(list(r), list)

    def test_repr(self):
        r = SimpleDemoReport.as_report()
        self.assertEqual(repr(r), "<SimpleDemoReport: on `SimpleDemoModel`>")

    def test_type_error_exception(self):
        with self.assertRaises(TypeError):
            BaseReport.as_report(models="")

    def test_improperly_configured_exception(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20)
        with self.assertRaises(ImproperlyConfigured):
            BaseReport.as_report(models=SimpleDemoModel)

    def test_slice(self):
        instances = G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20, boolean=True)
        r = BaseReport.as_report(model=SimpleDemoModel)
        self.assertSequenceEqual(list(r[:1]), [(instances[0].pk, u'abc', 10, 20, True)])

    def test_getitem(self):
        instances = G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20, boolean=True)
        r = BaseReport.as_report(model=SimpleDemoModel)
        self.assertSequenceEqual(r[1].values(), (instances[1].pk, u'abc', 10, 20, True))

    def test_datasource(self):
        instances = G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20, boolean=True)
        ds = Datasource.as_datasource(model=SimpleDemoModel)
        r = BaseReport.as_report(datasource=ds)
        self.assertSequenceEqual(r[1].values(), (instances[1].pk, u'abc', 10, 20, True))

    def test_datasource_custom_list_display(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20)

        ds = Datasource.as_datasource(model=SimpleDemoModel)
        r = BaseReport.as_report(datasource=ds,
                                 list_display=['integer2', 'char', 'integer1'])

        self.assertSequenceEqual(r[1], (20, u'abc', 10))
        self.assertSequenceEqual(r[:1], [(20, u'abc', 10)])

    def test_datasource_std_list_display(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20)

        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      columns=['integer2', 'char', 'integer1'])
        r = BaseReport.as_report(datasource=ds)

        self.assertSequenceEqual([c.name for c in ds.columns], r.display_order())
        self.assertSequenceEqual(r[1], (20, u'abc', 10))

    def test_headers(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20)

        ds = Datasource.as_datasource(model=SimpleDemoModel)
        r = BaseReport.as_report(datasource=ds,
                                 list_display=['integer2', 'char', 'integer1'])

        self.assertSequenceEqual(['Integer #2', 'Character', 'Integer #1'], r.headers)

        ds = Datasource.as_datasource(model=SimpleDemoModel,
                                      columns=['integer2', 'char', 'integer1'])
        r = BaseReport.as_report(datasource=ds)

        self.assertSequenceEqual(['Integer #2', 'Character', 'Integer #1'], r.headers)

    def test_get_column_values(self):
        G(SimpleDemoModel, n=10, data_fixture=SequentialDataFixture(0))
        ds = Datasource.as_datasource(model=SimpleDemoModel)
        r = BaseReport.as_report(datasource=ds,
                                 list_display=['integer2', 'char', 'integer1'])

        self.assertSequenceEqual([1, 3, 5, 7, 9, 11, 13, 15, 17, 19], r.get_column_values('integer1'))

    def test_get_config_form_class(self):
        r = SimpleDemoReport.as_report()
        f = reportform_factory(r, bases=(r.config_form_class,))
        self.assertIn('integer1', f.base_fields)
        self.assertIn('_format', f.base_fields)

    def test_get_format_labels(self):
        r = SimpleDemoReport.as_report()
        self.assertEqual(r.formats_dict, {'html': BaseHtmlRender, 'xls': BaseXlsRender})

    def test_format_labels(self):
        r = SimpleDemoReport.as_report()
        self.assertSequenceEqual(sorted(r.get_format_labels()), ['html', 'xls'])

    def test_get_renderer_class_format(self):
        r = SimpleDemoReport.as_report()
        self.assertEqual(r.get_renderer_class_for_format('html'), BaseHtmlRender)

    def test_get_renderer_for_format(self):
        r = SimpleDemoReport.as_report()
        renderer = r.get_renderer_for_format('html')
        self.assertIsInstance(renderer, BaseHtmlRender)

    def test_get_groups(self):
        r = SimpleDemoReport.as_report()

        with self.assertRaises(ImproperlyConfigured):
            r.get_groups()

        G(SimpleDateModel, char='abc', date=datetime.date.today(), date_range=datetime.date.today())
        r = SimpleDateReport.as_report(datasource=SimpleDateModelSource.as_datasource())
        g = r.get_groups()
        self.assertEqual(len(g), 1)

    def test_has_subtotals(self):
        r = SimpleDemoReport.as_report()

        self.assertFalse(r.has_subtotals())

        r.column_totals = ['integer1']
        self.assertTrue(r.has_subtotals())


class TestExtendedReport(WebTest):
    def test_datasource_custom_list_display(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=10, integer2=20)
        r = SimpleDemoReport.as_report()
        self.assertEqual(r.datasource[1].values(), [u'abc', 10])
        self.assertEqual(r[1], (u'abc',))
        self.assertSequenceEqual(r[:1], [(u'abc',)])
