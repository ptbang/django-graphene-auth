from datetime import timedelta

from graphql_auth.constants import Messages
from graphql_auth.testingx import BaseTestCase
from graphql_auth.utils import get_token


class PasswordSetBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user1 = self.create_user(email="gaa@email.com", username="gaa", verified=True, archived=False)
        self.user1_old_pass = self.user1.password

    def get_login_query(self) -> str:
        raise NotImplementedError

    def get_query(self, token, new_password1="new_password", new_password2="new_password") -> str:
        raise NotImplementedError

    def _test_reset_password_successfully(self):
        self.user1.set_unusable_password()
        self.user1.save()
        token = get_token(self.user1, "password_set")
        query = self.get_query(token)
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.has_usable_password())

    def _test_already_set_password(self):
        token = get_token(self.user1, "password_set")
        query = self.get_query(token)
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.PASSWORD_ALREADY_SET)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1_old_pass, self.user1.password)

    def _test_set_password_invalid_form(self):
        token = get_token(self.user1, "password_set")
        query = self.get_query(token, "wrong_pass")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIn('newPassword2', result['errors'].keys())
        self.user1.refresh_from_db()
        self.assertEqual(self.user1_old_pass, self.user1.password)

    def _test_set_password_invalid_token(self):
        query = self.get_query("fake_token")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.INVALID_TOKEN)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1_old_pass, self.user1.password)
        token = get_token(self.user1, "password_set")
        query = self.get_query(token)
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.PASSWORD_ALREADY_SET)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1_old_pass, self.user1.password)

    def _test_token_expired(self):
        token = get_token(self.user1, "password_set")
        query = self.get_query(token)
        with self.settings(GRAPHQL_AUTH={'EXPIRATION_PASSWORD_SET_TOKEN': timedelta(seconds=0.0000001)}):
            response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.EXPIRED_TOKEN)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1_old_pass, self.user1.password)


class PasswordSetTestCase(PasswordSetBaseTestCase):
    RESPONSE_RESULT_KEY = 'passwordSet'

    def get_login_query(self) -> str:
        return """
        mutation {
            tokenAuth(
                username: "foo_username",
                password: "%s",
            )
            { refreshToken }
        }
        """ % (
            self.default_password,
        )

    def get_query(self, token, new_password1="new_password", new_password2="new_password") -> str:
        return """
        mutation {
            passwordSet(
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


class PasswordSetRelayTestCase(PasswordSetBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayPasswordSet'

    def get_login_query(self) -> str:
        return """
            mutation {
                relayTokenAuth(
                    input: {
                        username: "foo_username",
                        password: "%s",
                    }
                )
                { success, refreshToken }
            }
            """ % (
            self.default_password,
        )

    def get_query(self, token, new_password1="new_password", new_password2="new_password") -> str:
        return """
            mutation {
                relayPasswordSet(
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
