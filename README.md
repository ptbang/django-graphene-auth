# Django Graphene Auth

[Django](https://github.com/django/django) GraphQL registration and authentication
compatible with the latest versions of Django, Django GraphQL JWT

[![downloads](https://img.shields.io/pypi/dm/django-graphene-auth)](https://pypistats.org/packages/django-graphene-auth)
[![Codecov Coverage](https://img.shields.io/codecov/c/github/ptbang/django-graphene-auth)](https://app.codecov.io/github/ptbang/django-graphene-auth/tree)
[![Pypi](https://img.shields.io/pypi/v/django-graphene-auth.svg)](https://pypi.org/project/django-graphene-auth/)
[![Documentation Status](https://readthedocs.org/projects/django-graphene-auth/badge/?version=latest)](https://django-graphene-auth.readthedocs.io/en/latest/?badge=latest)


## About

This project was based on the forked repository from
[Django GraphQL Auth](https://github.com/PedroBern/django-graphql-auth) -
created by *Pedro Bern* (thanks so much for a great job).

The reason I decided to create this project is that the original doesn't support
the newer versions of django, graphene-django and django-graphql-jwt.
Futhermore, it appears that the original one will not be further developed in the near future.


## Documentation

Documentation is available at [read the docs](https://django-graphene-auth.readthedocs.io/en/latest/).


## Features

* [x] [Docs](https://django-graphene-auth.readthedocs.io/en/latest/)
* [x] Fully compatible with [Relay](https://github.com/facebook/relay>)
* [x] Works with **default or custom** user model
* [x] JWT authentication *(with [Django GraphQL JWT](https://github.com/flavors/django-graphql-jwt))*
* [x] User query with filters *(with [Django Filter](https://github.com/carltongibson/django-filter) and [Graphene Django](https://github.com/graphql-python/graphene-django))*
* [x] User registration with email verification
* [x] Add secondary email, with email verification too
* [x] Resend activation email
* [x] Retrieve/Update user
* [x] Archive user
* [x] Permanently delete user or make it inactive
* [x] Turn archived user active again on login
* [x] Track user status (archived, verified, secondary email)
* [x] Password change
* [x] Password reset through email
* [x] Revoke user refresh tokens on account archive/delete/password change/reset
* [x] All mutations return `success` and `errors`
* [x] Default email templates *(you will customize though)*
* [x] Customizable, no lock-in

## Full Schema

```python

import graphene

from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations

class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    resend_activation_email = mutations.ResendActivationEmail.Field()
    send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    password_reset = mutations.PasswordReset.Field()
    password_set = mutations.PasswordSet.Field() # For passwordless registration
    password_change = mutations.PasswordChange.Field()
    update_account = mutations.UpdateAccount.Field()
    archive_account = mutations.ArchiveAccount.Field()
    delete_account = mutations.DeleteAccount.Field()
    send_secondary_email_activation =  mutations.SendSecondaryEmailActivation.Field()
    verify_secondary_email = mutations.VerifySecondaryEmail.Field()
    swap_emails = mutations.SwapEmails.Field()
    remove_secondary_email = mutations.RemoveSecondaryEmail.Field()

    # django-graphql-jwt inheritances
    token_auth = mutations.ObtainJSONWebToken.Field()
    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()


class Query(UserQuery, MeQuery, graphene.ObjectType):
    pass


class Mutation(AuthMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
```


## Relay

Import mutations from the ``relay`` module:

```python

from graphql_auth import relay

class AuthMutation(graphene.ObjectType):
   register = relay.Register.Field()
   # ...
```


## Example

Handling user accounts becomes super easy.

```python
mutation {
  register(
    email: "new_user@email.com",
    username: "new_user",
    password1: "123456super",
    password2: "123456super",
  ) {
    success,
    token,  # optional, depending on settings of GRAPHQL_AUTH['ALLOW_LOGIN_NOT_VERIFIED']
    refreshToken  # optional, depending on settings of GRAPHQL_JWT['JWT_LONG_RUNNING_REFRESH_TOKEN']
  }
}
```

Check the status of the new user:

```python
u = UserModel.objects.last()
u.status.verified
# False
```

During the registration, an email with a verification link was sent.

```python
mutation {
  verifyAccount(
    token:"<TOKEN ON EMAIL LINK>",
  ) {
    success
  }
}
```

Now user is verified.

```python
u.status.verified
# True
```

Check the [installation guide](https://django-graphene-auth.readthedocs.io/en/latest/installation/). Or if you prefer, browse the [api](https://django-graphene-auth.readthedocs.io/en/latest/api/).
