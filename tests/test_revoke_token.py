import json
from datetime import datetime

from .testCases import BaseTestCase


class RevokeTokenBaseTestCase(BaseTestCase):
    LOGIN_QUERY_RESPONSE_RESULT_KEY: str

    def setUp(self):
        self.user1 = self.register_user(email="foo@email.com", username="foo_username")

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
        result = json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]
        self.assertEqual(datetime.fromtimestamp(result['revoked']).date(), datetime.today().date())

    def _test_invalid_token(self):
        query = self.get_revoke_query('invalid_token')
        response = self.query(query)
        self.assertResponseHasErrors(response)
        error = json.loads(response.content.decode())['errors'][0]
        self.assertEqual(error['message'], 'Invalid refresh token')


class RevokeTokenTestCase(RevokeTokenBaseTestCase):
    RESPONSE_RESULT_KEY = 'revokeToken'
    LOGIN_QUERY_RESPONSE_RESULT_KEY = 'tokenAuth'

    def get_login_query(self):
        return """
        mutation {
        tokenAuth(email: "foo@email.com", password: "%s" )
            { refreshToken  }
        }
        """ % (self.default_password)

    def get_revoke_query(self, token):
        return """
        mutation {
        revokeToken(refreshToken: "%s" )
            { revoked  }
        }
        """ % (token)


class RevokeTokenRelayTestCase(RevokeTokenBaseTestCase):
    RESPONSE_RESULT_KEY = 'relayRevokeToken'
    LOGIN_QUERY_RESPONSE_RESULT_KEY = 'relayTokenAuth'

    def get_login_query(self):
        return """
        mutation {
            relayTokenAuth(input:{ email: "foo@email.com", password: "%s"  })
                { refreshToken  }
            }
        """ % (self.default_password)

    def get_revoke_query(self, token):
        return """
        mutation {
            relayRevokeToken(input: {refreshToken: "%s"} )
                { revoked  }
        }
        """ % (token)
