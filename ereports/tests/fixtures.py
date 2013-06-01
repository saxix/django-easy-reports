# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.http import QueryDict
from django.test.client import RequestFactory
from django_dynamic_fixture import G


def get_fake_request():
    u = G(User, username='sax', password='123')
    setattr(u, 'is_authenticated()', True)
    setattr(u, 'selected_office', False)

    request = RequestFactory().request()
    request.user = u

    querydict = QueryDict('arg2=one')
    querydict = querydict.copy()
    querydict.update({'arg1': 'test', 'arg2': "two"})
    request.GET = querydict
    request.POST = QueryDict('username=random')

    return request
