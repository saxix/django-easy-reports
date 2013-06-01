# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader

from ereports.models import ReportTemplate


class EReportTemplateLoader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        try:
            tpl = ReportTemplate.objects.get(name=template_name)
            return (unicode(tpl.body).decode(settings.FILE_CHARSET), template_name)
        except ReportTemplate.DoesNotExist:
            raise TemplateDoesNotExist(template_name)

    load_template_source.is_usable = True


_loader = EReportTemplateLoader()
