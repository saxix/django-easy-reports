# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django_dynamic_fixture import G
from django_webtest import WebTest

from ereports.engine.renderer import BaseHtmlRender, BaseXlsRender
from ereports.tests.app.models import SimpleDemoModel
from ereports.tests.app.reports import SimpleDemoReport, SimpleDateReport
from ereports.tests.fixtures import get_fake_request


class TestBaseHtmlRenderer(WebTest):
    def test_render_to_response(self):
        report = SimpleDemoReport.as_report()
        renderer = report.get_renderer_for_format('html')
        self.assertIsInstance(renderer, BaseHtmlRender)
        request = get_fake_request()
        r = renderer.render_to_response(request)
        self.assertIsInstance(r, HttpResponse)

    def test_render_to_response_with_groupby(self):
        report = SimpleDateReport.as_report()
        renderer = report.get_renderer_for_format('html')
        self.assertIsInstance(renderer, BaseHtmlRender)
        request = get_fake_request()
        r = renderer.render_to_response(request)
        self.assertIsInstance(r, HttpResponse)


class TestBaseXlsRenderer(WebTest):
    def test_render_to_response(self):
        G(SimpleDemoModel, n=2, char='abc', integer1=1, integer2=2, boolean=True)
        G(SimpleDemoModel, n=2, char=u'êbc', integer1=1, integer2=2, boolean=True)
        report = SimpleDemoReport.as_report()
        renderer = report.get_renderer_for_format('xls')
        self.assertIsInstance(renderer, BaseXlsRender)
        request = get_fake_request()
        r = renderer.render_to_response(request)
        self.assertIsInstance(r, HttpResponse)
