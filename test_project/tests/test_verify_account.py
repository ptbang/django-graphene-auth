from datetime import timedelta

from .base_test_case import BaseTestCase
from graphql_auth.constants import Messages
from graphql_auth.utils import get_token
from graphql_auth.signals import user_verified


class VerifyAccountBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user1 = self.register_user(
            email="foo@email.com", username="foo", verified=False
        )
        self.user2 = self.register_user(
            email="bar@email.com", username="bar", verified=True
        )

    def verify_query(self, token):
        raise NotImplementedError

    def _test_verify_user(self):
        signal_received = False

        def receive_signal(sender, user, signal):
            self.assertEqual(user.id, self.user1.pk)
            nonlocal signal_received
            signal_received = True

        user_verified.connect(receive_signal)
        token = get_token(self.user1, 'activation')
        response = self.query(self.verify_query(token))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertTrue(signal_received)

    def _test_verified_user(self):
        token = get_token(self.user2, 'activation')
        response = self.query(self.verify_query(token))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.ALREADY_VERIFIED)

    def _test_expired_token(self):
        token = get_token(self.user2, 'activation')
        with self.settings(GRAPHQL_AUTH={'EXPIRATION_ACTIVATION_TOKEN': timedelta(seconds=0.0000001)}):
            response = self.query(self.verify_query(token))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.EXPIRED_TOKEN)

    def _test_invalid_token(self):
        response = self.query(self.verify_query('fake-token'))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.INVALID_TOKEN)

    def _test_other_action_token(self):
        token = get_token(self.user2, 'password_reset')
        response = self.query(self.verify_query(token))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.INVALID_TOKEN)


class VerifyAccountTestCase(VerifyAccountBaseTestCase):
    RESPONSE_RESULT_KEY = 'verifyAccount'

    def verify_query(self, token):
        return """
        mutation {
            verifyAccount(token: "%s")
                { success, errors }
            }
        """ % (
            token
        )


class VerifyAccountRelayTestCase(VerifyAccountBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayVerifyAccount'

    def verify_query(self, token):
        return """
        mutation {
            relayVerifyAccount(input:{ token: "%s"})
                { success, errors }
        }
        """ % (
            token
        )
