import json

from graphql_auth.constants import Messages

from .testCases import BaseTestCase


class VerifyTokenBaseTestCase(BaseTestCase):
    LOGIN_QUERY_RESPONSE_RESULT_KEY: str

    def setUp(self):
        self.user = self.register_user(email="foo@email.com", username="foo", verified=False)

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
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertTrue(result['payload']['username'], self.user.username)  # type: ignore

    def _test_invalid_token(self):
        query = self.get_verify_query("invalid_token")
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], Messages.INVALID_TOKEN['message'])


class VerifyTokenTestCase(VerifyTokenBaseTestCase):
    RESPONSE_RESULT_KEY = 'verifyToken'
    LOGIN_QUERY_RESPONSE_RESULT_KEY: str = 'tokenAuth'

    def get_login_query(self):
        return """
        mutation {
        tokenAuth(email: "%s", password: "%s" )
            { token }
        }
        """ % (self.user.email, self.default_password)  # type: ignore

    def get_verify_query(self, token):
        return """
        mutation {
        verifyToken(token: "%s")
            { payload }
        }
        """ % (token)


class VerifyTokenRelayTestCase(VerifyTokenBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayVerifyToken'
    LOGIN_QUERY_RESPONSE_RESULT_KEY: str = 'relayTokenAuth'

    def get_login_query(self):
        return """
        mutation {
        relayTokenAuth(input:{ email: "%s", password: "%s" })
            { token }
        }
        """ % (self.user.email, self.default_password)  # type: ignore

    def get_verify_query(self, token):
        return """
        mutation {
        relayVerifyToken(input: {token: "%s"})
            { payload }
        }
        """ % (token)
