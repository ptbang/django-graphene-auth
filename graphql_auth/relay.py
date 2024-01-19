import graphene
import graphql_jwt
from graphene.types.generic import GenericScalar
from graphql_jwt.mixins import JSONWebTokenMixin, RefreshMixin
from graphql_jwt.settings import jwt_settings

from .bases import DynamicInputMixin, RelayMutationMixin
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


class Register(RelayMutationMixin, DynamicInputMixin, RegisterMixin, graphene.ClientIDMutation):
    _required_inputs = normalize_fields(
        app_settings.REGISTER_MUTATION_FIELDS,
        [] if app_settings.ALLOW_PASSWORDLESS_REGISTRATION else ["password1", "password2"],
    )
    _inputs = app_settings.REGISTER_MUTATION_FIELDS_OPTIONAL
    __doc__ = RegisterMixin.__doc__


class VerifyAccount(RelayMutationMixin, DynamicInputMixin, VerifyAccountMixin, graphene.ClientIDMutation):
    _required_inputs = ["token"]
    __doc__ = VerifyAccountMixin.__doc__


class ResendActivationEmail(
    RelayMutationMixin, DynamicInputMixin, ResendActivationEmailMixin, graphene.ClientIDMutation
):
    _required_inputs = ["email"]
    __doc__ = ResendActivationEmailMixin.__doc__


class SendPasswordResetEmail(
    RelayMutationMixin, DynamicInputMixin, SendPasswordResetEmailMixin, graphene.ClientIDMutation
):
    _required_inputs = ["email"]
    __doc__ = SendPasswordResetEmailMixin.__doc__


class SendSecondaryEmailActivation(
    RelayMutationMixin,
    DynamicInputMixin,
    SendSecondaryEmailActivationMixin,
    graphene.ClientIDMutation,
):
    _required_inputs = ["email", "password"]
    __doc__ = SendSecondaryEmailActivationMixin.__doc__


class VerifySecondaryEmail(RelayMutationMixin, DynamicInputMixin, VerifySecondaryEmailMixin, graphene.ClientIDMutation):
    _required_inputs = ["token"]
    __doc__ = VerifySecondaryEmailMixin.__doc__


class SwapEmails(RelayMutationMixin, DynamicInputMixin, SwapEmailsMixin, graphene.ClientIDMutation):
    _required_inputs = ["password"]
    __doc__ = SwapEmailsMixin.__doc__


class RemoveSecondaryEmail(RelayMutationMixin, DynamicInputMixin, RemoveSecondaryEmailMixin, graphene.ClientIDMutation):
    _required_inputs = ["password"]
    __doc__ = RemoveSecondaryEmailMixin.__doc__


class PasswordSet(RelayMutationMixin, DynamicInputMixin, PasswordSetMixin, graphene.ClientIDMutation):
    _required_inputs = ["token", "new_password1", "new_password2"]
    __doc__ = PasswordSetMixin.__doc__


class PasswordReset(RelayMutationMixin, DynamicInputMixin, PasswordResetMixin, graphene.ClientIDMutation):
    _required_inputs = ["token", "new_password1", "new_password2"]
    __doc__ = PasswordResetMixin.__doc__


class ObtainJSONWebToken(RelayMutationMixin, ObtainJSONWebTokenMixin, graphql_jwt.relay.JSONWebTokenMutation):
    __doc__ = ObtainJSONWebTokenMixin.__doc__

    @classmethod
    def Field(cls, *args, **kwargs):
        cls._meta.arguments["input"]._meta.fields.update(
            {"password": graphene.InputField(graphene.String, required=True)}
        )
        for field in app_settings.LOGIN_ALLOWED_FIELDS:
            cls._meta.arguments["input"]._meta.fields.update({field: graphene.InputField(graphene.String)})
        if not jwt_settings.JWT_HIDE_TOKEN_FIELDS:
            cls._meta.fields['token'] = graphene.Field(graphene.String, required=False)
            if jwt_settings.JWT_LONG_RUNNING_REFRESH_TOKEN:
                cls._meta.fields['refresh_token'] = graphene.Field(graphene.String, required=False)
        return super(JSONWebTokenMixin, cls).Field(*args, **kwargs)


class ArchiveAccount(RelayMutationMixin, ArchiveAccountMixin, DynamicInputMixin, graphene.ClientIDMutation):
    _required_inputs = ["password"]
    __doc__ = ArchiveAccountMixin.__doc__


class DeleteAccount(RelayMutationMixin, DeleteAccountMixin, DynamicInputMixin, graphene.ClientIDMutation):
    _required_inputs = ["password"]
    __doc__ = DeleteAccountMixin.__doc__


class PasswordChange(RelayMutationMixin, PasswordChangeMixin, DynamicInputMixin, graphene.ClientIDMutation):
    _required_inputs = ["old_password", "new_password1", "new_password2"]
    __doc__ = PasswordChangeMixin.__doc__


class UpdateAccount(RelayMutationMixin, DynamicInputMixin, UpdateAccountMixin, graphene.ClientIDMutation):
    _inputs = app_settings.UPDATE_MUTATION_FIELDS
    __doc__ = UpdateAccountMixin.__doc__


class VerifyToken(RelayMutationMixin, VerifyOrRefreshOrRevokeTokenMixin, graphql_jwt.relay.Verify):
    payload = GenericScalar(required=False)
    __doc__ = VerifyOrRefreshOrRevokeTokenMixin.__doc__

    class Input:
        token = graphene.String(required=True)


class RefreshToken(RelayMutationMixin, VerifyOrRefreshOrRevokeTokenMixin, graphql_jwt.relay.Refresh):
    refresh_expires_in = graphene.Int()
    payload = GenericScalar(required=False)
    __doc__ = VerifyOrRefreshOrRevokeTokenMixin.__doc__

    class Input(RefreshMixin.Fields):
        """Refresh Input"""

    @classmethod
    def Field(cls, *args, **kwargs):
        if not jwt_settings.JWT_HIDE_TOKEN_FIELDS:
            cls._meta.fields["token"] = graphene.Field(graphene.String, required=False)

            if jwt_settings.JWT_LONG_RUNNING_REFRESH_TOKEN:
                cls._meta.fields["refresh_token"] = graphene.Field(graphene.String, required=False)

        return super(JSONWebTokenMixin, cls).Field(*args, **kwargs)  # type: ignore


class RevokeToken(RelayMutationMixin, VerifyOrRefreshOrRevokeTokenMixin, graphql_jwt.relay.Revoke):
    revoked = graphene.Int(required=False)
    __doc__ = VerifyOrRefreshOrRevokeTokenMixin.__doc__

    class Input:
        refresh_token = graphene.String(required=True)
