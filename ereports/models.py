# -*- encoding: utf-8 -*-
import random
import string
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models


clean_field = lambda field: field.replace('.', '__').strip()
keygen = lambda: ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(100))


class ReportGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey('self', blank=True, null=True)

    class Meta:
        app_label = 'ereports'

    def __unicode__(self):
        return self.name


class ReportTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    body = models.TextField()
    system = models.BooleanField(default=False)

    class Meta:
        app_label = 'ereports'

    def __unicode__(self):
        return self.name


def validate_report_class(value):
    from ereports.engine.registry import registry

    if value not in registry:
        raise ValidationError(u'%s is not a registered Report class ' % value)


class ReportConfiguration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey(ReportGroup)
    template = models.ForeignKey(ReportTemplate, blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True, null=True)

    report_class = models.CharField(max_length=200, validators=[validate_report_class])

    target_model = models.ForeignKey(ContentType, blank=True, null=True)
    # datasource = models.CharField('PostProcessor', max_length=200, blank=True, null=True,
    #                               choices=[(k, k) for k, v in postprocessor.registry.iteritems()])

    published = models.BooleanField(default=False)
    select_related = models.BooleanField(default=False)
    use_distinct = models.BooleanField(default=False)

    columns = models.TextField(default='id\n')
    filtering = models.TextField(blank=True, null=True, default="")
    ordering = models.TextField(blank=True, null=True,
                                help_text="allowed ordering for the report. use comma to split fields and semicolon to "
                                          "split the label, ie `employee.lastname,employee.first_name; Name`")

    groupby = models.TextField(blank=True, null=True,
                               help_text="allowed groupby for the report. use semicolon to "
                                         "indicate field;label, ie `contract.type;Contract Group`")

    # extras = models.TextField(blank=True, null=True)
    # rawsql = models.TextField(blank=True, null=True)

    ttl = models.IntegerField('Cache validity (minutes)', default=0)
    cache_key = models.CharField('Cache entry seed', max_length=200, null=False, unique=True, default=keygen)

    class Meta:
        permissions = (('run_report', 'Can run a report'),
                       ('read_report', 'Can read a report'),)
        app_label = 'ereports'

    def __unicode__(self):
        return self.name

    def title(self):
        return self.name

    def get_hard_filters(self, context):
        filters = {}
        if self.filtering:
            for line in self.filtering.splitlines():
                if '=' in line:
                    key, value = line.strip().split('=')
                    if value.startswith('{{'):
                        value = context[value[2:-2].strip()]
                        filters[key.replace('.', "__")] = value
        return filters

    def get_allowed_group_by(self):
        grouping = []
        if self.groupby:
            for g in self.groupby.strip().splitlines():
                o = g.split(';', 1)
                grouping.append((o[0].strip(), o[-1].strip()))
        return grouping

    def get_allowed_order_by(self):
        order_clauses = []
        if self.ordering:
            for g in self.ordering.strip().splitlines():
                o = g.split(';', 1)
                order_clauses.append((o[0].strip(), o[-1].strip()))
        return order_clauses

    def get_allowed_filters(self):
        filters = []
        if self.filtering:
            for line in self.filtering.strip().splitlines():
                if '=' not in line:
                    filters.append(line.strip())
        return filters
