import json

from graphql_auth.constants import Messages
from graphql_auth.base_testcase import BaseTestCase


class PasswordChangeBaseTestCase(BaseTestCase):
    RESPONSE_TOKEN_AUTH_KEY: str

    def setUp(self):
        self.user = self.create_user(email="gaa@email.com", username="gaa", verified=True)
        self.user_old_pass = self.user.password

    def get_login_query(self):
        raise NotImplementedError

    def get_query(self, new_password1="new_password", new_password2="new_password"):
        raise NotImplementedError

    def _test_password_change(self):
        self.client.force_login(self.user)
        response = self.query(self.get_query())
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertTrue(result['token'])
        self.assertTrue(result['refreshToken'])
        self.user.refresh_from_db()
        self.assertNotEqual(self.user_old_pass, self.user.password)

    def _test_password_change_failed_with_unauthenticated_user(self):
        response = self.query(self.get_query())
        self.assertResponseHasErrors(response)
        error = self.get_response_errors(response)[0]
        self.assertEqual(error['extensions'], Messages.UNAUTHENTICATED)

    def _test_mismatch_passwords(self):
        self.client.force_login(self.user)
        response = self.query(self.get_query('wrong_password'))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIn('newPassword2', result['errors'].keys())
        self.assertIsNone(result['token'])
        self.assertIsNone(result['refreshToken'])
        self.user.refresh_from_db()
        self.assertEqual(self.user_old_pass, self.user.password)

    def _test_password_validation_failure(self):
        self.client.force_login(self.user)
        response = self.query(self.get_query('123', '123'))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIn(
            'This password is too short. It must contain at least 8 characters.', result['errors']['newPassword2']
        )
        self.assertIsNone(result['token'])
        self.assertIsNone(result['refreshToken'])
        self.user.refresh_from_db()
        self.assertEqual(self.user_old_pass, self.user.password)

    def _test_revoke_refresh_tokens_on_password_change(self):
        response = self.query(self.get_login_query())
        self.assertResponseNoErrors(response)
        token = json.loads(response.content.decode())['data'][self.RESPONSE_TOKEN_AUTH_KEY]['token']
        self.user.refresh_from_db()
        refresh_tokens = self.user.refresh_tokens.all()  # type: ignore
        for refresh_token in refresh_tokens:
            self.assertFalse(refresh_token.revoked)

        response = self.query(self.get_query(), headers=self.get_authorization_header(token))
        self.assertResponseNoErrors(response)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user_old_pass, self.user.password)
        new_refresh_tokens = self.user.refresh_tokens.all().order_by('-created')  # type: ignore
        i = 0
        for refresh_token in new_refresh_tokens:
            if i == 0:
                self.assertFalse(refresh_token.revoked)
            else:
                self.assertTrue(refresh_token.revoked)
            i += 1


class PasswordChangeTestCase(PasswordChangeBaseTestCase):
    RESPONSE_RESULT_KEY = 'passwordChange'
    RESPONSE_TOKEN_AUTH_KEY = 'tokenAuth'

    def get_login_query(self):
        return """
        mutation {
            tokenAuth(
                username: "%s",
                password: "%s",
            )
            { token, refreshToken }
        }
        """ % (
            self.user.username,  # type: ignore
            self.default_password,
        )

    def get_query(self, new_password1="new_password", new_password2="new_password"):
        return """
        mutation {
            passwordChange(
                oldPassword: "%s",
                newPassword1: "%s",
                newPassword2: "%s"
            )
            { token, refreshToken, errors, success }
        }
        """ % (
            self.default_password,
            new_password1,
            new_password2,
        )


class PasswordChangeRelayTestCase(PasswordChangeBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayPasswordChange'
    RESPONSE_TOKEN_AUTH_KEY = 'relayTokenAuth'

    def get_login_query(self):
        return """
            mutation {
                relayTokenAuth(
                    input: {
                        username: "%s",
                        password: "%s",
                    }
                )
                { token, refreshToken }
            }
        """ % (
            self.user.username,  # type: ignore
            self.default_password,
        )

    def get_query(self, new_password1="new_password", new_password2="new_password"):
        return """
            mutation {
                relayPasswordChange(
                    input: {
                        oldPassword: "%s",
                        newPassword1: "%s",
                        newPassword2: "%s"
                    })
                { token, refreshToken, errors, success }
            }
        """ % (
            self.default_password,
            new_password1,
            new_password2,
        )
