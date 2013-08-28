# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import ReportIndex, ReportFilter


urlpatterns = patterns(
    '',

    url(r'^$', ReportIndex.as_view(), name='ereports.list'),
    url(r'report/(?P<pk>\d+)/$', ReportFilter.as_view(), name='ereports.filter_report'),
)
