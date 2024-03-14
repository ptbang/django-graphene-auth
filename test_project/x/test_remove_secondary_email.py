from graphql_auth.constants import Messages
from graphql_auth.base_testcase import BaseTestCase


class RemoveSecondaryEmailBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user = self.create_user(
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
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.user.refresh_from_db()
        self.assertIsNone(self.user.status.secondary_email)  # type: ignore

    def _test_remove_email_failed_by_wrong_password(self):
        self.client.force_login(self.user)
        response = self.query(self.get_query('wrong_password'))
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], {'password': Messages.INVALID_PASSWORD})
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.status.secondary_email)  # type: ignore

    def _test_remove_email_failed_by_user_without_secondary_email(self):
        self.user.status.secondary_email = None  # type: ignore
        self.user.status.save()  # type: ignore
        self.user.refresh_from_db()
        self.assertIsNone(self.user.status.secondary_email)  # type: ignore
        self.client.force_login(self.user)
        response = self.query(self.get_query())
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.SECONDARY_EMAIL_REQUIRED)
        self.user.refresh_from_db()


class RemoveSecondaryEmailTestCase(RemoveSecondaryEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'removeSecondaryEmail'

    def get_query(self, password=None):
        return """
        mutation {
            removeSecondaryEmail(password: "%s")
                { success, errors }
            }
        """ % (
            password or self.default_password
        )


class RemoveSecondaryEmailRelayTestCase(RemoveSecondaryEmailBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayRemoveSecondaryEmail'

    def get_query(self, password=None):
        return """
        mutation {
            relayRemoveSecondaryEmail(input:{ password: "%s"})
                { success, errors }
            }
        """ % (
            password or self.default_password
        )
