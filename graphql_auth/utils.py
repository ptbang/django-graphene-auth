import inspect
import types
import warnings
from importlib import import_module

from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.core import signing
from django.utils.translation import gettext as _
from graphene_django.utils import camelize

from .exceptions import TokenScopeError

warnings.simplefilter("once")


def get_token(user, action, **kwargs):
    username = user.get_username()
    if hasattr(username, "pk"):
        username = username.pk
    payload = {user.USERNAME_FIELD: username, "action": action}
    if kwargs:
        payload.update(**kwargs)
    token = signing.dumps(payload)
    return token


def get_token_payload(token, action, exp=None):
    payload = signing.loads(token, max_age=exp)
    _action = payload.pop("action")
    if _action != action:
        raise TokenScopeError
    return payload


def get_token_paylod(token, action, exp=None):
    warnings.warn(
        "get_token_paylod is deprecated, use get_token_payload instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_token_payload(token, action, exp)


def using_refresh_tokens():
    return (
        hasattr(django_settings, "GRAPHQL_JWT")
        and django_settings.GRAPHQL_JWT.get("JWT_LONG_RUNNING_REFRESH_TOKEN", False)
        and "graphql_jwt.refresh_token.apps.RefreshTokenConfig" in django_settings.INSTALLED_APPS
    )


def revoke_user_refresh_token(user):
    if using_refresh_tokens():
        refresh_tokens = user.refresh_tokens.all()
        for refresh_token in refresh_tokens:
            try:
                refresh_token.revoke()
            except Exception:  # JSONWebTokenError
                pass


def flat_dict(dict_or_list):
    """
    if is dict, return list of dict keys,
    if is list, return the list
    """
    return list(dict_or_list.keys()) if isinstance(dict_or_list, dict) else dict_or_list


def normalize_fields(dict_or_list, extra_list):
    """
    helper merge settings defined fileds and
    other fields on mutations
    """
    if isinstance(dict_or_list, dict):
        for i in extra_list:
            dict_or_list[i] = "String"
        return dict_or_list
    else:
        return dict_or_list + extra_list


def get_classes(module: str | types.ModuleType, class_type: type | None = None) -> list[tuple[str, type]]:
    """
    Returns list of all classes od type `class_type` defined in the given module path.
    """
    if isinstance(module, str):
        module = import_module(module)
    if not class_type:
        return inspect.getmembers(module, inspect.isclass)
    return [item for item in inspect.getmembers(module, inspect.isclass) if issubclass(item[1], class_type)]


def camelize_form_errors(errors: dict) -> dict:
    """Camelize dict of django form errors"""
    if errors.get('__all__', False):
        errors['non_field_errors'] = errors.pop('__all__')
    return camelize(errors)  # type: ignore


def get_user_by_natural_key(username) -> AbstractBaseUser | None:
    """
    A difference approach from the original method (graphql_jwt.utils.get_user_by_natural_key)
    is using `select_related('status')`
    """
    UserModel = get_user_model()
    return UserModel._default_manager.select_related('status').filter(**{UserModel.USERNAME_FIELD: username}).first()  # type: ignore
