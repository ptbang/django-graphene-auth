from typing import Callable

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.module_loading import import_string

from .settings import graphql_auth_settings as app_settings
from .types import ExpectedErrorType

UserModel = get_user_model()


def get_user_by_email(email):
    """
    get user by email or by secondary email
    raise ObjectDoesNotExist
    """
    user = (
        UserModel._default_manager.select_related('status')
        .filter(Q(**{UserModel.EMAIL_FIELD: email}) | Q(status__secondary_email=email))  # type: ignore
        .first()
    )
    if user is None:
        raise ObjectDoesNotExist
    return user


def get_user_to_login(**kwargs):
    """
    get user by kwargs or secondary email
    to perform login
    raise ObjectDoesNotExist
    """
    if 'email' in kwargs.keys():
        lookup_filter = Q(email=kwargs['email'])
        if app_settings.ALLOW_LOGIN_WITH_SECONDARY_EMAIL:
            lookup_filter |= Q(status__secondary_email=kwargs['email'])
        user = UserModel._default_manager.select_related('status').filter(lookup_filter).first()
    else:
        user = UserModel._default_manager.select_related('status').filter(**kwargs).first()
    if user:
        return user
    else:
        raise ObjectDoesNotExist


def get_async_email_func() -> Callable | None:
    if app_settings.is_async_email:
        return import_string(app_settings.EMAIL_ASYNC_TASK)
    return None


async_email_func = get_async_email_func()


def get_output_error_type():
    if app_settings.CUSTOM_ERROR_TYPE and isinstance(app_settings.CUSTOM_ERROR_TYPE, str):
        return import_string(app_settings.CUSTOM_ERROR_TYPE)
    else:
        return ExpectedErrorType


OutputErrorType = get_output_error_type()
