from typing import Callable

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.module_loading import import_string

from .models import UserStatus
from .settings import graphql_auth_settings as app_settings


UserModel = get_user_model()


def get_user_by_email(email):
    """
    get user by email or by secondary email
    raise ObjectDoesNotExist
    """
    try:
        user = UserModel._default_manager.get(**{UserModel.EMAIL_FIELD: email})
        return user
    except ObjectDoesNotExist:
        status = UserStatus._default_manager.get(secondary_email=email)
        return status.user


def get_user_to_login(**kwargs):
    """
    get user by kwargs or secondary email
    to perform login
    raise ObjectDoesNotExist
    """
    try:
        user = UserModel._default_manager.get(**kwargs)
        return user
    except ObjectDoesNotExist:
        if app_settings.ALLOW_LOGIN_WITH_SECONDARY_EMAIL:
            email = kwargs.get(UserModel.EMAIL_FIELD, None)
            if email:
                status = UserStatus._default_manager.get(secondary_email=email)
                return status.user
        raise ObjectDoesNotExist


def get_async_email_func() -> Callable | None:
    if app_settings.is_declared_async_email:
        return import_string(app_settings.EMAIL_ASYNC_TASK)
    return None


async_email_func = get_async_email_func()
