from graphql_auth.constants import Messages
from graphql_auth.testcase import BaseTestCase


class UpdateAccountBaseTestCase(BaseTestCase):
    def setUp(self):
        self.user1 = self.create_user(email="foo@email.com", username="foo", verified=False, first_name="foo")
        self.user2 = self.create_user(email="bar@email.com", username="bar", verified=True, first_name="bar")
        self.user3 = self.create_user(email="gaa@email.com", username="gaa", verified=True, first_name="gaa")

    def get_query(self, first_name="firstname"):
        raise NotImplementedError

    def _test_update_account_unauthenticated(self):
        response = self.query(self.get_query())
        self.assertResponseHasErrors(response)
        error = self.get_response_errors(response)[0]
        self.assertEqual(error['message'], Messages.UNAUTHENTICATED['message'])
        self.assertEqual(error['extensions'], Messages.UNAUTHENTICATED)

    def _test_update_account_not_verified(self):
        self.client.force_login(self.user1)
        response = self.query(self.get_query())
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.NOT_VERIFIED)

    def _test_update_account(self):
        self.client.force_login(self.user2)
        new_first_name = 'new'
        self.assertNotEqual(self.user2.first_name, new_first_name)  # type: ignore
        response = self.query(self.get_query(new_first_name))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.first_name, new_first_name)  # type: ignore

    def _test_invalid_form(self):
        self.client.force_login(self.user2)
        old_first_name = self.user2.first_name  # type: ignore
        response = self.query(self.get_query(10 * 'too-long-first-name'))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertTrue('firstName', result['errors'].keys())


class UpdateAccountTestCase(UpdateAccountBaseTestCase):
    RESPONSE_RESULT_KEY = 'updateAccount'

    def get_query(self, first_name="firstname"):
        return """
        mutation {
            updateAccount(firstName: "%s")
                { success, errors }
        }
        """ % (
            first_name
        )


class UpdateAccountRelayTestCase(UpdateAccountBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayUpdateAccount'

    def get_query(self, first_name="firstname"):
        return """
        mutation {
            relayUpdateAccount(input:{ firstName: "%s" })
                { success, errors }
        }
        """ % (
            first_name
        )
