from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.models import User
from demoproject.demoapp.admin import DemoModelAdmin
from demoproject.demoapp.models import DemoModel
import ereports.urls

admin.autodiscover()


class PublicAdminSite(admin.AdminSite):
    def has_permission(self, request):
        request.user = User.objects.get_or_create(username='sax')[0]
        return True


public_site = PublicAdminSite()
admin.autodiscover()

for e, v in admin.site._registry.items():
    public_site.register(e, v.__class__)

public_site.register(DemoModel, DemoModelAdmin)

urlpatterns = patterns('',
                       (r'', include(include(ereports.urls))),
                       (r'^admin/', include(include(public_site.urls))),
)
