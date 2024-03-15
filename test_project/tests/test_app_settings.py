from copy import copy

from django.conf import settings as django_settings
from django.test import TestCase

from graphql_auth import settings


class AppSettingsTestCase(TestCase):
    def test_reload_settings(self):
        self.assertTrue(settings.graphql_auth_settings.ALLOW_LOGIN_NOT_VERIFIED)

        graphql_auth = copy(django_settings.GRAPHQL_AUTH)
        graphql_auth.update({'ALLOW_LOGIN_NOT_VERIFIED': False})
        settings.reload_graphql_auth_settings(setting="GRAPHQL_AUTH", value=graphql_auth)
        self.assertFalse(settings.graphql_auth_settings.ALLOW_LOGIN_NOT_VERIFIED)

        # back to the primary settings
        graphql_auth.update({'ALLOW_LOGIN_NOT_VERIFIED': True})
        settings.reload_graphql_auth_settings(setting="GRAPHQL_AUTH", value=graphql_auth)
        self.assertTrue(settings.graphql_auth_settings.ALLOW_LOGIN_NOT_VERIFIED)
