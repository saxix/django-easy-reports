# -*- coding: utf-8 -*-
from collections import defaultdict
from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateField, DateInput, ChoiceField
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.forms.util import flatatt
from django.utils.encoding import force_unicode
from ereports.utils import get_field_from_path, StartWithList


class MultiChoiceWidget(forms.SelectMultiple):
    class Media:
        js = (
            'ereports/multiselect/js/ui.multiselect2.min.js',
            'ereports/multiselect/js/plugins/localisation/jquery.localisation-min.js',
            'ereports/multiselect/js/plugins/tmpl/jquery.tmpl.1.1.1.min.js',
            'ereports/multiselect/js/plugins/blockUI/jquery.blockUI.min.js',
        )
        css = {'all': ("ereports/multiselect/css/ui.multiselect2.css",)}

    def value_from_datadict(self, data, files, name):
        return data.getlist(name)

    def render(self, name, value, attrs=None, choices=()):
        rendered = super(MultiChoiceWidget, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            $(document).ready(function() {
                var elem = $('#id_%(name)s');
                elem.addClass('multiselect');
                elem.multiselect({ animated: null, searchable:false, show: null });
            });
            </script>''' % {'name': name})


class ColumnsChoiceField(forms.MultipleChoiceField):
    widget = MultiChoiceWidget

    def __init__(self, report, required=True, widget=None, label=_('Columns'), initial=None, help_text=None, *args,
                 **kwargs):
        choices = [(report.get_column_by_name(col).name, report.get_column_by_name(col).title) for col in
                   report.display_order()]
        initial = report.display_order()
        super(ColumnsChoiceField, self).__init__(choices, required, widget, label, initial, help_text, *args, **kwargs)


class UIDateInput(DateInput):
    def render(self, name, value, attrs=None):
        attrs['class'] = 'uidate2'
        return super(UIDateInput, self).render(name, value, attrs)


class DateRangeInput(DateInput):
    input_type = 'text'

    def value_from_datadict(self, data, files, name):
        values = []
        for suffix in ('start', 'end'):
            n = "%s_%s" % (name, suffix)
            values.append(data.get(n, None))
        return values

    def render(self, name, values, attrs=None):
        if isinstance(values, (list, tuple)):
            start, end = values
            if start is None:
                start = ''
            if end is None:
                end = ''
        else:
            start, end = '', ''

        attrs['class'] = 'uidate2'
        base_final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        final_attrs_start = base_final_attrs.copy()
        final_attrs_end = base_final_attrs.copy()

        final_attrs_start['id'] = "%s_start" % base_final_attrs['id']
        final_attrs_start['name'] = "%s_start" % base_final_attrs['name']

        final_attrs_end['id'] = "%s_end" % base_final_attrs['id']
        final_attrs_end['name'] = "%s_end" % base_final_attrs['name']

        if start != '':
            final_attrs_start['value'] = force_unicode(self._format_value(start))
        if end != '':
            final_attrs_end['value'] = force_unicode(self._format_value(end))

        return mark_safe(u'From: <input%s /> To: <input%s />' % (flatatt(final_attrs_start), flatatt(final_attrs_end)))


class DateRange(list):
    pass


class DateRangeField(DateField):
    widget = DateRangeInput
    default_error_messages = {
        'required': _(u'This field is required.'),
        'invalid': _(u'Enter a valid value.'),
    }
    input_formats = ('%d/%m/%Y', '%Y-%m-%d')

    def to_python(self, values):
        try:
            start = super(DateRangeField, self).to_python(values[0])
        except ValidationError:
            raise ValidationError(self.error_messages['invalid'] + ' start')

        try:
            end = super(DateRangeField, self).to_python(values[1])
        except ValidationError:
            raise ValidationError(self.error_messages['invalid'] + ' end')

        return DateRange([start, end])

        # def clean(self, values):
        #     values = self.to_python(values)
        #     self.validate(values)
        #     self.run_validators(values)
        #     filters = {}
        #     if values[0]:
        #         filters['%s__gt' % self.name] = values[0]
        #     if values[1]:
        #         filters['%s__lt' % self.name] = values[1]
        #     return FilterSpec(filters)


class FilterSpec(object):
    def __init__(self, value=None, *args, **kwargs):
        self._value = value or {}

    def get_filter_description(self, field):
        return str(self._value)

    def get_filter(self):
        return self._value

    def __nonzero__(self):
        return bool(self._value)


class ConfigurationForm(forms.Form):
    configure_columns = True

    def get_lookup_fields(self):
        lk = []
        for attr_name in self.base_fields.keys():
            if not attr_name.startswith('_'):
                lk.append(attr_name)
        return StartWithList(lk)

    def get_filters(self):
        filters = []
        kwfilters = {}
        self._filters_summary = {}
        lookup_fields = self.get_lookup_fields()
        if lookup_fields:
            for field_name in lookup_fields:
                value = self.cleaned_data[field_name]
                field = self.fields[field_name]
                if value:
                    if isinstance(value, FilterSpec):
                        f = value.get_filter()
                        if isinstance(f, dict):
                            kwfilters.update(f)
                        else:
                            filters.append(f)
                    elif isinstance(value, DateRange):  # here for backward compatibility
                        if value[0]:
                            kwfilters['%s__gt' % field_name] = value[0]
                        if value[1]:
                            kwfilters['%s__lt' % field_name] = value[1]
                    elif isinstance(value, (list, tuple)):
                        kwfilters['%s__in' % field_name] = value
                    else:
                        kwfilters[field_name] = value

                    try:
                        self._filters_summary[field.label] = value.get_filter_description(field)
                    except AttributeError:
                        self._filters_summary[field.label] = value
        return filters, kwfilters

    def clean__report_group_by(self):
        value = self.cleaned_data['_report_group_by']
        if ',' in value:
            group, internal_order = value.split(',')
            if group:
                return group, internal_order
        return None

    def get_filters_summary(self):
        if not hasattr(self, '_filters_summary'):
            self.get_filters()
        return self._filters_summary

    def get_report_attributes(self):
        prefix = '_report_'
        extras = '_extras_'
        attributes = defaultdict(dict)
        for attr_name in self.base_fields.keys():
            if attr_name.startswith(extras):
                key = attr_name[len(extras):]
                attributes['extras'][key] = self.cleaned_data[attr_name]
            if attr_name.startswith(prefix):
                attributes[attr_name[len(prefix):]] = self.cleaned_data[attr_name]

        return attributes

    def clean__report_order_by(self):
        v = self.cleaned_data['_report_order_by']
        v = map(lambda s: s.strip().replace('.', '__'), v.split(','))
        return v

    def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        s = SortedDict()
        # for name, field in self.fields.items():
        for name in self._field_display_order:
            # if name in self.fields:
            s[name] = self.fields[name]
        self.fields = s
        return super(ConfigurationForm, self)._html_output(normal_row, error_row, row_ender, help_text_html,
                                                           errors_on_separate_row)


def base_has_attr(bases, name):
    none = object()
    for base in bases:
        attr = getattr(base, name, none)
        if attr is not none:
            return True

    return False


def get_attr_from_bases(bases, name, *args):
    # do not set default if not provided
    # we need to raise the exception if no default value
    if args:
        default = args[0]
    none = object()
    for base in bases:
        attr = getattr(base, name, none)
        if attr is not none:
            return attr

    return default


def get_field_from_bases(bases, name, *args):
    # do not set default if not provided
    # we need to raise the exception if no default value
    if args:
        default = args[0]
    none = object()
    for base in bases:
        # lookup both in pForm and mixins
        field = base.base_fields.get(name, getattr(base, name, none))
        if field is not none:
            return field

    return default


def reportform_factory(report, bases=(ConfigurationForm,), **kwargs):
    name = "%sFilterForm" % report.__class__.__name__
    attrs = {}
    field_display_order = []
    for fieldpath in kwargs.get('filtering', getattr(report, 'list_filter', [])):
        if '=' not in fieldpath:
            field = get_field_from_path(report.model, fieldpath)
            if field:
                field_name = fieldpath.replace('.', '__')
                field_display_order.append(field_name)
                attrs[field_name] = get_field_from_bases(bases, field_name, field.formfield(required=False))
            elif fieldpath.startswith('_extras_'):
                field_display_order.append(fieldpath)
                attrs[fieldpath] = get_field_from_bases(bases, fieldpath, None)

    choice_field_class = getattr(report, 'choice_field_class', None) or ChoiceField

    orders = kwargs.get('order_by', None)
    if orders:
        attrs['_report_order_by'] = choice_field_class(label='Order by', choices=orders)
        field_display_order.append('_report_order_by')

    groupby = kwargs.get('groupby', None)
    if groupby:
        attrs['_report_group_by'] = choice_field_class(label='Group by', choices=groupby)
        field_display_order.append('_report_group_by')
    else:
        groupby = get_field_from_bases(bases, '_report_group_by', None)
        if groupby:
            attrs['_report_group_by'] = groupby
            field_display_order.append('_report_group_by')

    # add report format options
    if report.formats:
        formats = [(f[0], f[0]) for f in report.formats]
        attrs['_format'] = choice_field_class(
            label='Format',
            choices=formats
        )
        field_display_order.append('_format')

    configure_columns = kwargs.get('configure_columns', None)
    if configure_columns or get_attr_from_bases(bases, 'configure_columns', False):
        columns_choice_field_class = getattr(report, 'columns_choice_field', ColumnsChoiceField)
        attrs['_report_list_display'] = columns_choice_field_class(report)
        field_display_order.append('_report_list_display')

    attrs['_report'] = report
    attrs['_field_display_order'] = field_display_order

    return type(name, bases, attrs)
