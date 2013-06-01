import datetime
import pytest

from django_webtest import WebTest
from django import forms
from django.core.exceptions import ValidationError
from django.utils.datastructures import MultiValueDict

from ereports.engine.config import reportform_factory, DateRange, DateRangeField, DateRangeInput, \
    ColumnsChoiceField, base_has_attr, get_attr_from_bases, get_field_from_bases, FilterSpec, UIDateInput, \
    MultiChoiceWidget
from ereports.tests.app.reports import SimpleDemoReport, SimpleDateReport, FilterSpecDemoReport, SimpleDemoExtraReport


class FakeBase(forms.Form):
    name = 'Fake'
    field_name = forms.CharField(max_length=255)


def test_base_has_attr():
    assert base_has_attr((FakeBase, ), 'name')
    assert base_has_attr((object(), FakeBase, ), 'name')
    assert not base_has_attr((FakeBase, ), 'wrong')
    assert not base_has_attr((object(), FakeBase, ), 'wrong')


def test_get_attr_from_bases():
    assert get_attr_from_bases((FakeBase,), 'name') == 'Fake'
    assert get_attr_from_bases((FakeBase,), 'wrong', 'default') == 'default'

    with pytest.raises(UnboundLocalError):
        get_attr_from_bases((FakeBase,), 'wrong')


def test_get_field_from_bases():
    assert isinstance(get_field_from_bases((FakeBase,), 'field_name'), forms.CharField)
    assert get_field_from_bases((FakeBase,), 'wrong', 'default') == 'default'

    with pytest.raises(UnboundLocalError):
        get_field_from_bases((FakeBase,), 'wrong')


class TestFilterSpec(WebTest):
    def test_init(self):
        f = FilterSpec()
        self.assertEqual(f._value, {})

        f = FilterSpec(value='abc')
        self.assertEqual(f._value, 'abc')

    def test_get_filter_description(self):
        f = FilterSpec(value='abc')
        self.assertEqual(f.get_filter_description('char'), "abc")

    def test_get_filter(self):
        f = FilterSpec(value='abc')
        self.assertEqual(f.get_filter(), 'abc')

    def test_nonzero(self):
        f = FilterSpec(value='abc')
        self.assertEqual(bool(f), True)

        f = FilterSpec()
        self.assertEqual(bool(f), False)

        f = FilterSpec(value='')
        self.assertEqual(bool(f), False)


class TestConfigurationForm(WebTest):
    def test_init(self):
        r = SimpleDemoReport.as_report()
        c = reportform_factory(r)
        self.assertIn('_format', c.base_fields)

    def test_get_lookup_fields(self):
        r = SimpleDemoReport.as_report()
        form = reportform_factory(r, (r.config_form_class,), filtering=['integer1'])()
        f = form.get_lookup_fields()
        self.assertEqual(['integer1'], f)

    def test_get_filters(self):
        r = SimpleDemoReport.as_report()
        form = reportform_factory(r, (r.config_form_class,), filtering=['integer1'])()
        form.cleaned_data = {
            'integer1': 1,
            'char': ['a', 'b', 'c']
        }
        f = form.get_filters()
        self.assertSequenceEqual(([], {'integer1': 1}), f)

        form.cleaned_data = {
            'integer1': [1, 2, 3]
        }
        f = form.get_filters()
        self.assertSequenceEqual(([], {'integer1__in': [1, 2, 3]}), f)

    def test_get_filters_filterspec(self):
        r = FilterSpecDemoReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()
        form.cleaned_data = {
            'date_range': FilterSpec('2001')
        }
        f = form.get_filters()
        self.assertSequenceEqual((['2001'], {}), f)

    def test_get_filters_filterspec_dict(self):
        r = FilterSpecDemoReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()
        form.cleaned_data = {
            'date_range': FilterSpec({1: '2001'})
        }
        f = form.get_filters()
        self.assertSequenceEqual(([], {1: '2001'}), f)

    def test_get_filters_date_range(self):
        r = SimpleDateReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()
        form.cleaned_data = {
            'date_range': DateRange(['2000-01-01', '2001-01-01']),
            'date': '2000-01-01'
        }
        f = form.get_filters()
        self.assertEqual({'date_range__gt': '2000-01-01',
                          'date_range__lt': '2001-01-01',
                          'date': '2000-01-01'}, f[1])

    def test_get_filters_summary(self):
        r = SimpleDemoReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()
        form.cleaned_data = {
            'integer1': 1,
        }
        self.assertEqual(form.get_filters_summary(), {u'Integer #1': 1})

        form.cleaned_data = {
            'integer1': [1, 2, 3]
        }
        form.get_filters()
        self.assertEqual(form.get_filters_summary(), {u'Integer #1': [1, 2, 3]})

    def test_get_filters_summary_date_range(self):
        r = SimpleDateReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()
        form.cleaned_data = {
            'date_range': DateRange(['2000-01-01', '2001-01-01']),
            'date': '2000-01-01'
        }
        self.assertEqual(form.get_filters_summary(),
                         {u'Date': '2000-01-01', u'Date Range': ['2000-01-01', '2001-01-01']})

    def test_get_filters_summary_filterspec(self):
        r = FilterSpecDemoReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()
        form.cleaned_data = {
            'date_range': FilterSpec('2001')
        }
        self.assertEqual(form.get_filters_summary(), {u'Date Range': '2001'})

    def test_get_report_attributes(self):
        r = SimpleDateReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()

        self.assertIn('_report_list_display', form.base_fields)
        self.assertIsInstance(form.base_fields['_report_list_display'], ColumnsChoiceField)

        form.cleaned_data = {
            '_report_list_display': 'abc',
            '_report_group_by': 'random',
        }
        a = form.get_report_attributes()
        self.assertEqual({'list_display': 'abc', 'group_by': 'random'}, a)

    def test_get_report_attributes_extras(self):
        r = SimpleDemoExtraReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()

        self.assertIn('_extras_data', form.base_fields)

        form.cleaned_data = {
            '_report_list_display': 'char',
            '_extras_data': 'more'
        }
        a = form.get_report_attributes()
        self.assertEqual({'list_display': 'char', 'extras': {'data': 'more'}}, a)

    def test_clean__report_order_by(self):
        r = SimpleDateReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()
        form.cleaned_data = {
            '_report_order_by': 'user.first_name',
        }
        o = form.clean__report_order_by()
        self.assertEqual(['user__first_name'], o)

        form.cleaned_data = {
            '_report_order_by': 'user.first_name, user.last_name',
        }
        o = form.clean__report_order_by()
        self.assertEqual(['user__first_name', 'user__last_name'], o)

    def test_html_output(self):
        r = SimpleDateReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()
        self.assertEqual(form.fields.keys(),
                         ['date_range', '_report_group_by', 'date', '_format', '_report_list_display'])
        form.as_p()
        self.assertEqual(form.fields.keys(), ['date', '_report_group_by', '_format', '_report_list_display'])

    def test_report_order_by(self):
        r = SimpleDemoReport.as_report()
        form = reportform_factory(r, (r.config_form_class,), order_by=[('date', 'Date'), ])()
        self.assertIn('_report_order_by', form.base_fields)
        self.assertIsInstance(form.base_fields['_report_order_by'], forms.ChoiceField)

    def test_report_groupby(self):
        r = SimpleDemoReport.as_report()
        form = reportform_factory(r, (r.config_form_class,), groupby=[('date', 'Date'), ])()
        self.assertIn('_report_group_by', form.base_fields)
        self.assertIsInstance(form.base_fields['_report_group_by'], forms.ChoiceField)

    def test_report_groupby_from_base(self):
        r = SimpleDateReport.as_report()
        form = reportform_factory(r, (r.config_form_class,))()
        self.assertIn('_report_group_by', form.base_fields)
        self.assertIsInstance(form.base_fields['_report_group_by'], forms.ChoiceField)

    def test_clean__report_group_by(self):
        r = SimpleDemoReport.as_report()
        form = reportform_factory(r, (r.config_form_class,), groupby=[('date', 'Date'), ])()
        form.cleaned_data = {
            'date': '2001-01-01',
            '_report_group_by': 'date'
        }
        self.assertIsNone(form.clean__report_group_by())

        form.cleaned_data = {
            'date': '2001-01-01',
            '_report_group_by': 'date,internal'
        }
        group, internal_order = form.clean__report_group_by()
        self.assertEqual(group, 'date')
        self.assertEqual(internal_order, 'internal')


