import json
from datetime import timedelta

from graphql_auth.constants import Messages
from graphql_auth.testingx import BaseTestCase


class VerifyTokenBaseTestCase(BaseTestCase):
    LOGIN_QUERY_RESPONSE_RESULT_KEY: str

    def setUp(self):
        self.user = self.create_user(email="foo@email.com", username="foo", verified=False)

    def get_login_query(self) -> str:
        raise NotImplementedError

    def get_verify_query(self, token) -> str:
        raise NotImplementedError

    def _test_verify_token(self):
        query = self.get_login_query()
        response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.LOGIN_QUERY_RESPONSE_RESULT_KEY]

        query = self.get_verify_query(result['token'])
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertTrue(result['payload']['username'], self.user.username)  # type: ignore

    def _test_expired_token(self):
        query = self.get_login_query()
        with self.settings(GRAPHQL_JWT={'JWT_EXPIRATION_DELTA': timedelta(seconds=-1)}):
            response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.LOGIN_QUERY_RESPONSE_RESULT_KEY]

        query = self.get_verify_query(result['token'])
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.EXPIRED_TOKEN)

    def _test_invalid_token(self):
        query = self.get_verify_query("invalid_token")
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.INVALID_TOKEN)


class VerifyTokenTestCase(VerifyTokenBaseTestCase):
    RESPONSE_RESULT_KEY = 'verifyToken'
    LOGIN_QUERY_RESPONSE_RESULT_KEY: str = 'tokenAuth'

    def get_login_query(self):
        return """
        mutation {
            tokenAuth(email: "%s", password: "%s" )
                { token }
        }
        """ % (
            self.user.email,  # type: ignore
            self.default_password,
        )

    def get_verify_query(self, token):
        return """
        mutation {
            verifyToken(token: "%s")
                { payload, success, errors }
        }
        """ % (
            token
        )


class VerifyTokenRelayTestCase(VerifyTokenBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayVerifyToken'
    LOGIN_QUERY_RESPONSE_RESULT_KEY: str = 'relayTokenAuth'

    def get_login_query(self):
        return """
        mutation {
            relayTokenAuth(input:{ email: "%s", password: "%s" })
                { token }
        }
        """ % (
            self.user.email,  # type: ignore
            self.default_password,
        )

    def get_verify_query(self, token):
        return """
        mutation {
            relayVerifyToken(input: {token: "%s"})
                { payload, success, errors }
        }
        """ % (
            token
        )
