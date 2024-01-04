import json
from copy import copy

from django.conf import settings

from graphql_auth.constants import Messages
from graphql_auth.exceptions import InvalidCredentialsError, UserNotVerifiedError

from .testCases import BaseTestCase


class LoginBaseTestCase(BaseTestCase):
    RESPONSE_RESULT_KEY: str

    def setUp(self):
        self.archived_user = self.register_user(email="gaa@email.com", username="gaa", verified=True, archived=True)
        self.not_verified_user = self.register_user(email="boo@email.com", username="boo", verified=False)
        self.verified_user = self.register_user(
            email="foo@email.com",
            username="foo",
            verified=True,
            secondary_email="secondary@email.com",
        )

    def get_query(self, field, username, password=None) -> str:
        raise NotImplementedError

    def _test_archived_user_becomes_active_on_login(self):
        self.assertEqual(self.archived_user.status.archived, True)  # type: ignore
        query = self.get_query("email", self.archived_user.email)  # type: ignore
        response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertResponseNoErrors(response)
        self.assertTrue(result["token"])
        self.assertTrue(result["refreshToken"])
        self.archived_user.refresh_from_db()
        self.assertEqual(self.archived_user.status.archived, False)  # type: ignore

    def _test_login_username(self):
        query = self.get_query("username", self.verified_user.username)  # type: ignore
        response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertResponseNoErrors(response)
        self.assertTrue(result["token"])
        self.assertTrue(result["refreshToken"])

        query = self.get_query("username", self.not_verified_user.username)  # type: ignore
        response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertResponseNoErrors(response)
        self.assertTrue(result["token"])
        self.assertTrue(result["refreshToken"])

    def _test_login_email(self):
        query = self.get_query("email", self.verified_user.email)  # type: ignore
        response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertTrue(result["token"])
        self.assertTrue(result["refreshToken"])

    def _test_login_secondary_email(self):
        query = self.get_query("email", "secondary@email.com")
        response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertTrue(result["token"])
        self.assertTrue(result["refreshToken"])

    def _test_login_wrong_credentials(self):
        query = self.get_query("username", "wrong-username")
        response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertResponseHasErrors(response)
        self.assertIsNone(result)

    def _test_login_wrong_credentials_2(self):
        query = self.get_query("username", self.verified_user.username, "wrongpass")  # type: ignore
        response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertResponseHasErrors(response)
        self.assertIsNone(result)

    def _test_not_verified_login_on_different_settings(self):
        query = self.get_query("username", self.not_verified_user.username)  # type: ignore
        graphql_auth = copy(settings.GRAPHQL_AUTH)
        graphql_auth.update({'ALLOW_LOGIN_NOT_VERIFIED': False})
        with self.settings(GRAPHQL_AUTH=graphql_auth):
            response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], UserNotVerifiedError.default_message)
        self.assertEqual(error['extensions'], Messages.NOT_VERIFIED)

    def _test_not_verified_login_on_different_settings_wrong_pass(self):
        query = self.get_query("username", self.not_verified_user.username, "wrongpass")  # type: ignore
        graphql_auth = copy(settings.GRAPHQL_AUTH)
        graphql_auth.update({'ALLOW_LOGIN_NOT_VERIFIED': False})
        with self.settings(GRAPHQL_AUTH=graphql_auth):
            response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content)['errors'][0]
        self.assertEqual(error['message'], InvalidCredentialsError.default_message)
        self.assertEqual(error['extensions'], Messages.INVALID_CREDENTIALS)


class LoginTestCase(LoginBaseTestCase):
    RESPONSE_RESULT_KEY = 'tokenAuth'

    def get_query(self, field, username, password=None):
        return """
            mutation {
                tokenAuth(%s: "%s", password: "%s" )
                    { token, refreshToken, user { username, id }, unarchiving  }
            }
            """ % (
            field,
            username,
            password or self.default_password,
        )


class LoginRelayTestCase(LoginBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayTokenAuth'

    def get_query(self, field, username, password=None):
        return """
            mutation {
                relayTokenAuth(input:{ %s: "%s", password: "%s" })
                    { token, refreshToken, user { username, id }, unarchiving  }
                }
            """ % (
            field,
            username,
            password or self.default_password,
        )
