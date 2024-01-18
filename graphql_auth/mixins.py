from smtplib import SMTPException

import graphene
from graphene.types.generic import GenericScalar
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import BadSignature, SignatureExpired
from django.db import transaction
from django.utils.translation import gettext as _
from graphql_jwt.decorators import token_auth
from graphql_jwt.exceptions import JSONWebTokenError, JSONWebTokenExpired

from .bases import SuccessErrorsOutput
from .constants import Messages, TokenAction
from .decorators import password_confirmation_required, secondary_email_required, verification_required
from .exceptions import (
    EmailAlreadyInUseError,
    InvalidCredentialsError,
    PasswordAlreadySetError,
    TokenScopeError,
    UserAlreadyVerifiedError,
    UserNotVerifiedError,
    WrongUsageError,
)
from .forms import EmailForm, PasswordLessRegisterForm, RegisterForm, UpdateAccountForm
from .models import UserStatus
from .queries import UserNode
from .settings import graphql_auth_settings as app_settings
from .shortcuts import async_email_func, get_user_by_email, get_user_to_login
from .signals import user_registered, user_verified
from .utils import get_token_payload, revoke_user_refresh_token, using_refresh_tokens

UserModel = get_user_model()


class RegisterMixin(SuccessErrorsOutput):
    """
    Register user with fields defined in the settings.

    If the email field of the user model is part of the
    registration fields (default), check if there is
    no user with that email or as a secondary email.

    If it exists, it does not register the user,
    even if the email field is not defined as unique
    (default of the default django user model).

    When creating the user, it also creates a `UserStatus`
    related to that user, making it possible to track
    if the user is archived, verified and has a secondary
    email.

    Send account verification email.

    If allowed to not verified users login, return token.
    """

    if app_settings.ALLOW_LOGIN_NOT_VERIFIED:
        token = graphene.Field(graphene.String)
        if using_refresh_tokens():
            refresh_token = graphene.Field(graphene.String)

    form = PasswordLessRegisterForm if app_settings.ALLOW_PASSWORDLESS_REGISTRATION else RegisterForm

    @classmethod
    @token_auth
    def login_on_register(cls, root, info, **kwargs):
        return cls()

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                f = cls.form(kwargs)
                if f.is_valid():
                    email = kwargs.get(UserModel.EMAIL_FIELD, False)  # type: ignore
                    UserStatus.clean_email(email)
                    user = f.save()
                    send_activation = app_settings.SEND_ACTIVATION_EMAIL is True and email
                    send_password_set = (
                        app_settings.ALLOW_PASSWORDLESS_REGISTRATION is True
                        and app_settings.SEND_PASSWORD_SET_EMAIL is True
                        and email
                    )
                    if send_activation:
                        if app_settings.is_async_email:
                            async_email_func(user.status.send_activation_email, (info,))  # type: ignore
                        else:
                            user.status.send_activation_email(info)

                    if send_password_set:
                        if async_email_func:
                            async_email_func(user.status.send_password_set_email, (info,))
                        else:
                            user.status.send_password_set_email(info)

                    user_registered.send(sender=cls, user=user)

                    if app_settings.ALLOW_LOGIN_NOT_VERIFIED:
                        payload = cls.login_on_register(root, info, password=kwargs.get("password1"), **kwargs)
                        return_value = {}
                        for field in cls._meta.fields:  # type: ignore
                            return_value[field] = getattr(payload, field)
                        return cls(**return_value)
                    return cls(success=True)
                else:
                    return cls(success=False, errors=f.errors)
        except EmailAlreadyInUseError:
            return cls(
                success=False,
                # if the email was set as a secondary email,
                # the RegisterForm will not catch it,
                # so we need to run UserStatus.clean_email(email)
                errors=Messages.EMAIL_IN_USE,
            )
        except SMTPException:
            return cls(success=False, errors=Messages.FAILED_SENDING_ACTIVATION_EMAIL)


class VerifyAccountMixin(SuccessErrorsOutput):
    """
    Verify user account.

    Receive the token that was sent by email.
    If the token is valid, make the user verified
    by making the `user.status.verified` field true.
    """

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        try:
            token = kwargs.get("token")
            UserStatus.verify(token)
            return cls(success=True)
        except UserAlreadyVerifiedError:
            return cls(success=False, errors=Messages.ALREADY_VERIFIED)
        except SignatureExpired:
            return cls(success=False, errors=Messages.EXPIRED_TOKEN)
        except (BadSignature, TokenScopeError):
            return cls(success=False, errors=Messages.INVALID_TOKEN)


