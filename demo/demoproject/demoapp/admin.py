from __future__ import absolute_import
from django.contrib.admin import ModelAdmin
from demoproject.demoapp.models import DemoModel
import demoproject.demoapp.reports  # NOQA


class DemoModelAdmin(ModelAdmin):
    # list_display = [f.name for f in DemoModel._meta.fields]
    list_display = ('id', 'char', 'integer')
    list_display_links = ('id', )
    list_editable = ('char', 'integer')
    actions = None


def register(site):
    site.register(DemoModel, DemoModelAdmin)
