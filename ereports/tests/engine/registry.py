# -*- coding: utf-8 -*-
from ereports.engine import registry
from ereports.utils import fqn

from ereports.tests.app.reports import SimpleDemoReport


class DemoReport(object):
    pass


def test_init():
    r = registry.Registry()
    assert r.reports == []


def test_register():
    r = registry.Registry()
    r.register(DemoReport)
    assert len(r.reports) == 1


def test_register_monitor():
    r = registry.Registry()
    r.register(SimpleDemoReport)
    assert len(r.reports) == 1
    assert len(r.monitors) == 1


def test_get():
    r = registry.Registry()
    r.register(DemoReport)
    assert r.get(fqn(DemoReport), None) == DemoReport
    assert r.get("Wrong", None) is None
    assert r.get("Wrong", DemoReport) == DemoReport
    assert r[0] == r.reports[0]
    assert r[fqn(DemoReport)] == DemoReport
    assert r.choices() == [(fqn(DemoReport), fqn(DemoReport))]
