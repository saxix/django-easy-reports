# -*- coding: utf-8 -*-
from django.contrib.admin.models import User
from ereports.engine.registry import registry
from ereports.engine.renderer import BaseHtmlRender, BaseXlsRender
from ereports.engine.report import BaseReport
from ereports.engine.datasource import Datasource


class UserDataSource(Datasource):
    model = User
    columns = ['username',
               'last_name',
               'first_name',
               'email',
               'is_staff',
               'is_active',
               'date_joined']


class UserReport(BaseReport):
    datasource = UserDataSource.as_datasource()
    title = 'Users'


registry.register(UserReport)
