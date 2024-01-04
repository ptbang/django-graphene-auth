import json
from smtplib import SMTPException
from unittest import mock

from django.core import mail

from graphql_auth.constants import Messages
from graphql_auth.exceptions import InvalidEmailAddressError

from .testCases import BaseTestCase


class SendPasswordResetEmailBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user1 = self.register_user(email="foo@email.com", username="foo", verified=False)
        self.user2 = self.register_user(
            email="bar@email.com",
            username="bar",
            verified=True,
            secondary_email="secondary@email.com",
        )

    def get_query(self, email) -> str:
        raise NotImplementedError

    def _test_send_email_invalid_email(self):
        query = self.get_query("invalid@email.com")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertEqual(result['success'], True)
        self.assertEqual(len(mail.outbox), 0)

    def _test_invalid_form(self):
        query = self.get_query("baremail.com")
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], InvalidEmailAddressError.default_message)

    def _test_send_email_valid_email_verified_user(self):
        query = self.get_query("bar@email.com")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertEqual(result['success'], True)
        self.assertEqual(len(mail.outbox), 1)

    def _test_send_to_secondary_email(self):
        query = self.get_query("secondary@email.com")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertEqual(result['success'], True)
        self.assertEqual(len(mail.outbox), 1)

    @mock.patch(
        "graphql_auth.models.UserStatus.send_password_reset_email",
        mock.MagicMock(side_effect=SMTPException),
    )
    def _test_send_email_fail_to_send_email(self):
        query = self.get_query("bar@email.com")
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['extensions'], Messages.EMAIL_FAIL)


class SendPasswordResetEmailTestCase(SendPasswordResetEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'sendPasswordResetEmail'

    def get_query(self, email):
        return """
            mutation {
                sendPasswordResetEmail(email: "%s")
                    { success }
                }
        """ % (email)


class SendPasswordResetEmailRelayTestCase(SendPasswordResetEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'relaySendPasswordResetEmail'

    def get_query(self, email):
        return """
            mutation {
                relaySendPasswordResetEmail(input:{ email: "%s"})
                    { success }
                }
        """ % (email)


