import json
from datetime import datetime, timedelta

from graphql_auth.constants import Messages
from graphql_auth.base_testcase import BaseTestCase


class RevokeTokenBaseTestCase(BaseTestCase):
    LOGIN_QUERY_RESPONSE_RESULT_KEY: str

    def setUp(self):
        self.user1 = self.create_user(email="foo@email.com", username="foo_username")

    def get_login_query(self) -> str:
        raise NotImplementedError

    def get_revoke_query(self, token) -> str:
        raise NotImplementedError

    def _test_revoke_token(self):
        query = self.get_login_query()
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = json.loads(response.content.decode())['data'][self.LOGIN_QUERY_RESPONSE_RESULT_KEY]

        query = self.get_revoke_query(result['refreshToken'])
        response = self.query(query)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertEqual(datetime.fromtimestamp(result['revoked']).date(), datetime.today().date())

    def _test_successfully_with_expired_token(self):
        query = self.get_login_query()
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = json.loads(response.content.decode())['data'][self.LOGIN_QUERY_RESPONSE_RESULT_KEY]

        query = self.get_revoke_query(result['refreshToken'])
        with self.settings(GRAPHQL_JWT={'JWT_REFRESH_EXPIRATION_DELTA': timedelta(seconds=-1)}):
            response = self.query(query)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertEqual(datetime.fromtimestamp(result['revoked']).date(), datetime.today().date())

    def _test_invalid_token(self):
        query = self.get_revoke_query('invalid_token')
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.INVALID_TOKEN)
        self.assertIsNone(result['revoked'])


class RevokeTokenTestCase(RevokeTokenBaseTestCase):
    RESPONSE_RESULT_KEY = 'revokeToken'
    LOGIN_QUERY_RESPONSE_RESULT_KEY = 'tokenAuth'

    def get_login_query(self):
        return """
        mutation {
            tokenAuth(email: "foo@email.com", password: "%s" )
                { refreshToken  }
        }
        """ % (
            self.default_password
        )

    def get_revoke_query(self, token):
        return """
        mutation {
            revokeToken(refreshToken: "%s" )
                { revoked, success, errors  }
        }
        """ % (
            token
        )


class RevokeTokenRelayTestCase(RevokeTokenBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayRevokeToken'
    LOGIN_QUERY_RESPONSE_RESULT_KEY = 'relayTokenAuth'

    def get_login_query(self):
        return """
        mutation {
            relayTokenAuth(input:{ email: "foo@email.com", password: "%s"  })
                { refreshToken  }
            }
        """ % (
            self.default_password
        )

    def get_revoke_query(self, token):
        return """
        mutation {
            relayRevokeToken(input: {refreshToken: "%s"} )
                { revoked, success, errors  }
        }
        """ % (
            token
        )
