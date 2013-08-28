# -*- coding: utf-8 -*-
from unittest import TestCase
from ereports.engine.exceptions import FilterDefinitionError


class TestFilterDefinitionError(TestCase):
    def test_init(self):
        e = FilterDefinitionError('oops')
        self.assertEqual(e.message, 'oops')
        self.assertEqual(str(e), 'oops')
        self.assertEqual(repr(e), 'oops')
