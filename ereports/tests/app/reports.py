from django.forms import ChoiceField, CharField

from ereports.engine.config import ConfigurationForm, DateRangeField, FilterSpec
from ereports.engine.datasource import Datasource
from ereports.engine.renderer import BaseHtmlRender, BaseXlsRender
from ereports.engine.report import BaseReport
from ereports.tests.app.models import SimpleDemoModel, SimpleDateModel


class SimpleDemoModelSource(Datasource):
    model = SimpleDemoModel
    columns = [
        'char',
        'integer1'
    ]


class SimpleDemoReport(BaseReport):
    datasource = SimpleDemoModelSource.as_datasource()
    list_filter = ['integer1']
    list_display = [
        'char',
    ]
    formats = [
        ('html', BaseHtmlRender),
        ('xls', BaseXlsRender),
    ]


class SimpleDemoExtraForm(ConfigurationForm):
    _extras_data = CharField(max_length=20)


class SimpleDemoExtraReport(SimpleDemoReport):
    config_form_class = SimpleDemoExtraForm
    list_filter = ['integer1', '_extras_data']


class SimpleDateModelSource(Datasource):
    model = SimpleDateModel
    columns = [
        'char',
        'date',
        'date_range',
    ]


class SimpleDateConfigForm(ConfigurationForm):
    date_range = DateRangeField(label='Date Range')
    _report_group_by = ChoiceField()


class SimpleDateReport(BaseReport):
    datasource = SimpleDateModelSource.as_datasource()
    list_filter = ['date']
    group_by = ['char', 'date']
    config_form_class = SimpleDateConfigForm
    forms = [
        ('html', BaseHtmlRender),
        ('xls', BaseXlsRender),
    ]


class FilterSpecField(CharField):
    filter_spec = FilterSpec


class FilterSpecConfigForm(ConfigurationForm):
    date_range = FilterSpecField(label='Date Range')


class FilterSpecDemoReport(BaseReport):
    datasource = SimpleDemoModelSource.as_datasource()
    list_filter = ['date_range']
    config_form_class = FilterSpecConfigForm