class VerifySecondaryEmailMixin(SuccessErrorsOutput):
    """
    Verify user secondary email.

    Receive the token that was sent by email.
    User is already verified when using this mutation.

    If the token is valid, add the secondary email
    to `user.status.secondary_email` field.

    Note that until the secondary email is verified,
    it has not been saved anywhere beyond the token,
    so it can still be used to create a new account.
    After being verified, it will no longer be available.
    """

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        try:
            token = kwargs.get("token")
            UserStatus.verify_secondary_email(token)
            return cls(success=True)
        except EmailAlreadyInUseError:
            # while the token for secondary email was sent and the user haven't
            # verified, the email has not been saved to database and it was free.
            return cls(success=False, errors=Messages.EMAIL_IN_USE)
        except SignatureExpired:
            return cls(success=False, errors=Messages.EXPIRED_TOKEN)
        except (BadSignature, TokenScopeError):
            return cls(success=False, errors=Messages.INVALID_TOKEN)


class ResendActivationEmailMixin(SuccessErrorsOutput):
    """
    Sends activation email.

    It is called resend because theoretically
    the first activation email was sent when
    the user registered.

    If there is no user with the requested email,
    a successful response is returned.
    """

    form = EmailForm

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        try:
            email = kwargs.get("email")
            f = cls.form({"email": email})
            if f.is_valid():
                user = get_user_by_email(email)
                if async_email_func:
                    async_email_func(user.status.resend_activation_email, (info,))  # type: ignore
                else:
                    user.status.resend_activation_email(info)  # type: ignore
                return cls(success=True)
            return cls(success=False, errors=f.errors)
        except ObjectDoesNotExist:
            return cls(success=True)  # even if user is not registered
        except SMTPException:
            return cls(success=False, errors=Messages.EMAIL_FAIL)
        except UserAlreadyVerifiedError:
            return cls(success=False, errors=Messages.ALREADY_VERIFIED)


class SendPasswordResetEmailMixin(SuccessErrorsOutput):
    """
    Send password reset email.

    For non verified users, send an activation
    email instead.

    Accepts both primary and secondary email.

    If there is no user with the requested email,
    a successful response is returned.
    """

    form = EmailForm

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        email = kwargs.get("email")
        try:
            f = cls.form({"email": email})
            if f.is_valid():
                user = get_user_by_email(email)
                if async_email_func:
                    async_email_func(user.status.send_password_reset_email, (info, [email]))  # type: ignore
                else:
                    user.status.send_password_reset_email(info, [email])  # type: ignore
                return cls(success=True)
            return cls(success=False, errors=f.errors)
        except ObjectDoesNotExist:
            return cls(success=True)  # even if user is not registered
        except SMTPException:
            return cls(success=False, errors=Messages.EMAIL_FAIL)

    @classmethod
    def _resend_activation_email(cls, info, user):  # pragma: no cover
        try:
            if async_email_func:
                async_email_func(user.status.resend_activation_email, (info,))  # type: ignore
            else:
                user.status.resend_activation_email(info)  # type: ignore
            return cls(success=False, errors=Messages.NOT_VERIFIED_PASSWORD_RESET)
        except SMTPException:
            return cls(success=False, errors=Messages.EMAIL_FAIL)


class PasswordResetMixin(SuccessErrorsOutput):
    """
    Change user password without old password.

    Receive the token that was sent by email.

    If token and new passwords are valid, update
    user password and in case of using refresh
    tokens, revoke all of them.

    Also, if user has not been verified yet, verify it.
    """

    form = SetPasswordForm

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        try:
            token = kwargs.pop("token")
            payload = get_token_payload(
                token,
                TokenAction.PASSWORD_RESET,
                app_settings.EXPIRATION_PASSWORD_RESET_TOKEN,
            )
            user = UserModel._default_manager.get(**payload)
            f = cls.form(user, kwargs)
            if f.is_valid():
                revoke_user_refresh_token(user)
                user = f.save()

                if user.status.verified is False:  # type: ignore
                    user.status.verified = True  # type: ignore
                    user.status.save(update_fields=["verified"])  # type: ignore
                    user_verified.send(sender=cls, user=user)

                return cls(success=True)
            return cls(success=False, errors=f.errors)
        except SignatureExpired:
            return cls(success=False, errors=Messages.EXPIRED_TOKEN)
        except (BadSignature, TokenScopeError):
            return cls(success=False, errors=Messages.INVALID_TOKEN)


