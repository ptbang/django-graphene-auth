# Django Graphene Auth

[Django](https://github.com/django/django) registration and authentication with GraphQL
with support for most newest versions of Django, Django Graphene, Django GraphQL JWT


[![downloads](https://img.shields.io/pypi/dm/django-graphene-auth)](https://pypistats.org/packages/django-graphene-auth)
[![Codecov Coverage](https://img.shields.io/codecov/c/github/ptbang/django-graphene-auth/master.svg?style=flat-square)](https://codecov.io/gh/ptbang/django-graphene-auth/)
[![Pypi](https://img.shields.io/pypi/v/django-graphene-auth.svg)](https://pypi.org/project/django-graphene-auth/)
[![Documentation Status](https://readthedocs.org/projects/django-graphene-auth/badge/?version=latest)](https://django-graphene-auth.readthedocs.io/en/latest/?badge=latest)


---

## About

This project was based on the forked repository from
[Django GraphQL Auth](https://github.com/PedroBern/django-graphql-auth) -
created by *Pedro Bern* (thanks so much for a great job).

The reason I decided to create this project is that the original doesn't support
the newer versions of django, graphene-django and django-graphql-jwt.
Futhermore, it appears that the original one will not be further developed in the near future.

---

## Features

* [x] Awesome docs! (big thanks for *Pedro Bern*)
* [x] Fully compatible with [Relay](https://github.com/facebook/relay>)
* [x] Works with ==default or custom== user model
* [x] JWT authentication <small>(with [Django GraphQL JWT](https://github.com/flavors/django-graphql-jwt))</small>
* [x] User query with filters <small>(with [Django Filter](https://github.com/carltongibson/django-filter) and [Graphene Django](https://github.com/graphql-python/graphene-django))</small>
* [x] User registration with email verification
* [x] Add secondary email, with email verification too
* [x] Resend activation email
* [x] Retrieve/Update user
* [x] Archive user
* [x] Permanently delete user or make it inactive
* [x] Turn archived user active again on login
* [x] Track user status <small>(archived, verified, secondary email)</small>
* [x] Password change
* [x] Password reset through email
* [x] Revoke user tokens on account archive/delete/password change/reset
* [x] All mutations return `success` and `errors`
* [x] Default email templates <small>(you will customize though)</small>
* [x] Customizable, no lock-in
* [x] Passwordless registration

---

## Example

Handling user accounts becomes super easy.

```graphql
mutation {
  register(
    email: "new_user@email.com",
    username: "new_user",
    password1: "123456super",
    password2: "123456super"
  ) {
    success,
    errors,
    token,
    refreshToken
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
    success,
    errors
  }
}
```

Now user is verified.

```python
u.status.verified
# True
```

Check the [installation guide](installation.md). Or if you prefer, browse the [api](api.md).
