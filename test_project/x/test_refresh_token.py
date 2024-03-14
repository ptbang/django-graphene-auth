import json
from datetime import timedelta

from graphql_auth.constants import Messages
from graphql_auth.base_testcase import BaseTestCase


class RefreshTokenBaseTestCase(BaseTestCase):
    RESPONSE_RESULT_KEY: str
    TOKEN_AUTH_RESPONSE_RESULT_KEY: str

    def get_login_query(self):
        raise NotImplementedError()

    def get_refresh_token_query(self, token):
        raise NotImplementedError()

    def setUp(self):
        self.user = self.create_user(email='foo@email.com', username='foo', verified=True, archived=False)

    def _test_refresh_token(self):
        query = self.get_login_query()
        response = self.query(query)
        result = json.loads(response.content)['data'][self.TOKEN_AUTH_RESPONSE_RESULT_KEY]
        self.assertTrue(result['refreshToken'])

        query = self.get_refresh_token_query(result['refreshToken'])
        response = self.query(query)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertTrue(result['refreshToken'])
        self.assertTrue(result['token'])
        self.assertTrue(result['payload'])

    def _test_expired_token(self):
        query = self.get_login_query()
        response = self.query(query)
        result = json.loads(response.content.decode())['data'][self.TOKEN_AUTH_RESPONSE_RESULT_KEY]

        query = self.get_refresh_token_query(result['refreshToken'])
        with self.settings(GRAPHQL_JWT={'JWT_REFRESH_EXPIRATION_DELTA': timedelta(seconds=-1)}):
            response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.EXPIRED_TOKEN)

    def _test_invalid_token(self):
        query = self.get_refresh_token_query('invalid_token')
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.INVALID_TOKEN)
        self.assertIsNone(result['refreshToken'])
        self.assertIsNone(result['token'])
        self.assertIsNone(result['payload'])


class RefreshTokenTestCase(RefreshTokenBaseTestCase):
    RESPONSE_RESULT_KEY = 'refreshToken'
    TOKEN_AUTH_RESPONSE_RESULT_KEY = 'tokenAuth'

    def get_login_query(self):
        return """
        mutation {
            tokenAuth(email: "foo@email.com", password: "%s" )
                { refreshToken }
        }
        """ % (
            self.default_password
        )

    def get_refresh_token_query(self, token):
        return """
        mutation {
            refreshToken(refreshToken: "%s" )
                { token, refreshToken, refreshExpiresIn, payload, success, errors }
            }
        """ % (
            token
        )


class RefreshTokenRelayTestCase(RefreshTokenBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayRefreshToken'
    TOKEN_AUTH_RESPONSE_RESULT_KEY = 'relayTokenAuth'

    def get_login_query(self):
        return """
        mutation {
            relayTokenAuth(input:{ email: "foo@email.com", password: "%s"  })
                { refreshToken  }
        }
        """ % (
            self.default_password
        )

    def get_refresh_token_query(self, token):
        return """
        mutation {
            relayRefreshToken(input: {refreshToken: "%s"} )
                { token, refreshToken, refreshExpiresIn, payload, success, errors  }
        }
        """ % (
            token
        )
