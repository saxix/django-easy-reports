from django import forms
from django.contrib import admin
from django.db import models
from ereports.forms import ReportConfigurationForm
from ereports.models import ReportConfiguration, ReportGroup, ReportTemplate


class IReport(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'description', 'target_model', 'report_class', 'published', 'template', 'group')
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
        (None, {'fields': (('name', 'description', 'target_model', 'published', 'select_related', 'use_distinct'),
                           ('template', 'group', 'report_class'))}),
        ('Columns', {'classes': ['collapse', 'textarea-fields', ],
                     'fields': [('columns', 'filtering', 'ordering', 'groupby'), ]}),
    ]


admin.site.register(ReportConfiguration, IReport)
admin.site.register(ReportTemplate, admin.ModelAdmin)
admin.site.register(ReportGroup, admin.ModelAdmin)
