# -*- coding: utf-8 -*-
from logging import getLogger
import operator
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django import forms
from ereports.utils import StartWithList, get_field_from_path, filter_dictionary

logger = getLogger(__name__)


class QueryField(forms.CharField):
    def __init__(self, max_length=None, min_length=None, label="", required=False,
                 widget=forms.TextInput({"class": "search-query",
                                         "placeholder": "Type something…"}), *args, **kwargs):
        super(QueryField, self).__init__(max_length, min_length, label=label, required=required,
                                         widget=widget, *args, **kwargs)


class SearchForm(forms.Form):
    pass


ANY_LOOKUP_ALLOWED = 888


class FilterQuerysetMixin(object):
    search_fields = None
    lookup_fields = None
    search_form_class = SearchForm
    filters = []
    method = 'GET'

    def dispatch(self, request, *args, **kwargs):
        self.params = self.get_params(request)
        self.querydict = self.get_querydict(request)
        return super(FilterQuerysetMixin, self).dispatch(request, *args, **kwargs)

    def get_params(self, request):
        querydict = self.get_querydict(request)
        return dict(querydict.items())

    def get_querydict(self, request):
        return getattr(request, self.method)

    @property
    def query_param(self):
        search_form = type(self.get_search_form())
        return filter_dictionary(search_form.base_fields, lambda x: isinstance(x, QueryField))

    @property
    def query(self):
        return self.params.get(self.query_param, '')

    def get_search_form_class(self):
        return self.search_form_class

    def get_search_form(self, *args, **kwargs):
        return self.get_search_form_class()(*args, **kwargs)

    def get_query_help_message(self):
        if not self.search_fields:
            return ''
        fields = []
        for search_field in self.search_fields:
            field = get_field_from_path(self.model, search_field)
            if field is None:
                raise ImproperlyConfigured("cannot access to `%s` from %s " % (search_field, self.model))
            fields.append(field.verbose_name.title())
        return ",".join(fields)

    def get_lookup_fields(self):
        if self.lookup_fields == ANY_LOOKUP_ALLOWED:
            return ANY_LOOKUP_ALLOWED
        lk = self.lookup_fields or []
        form = self.get_search_form()
        if form:
            for attr_name in form.base_fields.keys():
                if not attr_name == self.query_param and not attr_name.startswith('_'):
                    lk.append(attr_name)
        return StartWithList(lk)

    def _get_filters(self):
        filters = {}
        lookup_fields = self.get_lookup_fields()
        if lookup_fields:
            for k, v in self.params.items():
                if v and ((lookup_fields == ANY_LOOKUP_ALLOWED) or (k in lookup_fields)):
                    real_value = self.querydict.getlist(k)
                    if len(real_value) == 1:
                        filters[k] = real_value[0]
                    else:
                        filters['%s__in' % k] = real_value
        return filters

    def _filter_qs(self, qs):
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        filters = self._get_filters()
        if self.search_fields and self.query:
            orm_lookups = [construct_search(str(search_field).replace('.', '__'))
                           for search_field in self.search_fields]
            for bit in self.query.split():
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                qs = qs.filter(reduce(operator.or_, or_queries))

        return qs.filter(**filters).select_related()

    def get_queryset(self):
        qs = super(FilterQuerysetMixin, self).get_queryset()
        return self._filter_qs(qs)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'query': self.query,
            'query_param': self.query_param,
            'searchform': self.get_search_form(self.querydict, initial=dict(self.querydict.items())),
            'query_help_message': self.get_query_help_message(),
            'search_fields': self.search_fields,
        })
        return kwargs
