from smtplib import SMTPException
from unittest import mock

from django.core import mail

from graphql_auth.constants import Messages
from graphql_auth.testingx import BaseTestCase


class SendSecondaryEmailActivationBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user1 = self.create_user(email="gaa@email.com", username="gaa", verified=False)
        self.user2 = self.create_user(email="bar@email.com", username="bar", verified=True)

    def get_query(self, email, password=None) -> str:
        raise NotImplementedError

    def _test_not_verified_user(self):
        self.client.force_login(self.user1)
        response = self.query(self.get_query(self.user1.email))  # type: ignore
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.NOT_VERIFIED)
        self.assertEqual(len(mail.outbox), 0)

    def _test_invalid_email(self):
        self.client.force_login(self.user2)
        response = self.query(self.get_query('invalid-email@email'))  # type: ignore
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIn('email', result['errors'].keys())
        self.assertEqual(len(mail.outbox), 0)

    def _test_used_email(self):
        self.client.force_login(self.user2)
        response = self.query(self.get_query(self.user1.email))  # type: ignore
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.EMAIL_IN_USE)
        self.assertEqual(len(mail.outbox), 0)

    def _test_valid_email(self):
        self.client.force_login(self.user2)
        new_email = 'new@email.com'
        response = self.query(self.get_query(new_email))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertEqual(result['success'], True)
        self.assertIsNone(result['errors'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Activate your account on", mail.outbox[0].subject)

    def _test_with_wrong_password(self):
        self.client.force_login(self.user2)
        new_email = 'new@email.com'
        response = self.query(self.get_query(new_email, 'wrong-password'))
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], {'password': Messages.INVALID_PASSWORD})
        self.assertEqual(len(mail.outbox), 0)

    def _test_with_unauthenticated_user(self):
        new_email = 'new@email.com'
        response = self.query(self.get_query(new_email))
        self.assertResponseHasErrors(response)
        error = self.get_response_errors(response)[0]
        self.assertEqual(error['message'], Messages.UNAUTHENTICATED['message'])
        self.assertEqual(error['extensions'], Messages.UNAUTHENTICATED)

    @mock.patch(
        "graphql_auth.models.UserStatus.send_secondary_email_activation",
        mock.MagicMock(side_effect=SMTPException),
    )
    def _test_resend_email_fail_to_send_email(self):
        self.client.force_login(self.user2)
        new_email = 'new@email.com'
        response = self.query(self.get_query(new_email))
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.EMAIL_FAIL)
        self.assertEqual(len(mail.outbox), 0)


class SendSecondaryEmailActivationTestCase(SendSecondaryEmailActivationBaseTestCase):
    RESPONSE_RESULT_KEY = 'sendSecondaryEmailActivation'

    def get_query(self, email, password=None) -> str:
        return """
        mutation {
            sendSecondaryEmailActivation(email: "%s", password: "%s")
                { success, errors }
        }
        """ % (
            email,
            password or self.default_password,
        )


class SendSecondaryEmailActivationRelayTestCase(SendSecondaryEmailActivationBaseTestCase):
    RESPONSE_RESULT_KEY = 'relaySendSecondaryEmailActivation'

    def get_query(self, email, password=None) -> str:
        return """
        mutation {
            relaySendSecondaryEmailActivation(input:{ email: "%s", password: "%s"})
                { success, errors }
        }
        """ % (
            email,
            password or self.default_password,
        )
