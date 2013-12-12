# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.test.testcases import TestCase

from ereports.engine.utils import get_tables_for_query


class TestGetTablesForQuery(TestCase):
    def test_get_tables(self):
        qs = User.objects.filter(username='*')
        tables = get_tables_for_query(qs.query)
        self.assertEqual(tables, ['auth_user'])

    def test_get_tables_children(self):
        qs = Permission.objects.filter(name='*', content_type=ContentType.objects.filter(name='*'))
        tables = get_tables_for_query(qs.query)
        self.assertEqual(sorted(tables), ['auth_permission', 'django_content_type'])

    def test_get_tables_children_wherenode(self):
        qs = Permission.objects.filter(Q(name__startswith='a'), Q(content_type__name='*'))
        tables = get_tables_for_query(qs.query)
        self.assertEqual(sorted(tables), ['auth_permission', 'django_content_type'])
