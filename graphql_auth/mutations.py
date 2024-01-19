import graphene
import graphql_jwt
from graphene.types.generic import GenericScalar
from graphql_jwt.mixins import JSONWebTokenMixin
from graphql_jwt.settings import jwt_settings

from .bases import DynamicArgsMixin, MutationMixin
from .mixins import (
    ArchiveAccountMixin,
    DeleteAccountMixin,
    ObtainJSONWebTokenMixin,
    PasswordChangeMixin,
    PasswordResetMixin,
    PasswordSetMixin,
    RegisterMixin,
    RemoveSecondaryEmailMixin,
    ResendActivationEmailMixin,
    SendPasswordResetEmailMixin,
    SendSecondaryEmailActivationMixin,
    SwapEmailsMixin,
    UpdateAccountMixin,
    VerifyAccountMixin,
    VerifyOrRefreshOrRevokeTokenMixin,
    VerifySecondaryEmailMixin,
)
from .settings import graphql_auth_settings as app_settings
from .utils import normalize_fields


class Register(MutationMixin, DynamicArgsMixin, RegisterMixin, graphene.Mutation):
    _required_args = normalize_fields(
        app_settings.REGISTER_MUTATION_FIELDS,
        [] if app_settings.ALLOW_PASSWORDLESS_REGISTRATION else ["password1", "password2"],
    )
    _args = app_settings.REGISTER_MUTATION_FIELDS_OPTIONAL
    __doc__ = RegisterMixin.__doc__


class VerifyAccount(MutationMixin, DynamicArgsMixin, VerifyAccountMixin, graphene.Mutation):
    _required_args = ["token"]
    __doc__ = VerifyAccountMixin.__doc__


class ResendActivationEmail(MutationMixin, DynamicArgsMixin, ResendActivationEmailMixin, graphene.Mutation):
    _required_args = ["email"]
    __doc__ = ResendActivationEmailMixin.__doc__


class SendPasswordResetEmail(MutationMixin, DynamicArgsMixin, SendPasswordResetEmailMixin, graphene.Mutation):
    _required_args = ["email"]
    __doc__ = SendPasswordResetEmailMixin.__doc__


class SendSecondaryEmailActivation(
    MutationMixin, DynamicArgsMixin, SendSecondaryEmailActivationMixin, graphene.Mutation
):
    _required_args = ["email", "password"]
    __doc__ = SendSecondaryEmailActivationMixin.__doc__


class VerifySecondaryEmail(MutationMixin, DynamicArgsMixin, VerifySecondaryEmailMixin, graphene.Mutation):
    _required_args = ["token"]
    __doc__ = VerifySecondaryEmailMixin.__doc__


class SwapEmails(MutationMixin, DynamicArgsMixin, SwapEmailsMixin, graphene.Mutation):
    _required_args = ["password"]
    __doc__ = SwapEmailsMixin.__doc__


class RemoveSecondaryEmail(MutationMixin, DynamicArgsMixin, RemoveSecondaryEmailMixin, graphene.Mutation):
    _required_args = ["password"]
    __doc__ = RemoveSecondaryEmailMixin.__doc__


class PasswordSet(MutationMixin, PasswordSetMixin, DynamicArgsMixin, graphene.Mutation):
    _required_args = ["token", "new_password1", "new_password2"]
    __doc__ = PasswordSetMixin.__doc__


class PasswordReset(MutationMixin, DynamicArgsMixin, PasswordResetMixin, graphene.Mutation):
    _required_args = ["token", "new_password1", "new_password2"]
    __doc__ = PasswordResetMixin.__doc__


class ObtainJSONWebToken(MutationMixin, ObtainJSONWebTokenMixin, graphql_jwt.JSONWebTokenMutation):
    __doc__ = ObtainJSONWebTokenMixin.__doc__

    @classmethod
    def Field(cls, *args, **kwargs):
        cls._meta.arguments.update({"password": graphene.String(required=True)})
        for field in app_settings.LOGIN_ALLOWED_FIELDS:
            cls._meta.arguments.update({field: graphene.String()})
        if not jwt_settings.JWT_HIDE_TOKEN_FIELDS:
            cls._meta.fields['token'] = graphene.Field(graphene.String, required=False)
            if jwt_settings.JWT_LONG_RUNNING_REFRESH_TOKEN:
                cls._meta.fields['refresh_token'] = graphene.Field(graphene.String, required=False)
        return super(JSONWebTokenMixin, cls).Field(*args, **kwargs)


class ArchiveAccount(MutationMixin, ArchiveAccountMixin, DynamicArgsMixin, graphene.Mutation):
    _required_args = ["password"]
    __doc__ = ArchiveAccountMixin.__doc__


class DeleteAccount(MutationMixin, DeleteAccountMixin, DynamicArgsMixin, graphene.Mutation):
    _required_args = ["password"]
    __doc__ = DeleteAccountMixin.__doc__


class PasswordChange(MutationMixin, PasswordChangeMixin, DynamicArgsMixin, graphene.Mutation):
    _required_args = ["old_password", "new_password1", "new_password2"]
    __doc__ = PasswordChangeMixin.__doc__


class UpdateAccount(MutationMixin, DynamicArgsMixin, UpdateAccountMixin, graphene.Mutation):
    _args = app_settings.UPDATE_MUTATION_FIELDS
    __doc__ = UpdateAccountMixin.__doc__


class VerifyToken(MutationMixin, VerifyOrRefreshOrRevokeTokenMixin, graphql_jwt.Verify):
    payload = GenericScalar(required=False)
    __doc__ = VerifyOrRefreshOrRevokeTokenMixin.__doc__


class RefreshToken(MutationMixin, VerifyOrRefreshOrRevokeTokenMixin, graphql_jwt.Refresh):
    payload = GenericScalar(required=False)
    refresh_expires_in = graphene.Int()
    __doc__ = VerifyOrRefreshOrRevokeTokenMixin.__doc__

    @classmethod
    def Field(cls, *args, **kwargs):
        if not jwt_settings.JWT_HIDE_TOKEN_FIELDS:
            cls._meta.fields["token"] = graphene.Field(graphene.String, required=False)

            if jwt_settings.JWT_LONG_RUNNING_REFRESH_TOKEN:
                cls._meta.fields["refresh_token"] = graphene.Field(graphene.String, required=False)

        return super(JSONWebTokenMixin, cls).Field(*args, **kwargs)  # type: ignore


class RevokeToken(MutationMixin, VerifyOrRefreshOrRevokeTokenMixin, graphql_jwt.Revoke):
    revoked = graphene.Int(required=False)
    __doc__ = VerifyOrRefreshOrRevokeTokenMixin.__doc__
