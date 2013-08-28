# -*- coding: utf-8 -*-
import logging
from collections import namedtuple
from ereports.engine.cache import monitor_model
from ereports.utils import fqn, get_attr

logger = logging.getLogger(__name__)

_Entry = namedtuple('Entry', "classname,type")


class Registry(object):
    """
        Registry of all known Report(s)
    """

    def __init__(self):
        super(Registry, self).__init__()
        self.reports = []
        self.monitors = []

    def register(self, report_class):
        model = get_attr(report_class, 'datasource.model', None)
        if model is None:
            logger.error("Unable to monitor {0}".format(report_class))

        elif model not in self.monitors:
            self.monitors.append(model)
            monitor_model(model)

        self.reports.append(_Entry(fqn(report_class), report_class))

    def __iter__(self):
        for el in self.reports:
            yield el

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.reports[item]
        elif isinstance(item, basestring):
            return filter(lambda el: el.classname == item, self)[0][1]

    def __contains__(self, item):
        return item in [r.classname for r in self]

    def choices(self):
        return [(el.classname, el.classname) for el in self]

    def get(self, class_name, default=None):
        if class_name in self:
            return self[class_name]
        return default


registry = Registry()
