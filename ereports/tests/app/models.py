from django.contrib.auth.models import User
from django.db import models
import itertools


class DemoModelGroup(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.name


class DemoOptionalModel(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, null=True)


class DemoModelDetail(models.Model):
    name = models.CharField(max_length=255)


counter = itertools.count()


class SimpleDemoModel(models.Model):
    char = models.CharField('Character', max_length=255)
    integer1 = models.IntegerField('Integer #1')
    integer2 = models.IntegerField('Integer #2', null=True, blank=True, default=0)
    boolean = models.BooleanField('Boolean', default=False)

    def filter_source(self):
        return counter.next()


class SimpleDateModel(models.Model):
    char = models.CharField('Character', max_length=255)
    date = models.DateField('Date')
    date_range = models.DateField('Date Range')


class DemoModel(models.Model):
    group = models.ForeignKey(DemoModelGroup)
    m2m = models.ManyToManyField(DemoModelDetail)

    char = models.CharField(max_length=255)
    integer = models.IntegerField()
    logic = models.BooleanField()
    null_logic = models.NullBooleanField()
    date = models.DateField()
    datetime = models.DateTimeField()
    time = models.TimeField()
    decimal = models.DecimalField(max_digits=10, decimal_places=3)
    email = models.EmailField()
    float = models.FloatField()
    bigint = models.BigIntegerField()
    ip = models.IPAddressField()
    url = models.URLField()
    text = models.TextField()

    nullable = models.CharField(max_length=255, null=True, default=None)
    blank = models.CharField(max_length=255, blank=True, null=False, default="")
    not_editable = models.CharField(max_length=255, editable=False, blank=True, null=True)
    choices = models.IntegerField(choices=((1, 'Choice 1'), (2, 'Choice 2'), (3, 'Choice 3')))

    class Meta:
        app_label = 'app'
        db_table = 'ereports_demoapp_demomodel'

    def get_attribute_getter(self):
        return "getter"

    @property
    def attribute_property(self):
        return "property"
