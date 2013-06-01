# -*- coding: utf-8 -*-
import pytest

from ereports.template_loaders import EReportTemplateLoader
from django.template import TemplateDoesNotExist


@pytest.mark.django_db
def test_load_template_source():
    template_name = 'ereports/tpls/report.html'
    t = EReportTemplateLoader()

    with pytest.raises(TemplateDoesNotExist):
        t.load_template_source(template_name)
