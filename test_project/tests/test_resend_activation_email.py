import json
from smtplib import SMTPException
from unittest import mock

from django.core import mail

from graphql_auth.constants import Messages
from graphql_auth.exceptions import InvalidEmailAddressError, UserAlreadyVerifiedError

from .testCases import BaseTestCase


class ResendActivationEmailBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user1 = self.register_user(email="gaa@email.com", username="gaa", verified=False)
        self.user2 = self.register_user(email="bar@email.com", username="bar", verified=True)

    def get_query(self, email: str) -> str:
        raise NotImplementedError

    def _test_resend_email_invalid_email(self):
        """
        invalid email should be successful request
        """
        query = self.get_query("invalid@email.com")
        response = self.query(query)
        result = self.get_response_result(response)
        self.assertTrue(result["success"])
        self.assertEqual(len(mail.outbox), 0)

    def _test_resend_email_valid_email(self):
        query = self.get_query("gaa@email.com")
        response = self.query(query)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Activate your account on", mail.outbox[0].subject)

    def _test_resend_email_already_verified(self):
        query = self.get_query("bar@email.com")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.ALREADY_VERIFIED)

    def _test_invalid_email_address(self):
        query = self.get_query("bar@email")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIn('email', result['errors'].keys())

    @mock.patch(
        "graphql_auth.models.UserStatus.resend_activation_email",
        mock.MagicMock(side_effect=SMTPException),
    )
    def _test_fail_to_send_email(self):
        """
        Something went wrong when sending email
        """
        query = self.get_query("gaa@email.com")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.EMAIL_FAIL)


class ResendActivationEmailTestCase(ResendActivationEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'resendActivationEmail'

    def get_query(self, email):
        return """
            mutation {
                resendActivationEmail(email: "%s")
                    { success, errors }
            }
            """ % (email)


class ResendActivationEmailRelayTestCase(ResendActivationEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayResendActivationEmail'

    def get_query(self, email):
        return """
            mutation {
                relayResendActivationEmail(input:{ email: "%s"})
                    { success, errors }
            }
        """ % (email)
