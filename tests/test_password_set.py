import json

from graphql_auth.constants import Messages
from graphql_auth.utils import get_token

from .testCases import BaseTestCase


class PasswordSetBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user1 = self.register_user(email="gaa@email.com", username="gaa", verified=True, archived=False)
        self.user1_old_pass = self.user1.password

    def get_login_query(self) -> str:
        raise NotImplementedError

    def get_query(self, token, new_password1="new_password", new_password2="new_password") -> str:
        raise NotImplementedError

    def _test_already_set_password(self):
        token = get_token(self.user1, "password_set")
        query = self.get_query(token)
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], Messages.PASSWORD_ALREADY_SET['message'])
        self.assertEqual(error['extensions'], Messages.PASSWORD_ALREADY_SET)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1_old_pass, self.user1.password)

    def _test_set_password_invalid_form(self):
        token = get_token(self.user1, "password_set")
        query = self.get_query(token, "wrong_pass")
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], Messages.FAILED_PASSWORD_CHANGE_MESSAGE)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1_old_pass, self.user1.password)

    def _test_set_password_invalid_token(self):
        query = self.get_query("fake_token")
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], Messages.FAILED_PASSWORD_CHANGE_MESSAGE)
        self.assertEqual(error['extensions'], Messages.INVALID_TOKEN)
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
        """ % (self.default_password,)

    def get_query(self, token, new_password1="new_password", new_password2="new_password") -> str:
        return """
        mutation {
            passwordSet(
                token: "%s",
                newPassword1: "%s",
                newPassword2: "%s"
            )
            { success }
        }
        """ % (token, new_password1, new_password2)


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
            """ % (self.default_password,)

    def get_query(self, token, new_password1="new_password", new_password2="new_password") -> str:
        return """
            mutation {
                relayPasswordSet(
                    input: {
                        token: "%s",
                        newPassword1: "%s",
                        newPassword2: "%s"
                    })
                { success }
            }
        """ % (token, new_password1, new_password2)
