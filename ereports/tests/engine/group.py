from unittest import TestCase
from django.contrib.auth.models import User
from ereports.engine.columns import StringFormatColumn
from ereports.engine.datasource import Datasource
from ereports.engine.report import BaseReport
from ereports.tests.engine.fixtures import FakeQuerySet


class TestGroup(TestCase):
    def test_simple_group(self):
        itms = [User(username='username%s' % x, is_staff=bool(x % 2)) for x in range(6)]

        ds = Datasource.as_datasource(model=User,
                                      queryset=FakeQuerySet(model=User, items=itms))

        TestReport = type('TestReport', (BaseReport,), {'model': User,
                                                        'list_display': ('is_staff', 'username'),
                                                        'group_by': ('is_staff', 'username'),
                                                        'datasource': ds})
        report = TestReport.as_report()
        self.assertSequenceEqual(list(report),
                                 [(False, 'username0'),
                                  (False, 'username2'),
                                  (False, 'username4'),
                                  (True, 'username1'),
                                  (True, 'username3'),
                                  (True, 'username5')])

    def test_callback_group(self):
        itms = [User(username='username%s' % x, is_staff=bool(x % 2)) for x in range(6)]

        ds = Datasource.as_datasource(model=User,
                                      queryset=FakeQuerySet(model=User, items=itms))

        def is_staff(rec):
            return str(rec.is_staff)

        TestReport = type('TestReport', (BaseReport,), {'model': User,
                                                        'list_display': ('is_staff', 'username'),
                                                        'group_by': (is_staff, 'username'),
                                                        'datasource': ds})
        report = TestReport.as_report()
        self.assertItemsEqual(dict(report.get_groups()).keys(), ['True', 'False'])
        self.assertSequenceEqual(list(report),
                                 [(False, 'username0'),
                                  (False, 'username2'),
                                  (False, 'username4'),
                                  (True, 'username1'),
                                  (True, 'username3'),
                                  (True, 'username5')])

    def test_by_custom_column(self):
        itms = [User(username='username%s' % x,
                     first_name='fn%s' % int(x % 2),
                     last_name='ln%s' % int(x % 2),
                     is_staff=bool(x % 2)) for x in range(6)]

        ds = Datasource.as_datasource(model=User,
                                      columns=('is_staff',
                                               'username',
                                               StringFormatColumn('group',
                                                                  format='{0.last_name} {0.first_name}')),
                                      queryset=FakeQuerySet(model=User, items=itms))

        TestReport = type('Report', (BaseReport,), {'datasource': ds,
                                                    'group_by': ('group', 'username'),
                                                    'list_display': ('group', 'username')})
        report = TestReport.as_report()
        self.assertSequenceEqual(sorted(dict(report.get_groups()).keys()),
                                 ['ln0 fn0', 'ln1 fn1'])

        self.assertSequenceEqual(list(report),
                                 [('ln0 fn0', 'username0'),
                                  ('ln0 fn0', 'username2'),
                                  ('ln0 fn0', 'username4'),
                                  ('ln1 fn1', 'username1'),
                                  ('ln1 fn1', 'username3'),
                                  ('ln1 fn1', 'username5')])
