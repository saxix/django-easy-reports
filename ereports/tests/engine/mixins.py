from django_webtest import WebTest
from ereports.engine.mixins import ReportRender
from ereports.tests.app.reports import SimpleDemoReport


class TestReportRender(WebTest):
    def test_init(self):
        r = ReportRender(SimpleDemoReport)
        self.assertEqual(r.report, SimpleDemoReport)