class PasswordSetMixin(SuccessErrorsOutput):
    """
    Set user password - for passwordless registration

    Receive the token that was sent by email.

    If token and new passwords are valid, set
    user password and in case of using refresh
    tokens, revoke all of them.

    Also, if user has not been verified yet, verify it.
    """

    form = SetPasswordForm

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        try:
            token = kwargs.pop("token")
            payload = get_token_payload(
                token,
                TokenAction.PASSWORD_SET,
                app_settings.EXPIRATION_PASSWORD_SET_TOKEN,
            )
            user = UserModel._default_manager.get(**payload)
            f = cls.form(user, kwargs)
            if f.is_valid():
                # Check if user has already set a password
                if user.has_usable_password():
                    raise PasswordAlreadySetError
                revoke_user_refresh_token(user)
                user = f.save()

                if user.status.verified is False:  # type: ignore
                    user.status.verified = True  # type: ignore
                    user.status.save(update_fields=["verified"])  # type: ignore

                return cls(success=True)
            return cls(success=False, errors=f.errors)
        except SignatureExpired:
            return cls(success=False, errors=Messages.EXPIRED_TOKEN)
        except (BadSignature, TokenScopeError):
            return cls(success=False, errors=Messages.INVALID_TOKEN)
        except PasswordAlreadySetError:
            return cls(success=False, errors=Messages.PASSWORD_ALREADY_SET)


class ObtainJSONWebTokenMixin(SuccessErrorsOutput):
    """
    Obtain JSON web token for given user.

    Allow to perform login with different fields,
    and secondary email if set. The fields are
    defined on settings.

    Not verified users can login by default. This
    can be changes on settings.

    If user is archived, make it unarchive and
    return `unarchiving=True` on output.
    """

    refresh_expires_in = graphene.Int()
    payload = GenericScalar()
    user = graphene.Field(UserNode)
    unarchiving = graphene.Boolean(default_value=False)

    user_to_login = None

    @classmethod
    def resolve(cls, root, info, **kwargs):
        user = cls.user_to_login if cls.user_to_login == info.context.user else info.context.user
        if user.status.archived is True:  # unarchive on login # type: ignore
            UserStatus.unarchive(user)
            unarchiving = True
        else:
            unarchiving = False
        return cls(user=info.context.user, unarchiving=unarchiving)

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        if len(kwargs.items()) != 2:
            raise WrongUsageError(
                "Must login with password and one of the following fields %s." % (app_settings.LOGIN_ALLOWED_FIELDS)
            )

        try:
            final_kwargs = None
            USERNAME_FIELD = UserModel.USERNAME_FIELD  # type: ignore

            # extract USERNAME_FIELD to use in query
            if USERNAME_FIELD in kwargs:
                data_to_login = {USERNAME_FIELD: kwargs[USERNAME_FIELD]}
                final_kwargs = kwargs
                password = kwargs.get("password")
            else:  # use what is left to query
                password = kwargs.pop("password")
                query_field, query_value = kwargs.popitem()
                data_to_login = {query_field: query_value}

            cls.user_to_login = get_user_to_login(**data_to_login)

            if not final_kwargs:
                final_kwargs = {
                    "password": password,
                    USERNAME_FIELD: getattr(cls.user_to_login, USERNAME_FIELD),
                }

            if cls.user_to_login.status.verified or app_settings.ALLOW_LOGIN_NOT_VERIFIED:  # type: ignore
                return cls.parent_resolve(root, info, **final_kwargs)  # type: ignore
            else:
                raise UserNotVerifiedError
        except (JSONWebTokenError, ObjectDoesNotExist, InvalidCredentialsError):
            return cls(success=False, errors=Messages.INVALID_CREDENTIALS)
        except UserNotVerifiedError:
            return cls(success=False, errors=Messages.NOT_VERIFIED)


class ArchiveOrDeleteMixin(SuccessErrorsOutput):
    @classmethod
    @verification_required
    @password_confirmation_required
    def resolve_mutation(cls, root, info, *args, **kwargs):
        user = info.context.user
        cls.resolve_action(user, root=root, info=info)
        return cls(success=True)

    @classmethod
    def resolve_action(cls, user, *args, **kwargs):
        raise NotImplementedError


class ArchiveAccountMixin(ArchiveOrDeleteMixin):
    """
    Archive account and revoke refresh tokens.

    User must be verified and confirm password.
    """

    @classmethod
    def resolve_action(cls, user, *args, **kwargs):
        UserStatus.archive(user)
        revoke_user_refresh_token(user=user)


