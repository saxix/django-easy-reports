# -*- coding: utf-8 -*-
from importlib import import_module
from optparse import make_option
import sys
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from ereports.models import ReportConfiguration, ReportGroup, keygen
from ereports.utils import import_by_path


class Command(BaseCommand):
    args = ''
    help = 'register Report classes and create one ReportConfiguration per each'
    option_list = BaseCommand.option_list + (
        make_option('-m', '--module',
                    action='store',
                    dest='module',
                    default=None,
                    help='extra module to scan'),
        make_option('-o', '--overwrite',
                    action='store_true',
                    dest='overwrite',
                    default=False,
                    help='overwrite existing imported reports'),
        make_option('-z', '--clean',
                    action='store_true',
                    dest='clean',
                    default=False,
                    help='remove existing reports in the selected group'),
        make_option('-g', '--group',
                    action='store',
                    dest='group',
                    default='Standard Report',
                    help='group name the reports will belong to'),
    )

    def handle(self, *args, **options):
        stdout = options.get('stdout', sys.stdout)
        module = options.get('module')
        overwrite = options.get('overwrite')
        clean = options.get('clean')
        groupname = options.get('group')
        verbosity = int(options.get('verbosity'))

        group, __ = ReportGroup.objects.get_or_create(name=groupname)

        from ereports.engine.registry import registry
        from ereports.engine.report import BaseReport

        if module:
            import_module(module.strip())
        if clean:
            ReportConfiguration.objects.filter(group=group).delete()

        # entry is (fqn(report_class), report_class)
        for entry in registry:
            report = import_by_path(entry.classname)

            if not report is BaseReport:
                report = report.as_report()
                if verbosity >= 1:
                    stdout.write("Importing...%s" % entry.classname)
                model = report.model or report.datasource.model
                name = report.title
                i = 0
                while True:
                    try:
                        cfg, isnew = ReportConfiguration.objects.get_or_create(group=group,
                                                                               report_class=entry.classname,
                                                                               defaults={'name': name})
                        break
                    except IntegrityError:
                        i += 1
                        name = "{0.title}_{1}".format(report, i)

                if isnew or overwrite:
                    cfg.columns = "\r\n".join([col.name for col in report.datasource.columns])
                    cfg.target_model = ContentType.objects.get_for_model(model)
                    cfg.published = True
                    cfg.filtering = "\r\n".join(report.list_filter)

                    cfg.cache_key = keygen()
                cfg.save()
                if verbosity >= 1:
                    stdout.write("...Done\n")
