from django.conf.urls import patterns, url
from views import ReportIndex


urlpatterns = patterns('',
                       url(r'^reports/$',
                           ReportIndex.as_view(),
                           name='reports.list_reports'),)
