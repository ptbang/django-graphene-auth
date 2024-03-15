from graphql_auth.common_testcase import CommonTestCase
from graphql_auth.constants import Messages
from graphql_auth.utils import get_token


class VerifySecondaryEmailCommonTestCase(CommonTestCase):
    def setUp(self):
        self.user = self.create_user(email="bar@email.com", username="bar", verified=True)
        self.user2 = self.create_user(email="foo@email.com", username="foo", verified=True)

    def get_verify_query(self, token):
        raise NotImplementedError

    def _test_verify_secondary_email(self):
        self.assertEqual(self.user.status.secondary_email, '')  # type: ignore
        secondary_email = 'new_email@email.com'
        token = get_token(
            self.user,
            "activation_secondary_email",
            secondary_email=secondary_email,
        )
        response = self.query(self.get_verify_query(token))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.user.status.refresh_from_db()  # type: ignore
        self.assertEqual(self.user.status.secondary_email, secondary_email)  # type: ignore

    def _test_invalid_token(self):
        response = self.query(self.get_verify_query('fake-token'))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.INVALID_TOKEN)

    def _test_email_in_use(self):
        token = get_token(self.user, "activation_secondary_email", secondary_email=self.user2.email)  # type: ignore
        response = self.query(self.get_verify_query(token))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.EMAIL_IN_USE)


class VerifySecondaryEmailCase(VerifySecondaryEmailCommonTestCase):
    RESPONSE_RESULT_KEY = 'verifySecondaryEmail'

    def get_verify_query(self, token):
        return """
        mutation {
            verifySecondaryEmail(token: "%s")
                { success, errors }
            }
        """ % (
            token
        )


class VerifySecondaryEmailRelayTestCase(VerifySecondaryEmailCommonTestCase):
    RESPONSE_RESULT_KEY = 'relayVerifySecondaryEmail'

    def get_verify_query(self, token):
        return """
        mutation {
        relayVerifySecondaryEmail(input:{ token: "%s"})
            { success, errors }
        }
        """ % (
            token
        )
