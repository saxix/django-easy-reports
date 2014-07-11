import hashlib
import logging
import datetime
from django.contrib import messages
from django.core.cache import cache
from django.views.generic import TemplateView
from ereports.engine.config import reportform_factory
from ereports.engine.registry import registry
from ereports.engine.report import BaseReport
from ereports.filtering import FilterQuerysetMixin
from ereports.models import ReportConfiguration

logger = logging.getLogger(__name__)


class ReportIndex(TemplateView):
    """ Index of all available reports for an office
    """
    template_name = 'ereports/index.html'

    def get_context_data(self, **kwargs):
        reports = []
        for report in ReportConfiguration.objects.filter(published=True).order_by('group', 'name'):
            reports.append(report)
        return {'reports': reports}


class ReportFilter(FilterQuerysetMixin, TemplateView):
    """ Filter and generated selected report
    """
    template_name = 'ereports/filter.html'
    method = 'POST'

    def get_config(self):
        return ReportConfiguration.objects.get(pk=self.kwargs.get('pk'))

    def get_report(self, **kwargs):
        if self.config.target_model:
            kwargs['model'] = self.config.target_model.model_class()

        Class = self.get_report_class()
        return Class.as_report(**kwargs)

    def get_report_class(self):
        return registry.get(self.config.report_class, BaseReport)

    def get_search_form_class(self):
        kwargs = {'order_by': self.config.get_allowed_order_by(),
                  'filtering': self.config.get_allowed_filters(),
                  'groupby': self.config.get_allowed_group_by()}
        return reportform_factory(self.report, bases=(self.report.config_form_class,), **kwargs)

    def get_search_form(self, *args, **kwargs):
        return self.get_search_form_class()(*args, **kwargs)

    def get_context_data(self, **kwargs):
        today = datetime.datetime.today()

        kwargs.update({
            'configuration': self.config,
            'today': today,
            'user': self.request.user,
        })
        return super(ReportFilter, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.config = self.get_config()
        self.report = self.get_report()
        kwargs.setdefault('form', self.get_search_form())
        return super(ReportFilter, self).get(request, *args, **kwargs)

    def _run_report(self, request, *args, **kwargs):
        pass

    def finalize_filters(self, *filters, **kwfilters):
        self.report.datasource.add_filters(*filters, **kwfilters)
        return filters, kwfilters

    def render_in_background(self):
        """Hook to allow running rendering of report in background

        Check if report needs to be rendered in background task
        """
        return False

    def background_render_task(self, request, form, **context):
        """Hook to allow running rendering of report in background

        Overwrite this method as background task
        """
        pass

    def post(self, request, *args, **kwargs):
        self.config = self.get_config()
        self.report = self.get_report()

        form = self.get_search_form(request.POST)
        context = self.get_context_data()
        if form.is_valid():
            filters, kwfilters = form.get_filters()
            kwfilters.update(**self.config.get_hard_filters(context))

            report_attributes = form.get_report_attributes()
            self.report = self.get_report(**report_attributes)

            filters, kwfilters = self.finalize_filters(*filters, **kwfilters)

            m = hashlib.md5()
            m.update("filters={0}".format(str(kwfilters)))
            m.update("list_display={0}".format(str(self.report.list_display)))
            m.update("report_attributes={0}".format(str(report_attributes)))

            cache_key = m.hexdigest()
            context['hash'] = cache_key
            page = cache.get(cache_key)
            if page:
                return page

            context['report'] = self.report
            context['filters_legend'] = form.get_filters_summary()
            context['filters'] = kwfilters

            if self.render_in_background():
                context["nfilters"] = filters
                self.background_render_task(request, form, **context)
                messages.error(self.request, "Report is being generated in the background.")
                kwargs.setdefault('form', form)
                return super(ReportFilter, self).get(request, *args, **kwargs)

            ds = self.report.datasource

            if ds:
                renderer = self.report.get_renderer_for_format(form.cleaned_data['_format'])
                page = renderer.render_to_response(request, **context)

                # cache.set(cache_key, page)
                return page
            else:
                messages.error(self.request, "Report has no data to display")
                kwargs.setdefault('form', form)
                kwargs.setdefault('query', ds.query)
                logger.debug('Report returns no data `%s`' % ds.query)
                return super(ReportFilter, self).get(request, *args, **kwargs)
        else:
            messages.error(self.request, (str(form.errors).replace('\n', ';')))
            return super(ReportFilter, self).get(request, *args, form=form)
