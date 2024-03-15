import json
import types
from typing import Any

import django
from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase

from graphql_auth.models import UserStatus

_DJANGO_VERSION_AT_LEAST_4_2 = django.VERSION[0] > 4 or (django.VERSION[0] == 4 and django.VERSION[1] >= 2)


class TestCaseMeta(type):
    def __new__(cls, name: str, bases: tuple[type], dct: dict) -> type:
        if 'Base' not in name:
            for base in bases:
                for key, value in base.__dict__.items():
                    if key.startswith('_test_') and isinstance(value, types.FunctionType) and key[1:] not in dct:
                        dct[key[1:]] = value
        return super().__new__(cls, name, bases, dct)


class CommonTestCase(GraphQLTestCase, metaclass=TestCaseMeta):
    """
    Thanks to metaclass TestCaseMeta we can create a base test class with
    common test methods for both GraphQL and Relay request.

    For example we create a LoginCommonTestCase class that:
        - inherits from this CommonTestCase
        - contains a test method with the name of prefix `_test_some_method`.

    Next, let's create 2 test classes named LoginTestCase and LoginRelayTestCase
    that inherit from above LoginCommonTestCase class.
    The LoginTestCase will be used to test with GraphQL requests and
    the LoginRelayTestCase will be used to Relay requests.
    Each of these test classes will automatically have a test method named `test_some_method`
    """

    RESPONSE_RESULT_KEY: str
    RESPONSE_ERROR_KEY: str = 'errors'

    default_password = 'very-strong-password'

    def create_user(self, password=None, verified=False, archived=False, secondary_email="", *args, **kwargs):
        if kwargs.get("username"):
            kwargs.update({"first_name": kwargs.get("username")})
        user = get_user_model().objects.create(*args, **kwargs)
        user.set_password(password or self.default_password)
        user.save()
        user_status = UserStatus._default_manager.get(user=user)
        user_status.verified = verified
        user_status.archived = archived
        user_status.secondary_email = secondary_email
        user_status.save()
        user_status.refresh_from_db()
        user.refresh_from_db()
        return user

    def get_authorization_header(self, token) -> dict[str, str | dict[str, str]]:
        key = 'authorization' if _DJANGO_VERSION_AT_LEAST_4_2 else 'HTTP_AUTHORIZATION'
        return {key: f'JWT {token}'}

    def get_response_result(self, response) -> dict[str, Any]:
        return json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]

    def get_response_errors(self, response) -> list[dict[str, str]]:
        return json.loads(response.content.decode())[self.RESPONSE_ERROR_KEY]
