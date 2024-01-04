import json

from graphql_auth.constants import Messages

from .testCases import BaseTestCase


class ArchiveAccountBaseTestCase(BaseTestCase):
    RESPONSE_RESULT_KEY = 'archiveAccount'

    def setUp(self):
        self.user1 = self.register_user(email="foo@email.com", username="foo")
        self.user2 = self.register_user(email="bar@email.com", username="bar", verified=True)

    def get_login_query(self) -> str:
        raise NotImplementedError

    def archive_account_query(self, password=None) -> str:
        raise NotImplementedError

    def _test_not_authenticated(self):
        """
        try to archive not authenticated
        """
        response = self.query(self.archive_account_query())
        self.assertResponseHasErrors(response)
        error = self.get_response_errors(response)[0]
        self.assertEqual(error['message'], Messages.UNAUTHENTICATED['message'])
        self.assertEqual(error['extensions'], Messages.UNAUTHENTICATED)

    def _test_invalid_password(self):
        """
        try to archive account with invalid password
        """
        query = self.archive_account_query(password='invalid_password')
        self.client.force_login(self.user2)
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = self.get_response_errors(response)[0]
        self.assertEqual(error['message'], Messages.INVALID_PASSWORD['message'])
        self.assertEqual(error['extensions'], Messages.INVALID_PASSWORD)

    def _test_valid_password(self):
        """
        try to archive account
        """
        query = self.archive_account_query()
        self.assertEqual(self.user2.status.archived, False)  # type: ignore
        self.client.force_login(self.user2)
        response = self.query(query)
        result = self.get_response_result(response)
        self.assertEqual(result["success"], True)
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.status.archived, True)  # type: ignore

    def _test_revoke_refresh_tokens_on_archive_account(self):
        """
        when archive account, all refresh tokens should be revoked
        """
        response = self.query(self.get_login_query())
        self.user2.refresh_from_db()
        refresh_tokens = self.user2.refresh_tokens.all()  # type: ignore
        self.assertTrue(len(refresh_tokens) > 0)
        for token in refresh_tokens:
            self.assertFalse(token.revoked)

        query = self.archive_account_query()
        self.assertEqual(self.user2.status.archived, False)  # type: ignore
        self.client.force_login(self.user2)
        response = self.query(query)
        result = self.get_response_result(response)
        self.assertEqual(result["success"], True)
        self.user2.refresh_from_db()
        self.assertTrue(self.user2.status.archived)  # type: ignore
        refresh_tokens = self.user2.refresh_tokens.all()  # type: ignore
        for token in refresh_tokens:
            self.assertTrue(token.revoked)

    def _test_not_verified_user(self):
        """
        try to archive account
        """
        query = self.archive_account_query()
        self.assertEqual(self.user1.status.archived, False)  # type: ignore
        self.client.force_login(self.user1)
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = self.get_response_errors(response)[0]
        self.assertEqual(error['message'], Messages.NOT_VERIFIED['message'])
        self.assertEqual(error['extensions'], Messages.NOT_VERIFIED)
        self.assertEqual(self.user1.status.archived, False)  # type: ignore


class ArchiveAccountTestCase(ArchiveAccountBaseTestCase):
    RESPONSE_RESULT_KEY = 'archiveAccount'

    def get_login_query(self):
        return """
        mutation {
            tokenAuth(
                email: "bar@email.com",
                password: "%s",
            )
            { refreshToken }
        }
        """ % (self.default_password,)

    def archive_account_query(self, password=None):
        return """
            mutation {
              archiveAccount(password: "%s") {
                success
              }
            }
        """ % (password or self.default_password,)


class ArchiveAccountRelayTestCase(ArchiveAccountBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayArchiveAccount'

    def get_login_query(self):
        return """
        mutation {
            relayTokenAuth(
                input: {
                    email: "bar@email.com",
                    password: "%s",
                }
            )
            { refreshToken }
        }
        """ % (self.default_password,)

    def archive_account_query(self, password=None):
        return """
            mutation {
              relayArchiveAccount(input: { password: "%s"}) {
                success
              }
            }
        """ % (password or self.default_password,)
