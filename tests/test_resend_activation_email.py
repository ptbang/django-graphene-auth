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
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertEqual(result["success"], True)

    def _test_resend_email_valid_email(self):
        query = self.get_query("gaa@email.com")
        response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertEqual(result['success'], True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Activate your account on", mail.outbox[0].subject)

    def _test_resend_email_valid_email_verified(self):
        query = self.get_query("bar@email.com")
        response = self.query(query)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertResponseHasErrors(response)
        self.assertEqual(error['message'], UserAlreadyVerifiedError.default_message)
        self.assertEqual(error['extensions'], Messages.ALREADY_VERIFIED)

    def _test_invalid_form(self):
        query = self.get_query("baremail.com")
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], InvalidEmailAddressError.default_message)

    @mock.patch(
        "graphql_auth.models.UserStatus.resend_activation_email",
        mock.MagicMock(side_effect=SMTPException),
    )
    def _test_resend_email_fail_to_send_email(self):
        """
        Something went wrong when sending email
        """
        query = self.get_query("gaa@email.com")
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], Messages.EMAIL_FAIL['message'])
        self.assertEqual(error['extensions'], Messages.EMAIL_FAIL)


class ResendActivationEmailTestCase(ResendActivationEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'resendActivationEmail'

    def get_query(self, email):
        return """
            mutation {
                resendActivationEmail(email: "%s")
                    { success }
            }
            """ % (email)


class ResendActivationEmailRelayTestCase(ResendActivationEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayResendActivationEmail'

    def get_query(self, email):
        return """
            mutation {
                relayResendActivationEmail(input:{ email: "%s"})
                    { success }
            }
        """ % (email)
