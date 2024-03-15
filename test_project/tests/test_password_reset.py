import json

from graphql_auth.common_testcase import CommonTestCase
from graphql_auth.constants import Messages
from graphql_auth.utils import get_token


class PasswordResetCommonTestCase(CommonTestCase):
    def setUp(self):
        self.user1 = self.create_user(email="gaa@email.com", username="gaa", verified=True, archived=False)
        self.user1_old_pass = self.user1.password

    def get_login_query(self) -> str:
        raise NotImplementedError

    def get_query(self, token, new_password1="new_password", new_password2="new_password"):
        raise NotImplementedError

    def _test_reset_password_successfully(self):
        token = get_token(self.user1, "password_reset")
        query = self.get_query(token)
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertEqual(result['success'], True)
        self.user1.refresh_from_db()
        self.assertNotEqual(self.user1_old_pass, self.user1.password)

    def _test_reset_password_invalid_form(self):
        token = get_token(self.user1, "password_reset")
        query = self.get_query(token, "wrong_pass")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIn('newPassword2', result['errors'])
        self.user1.refresh_from_db()
        self.assertEqual(self.user1_old_pass, self.user1.password)

    def _test_reset_password_invalid_token(self):
        query = self.get_query("fake_token")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.INVALID_TOKEN)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1_old_pass, self.user1.password)

    def _test_revoke_refresh_tokens_on_password_reset(self):
        self.query(self.get_login_query())
        self.user1.refresh_from_db()
        refresh_tokens = self.user1.refresh_tokens.all()  # type: ignore
        for token in refresh_tokens:
            self.assertFalse(token.revoked)
        token = get_token(self.user1, "password_reset")
        query = self.get_query(token)
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.user1.refresh_from_db()
        self.assertNotEqual(self.user1_old_pass, self.user1.password)
        refresh_tokens = self.user1.refresh_tokens.all()  # type: ignore
        for token in refresh_tokens:
            self.assertTrue(token.revoked)

    def _test_password_reset_verifies_user(self):
        self.user1.verified = False  # type: ignore
        self.user1.save()

        token = get_token(self.user1, "password_reset")
        query = self.get_query(token)
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.user1.refresh_from_db()
        self.assertNotEqual(self.user1_old_pass, self.user1.password)
        self.assertTrue(self.user1.status.verified)  # type: ignore


class PasswordResetTestCase(PasswordResetCommonTestCase):
    RESPONSE_RESULT_KEY = 'passwordReset'

    def get_login_query(self):
        return """
        mutation {
            tokenAuth(
                username: "foo_username",
                password: "%s",
            )
            { success, token, refreshToken }
        }
        """ % (
            self.default_password,
        )

    def get_query(self, token, new_password1="new_password", new_password2="new_password"):
        return """
        mutation {
            passwordReset(
                token: "%s",
                newPassword1: "%s",
                newPassword2: "%s"
            )
            { success, errors }
        }
        """ % (
            token,
            new_password1,
            new_password2,
        )


class PasswordResetRelayTestCase(PasswordResetCommonTestCase):
    RESPONSE_RESULT_KEY = 'relayPasswordReset'

    def get_login_query(self) -> str:
        return """
        mutation {
            relayTokenAuth(
                input: {
                    username: "foo_username",
                    password: "%s",
                }
            )
            { success, token, refreshToken }
        }
        """ % (
            self.default_password,
        )

    def get_query(self, token, new_password1="new_password", new_password2="new_password") -> str:
        return """
        mutation {
            relayPasswordReset(
                input: {
                    token: "%s",
                    newPassword1: "%s",
                    newPassword2: "%s"
                })
            { success, errors }
        }
        """ % (
            token,
            new_password1,
            new_password2,
        )
