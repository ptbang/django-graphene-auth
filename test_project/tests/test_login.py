from copy import copy

from django.conf import settings

from graphql_auth.common_testcase import CommonTestCase
from graphql_auth.constants import Messages


class LoginCommonTestCase(CommonTestCase):
    RESPONSE_RESULT_KEY: str

    def setUp(self):
        self.archived_user = self.create_user(email="gaa@email.com", username="gaa", verified=True, archived=True)
        self.not_verified_user = self.create_user(email="boo@email.com", username="boo", verified=False)
        self.verified_user = self.create_user(
            email="foo@email.com",
            username="foo",
            verified=True,
            secondary_email="secondary@email.com",
        )

    def get_query(self, field, username, password=None) -> str:
        raise NotImplementedError

    def get_query_with_more_than_2_args(self, field, username, password=None):
        raise NotImplementedError

    def _test_archived_user_becomes_active_on_login(self):
        self.assertEqual(self.archived_user.status.archived, True)  # type: ignore
        query = self.get_query("email", self.archived_user.email)  # type: ignore
        with self.assertNumQueries(4):
            response = self.query(query)
        result = self.get_response_result(response)
        self.assertResponseNoErrors(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertTrue(result["token"])
        self.assertTrue(result["refreshToken"])
        self.assertTrue(result['unarchiving'])
        self.archived_user.refresh_from_db()
        self.assertEqual(self.archived_user.status.archived, False)  # type: ignore

    def _test_login_by_username(self):
        query = self.get_query("username", self.verified_user.username)  # type: ignore
        with self.assertNumQueries(3):
            response = self.query(query)
        result = self.get_response_result(response)
        self.assertResponseNoErrors(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertTrue(result["token"])
        self.assertTrue(result["payload"])
        self.assertTrue(result["refreshExpiresIn"])
        self.assertTrue(result["refreshToken"])
        self.assertTrue(result["refreshToken"])
        self.assertFalse(result['unarchiving'])

    def _test_not_verified_user_login_by_username(self):
        query = self.get_query("username", self.not_verified_user.username)  # type: ignore
        with self.assertNumQueries(3):
            response = self.query(query)
        result = self.get_response_result(response)
        self.assertResponseNoErrors(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertTrue(result["token"])
        self.assertTrue(result["refreshToken"])
        self.assertFalse(result['unarchiving'])

    def _test_login_by_email(self):
        query = self.get_query("email", self.verified_user.email)  # type: ignore
        with self.assertNumQueries(3):
            response = self.query(query)
        result = self.get_response_result(response)
        self.assertResponseNoErrors(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertTrue(result["token"])
        self.assertTrue(result["refreshToken"])
        self.assertFalse(result['unarchiving'])

    def _test_login_by_secondary_email(self):
        query = self.get_query("email", self.verified_user.status.secondary_email)  # type: ignore
        with self.assertNumQueries(3):
            response = self.query(query)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertTrue(result["token"])
        self.assertTrue(result["refreshToken"])

    def _test_login_failed_by_wrong_username(self):
        query = self.get_query("username", "wrong-username")
        with self.assertNumQueries(1):
            response = self.query(query)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.INVALID_CREDENTIALS)
        self.assertIsNone(result["token"])
        self.assertIsNone(result["refreshToken"])
        self.assertIsNone(result["payload"])
        self.assertIsNone(result["refreshExpiresIn"])

    def _test_login_failed_by_wrong_password(self):
        query = self.get_query("username", self.verified_user.username, "wrongpass")  # type: ignore
        with self.assertNumQueries(2):
            response = self.query(query)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.INVALID_CREDENTIALS)
        self.assertIsNone(result["token"])
        self.assertIsNone(result["refreshToken"])

    def _test_not_verified_user_login_on_different_settings(self):
        query = self.get_query("username", self.not_verified_user.username)  # type: ignore
        graphql_auth = copy(settings.GRAPHQL_AUTH)
        graphql_auth.update({'ALLOW_LOGIN_NOT_VERIFIED': False})
        with self.settings(GRAPHQL_AUTH=graphql_auth):
            with self.assertNumQueries(1):
                response = self.query(query)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.NOT_VERIFIED)
        self.assertIsNone(result["token"])
        self.assertIsNone(result["refreshToken"])

    def _test_with_more_than_2_args(self):
        query = self.get_query_with_more_than_2_args()  # type: ignore
        with self.assertNumQueries(0):
            response = self.query(query)
        self.assertResponseHasErrors(response)
        errors = self.get_response_errors(response)
        self.assertIn("Must login with password and one of the following fields", errors[0]['message'])


class LoginTestCase(LoginCommonTestCase):
    RESPONSE_RESULT_KEY = 'tokenAuth'

    def get_query(self, field, username, password=None):
        return """
            mutation {
                tokenAuth(%s: "%s", password: "%s")
                    { success, errors, token, payload, refreshToken, refreshExpiresIn, user { username, id }, unarchiving  }
            }
            """ % (
            field,
            username,
            password or self.default_password,
        )

    def get_query_with_more_than_2_args(self):
        return """
            mutation {
                tokenAuth(username: "%s", password: "%s", email: "%s")
                    { success, errors, token, payload, refreshToken, refreshExpiresIn, user { username, id }, unarchiving  }
            }
            """ % (
            self.verified_user.username,  # type: ignore
            self.default_password,
            self.verified_user.email,  # type: ignore
        )


class LoginRelayTestCase(LoginCommonTestCase):
    RESPONSE_RESULT_KEY = 'relayTokenAuth'

    def get_query(self, field, username, password=None):
        return """
            mutation {
                relayTokenAuth(input:{ %s: "%s", password: "%s"})
                    { success, errors, token, payload, refreshToken, refreshExpiresIn, user { username, id }, unarchiving  }
                }
            """ % (
            field,
            username,
            password or self.default_password,
        )

    def get_query_with_more_than_2_args(self):
        return """
            mutation {
                relayTokenAuth(input:{username: "%s", password: "%s", email: "%s"})
                    { success, errors, token, payload, refreshToken, refreshExpiresIn, user { username, id }, unarchiving  }
                }
            """ % (
            self.verified_user.username,  # type: ignore
            self.default_password,
            self.verified_user.email,  # type: ignore
        )
