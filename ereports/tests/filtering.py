# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from django.test.testcases import TestCase

from ereports.filtering import QueryField, FilterQuerysetMixin, ANY_LOOKUP_ALLOWED
from ereports.tests.fixtures import get_fake_request
from ereports.utils import StartWithList


class FakeSearchForm(forms.Form):
    arg1 = forms.CharField(max_length=150)
    arg2 = forms.CharField(max_length=150)
    _random = forms.CharField(max_length=20)
    username = QueryField(max_length=20)


class TestQueryField(TestCase):
    def test_init(self):
        q = QueryField()
        self.assertIsInstance(q, QueryField)


class TestFilterQuerysetMixin(TestCase):
    def setUp(self):
        self.mixin = FilterQuerysetMixin()
        self.mixin.model = User
        self.request = get_fake_request()

    def test_get_params(self):
        params = self.mixin.get_params(self.request)
        self.assertEqual(params, {u'arg1': u'test', u'arg2': u'two'})

    def test_get_querydict(self):
        querydict = self.mixin.get_querydict(self.request)
        self.assertIsInstance(querydict, QueryDict)

    def test_get_search_form(self):
        form = self.mixin.get_search_form()
        self.assertIsInstance(form, self.mixin.search_form_class)

    def test_get_query_help_message(self):
        self.assertEqual(self.mixin.get_query_help_message(), "")

        self.mixin.search_fields = ['nonexistant']
        with self.assertRaises(ImproperlyConfigured):
            self.mixin.get_query_help_message()

        self.mixin.search_fields = ['username']
        self.assertEqual(self.mixin.get_query_help_message(), 'Username')

        self.mixin.search_fields = ['username', 'password']
        self.assertEqual(self.mixin.get_query_help_message(), 'Username,Password')

    def test_query_param(self):
        self.assertEqual(self.mixin.query_param, None)

        self.mixin.search_form_class = FakeSearchForm
        self.assertEqual(self.mixin.query_param, 'username')

    def test_query(self):
        self.mixin.params = self.mixin.get_params(self.request)
        self.assertEqual(self.mixin.query, '')

        self.mixin.method = 'POST'
        self.mixin.params = self.mixin.get_params(self.request)
        self.mixin.search_form_class = FakeSearchForm
        self.assertEqual(self.mixin.query, u'random')

    def test_get_lookup_fields(self):
        lk = self.mixin.get_lookup_fields()
        self.assertEqual(lk, [])
        self.assertIsInstance(lk, StartWithList)

        self.mixin.search_form_class = FakeSearchForm
        lk = self.mixin.get_lookup_fields()
        self.assertEqual(lk, ["arg1", "arg2"])

        self.mixin.lookup_fields = ANY_LOOKUP_ALLOWED
        self.assertEqual(self.mixin.get_lookup_fields(), ANY_LOOKUP_ALLOWED)

    def test_get_filters(self):
        self.assertEqual(self.mixin._get_filters(), {})

        self.mixin.search_form_class = FakeSearchForm
        self.mixin.params = self.mixin.get_params(self.request)
        self.mixin.querydict = self.mixin.get_querydict(self.request)
        self.assertEqual(self.mixin._get_filters(), {u"arg1": u"test", "arg2__in": ["one", "two"]})

    def test_filter_qs(self):
        qs = User.objects.all()
        res = self.mixin._filter_qs(qs)
        self.assertEqual(len(qs), len(res))

        self.mixin.method = 'POST'
        self.mixin.search_form_class = FakeSearchForm
        self.mixin.params = self.mixin.get_params(self.request)
        self.mixin.querydict = self.mixin.get_querydict(self.request)

        self.mixin.search_fields = ['username']
        self.mixin.params = {u'username': 'Sax'}
        res = self.mixin._filter_qs(qs)
        self.assertEqual(len(res), 1)

        self.mixin.search_fields = ['^username']
        self.mixin.params = {u'username': 'sa'}
        res = self.mixin._filter_qs(qs)
        self.assertEqual(len(res), 1)

        self.mixin.search_fields = ['=username']
        self.mixin.params = {u'username': 'sax'}
        res = self.mixin._filter_qs(qs)
        self.assertEqual(len(res), 1)

        #NOTE Full-text search not implemented for testing db backend
        # self.mixin.search_fields = ['@username']
        # self.mixin.params = {u'username': 'sax'}
        # res = self.mixin._filter_qs(qs)
        # self.assertEqual(len(res), 1)
