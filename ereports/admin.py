from django import forms
from django.contrib import admin
from django.db import models
from ereports.forms import ReportConfigurationForm
from .models import ReportConfiguration, ReportGroup, ReportTemplate


class IReport(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'description', 'target_model', 'report_class',
                    'published', 'template', 'group')
    list_filter = ('published', 'template', 'group')
    form = ReportConfigurationForm
    actions = ['publish', 'unpublish']

    def publish(self, request, queryset):
        queryset.update(published=True)

    def unpublish(self, request, queryset):
        queryset.update(published=False)

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea({'cols': '60', 'rows': '20'})}, }
    #
    search_fields = ('name', )
    fieldsets = [
        (None, {'fields': (('name', 'description', 'target_model', 'published'),
                           ('template', 'group', 'report_class'))}),
        ('Columns', {'classes': ['collapse', 'textarea-fields', ],
                     'fields': [('columns', 'filtering', 'ordering', 'groupby'), ]}),
    ]
    #
    # class Media:
    #     css = {
    #         'all': ('admin/css/jquery-ui-1.8.1.custom.css',)
    #     }
    #     js = (
    #         'admin/js/jquery.min.js',
    #         'admin/js/jquery-ui.min.js',
    #         'admin/js/jquery.cookie.js'
    #     )
    #
    # def preview(self, u):
    #     url = reverse('ereports.do_report', args=[PasportOffice.objects.get(pk=1).code, u.pk, 'html'])
    #     return '<a target="_new" href="%s">HTML</a>' % url
    #
    # preview.allow_tags = True
    #
    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     object = Report.objects.get(pk=object_id)
    #     import sqlparse
    #
    #     ctx = {}
    #     for cp in get_standard_processors():
    #         ctx.update(**cp(request))
    #     ctx.update(**object.get_extra_context())
    #     try:
    #         qs = object.get_target_queryset(**ctx)
    #     except ValidationError:
    #         qs = object.target_model.model_class().objects.all()
    #
    #     context = {'qs': qs,
    #                'fields': sorted(qs.model._meta.fields, key=lambda x: x.verbose_name),
    #                'query': sqlparse.format(str(qs.query), reindent=True, keyword_case='upper')}
    #     if extra_context:
    #         context.update(extra_context)
    #
    #     return super(IReport, self).change_view(request, object_id, form_url, context)
    #


admin.site.register(ReportConfiguration, IReport)
admin.site.register(ReportTemplate, admin.ModelAdmin)
admin.site.register(ReportGroup, admin.ModelAdmin)
