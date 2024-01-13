# API

---

## Query

GraphQL Auth provides the UserQuery to query users with some useful filters.

GraphQL Auth also provides the MeQuery to retrieve data for the currently authenticated user.

### UserQuery

```python
from graphql_auth.schema import UserQuery
```

The easiest way to explore it is by using [graphQL](https://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/#creating-graphql-and-graphiql-views).

Examples:

=== "query1"
    ```graphql
    query {
      users {
        edges {
          node {
            username,
            archived,
            verified,
            email,
            secondaryEmail,
          }
        }
      }
    }
    ```

=== "response1"
    ```graphql
    {
      "data": {
        "users": {
          "edges": [
            {
              "node": {
                "username": "user1",
                "archived": false,
                "verified": false,
                "email": "user1@email.com",
                "secondaryEmail": null
              }
            },
            {
              "node": {
                "username": "user2",
                "archived": false,
                "verified": true,
                "email": "user2@email.com",
                "secondaryEmail": null
              }
            },
            {
              "node": {
                "username": "user3",
                "archived": true,
                "verified": true,
                "email": "user3@email.com",
                "secondaryEmail": null
              }
            },
            {
              "node": {
                "username": "user4",
                "archived": false,
                "verified": true,
                "email": "user4@email.com",
                "secondaryEmail": "user4_secondary@email.com"
              }
            }
          ]
        }
      }
    }
    ```

=== "query2"
    ```graphql
    query {
      users (last: 1){
        edges {
          node {
            id,
            username,
            email,
            isActive,
            archived,
            verified,
            secondaryEmail
          }
        }
      }
    }
    ```

=== "response2"
    ```graphql
    {
      "data": {
        "users": {
          "edges": [
            {
              "node": {
                "id": "VXNlck5vZGU6NQ==",
                "username": "new_user",
                "email": "new_user@email.com",
                "isActive": true,
                "archived": false,
                "verified": false,
                "secondaryEmail": null
              }
            }
          ]
        }
      }
    }
    ```

=== "query3"
    ```graphql
    query {
      user (id: "VXNlck5vZGU6NQ=="){
        username,
        verified
      }
    }
    ```

=== "response3"
    ```graphql
    {
      "data": {
        "user": {
          "username": "new_user",
          "verified": true
        }
      }
    }
    ```

### MeQuery

```python
from graphql_auth.schema import MeQuery
```

Since this query requires an authenticated user it can be explored by using the [insomnia API client](https://insomnia.rest/).

Example:

=== "query"
    ```graphql
    query {
      me {
        username,
        verified
      }
    }
    ```

=== "response"
    ```graphql
    {
      "data": {
        "user": {
          "username": "new_user",
          "verified": true
        }
      }
    }
    ```

---

## Mutations

All mutations can be imported like this:

=== "mutations"
    ```python
    from graphql_auth import mutations

    # on your mutations
    register = mutations.Register
    ```

=== "relay"
    ```python
    from graphql_auth import relay

    # on your mutations
    register = use relay.Register
    ```

### Standard response

All mutations return a standard response containing `#!python errors` and `#!python success`.

- Example:

=== "graphql"
    ```graphql
    mutation {
      register(
        email: "new_user@email.com",
        username: "new_user",
        password1: "123456",
        password2: "123456",
      ) {
        success,
        errors,
        token,
        refreshToken
      }
    }
    ```

=== "response"
    ```graphql
    {
      "data": {
        "register": {
          "success": false,
          "errors": {
            "password2": [
              {
                "message": "This password is too short. It must contain at least 8 characters.",
                "code": "password_too_short"
              },
              {
                "message": "This password is too common.",
                "code": "password_too_common"
              },
              {
                "message": "This password is entirely numeric.",
                "code": "password_entirely_numeric"
              }
            ]
          },
          "token": null
          "refreshToken": null
        }
      }
    }
    ```

=== "relay"
    ```python hl_lines="3 8"
    mutation {
      register(
        input: {
          email: "new_user@email.com",
          username: "new_user",
          password1: "123456",
          password2: "123456",
        }
      ) {
        success,
        errors,
        token,
        refreshToken
      }
    }
    ```

---

### Public

Public mutations don't require user to be logged in.
You should add all of them in `#!python GRAPHQL_JWT["JWT_ALLOW_ANY_CLASSES"]` setting.

---

#### ObtainJSONWebToken

{{ api.ObtainJSONWebToken }}

=== "graphql"
    ```graphql
    mutation {
      tokenAuth(
        # username or email
        email: "skywalker@email.com"
        password: "123456super"
      ) {
        success,
        errors,
        token,
        refreshToken,
        unarchiving,
        user {
          id,
          username
        }
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "tokenAuth": {
          "success": true,
          "errors": null,
          "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNreXdhbGtlciIsImV4cCI6MTU3OTQ1ODI2Niwib3JpZ0lhdCI6MTU3OTQ1Nzk2Nn0.BKz4ohxQCGtJWnyd5tIbYFD2kpGYDiAVzWTDO2ZyUYY",
          "refreshToken": "5f5fad67cd043437952ddde2750be20201f1017b",
          "unarchiving": false,
          "user": {
            "id": "VXNlck5vZGU6MQ==",
            "username": "skywalker"
          }
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      tokenAuth(
        input: {
          email: "skywalker@email.com"
          password: "123456super"
        }
      ) {
        success,
        errors,
        token,
        refreshToken,
        user {
          id,
          username
        }
      }
    }
    ```

=== "Invalid credentials"
    ```graphql
    {
      "data": {
        "tokenAuth": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Please, enter valid credentials.",
                "code": "invalid_credentials"
              }
            ]
          },
          "token": null,
          "refreshToken": null,
          "unarchiving": false,
          "user": null
        }
      }
    }
    ```

---

#### PasswordSet

{{ api.PasswordSet }}

=== "graphql"
    ```graphql
    mutation {
      passwordSet(
        token: "1eyJ1c2VybmFtZSI6InNreXdhbGtlciIsImFjdGlvbiI6InBhc3N3b3JkX3Jlc2V0In0:1itExL:op0roJi-ZbO9cszNEQMs5mX3c6s",
        newPassword1: "supersecretpassword",
        newPassword2: "supersecretpassword"
      ) {
        success,
        errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "passwordSet": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      passwordSet(
        input: {
          token: "1eyJ1c2VybmFtZSI6InNreXdhbGtlciIsImFjdGlvbiI6InBhc3N3b3JkX3Jlc2V0In0:1itExL:op0roJi-ZbO9cszNEQMs5mX3c6s",
          newPassword1: "supersecretpassword",
          newPassword2: "supersecretpassword"
        }
      ) {
        success,
        errors
      }
    }
    ```

=== "Invalid token"
    ```graphql
    {
      "data": {
        "passwordSet": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Invalid token.",
                "code": "invalid_token"
              }
            ]
          }
        }
      }
    }
    ```

=== "Password mismatch"
    ```graphql
    {
      "data": {
        "passwordSet": {
          "success": false,
          "errors": {
            "newPassword2": [
              {
                "message": "The two password fields didn’t match.",
                "code": "password_mismatch"
              }
            ]
          }
        }
      }
    }
    ```

=== "Password validators"
    ```graphql
    {
      "data": {
        "passwordSet": {
          "success": false,
          "errors": {
            "newPassword2": [
              {
                "message": "This password is too short. It must contain at least 8 characters.",
                "code": "password_too_short"
              },
              {
                "message": "This password is too common.",
                "code": "password_too_common"
              },
              {
                "message": "This password is entirely numeric.",
                "code": "password_entirely_numeric"
              }
            ]
          }
        }
      }
    }
    ```

=== "Password Set"
    ```graphql
    {
      "data": {
        "passwordSet": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Password already set for account.",
                "code": "password_already_set"
              }
            ]
          }
        }
      }
    }
    ```

---

#### PasswordReset

{{ api.PasswordReset }}

=== "graphql"
    ```graphql
    mutation {
      passwordReset(
        token: "1eyJ1c2VybmFtZSI6InNreXdhbGtlciIsImFjdGlvbiI6InBhc3N3b3JkX3Jlc2V0In0:1itExL:op0roJi-ZbO9cszNEQMs5mX3c6s",
        newPassword1: "supersecretpassword",
        newPassword2: "supersecretpassword"
      ) {
        success,
        errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "passwordReset": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      passwordReset(
        input: {
          token: "1eyJ1c2VybmFtZSI6InNreXdhbGtlciIsImFjdGlvbiI6InBhc3N3b3JkX3Jlc2V0In0:1itExL:op0roJi-ZbO9cszNEQMs5mX3c6s",
          newPassword1: "supersecretpassword",
          newPassword2: "supersecretpassword"
        }
      ) {
        success,
        errors
      }
    }
    ```

=== "Invalid token"
    ```graphql
    {
      "data": {
        "passwordReset": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Invalid token.",
                "code": "invalid_token"
              }
            ]
          }
        }
      }
    }
    ```

=== "Password mismatch"
    ```graphql
    {
      "data": {
        "passwordReset": {
          "success": false,
          "errors": {
            "newPassword2": [
              {
                "message": "The two password fields didn’t match.",
                "code": "password_mismatch"
              }
            ]
          }
        }
      }
    }
    ```

=== "Password validators"
    ```graphql
    {
      "data": {
        "passwordReset": {
          "success": false,
          "errors": {
            "newPassword2": [
              {
                "message": "This password is too short. It must contain at least 8 characters.",
                "code": "password_too_short"
              },
              {
                "message": "This password is too common.",
                "code": "password_too_common"
              },
              {
                "message": "This password is entirely numeric.",
                "code": "password_entirely_numeric"
              }
            ]
          }
        }
      }
    }
    ```

---

#### RefreshToken

{{ api.VerifyOrRefreshOrRevokeToken }}

=== "graphql"
    ```graphql
    mutation {
      refreshToken(
        refreshToken: "d9b58dce41cf14549030873e3fab3be864f76ce44"
      ) {
        success,
        errors,
        payload,
        refreshExpiresIn,
        token,
        refreshToken
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "refreshToken": {
          "success": true,
          "errors": null,
          "payload": {
            "username": "skywalker",
            "exp": 1601646082,
            "origIat": 1601645782
          },
          "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNreXdhbGtlciIsImV4cCI6MTYwMTY0NjA4Miwib3JpZ0lhdCI6MTYwMTY0NTc4Mn0.H6gLeky7lX834kBI5RFT8ziNNfGOL3XXg1dRwvpQuRI",
          "refreshToken": "a64f732b4e00432f2ff1b47537a11458be13fc82",
          "refreshExpiresIn": 1602250582
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      refreshToken(
        input: {
          refreshToken: "d9b58dce41cf14549030873e3fab3be864f76ce44"
        }
      ) {
        success,
        errors,
        payload,
        refreshExpiresIn,
        token,
        refreshToken
      }
    }
    ```

=== "Invalid token"
    ```graphql
    {
      "data": {
        "refreshToken": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Invalid token.",
                "code": "invalid_token"
              }
            ]
          }
        }
      }
    }
    ```

---

#### Register

{{ api.Register }}

=== "graphql"
    ```graphql
    mutation {
      register(
        email:"skywalker@email.com",
        username:"skywalker",
        password1: "qlr4nq3f3",
        password2:"qlr4nq3f3"
      ) {
        success,
        errors,
        token,
        refreshToken
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "register": {
          "success": true,
          "errors": null,
          "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImpvZWpvZSIsImV4cCI6MTU4MDE0MjE0MCwib3JpZ0lhdCI6MTU4MDE0MTg0MH0.BGUSGKUUd7IuHnWKy8V6MU3slJ-DHsyAdAjGrGb_9fw",
          "refreshToken": "d9b58dce41cf14549030873e3fab3be864f76ce44"
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      register(
        input: {
          email:"skywalker@email.com",
          username:"skywalker",
          password1: "qlr4nq3f3",
          password2:"qlr4nq3f3"
        }
      ) {
        success,
        errors,
        token,
        refreshToken
      }
    }
    ```

=== "unique"
    ```graphql
    {
      "data": {
        "register": {
          "success": false,
          "errors": {
            "username": [
              {
                "message": "A user with that username already exists.",
                "code": "unique"
              }
            ]
          },
          "token": null,
          "refreshToken": null
        }
      }
    }
    ```

=== "password mismatch"
    ```graphql
    {
      "data": {
        "register": {
          "success": false,
          "errors": {
            "password2": [
              {
                "message": "The two password fields didn’t match.",
                "code": "password_mismatch"
              }
            ]
          },
          "token": null,
          "refreshToken": null
        }
      }
    }
    ```

=== "password validators"
    ```graphql
    {
      "data": {
        "register": {
          "success": false,
          "errors": {
            "password2": [
              {
                "message": "This password is too short. It must contain at least 8 characters.",
                "code": "password_too_short"
              },
              {
                "message": "This password is too common.",
                "code": "password_too_common"
              },
              {
                "message": "This password is entirely numeric.",
                "code": "password_entirely_numeric"
              }
            ]
          },
          "token": null,
          "refreshToken": null
        }
      }
    }
    ```

=== "invalid email"
    ```graphql
    {
      "data": {
        "register": {
          "success": false,
          "errors": {
            "email": [
              {
                "message": "Enter a valid email address.",
                "code": "invalid"
              }
            ]
          },
          "token": null,
          "refreshToken": null
        }
      }
    }
    ```

---

#### ResendActivationEmail

{{ api.ResendActivationEmail }}

=== "graphql"
    ```graphql
    mutation {
      resendActivationEmail(
        email:"skywalker@email.com",
      ) {
        success,
        errors

      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "register": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      resendActivationEmail(
        input: {
          email:"skywalker@email.com",
        }
      ) {
        success,
        errors

      }
    }
    ```

=== "Already verified"
    ```graphql
    {
      "data": {
        "resendActivationEmail": {
          "success": false,
          "errors": {
            "email": [
              [
                {
                  "message": "Account already verified.",
                  "code": "already_verified"
                }
              ]
            ]
          }
        }
      }
    }
    ```

=== "Invalid email"
    ```graphql
    {
      "data": {
        "resendActivationEmail": {
          "success": false,
          "errors": {
            "email": [
              {
                "message": "Enter a valid email address.",
                "code": "invalid"
              }
            ]
          }
        }
      }
    }
    ```

=== "Email fail"
    ```graphql
    {
      "data": {
        "resendActivationEmail": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
                {
                  "message": "Failed to send email.",
                  "code": "email_fail"
                }
            ]
          }
        }
      }
    }
    ```

---

#### RevokeToken

{{ api.VerifyOrRefreshOrRevokeToken }}

=== "graphql"
    ```graphql
    mutation {
      revokeToken(
        refreshToken: "a64f732b4e00432f2ff1b47537a11458be13fc82"
      ) {
        success,
        errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "revokeToken": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      revokeToken(
        input: {
          refreshToken: "a64f732b4e00432f2ff1b47537a11458be13fc82"
        }
      ) {
        success,
        errors
      }
    }
    ```

=== "Invalid token"
    ```graphql
    {
      "data": {
        "revokeToken": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Invalid token.",
                "code": "invalid_token"
              }
            ]
          }
        }
      }
    }
    ```

---

#### SendPasswordResetEmail

{{ api.SendPasswordResetEmail }}

=== "graphql"
    ```graphql
    mutation {
      sendPasswordResetEmail(
        email: "skywalker@email.com"
      ) {
        success,
        errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "register": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      sendPasswordResetEmail(
        input: {
          email: "skywalker@email.com"
        }
      ) {
        success,
        errors
      }
    }
    ```

=== "Invalid email"
    ```graphql
    {
      "data": {
        "sendPasswordResetEmail": {
          "success": false,
          "errors": {
            "email": [
              {
                "message": "Enter a valid email address.",
                "code": "invalid"
              }
            ]
          }
        }
      }
    }
    ```

=== "Email fail"
    ```graphql"Email fail"
    {
      "data": {
        "sendPasswordResetEmail": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
                {
                  "message": "Failed to send email.",
                  "code": "email_fail"
                }
            ]
          }
        }
      }
    }
    ```

=== "Email not verified"
    ```graphql
    {
      "data": {
        "sendPasswordResetEmail": {
          "success": false,
          "errors": {
            "email": [
              {
                "message": "Verify your account. A new verification email was sent.",
                "code": "not_verified"
              }
            ]
          }
        }
      }
    }
    ```

---

#### VerifyAccount

{{ api.VerifyAccount }}

== "graphql"
    ```graphql
    mutation {
      verifyAccount(
        token:"eyJ1c2VybmFtZSI6InNreXdhbGtlciIsImFjdGlvbiI6ImFjdGl2YXRpb24ifQ:1itC5A:vJhRJwBcrNxvmEKxHrZa6Yoqw5Q",
      ) {
        success, errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "verifyAccount": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      verifyAccount(
        input: {
          token:"eyJ1c2VybmFtZSI6InNreXdhbGtlciIsImFjdGlvbiI6ImFjdGl2YXRpb24ifQ:1itC5A:vJhRJwBcrNxvmEKxHrZa6Yoqw5Q",
        }
      ) {
        success, errors
      }
    }
    ```

=== "Invalid token"
    ```graphql
    {
      "data": {
        "verifyAccount": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Invalid token.",
                "code": "invalid_token"
              }
            ]
          }
        }
      }
    }
    ```

=== "Already verified"
    ```graphql
    {
      "data": {
        "verifyAccount": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Account already verified.",
                "code": "already_verified"
              }
            ]
          }
        }
      }
    }
    ```

---

#### VerifySecondaryEmail

{{ api.VerifySecondaryEmail }}

=== "graphql"
    ```graphql
    mutation {
      verifySecondaryEmail(
        token: "eyJ1c2VybmFtZSI6Im5ld191c2VyMSIsImFjdGlvbiI6ImFjdGl2YXRpb25fc2Vjb25kYXJ5X2VtYWlsIiwic2Vjb25kYXJ5X2VtYWlsIjoibXlfc2Vjb25kYXJ5X2VtYWlsQGVtYWlsLmNvbSJ9:1ivhfJ:CYZswRKV3avWA8cb41KqZ1-zdVo"
        ) {
        success, errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "verifySecondaryEmail": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      verifySecondaryEmail(
        input: {
          token: "eyJ1c2VybmFtZSI6Im5ld191c2VyMSIsImFjdGlvbiI6ImFjdGl2YXRpb25fc2Vjb25kYXJ5X2VtYWlsIiwic2Vjb25kYXJ5X2VtYWlsIjoibXlfc2Vjb25kYXJ5X2VtYWlsQGVtYWlsLmNvbSJ9:1ivhfJ:CYZswRKV3avWA8cb41KqZ1-zdVo"
        }
      ) {
        success, errors
      }
    }
    ```

=== "Invalid token"
    ```graphql
    {
      "data": {
        "verifySecondaryEmail": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Invalid token.",
                "code": "invalid_token"
              }
            ]
          }
        }
      }
    }
    ```

=== "Expired token"
    ```graphql
    {
      "data": {
        "verifySecondaryEmail": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Expired token.",
                "code": "expired_token"
              }
            ]
          }
        }
      }
    }
    ```


---

#### VerifyToken

{{ api.VerifyOrRefreshOrRevokeToken }}

=== "graphql"
    ```graphql
    mutation {
      verifyToken(
        token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNreXdhbGtlciIsImV4cCI6MTU3OTQ1ODY3Miwib3JpZ0lhdCI6MTU3OTQ1ODM3Mn0.rrB4sMA-v7asrr8Z2ru69U1x-d98DuEJVBnG2F1C1S0"
      ) {
        success,
        errors,
        payload
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "verifyToken": {
          "success": true,
          "errors": null,
          "payload": {
            "username": "skywalker",
            "exp": 1579458672,
            "origIat": 1579458372
          }
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      verifyToken(
        input: {
          token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNreXdhbGtlciIsImV4cCI6MTU3OTQ1ODY3Miwib3JpZ0lhdCI6MTU3OTQ1ODM3Mn0.rrB4sMA-v7asrr8Z2ru69U1x-d98DuEJVBnG2F1C1S0"
        }
      ) {
        success,
        errors,
        payload
      }
    }
    ```

=== "Invalid token"
    ```graphql
    {
      "data": {
        "verifyToken": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Invalid token.",
                "code": "invalid_token"
              }
            ]
          },
          "payload": null
        }
      }
    }
    ```

=== "Expired token"
    ```graphql
    {
      "data": {
        "verifyToken": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Expired token.",
                "code": "expired_token"
              }
            ]
          }
        }
      }
    }
    ```

---

### Protected

Protected mutations require the http Authorization header.

If you send a request **without** the http Authorization header, or a **bad token**:

- If using `graphql_jwt.backends.JSONWebTokenBackend`, it will raise.
- If using `graphql_auth.backends.GraphQLAuthBackend`, it will return a standard response, with `success=False` and `errors`.

As explained on the [installation guide](installation.md)

---

#### ArchiveAccount

{{ api.ArchiveAccount }}

=== "graphql"
    ```graphql
    mutation {
      archiveAccount(
        password: "supersecretpassword",
      ) {
        success,
        errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "register": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      archiveAccount(
        input: {
          password: "supersecretpassword",
        }
      ) {
        success,
        errors
      }
    }
    ```

=== "Unauthenticated"
    ```graphql
    {
      "data": {
        "archiveAccount": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Unauthenticated.",
                "code": "unauthenticated"
              }
            ]
          }
        }
      }
    }
    ```

=== "Invalid password"
    ```graphql
    {
      "data": {
        "archiveAccount": {
          "success": false,
          "errors": {
            "password": [
              {
                "message": "Invalid password.",
                "code": "invalid_password"
              }
            ]
          }
        }
      }
    }
    ```

=== "Not verified"
    ```graphql
    {
      "data": {
        "archiveAccount": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Please verify your account."
                "code": "not_verified"
              }
            ]
          }
        }
      }
    }
    ```

---

#### DeleteAccount

{{ api.DeleteAccount }}

=== "graphql"
    ```graphql
    mutation {
      deleteAccount(
        password: "supersecretpassword",
      ) {
        success,
        errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "deleteAccount": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      deleteAccount(
        input: {
          password: "supersecretpassword",
        }
      ) {
        success,
        errors
      }
    }
    ```

=== "Unauthenticated"
    ```graphql
    {
      "data": {
        "deleteAccount": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Unauthenticated.",
                "code": "unauthenticated"
              }
            ]
          }
        }
      }
    }
    ```

=== "Invalid password"
    ```graphql
    {
      "data": {
        "deleteAccount": {
          "success": false,
          "errors": {
            "password": [
              {
                "message": "Invalid password.",
                "code": "invalid_password"
              }
            ]
          }
        }
      }
    }
    ```

=== "Not verified"
      ```graphql
      {
        "data": {
          "deleteAccount": {
            "success": false,
            "errors": {
              "nonFieldErrors": [
                {
                  "message": "Please verify your account."
                  "code": "not_verified"
                }
              ]
            }
          }
        }
      }
      ```

---

#### PasswordChange

{{ api.PasswordChange }}

=== "graphql"
    ```graphql
    mutation {
    passwordChange(
        oldPassword: "supersecretpassword",
        newPassword1: "123456super",
        newPassword2: "123456super"
      ) {
        success,
        errors,
        token,
        refreshToken
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "passwordChange": {
          "success": true,
          "errors": null,
          "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImpvZWpvZSIsImV4cCI6MTU4MDE0MjE0MCwib3JpZ0lhdCI6MTU4MDE0MTg0MH0.BGUSGKUUd7IuHnWKy8V6MU3slJ-DHsyAdAjGrGb_9fw",
          "refreshToken": "67eb63ba9d279876d3e9ae4d39c311e845e728fc"
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
    passwordChange(
      input: {
          oldPassword: "supersecretpassword",
          newPassword1: "123456super",
          newPassword2: "123456super"
        }
      ) {
        success,
        errors,
        token,
        refreshToken
      }
    }
    ```

=== "Unauthenticated"
    ```graphql
    {
      "data": {
        "passwordChange": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Unauthenticated.",
                "code": "unauthenticated"
              }
            ]
          },
          "token": null,
          "refreshToken": null
        }
      }
    }
    ```

=== "Not verified"
    ```graphql
    {
      "data": {
        "passwordChange": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Please verify your account.",
                "code": "not_verified"
              }
            ]
          },
          "token": null,
          "refreshToken": null
        }
      }
    }
    ```

=== "Password validation"
    ```graphql
    {
      "data": {
        "passwordChange": {
          "success": false,
          "errors": {
            "newPassword2": [
              {
                "message": "This password is too short. It must contain at least 8 characters.",
                "code": "password_too_short"
              },
              {
                "message": "This password is too common.",
                "code": "password_too_common"
              },
              {
                "message": "This password is entirely numeric.",
                "code": "password_entirely_numeric"
              }
            ]
          },
          "token": null,
          "refreshToken": null
        }
      }
    }
    ```

=== "Password mismatch"
    ```graphql
    {
      "data": {
        "passwordChange": {
          "success": false,
          "errors": {
            "newPassword2": [
              {
                "message": "The two password fields didn’t match.",
                "code": "password_mismatch"
              }
            ]
          },
          "token": null,
          "refreshToken": null
        }
      }
    }
    ```

=== "Invalid password"
    ```graphql
    {
      "data": {
        "passwordChange": {
          "success": false,
          "errors": {
            "oldPassword": [
              {
                "message": "Invalid password.",
                "code": "invalid_password"
              }
            ]
          },
          "token": null,
          "refreshToken": null
        }
      }
    }
    ```

---

#### RemoveSecondaryEmail

{{ api.RemoveSecondaryEmail }}

=== "graphql"
    ```graphql
    mutation {
      removeSecondaryEmail(
        password: "supersecretpassword"
      ) {
        success,
        errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "removeSecondaryEmail": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      removeSecondaryEmail(
        input: {
          password: "supersecretpassword"
        }
      ) {
        success,
        errors
      }
    }
    ```

=== "Invalid password"
    ```graphql
    {
      "data": {
        "removeSecondaryEmail": {
          "success": false,
          "errors": {
            "password": [
              {
                "message": "Invalid password.",
                "code": "invalid_password"
              }
            ]
          }
        }
      }
    }
    ```

---

#### SendSecondaryEmailActivation

{{ api.SendSecondaryEmailActivation }}

=== "graphql"
    ```graphql
    mutation {
      sendSecondaryEmailActivation(
        email: "my_secondary_email@email.com"
        password: "supersecretpassword",
      ) {
        success,
        errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "sendSecondaryEmailActivation": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      sendSecondaryEmailActivation(
        input: {
          email: "my_secondary_email@email.com"
          password: "supersecretpassword",
        }
      ) {
        success,
        errors
      }
    }
    ```

=== "Unauthenticated"
    ```graphql
    {
      "data": {
        "sendSecondaryEmailActivation": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Unauthenticated.",
                "code": "unauthenticated"
              }
            ]
          }
        }
      }
    }
    ```

=== "Invalid email"
    ```graphql
    {
      "data": {
        "sendSecondaryEmailActivation": {
          "success": false,
          "errors": {
            "email": [
              {
                "message": "Enter a valid email address.",
                "code": "invalid"
              }
            ]
          }
        }
      }
    }
    ```

=== "Invalid password"
    ```graphql
    {
      "data": {
        "sendSecondaryEmailActivation": {
          "success": false,
          "errors": {
            "password": [
              {
                "message": "Invalid password.",
                "code": "invalid_password"
              }
            ]
          }
        }
      }
    }
    ```

=== "Not verified"
    ```graphql
    {
      "data": {
        "sendSecondaryEmailActivation": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Please verify your account."
                "code": "not_verified"
              }
            ]
          }
        }
      }
    }
    ```

---

#### SwapEmails

{{ api.SwapEmails }}


=== "graphql"
    ```graphql
    mutation {
      swapEmails(
        password: "supersecretpassword"
      ) {
        success,
        errors
      }
    }
    ```

=== "success"
    ```graphql
    {
      "data": {
        "swapEmails": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      swapEmails(
        input: {
          password: "supersecretpassword"
        }
      ) {
        success,
        errors
      }
    }
    ```

=== "Invalid password"
    ```graphql
    {
      "data": {
        "swapEmails": {
          "success": false,
          "errors": {
            "password": [
              {
                "message": "Invalid password.",
                "code": "invalid_password"
              }
            ]
          }
        }
      }
    }
    ```

---

#### UpdateAccount

{{ api.UpdateAccount }}

    === "graphql"
    ```graphql
    mutation {
      updateAccount(
        firstName: "Luke"
      ) {
        success,
        errors
      }
    }
```

=== "success"
    ```graphql
    {
      "data": {
        "updateAccount": {
          "success": true,
          "errors": null
        }
      }
    }
    ```

=== "relay"
    ```graphql
    mutation {
      updateAccount(
        input: {
          firstName: "Luke"
        }
      ) {
        success,
        errors
      }
    }
    ```

=== "Unauthenticated"
    ```graphql
    {
      "data": {
        "updateAccount": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Unauthenticated.",
                "code": "unauthenticated"
              }
            ]
          }
        }
      }
    }
    ```

=== "Not verified"
    ```graphql
    {
      "data": {
        "updateAccount": {
          "success": false,
          "errors": {
            "nonFieldErrors": [
              {
                "message": "Please verify your account."
                "code": "not_verified"
              }
            ]
          }
        }
      }
    }
    ```
