import json

from graphql_auth.constants import Messages

from .testCases import BaseTestCase


class RemoveSecondaryEmailBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user = self.register_user(
            email="bar@email.com",
            username="bar",
            verified=True,
            secondary_email="secondary@email.com",
        )

    def get_query(self, password=None) -> str:
        raise NotImplementedError

    def _test_remove_email(self):
        self.client.force_login(self.user)
        response = self.query(self.get_query())
        self.assertResponseNoErrors(response)
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertEqual(result['success'], True)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.status.secondary_email)  # type: ignore

    def _test_remove_email_failed_by_wrong_password(self):
        self.client.force_login(self.user)
        response = self.query(self.get_query('wrong_password'))
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], Messages.INVALID_PASSWORD['message'])
        self.assertEqual(error['extensions'], Messages.INVALID_PASSWORD)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.status.secondary_email)  # type: ignore

    def _test_remove_email_failed_by_user_without_secondary_email(self):
        self.user.status.secondary_email = None  # type: ignore
        self.user.status.save()  # type: ignore
        self.user.refresh_from_db()
        self.assertIsNone(self.user.status.secondary_email)  # type: ignore
        self.client.force_login(self.user)
        response = self.query(self.get_query())
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], Messages.SECONDARY_EMAIL_REQUIRED['message'])
        self.assertEqual(error['extensions'], Messages.SECONDARY_EMAIL_REQUIRED)


class RemoveSecondaryEmailTestCase(RemoveSecondaryEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'removeSecondaryEmail'

    def get_query(self, password=None):
        return """
        mutation {
            removeSecondaryEmail(password: "%s")
                { success }
            }
        """ % (password or self.default_password)


class RemoveSecondaryEmailRelayTestCase(RemoveSecondaryEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayRemoveSecondaryEmail'

    def get_query(self, password=None):
        return """
        mutation {
        relayRemoveSecondaryEmail(input:{ password: "%s"})
            { success }
        }
        """ % (password or self.default_password)
