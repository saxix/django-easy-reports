# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext
from ereports.engine.mixins import TemplateRender, ReportRender, XlsRender

DEFAULT_FILENAME = 'report'


class BaseHtmlRender(ReportRender, TemplateRender):
    template_name = 'ereports/tpls/report.html'
    grouped_template_name = 'ereports/tpls/grouped.html'

    def render(self, request, context, **response_kwargs):

        if self.report.group_by:
            context['groups'] = self.report.get_groups()
            self.active_template_name = self.grouped_template_name
        else:
            self.active_template_name = self.template_name

        context.update(self.get_extra_context())
        return super(BaseHtmlRender, self).render(request, context)

    def render_to_response(self, request, **response_kwargs):
        context = RequestContext(request, response_kwargs)
        return HttpResponse(self.render(request, context))

    def get_extra_context(self):
        if self.report.column_totals:
            return {'SUMMARY_FIELDS': filter(lambda x: x in self.report.display_order(), self.report.column_totals)}
        return {}


class BaseXlsRender(ReportRender, XlsRender):
    def render_to_response(self, request, **response_kwargs):
        filename = "{filename}.xls".format(filename=response_kwargs.get("report_name", DEFAULT_FILENAME))
        response = HttpResponse(content_type=self.content_type)
        response['Content-Disposition'] = 'attachment;filename="%s"' % filename
        # ensure we have report context
        if 'report' not in response_kwargs:
            response_kwargs['report'] = self.report
        body = self.render(request, response_kwargs)

        response.write(body)
        return response
