# -*- encoding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.forms import ChoiceField
from django_dynamic_fixture import N
from unittest import TestCase

from ereports.forms import MyModelChoiceField, ReportConfigurationForm
from ereports.engine.registry import registry


class TestMyModelChoiceField(TestCase):
    def test_label_from_instance(self):
        c = N(ContentType, app_label='label', name='name')
        m = MyModelChoiceField(queryset=ContentType.objects.order_by('app_label', 'name'))
        self.assertEqual(m.label_from_instance(c), "Label - Name")


class TestReportConfigurationForm(TestCase):
    def test_init(self):
        form = ReportConfigurationForm()
        self.assertIsInstance(form.fields['report_class'], ChoiceField)
        self.assertEqual(form.fields['report_class'].choices, registry.choices())

    def test_clean_groupby(self):
        form = ReportConfigurationForm()

        form.cleaned_data = {'groupby': "one;two"}
        self.assertEqual(form.clean_groupby(), "one;two")

        with self.assertRaises(ValidationError):
            form.cleaned_data = {'groupby': 'one'}
            form.clean_groupby()