class DeleteAccountMixin(ArchiveOrDeleteMixin):
    """
    Delete account permanently or make `user.is_active=False`.

    The behavior is defined on settings.
    Anyway user refresh tokens are revoked.

    User must be verified and confirm password.
    """

    @classmethod
    def resolve_action(cls, user, *args, **kwargs):
        if app_settings.ALLOW_DELETE_ACCOUNT:
            revoke_user_refresh_token(user=user)
            user.delete()
        else:
            user.is_active = False
            user.save(update_fields=["is_active"])
            revoke_user_refresh_token(user=user)


class PasswordChangeMixin(SuccessErrorsOutput):
    """
    Change account password when user knows the old password.

    A new token and refresh token are sent. User must be verified.
    """

    token = graphene.Field(graphene.String)
    if using_refresh_tokens():
        refresh_token = graphene.Field(graphene.String)

    form = PasswordChangeForm

    @classmethod
    @token_auth
    def login_on_password_change(cls, root, info, **kwargs):
        return cls()

    @classmethod
    @verification_required
    @password_confirmation_required
    def resolve_mutation(cls, root, info, **kwargs):
        user = info.context.user
        f = cls.form(user, kwargs)
        if f.is_valid():
            revoke_user_refresh_token(user)
            user = f.save()
            payload = cls.login_on_password_change(
                root,
                info,
                password=kwargs.get("new_password1"),
                **{user.USERNAME_FIELD: getattr(user, user.USERNAME_FIELD)}  # type: ignore
            )
            return_value = {}
            for field in cls._meta.fields:  # type: ignore
                return_value[field] = getattr(payload, field)
            return cls(**return_value)
        else:
            return cls(success=False, errors=f.errors)


class UpdateAccountMixin(SuccessErrorsOutput):
    """
    Update user model fields, defined on settings.

    User must be verified.
    """

    form = UpdateAccountForm

    @classmethod
    @verification_required
    def resolve_mutation(cls, root, info, **kwargs):
        user = info.context.user
        fields = cls.form.Meta.fields
        for field in fields:
            if field not in kwargs:
                kwargs[field] = getattr(user, field)
        f = cls.form(kwargs, instance=user)
        if f.is_valid():
            f.save()
            return cls(success=True)
        return cls(success=False, errors=f.errors)


class VerifyOrRefreshOrRevokeTokenMixin(SuccessErrorsOutput):
    """
    Same as `grapgql_jwt` implementation,
    with change exception error message from "Error decoding signature" to "Invalid token.".
    """

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        try:
            return cls.parent_resolve(root, info, **kwargs)  # type: ignore
        except JSONWebTokenExpired:
            return cls(success=False, errors=Messages.EXPIRED_TOKEN)
        except JSONWebTokenError as e:
            if str(e).endswith('expired'):
                return cls(success=False, errors=Messages.EXPIRED_TOKEN)
            return cls(success=False, errors=Messages.INVALID_TOKEN)


class SendSecondaryEmailActivationMixin(SuccessErrorsOutput):
    """
    Send activation to secondary email.

    User must be verified and confirm password.
    """

    @classmethod
    @verification_required
    @password_confirmation_required
    def resolve_mutation(cls, root, info, **kwargs):
        try:
            email = kwargs.get("email")
            f = EmailForm({"email": email})
            if f.is_valid():
                user = info.context.user
                if async_email_func:
                    async_email_func(user.status.send_secondary_email_activation, (info, email))
                else:
                    user.status.send_secondary_email_activation(info, email)
                return cls(success=True)
            return cls(success=False, errors=f.errors)
        except EmailAlreadyInUseError:
            return cls(success=False, errors=Messages.EMAIL_IN_USE)
        except SMTPException:
            return cls(success=False, errors=Messages.EMAIL_FAIL)


class SwapEmailsMixin(SuccessErrorsOutput):
    """
    Swap between primary and secondary emails.

    Require password confirmation.
    """

    @classmethod
    @secondary_email_required
    @password_confirmation_required
    def resolve_mutation(cls, root, info, **kwargs):
        info.context.user.status.swap_emails()
        return cls(success=True)


class RemoveSecondaryEmailMixin(SuccessErrorsOutput):
    """
    Remove user secondary email.

    Require password confirmation.
    """

    @classmethod
    @secondary_email_required
    @password_confirmation_required
    def resolve_mutation(cls, root, info, **kwargs):
        info.context.user.status.remove_secondary_email()
        return cls(success=True)
