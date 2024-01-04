from graphql_auth.constants import Messages

from .testCases import BaseTestCase


class SwapEmailsBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user = self.register_user(
            email="bar@email.com",
            username="bar",
            verified=True,
            secondary_email="secondary@email.com",
        )
        self.user2 = self.register_user(email="baa@email.com", username="baa", verified=True)

    def get_query(self, password=None) -> str:
        raise NotImplementedError

    def _test_swap_emails(self):
        self.client.force_login(self.user)
        response = self.query(self.get_query())
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertEqual(result['success'], True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "secondary@email.com")  # type: ignore
        self.assertEqual(self.user.status.secondary_email, "bar@email.com")  # type: ignore

    def _test_swap_emails_without_secondary_email(self):
        self.client.force_login(self.user2)
        response = self.query(self.get_query())
        self.assertResponseHasErrors(response)
        error = self.get_response_errors(response)[0]
        self.assertEqual(error['message'], Messages.SECONDARY_EMAIL_REQUIRED['message'])
        self.assertEqual(error['extensions'], Messages.SECONDARY_EMAIL_REQUIRED)


class SwapEmailsTestCase(SwapEmailsBaseTestCase):
    RESPONSE_RESULT_KEY = 'swapEmails'

    def get_query(self, password=None):
        return """
        mutation {
            swapEmails(password: "%s")
                { success }
            }
        """ % (password or self.default_password)


class SwapEmailsRelayTestCase(SwapEmailsBaseTestCase):
    RESPONSE_RESULT_KEY = 'relaySwapEmails'

    def get_query(self, password=None):
        return """
        mutation {
            relaySwapEmails(input:{ password: "%s"})
                { success }
        }
        """ % (password or self.default_password)
