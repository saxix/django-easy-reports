# -*- coding: utf-8 -*-
import datetime

from django.contrib.contenttypes.models import ContentType
from django.http import QueryDict
from django_dynamic_fixture import G
from django_webtest import WebTest
from mock import patch

from ereports.views import ReportIndex, ReportFilter
from ereports.models import ReportConfiguration
from ereports.tests.app.models import SimpleDemoModel

from .fixtures import get_fake_request


class TestReportIndex(WebTest):
    def setUp(self):
        self.request = get_fake_request()

    def test_get_no_reports(self):
        response = ReportIndex.as_view()(self.request)
        self.assertIn('reports', response.context_data)
        self.assertEqual(response.context_data['reports'], [])

    def test_get(self):
        G(ReportConfiguration, name='Standard', published=True)
        response = ReportIndex.as_view()(self.request)
        self.assertIn('reports', response.context_data)
        self.assertEqual(len(response.context_data['reports']), 1)


class TestReportFilter(WebTest):
    def setUp(self):
        self.request = get_fake_request()
        self.config = G(ReportConfiguration,
                        name='Standard',
                        target_model=ContentType.objects.get_for_model(SimpleDemoModel),
                        report_class='ereports.tests.app.reports.SimpleDemoReport',
                        filtering='',
                        ordering='',
                        groupby='')
        self.querydict = QueryDict('')
        self.querydict = self.querydict.copy()
        self.querydict.update({'_format': 'html',
                               '_report_list_display': 'integer1'})

    def test_get(self):
        response = ReportFilter.as_view()(self.request, pk=self.config.pk)
        self.assertIn('configuration', response.context_data)
        self.assertIn('today', response.context_data)
        self.assertEqual(response.context_data['today'].strftime("%Y-%m-%d"),
                         datetime.datetime.today().strftime("%Y-%m-%d"))

        self.assertIn('user', response.context_data)
        self.assertEqual(response.context_data['user'], self.request.user)

    def test_post_invalid(self):
        self.request.method = 'POST'
        #TODO catch message error value and confirm
        with patch('ereports.views.messages'):
            response = ReportFilter.as_view()(self.request, pk=self.config.pk)
            self.assertIn('form', response.context_data)

    def test_post_valid_no_ds(self):
        self.request.method = 'POST'
        self.request.POST = self.querydict
        #TODO catch message error value and confirm
        with patch('ereports.views.messages'):
            response = ReportFilter.as_view()(self.request, pk=self.config.pk)
            self.assertIn('query', response.context_data)

    def test_post_valid(self):
        self.request.method = 'POST'
        self.request.POST = self.querydict
        G(SimpleDemoModel, char='abc', integer1=10)
        response = ReportFilter.as_view()(self.request, pk=self.config.pk)
        self.assertIn('ereports.engine.report.BaseReport', str(response))
        self.assertIn('Integer #1', str(response))
