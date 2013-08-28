from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.forms import ChoiceField
from django.forms.models import ModelForm
from ereports.models import ReportConfiguration


class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s - %s" % (obj.app_label.title(), obj.name.title(),)


class ReportConfigurationForm(ModelForm):
    target_model = MyModelChoiceField(queryset=ContentType.objects.order_by('app_label', 'name'), required=False)
    report_class = ChoiceField()

    def __init__(self, *args, **kwargs):
        from ereports.engine.registry import registry
        super(ReportConfigurationForm, self).__init__(*args, **kwargs)

        self.fields['report_class'].choices = registry.choices()

    def clean_groupby(self):
        value = self.cleaned_data['groupby']
        for line in value.splitlines():
            if len(line.split(';')) != 2:
                raise ValidationError('wqww')
        return value

    class Meta:
        model = ReportConfiguration
