from smtplib import SMTPException
from unittest import mock

from django.core import mail

from graphql_auth.constants import Messages
from graphql_auth.testingx import BaseTestCase


class SendPasswordResetEmailBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user1 = self.create_user(email="foo@email.com", username="foo", verified=False)
        self.user2 = self.create_user(
            email="bar@email.com",
            username="bar",
            verified=True,
            secondary_email="secondary@email.com",
        )

    def get_query(self, email) -> str:
        raise NotImplementedError

    def _test_with_nonexistent_email(self):
        query = self.get_query("nonexistent@email.com")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertEqual(len(mail.outbox), 0)

    def _test_invalid_form(self):
        query = self.get_query("bar@email")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIn('email', result['errors'].keys())

    def _test_send_email_successfully(self):
        query = self.get_query(self.user2.email)  # type: ignore
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertEqual(result['success'], True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reset your password", mail.outbox[0].subject)

    def _test_send_to_secondary_email_successfully(self):
        query = self.get_query(self.user2.status.secondary_email)  # type: ignore
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertEqual(result['success'], True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reset your password", mail.outbox[0].subject)

    def _test_send_to_unverified_user_successfully(self):
        query = self.get_query(self.user1.email)  # type: ignore
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reset your password", mail.outbox[0].subject)

    @mock.patch(
        "graphql_auth.models.UserStatus.send_password_reset_email",
        mock.MagicMock(side_effect=SMTPException),
    )
    def _test_send_email_fail_to_send_email(self):
        query = self.get_query("bar@email.com")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.EMAIL_FAIL)
        self.assertEqual(len(mail.outbox), 0)


class SendPasswordResetEmailTestCase(SendPasswordResetEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'sendPasswordResetEmail'

    def get_query(self, email):
        return """
            mutation {
                sendPasswordResetEmail(email: "%s")
                    { success, errors }
                }
        """ % (
            email
        )


class SendPasswordResetEmailRelayTestCase(SendPasswordResetEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'relaySendPasswordResetEmail'

    def get_query(self, email):
        return """
            mutation {
                relaySendPasswordResetEmail(input:{ email: "%s"})
                    { success, errors }
                }
        """ % (
            email
        )
