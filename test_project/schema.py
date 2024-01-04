import graphene

from graphql_auth.queries import UserQuery, MeQuery
from graphql_auth import mutations, relay


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    resend_activation_email = mutations.ResendActivationEmail.Field()
    send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    password_reset = mutations.PasswordReset.Field()
    password_set = mutations.PasswordSet.Field()
    archive_account = mutations.ArchiveAccount.Field()
    delete_account = mutations.DeleteAccount.Field()
    password_change = mutations.PasswordChange.Field()
    update_account = mutations.UpdateAccount.Field()
    send_secondary_email_activation = mutations.SendSecondaryEmailActivation.Field()
    verify_secondary_email = mutations.VerifySecondaryEmail.Field()
    swap_emails = mutations.SwapEmails.Field()
    remove_secondary_email = mutations.RemoveSecondaryEmail.Field()

    token_auth = mutations.ObtainJSONWebToken.Field()
    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()

class AuthRelayMutation(graphene.ObjectType):
    relay_register = relay.Register.Field()
    relay_verify_account = relay.VerifyAccount.Field()
    relay_resend_activation_email = relay.ResendActivationEmail.Field()
    relay_send_password_reset_email = relay.SendPasswordResetEmail.Field()
    relay_password_reset = relay.PasswordReset.Field()
    relay_password_set = relay.PasswordSet.Field()
    relay_archive_account = relay.ArchiveAccount.Field()
    relay_delete_account = relay.DeleteAccount.Field()
    relay_password_change = relay.PasswordChange.Field()
    relay_update_account = relay.UpdateAccount.Field()
    relay_send_secondary_email_activation = relay.SendSecondaryEmailActivation.Field()
    relay_verify_secondary_email = relay.VerifySecondaryEmail.Field()
    relay_swap_emails = relay.SwapEmails.Field()
    relay_remove_secondary_email = relay.RemoveSecondaryEmail.Field()

    relay_token_auth = relay.ObtainJSONWebToken.Field()
    relay_verify_token = relay.VerifyToken.Field()
    relay_refresh_token = relay.RefreshToken.Field()
    relay_revoke_token = relay.RevokeToken.Field()


class Query(UserQuery, MeQuery):
    pass


class Mutation(AuthMutation, AuthRelayMutation):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
