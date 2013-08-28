from django.core.exceptions import ValidationError
from django.test.testcases import TestCase
from ereports.models import ReportConfiguration, ReportGroup, ReportTemplate, validate_report_class


class TestReportGroup(TestCase):
    def test_init(self):
        r = ReportGroup(name="Name")
        self.assertEqual(unicode(r), u"Name")


class TestReportTemplate(TestCase):
    def test_init(self):
        r = ReportTemplate(name="Name", body="Body Text", system=True)
        self.assertEqual(unicode(r), u"Name")


class TestValidateReportClass(TestCase):
    def test_validate_report_class_exception(self):
        with self.assertRaises(ValidationError):
            validate_report_class("WrongReport")

    # def test_validate_report_class(self):
    #     validate_report_class(fqn(Payroll))


class TestReportConfiguration(TestCase):
    def test_unicode(self):
        r = ReportConfiguration(name="Name")
        self.assertEqual(unicode(r), u"Name")

    def test_title(self):
        r = ReportConfiguration(name="Name")
        self.assertEqual(r.title(), u"Name")

    def test_get_hard_filters(self):
        r = ReportConfiguration(
            filtering="office={{selected_office}}\nnte__lt={{ today }}\nuser.first_name={{ first_name }}"
        )
        context = dict(
            selected_office="Testing",
            today="Now",
            first_name="User"
        )
        filters = r.get_hard_filters(context)
        self.assertIn('office', filters.keys())
        self.assertIn('nte__lt', filters.keys())
        self.assertIn('user__first_name', filters.keys())
        self.assertEqual(filters['office'], 'Testing')
        self.assertEqual(filters['nte__lt'], 'Now')
        self.assertEqual(filters['user__first_name'], 'User')

    def test_hard_filters_none(self):
        r = ReportConfiguration(
            filtering=None
        )
        context = dict()
        filters = r.get_hard_filters(context)
        self.assertEqual(filters, {})

    def test_get_allowed_group_by(self):
        r = ReportConfiguration(
            groupby='user.first_name'
        )
        g = r.get_allowed_group_by()
        self.assertEqual([('user.first_name', 'user.first_name')], g)

        r = ReportConfiguration(
            groupby='user.first_name  ;  First Name'
        )
        g = r.get_allowed_group_by()
        self.assertEqual([('user.first_name', 'First Name')], g)

        r = ReportConfiguration(
            groupby='''user.first_name;First Name
            user.last_name;Last Name
            random;extra;items
            single
            '''
        )
        g = r.get_allowed_group_by()
        self.assertEqual([('user.first_name', 'First Name'),
                          ('user.last_name', 'Last Name'),
                          ('random', 'extra;items'),
                          ('single', 'single')], g)

    def test_get_allowed_order_by(self):
        r = ReportConfiguration(
            ordering='user.first_name'
        )
        g = r.get_allowed_order_by()
        self.assertEqual([('user.first_name', 'user.first_name')], g)

        r = ReportConfiguration(
            ordering='user.first_name  ;   First Name'
        )
        g = r.get_allowed_order_by()
        self.assertEqual([('user.first_name', 'First Name')], g)

        r = ReportConfiguration(
            ordering='''user.first_name;First Name
            user.last_name;Last Name
            random;extra;items
            single
            '''
        )
        g = r.get_allowed_order_by()
        self.assertEqual([('user.first_name', 'First Name'),
                          ('user.last_name', 'Last Name'),
                          ('random', 'extra;items'),
                          ('single', 'single')], g)

    def test_get_allowed_filters(self):
        r = ReportConfiguration(
            filtering='user.first_name'
        )
        g = r.get_allowed_filters()
        self.assertEqual(['user.first_name'], g)

        r = ReportConfiguration(
            filtering='user=first_name'
        )
        g = r.get_allowed_filters()
        self.assertEqual([], g)

        r = ReportConfiguration(
            filtering='''user.first_name
            user.last_name
            user=email
            '''
        )
        g = r.get_allowed_filters()
        self.assertEqual(['user.first_name', 'user.last_name'], g)
