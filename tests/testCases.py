import json
import pprint
import re
import types
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from graphene.test import Client
from graphene.types.schema import Schema
from graphene_django.utils.testing import GraphQLTestCase

from graphql_auth.models import UserStatus
from graphql_auth.utils import get_classes

from .schema import default_schema, relay_schema


class TestCaseMeta(type):
    def __new__(cls, name: str, bases: tuple[type], dct: dict) -> type:
        if 'Base' not in name:
            for base in bases:
                for key, value in base.__dict__.items():
                    if key.startswith('_test_') and isinstance(value, types.FunctionType) and key[1:] not in dct:
                        dct[key[1:]] = value
        return super().__new__(cls, name, bases, dct)


class BaseTestCase(GraphQLTestCase, metaclass=TestCaseMeta):
    """
    provide make_request helper to easily make
    requests with context variables.

    Return a shortcut of the client.execute["data"]["<query name>"].

    example:
        query = `
            mutation {
             register ...
            }
        `
        return client.execute["data"]["register"]
    """

    RESPONSE_RESULT_KEY: str
    RESPONSE_ERROR_KEY: str = 'errors'

    default_password = "23kegbsi7g2k"

    def register_user(self, password=None, verified=False, archived=False, secondary_email="", *args, **kwargs):
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

    def get_authorization_header(self, token) -> dict[str, str]:
        return {'HTTP_AUTHORIZATION': f'JWT {token}'}

    def get_response_result(self, response) -> dict[str, Any]:
        return json.loads(response.content.decode())['data'][self.RESPONSE_RESULT_KEY]

    def get_response_errors(self, response) -> list[dict[str, str]]:
        return json.loads(response.content.decode())[self.RESPONSE_ERROR_KEY]

    def make_request(self, query, variables={"user": AnonymousUser()}, raw=False, client=None):
        request_factory = RequestFactory()
        my_request = request_factory.post("/graphql/")

        for key in variables:
            setattr(my_request, key, variables[key])

        executed = client.execute(query, context=my_request)
        if raw:
            return executed
        pattern = r"{\s*(?P<target>\w*)"
        m = re.search(pattern, query)
        m = m.groupdict()
        try:
            return executed["data"][m["target"]]
        except:
            print("\nInvalid query!")
            raise Exception(executed["errors"])
        finally:
            pprint.pprint(executed)


# class RelayTestCase(TestBase):
#     def make_request(self, *args, **kwargs):
#         client = Client(relay_schema)
#         return super().make_request(client=client, *args, **kwargs)


# class DefaultTestCase(TestBase):
#     def make_request(self, *args, **kwargs):
#         client = Client(default_schema)
#         return super().make_request(client=client, *args, **kwargs)


def set_test_methods(test_classes: list[type[BaseTestCase]]) -> None:
    for test_class in test_classes:
        test_methods = [method for method in dir(test_class) if method.startswith('_test_')]
        for method in test_methods:
            setattr(test_class, method[1:], getattr(test_class, method))


def prepare_test_classes(module: str | types.ModuleType) -> None:
    """
    Sets test methods from defined methods, which names start by prefix "_test_"
    for all test class inside the module.
    """
    test_classes = get_classes(module, BaseTestCase)
    for test_class in test_classes:
        if not test_class[0].endswith('BaseTestCase'):
            set_test_methods([test_class[1]])
