from django.db import models


class DemoModel(models.Model):
    char = models.CharField(max_length=255)
    integer = models.IntegerField(blank=True, null=True)
    logic = models.BooleanField(default=False)
    text = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'demoapp'


class ProxyDemoModel(DemoModel):
    class Meta:
        app_label = 'demoapp'
        proxy = True


def proxy_factory(name):
    return type(name, (ProxyDemoModel,), {'__module__': ProxyDemoModel.__module__,
                                          'Meta': type('Meta', (object,), {'proxy': True, 'app_label': 'demoapp'})})
