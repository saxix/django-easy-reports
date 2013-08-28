from django.conf import settings
import os
import sys


def pytest_configure(config):
    here = os.path.dirname(__file__)
    sys.path.insert(0, here)

    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'ereports.tests.settings'
