import json

from django.contrib.auth import forms

from graphql_auth.constants import Messages

from .testCases import BaseTestCase


class PasswordChangeBaseTestCase(BaseTestCase):
    RESPONSE_TOKEN_AUTH_KEY: str

    def setUp(self):
        self.user = self.register_user(email="gaa@email.com", username="gaa", verified=True)
        self.user_old_pass = self.user.password

    def get_login_query(self):
        raise NotImplementedError

    def get_query(self, new_password1="new_password", new_password2="new_password"):
        raise NotImplementedError

    def _test_password_change(self):
        self.client.force_login(self.user)
        response = self.query(self.get_query())
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertTrue(result['token'])
        self.assertTrue(result['refreshToken'])
        self.user.refresh_from_db()
        self.assertNotEqual(self.user_old_pass, self.user.password)

    def _test_password_change_failed_with_unauthenticated_user(self):
        response = self.query(self.get_query())
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['extensions'], Messages.UNAUTHENTICATED)

    def _test_mismatch_passwords(self):
        self.client.force_login(self.user)
        response = self.query(self.get_query('wrong_password'))
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], Messages.FAILED_PASSWORD_CHANGE_MESSAGE)
        self.assertEqual(
            error['extensions']['newPassword2'][0], forms.PasswordChangeForm.error_messages['password_mismatch']
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user_old_pass, self.user.password)

    def _test_password_validation_failure(self):
        self.client.force_login(self.user)
        response = self.query(self.get_query('123', '123'))
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], Messages.FAILED_PASSWORD_CHANGE_MESSAGE)

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
        """ % (self.user.username, self.default_password)  # type: ignore

    def get_query(self, new_password1="new_password", new_password2="new_password"):
        return """
        mutation {
            passwordChange(
                oldPassword: "%s",
                newPassword1: "%s",
                newPassword2: "%s"
            )
            { token, refreshToken }
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
                { token, refreshToken }
            }
        """ % (
            self.default_password,
            new_password1,
            new_password2,
        )