class TestDateRangeField(WebTest):
    def test_to_python(self):
        d = DateRangeField()

        r = d.to_python(['2000-01-01', '2001-01-01'])
        self.assertIsInstance(r, DateRange)
        self.assertEqual(r, DateRange([datetime.date(2000, 1, 1), datetime.date(2001, 1, 1)]))

        with self.assertRaises(ValidationError):
            r = d.to_python(['2000', '2001-01-01'])

        with self.assertRaises(ValidationError):
            r = d.to_python(['2000-01-01', '2001'])

    def test_clean(self):
        d = DateRangeField()
        r = d.clean(['2000-01-01', '2001-01-01'])

        self.assertIsInstance(r, DateRange)
        self.assertEqual(r, DateRange([datetime.date(2000, 1, 1), datetime.date(2001, 1, 1)]))

        with self.assertRaises(ValidationError):
            r = d.clean(['2000', '2001-01-01'])

        with self.assertRaises(ValidationError):
            r = d.clean(['2000-01-01', '2001'])


class TestDateRangeInput(WebTest):
    def test_value_from_datadict(self):
        d = DateRangeInput()
        data = {
            'date_start': '2000-01-01',
            'date_end': '2001-01-01',
        }
        name = 'date'

        v = d.value_from_datadict(data, None, name)
        self.assertEqual(v, ['2000-01-01', '2001-01-01'])

    def test_render(self):
        d = DateRangeInput()
        v = ['2000-01-01', '2001-01-01']
        r = d.render('date', v, {'id': 'id_date'})
        self.assertIn('name="date_start"', r)
        self.assertIn('name="date_end"', r)

        v = [None, '2001-01-01']
        r = d.render('date', v, {'id': 'id_date'})
        self.assertIn('name="date_start"', r)
        self.assertIn('name="date_end"', r)
        self.assertNotIn('value="2000-01-01"', r)
        self.assertIn('value="2001-01-01"', r)

        v = ['2000-01-01', None]
        r = d.render('date', v, {'id': 'id_date'})
        self.assertIn('name="date_start"', r)
        self.assertIn('name="date_end"', r)
        self.assertIn('value="2000-01-01"', r)
        self.assertNotIn('value="2001-01-01"', r)

        v = '2000-01-01'
        r = d.render('date', v, {'id': 'id_date'})
        self.assertIn('name="date_start"', r)
        self.assertIn('name="date_end"', r)
        self.assertNotIn('value="2000-01-01"', r)


class TestUIDateInput(WebTest):
    def test_render(self):
        d = UIDateInput()
        v = '2001-01-01'
        name = 'date'
        r = d.render(name, v, {})
        self.assertIn('name="date"', r)
        self.assertIn('class="uidate2"', r)


class TestMultiChoiceWidget(WebTest):
    def test_value_from_datadict(self):
        m = MultiChoiceWidget()
        d = MultiValueDict({'name': [1, 2, 3]})
        self.assertEqual(m.value_from_datadict(d, {}, 'name'), [1, 2, 3])
