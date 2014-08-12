"""
Minor test to ensure that API DOC based on swagger is ok when enabled
"""
from django.test import TestCase
from django.test.client import Client
from django.conf import settings


class ApiDocTestCase(TestCase):
    c = Client(enforce_csrf_checks=True)

    def test_apidoc(self):
        """test api/doc"""
        if 'tastypie_swagger' in settings.INSTALLED_APPS:
            ret = self.c.get("/api/doc/")
            self.assertEqual(ret.status_code, 200)

