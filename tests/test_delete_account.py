import json

from django.core.exceptions import ObjectDoesNotExist

from graphql_auth.constants import Messages

from .testCases import BaseTestCase


class DeleteAccountBaseTestCase(BaseTestCase):
    LOGIN_RESPONSE_RESULT_KEY: str

    def setUp(self):
        self.user1 = self.register_user(email="foo@email.com", username="foo")
        self.user2 = self.register_user(email="bar@email.com", username="bar", verified=True)

    def get_login_query(self, user) -> str:
        raise NotImplementedError

    def get_query(self, password=None) -> str:
        raise NotImplementedError

    def _test_with_user_not_authenticated(self):
        query = self.get_query()
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = self.get_response_errors(response)[0]
        self.assertEqual(error['message'], Messages.UNAUTHENTICATED['message'])
        self.assertEqual(error['extensions'], Messages.UNAUTHENTICATED)

    def _test_invalid_password(self):
        self.client.force_login(self.user2)
        query = self.get_query(password='wrong-password')
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = self.get_response_errors(response)[0]
        self.assertEqual(error['message'], Messages.INVALID_PASSWORD['message'])
        self.assertEqual(error['extensions'], Messages.INVALID_PASSWORD)

    def _test_revoke_refresh_tokens_on_delete_account(self):
        response = self.query(self.get_login_query(self.user2))
        tokens = json.loads(response.content.decode())['data'][self.LOGIN_RESPONSE_RESULT_KEY]
        self.user2.refresh_from_db()
        refresh_tokens = self.user2.refresh_tokens.all()  # type: ignore
        for token in refresh_tokens:
            self.assertFalse(token.revoked)

        query = self.get_query()
        self.assertEqual(self.user2.is_active, True)
        response = self.query(query, headers=self.get_authorization_header(tokens['token']))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)

        self.assertTrue(result['success'])
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.is_active, False)

        refresh_tokens = self.user2.refresh_tokens.all()  # type: ignore
        for token in refresh_tokens:
            self.assertTrue(token.revoked)

    def _test_not_verified_user(self):
        query = self.get_query()
        self.client.force_login(self.user1)
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = self.get_response_errors(response)[0]
        self.assertEqual(error['message'], Messages.NOT_VERIFIED['message'])
        self.assertEqual(error['extensions'], Messages.NOT_VERIFIED)

    def _test_permanently_delete(self):
        self.client.force_login(self.user2)
        query = self.get_query()
        self.assertEqual(self.user2.is_active, True)
        with self.settings(GRAPHQL_AUTH={'ALLOW_DELETE_ACCOUNT': True}):
            response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        with self.assertRaises(ObjectDoesNotExist):
            self.user2.refresh_from_db()


class DeleteAccountTestCase(DeleteAccountBaseTestCase):
    RESPONSE_RESULT_KEY = 'deleteAccount'
    LOGIN_RESPONSE_RESULT_KEY = 'tokenAuth'

    def get_login_query(self, user):
        return """
        mutation {
            tokenAuth(
                email: "%s",
                password: "%s",
            )
            { token, refreshToken }
        }
        """ % (
            user.email,
            self.default_password,
        )

    def get_query(self, password=None):
        return """
            mutation {
              deleteAccount(password: "%s") {
                success
              }
            }
        """ % (password or self.default_password,)


class DeleteAccountRelayTestCase(DeleteAccountBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayDeleteAccount'
    LOGIN_RESPONSE_RESULT_KEY = 'relayTokenAuth'

    def get_login_query(self, user):
        return """
        mutation {
            relayTokenAuth(
                input: {
                    email: "%s",
                    password: "%s",
                }
            )
            { token, refreshToken }
        }
        """ % (
            user.email,
            self.default_password,
        )

    def get_query(self, password=None):
        return """
        mutation {
            relayDeleteAccount(input: { password: "%s"})
                { success }
        }
        """ % (password or self.default_password,)
