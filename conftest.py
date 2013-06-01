import os
import sys
from django.conf import settings


def pytest_configure(config):
    here = os.path.dirname(__file__)
    sys.path.insert(0, here)

    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'ereports.tests.settings'


    settings.INSTALLED_APPS = tuple(settings.INSTALLED_APPS) + (
        'ereports',
        'ereports.tests.app',
    )
    settings.LOGGING['loggers'][''] = {'handlers': ['null'],
                          'propagate': True,
                          'level': 'DEBUG'}

    os.environ['PREFIX'] = os.path.join(here, "~build")


def runtests(args=None):
    import pytest

    if not args:
        args = []

    if not any(a for a in args[1:] if not a.startswith('-')):
        args.append('ereports')

    sys.exit(pytest.main(args))


if __name__ == '__main__':
    runtests(sys.argv)
