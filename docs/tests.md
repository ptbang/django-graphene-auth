# Testing

---

!!! attention "New in version 1.1.0"

For testing you can use CommonTestCase class, which implements original GraphQLTestCase and contains
additional feature for testing GraphQL and Relay queries.
Thanks to this approach, you can write test methods once and use it for testing both GraphQL and Relay request.

For example, create a LoginCommonTestCase that implements the CommonTestCase class,
and add method named `_test_login` to this class.

Next, create LoginTestCase class for GraphQL queries and LoginRelayTestCase for Relay queries as below:

```python
# test_login.py
from copy import copy
from django.conf import settings
from graphql_auth.common_testcase import CommonTestCase


class LoginCommonTestCase(CommonTestCase):
    def _test_login(self):
        query = self.get_query("username", self.verified_user.username)  # type: ignore
        with self.assertNumQueries(3):
            response = self.query(query)
        result = self.get_response_result(response)
        self.assertResponseNoErrors(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertTrue(result["token"])
        self.assertTrue(result["payload"])
        self.assertTrue(result["refreshExpiresIn"])
        self.assertTrue(result["refreshToken"])
        self.assertTrue(result["refreshToken"])
        self.assertFalse(result['unarchiving'])

# GraphQL query
class LoginTestCase(LoginCommonTestCase):
    RESPONSE_RESULT_KEY = 'tokenAuth'

    def get_query(self, field, username, password):
        return """
            mutation {
                tokenAuth(%s: "%s", password: "%s")
                    { success, errors, token, payload, refreshToken, refreshExpiresIn, user { username, id }, unarchiving  }
            }
            """ % (
            field,
            username,
            password,
        )

# Relay query
class LoginRelayTestCase(LoginCommonTestCase):
    RESPONSE_RESULT_KEY = 'relayTokenAuth'

    def get_query(self, field, username, password):
        return """
            mutation {
                relayTokenAuth(input:{ %s: "%s", password: "%s"})
                    { success, errors, token, payload, refreshToken, refreshExpiresIn, user { username, id }, unarchiving  }
                }
            """ % (
            field,
            username,
            password,
        )
```

Both of these login classes will automatically contain a method `test_login` (without prefix `_`)
thanks to the metaclass defined in the CommonTestCase class.
