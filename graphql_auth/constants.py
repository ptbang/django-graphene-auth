from django.utils.translation import gettext as _


class Messages:
    INVALID_PASSWORD = {"message": _("Invalid password."), "code": "invalid_password"}
    UNAUTHENTICATED = {"message": _("Unauthenticated."), "code": "unauthenticated"}
    INVALID_TOKEN = {"message": _("Invalid token."), "code": "invalid_token"}
    EXPIRED_TOKEN = {"message": _("Expired token."), "code": "expired_token"}
    ALREADY_VERIFIED = {"message": _("Account already verified."), "code": "already_verified"}
    EMAIL_FAIL = {"message": _("Failed to send email."), "code": "email_fail"}
    INVALID_CREDENTIALS = {
        "message": _("Please, enter valid credentials."),
        "code": "invalid_credentials",
    }
    NOT_VERIFIED = {"message": _("Please verify your account."), "code": "not_verified"}
    NOT_VERIFIED_PASSWORD_RESET = {
        "message": _("Verify your account first. A new verification email was sent."),
        "code": "not_verified",
    }
    EMAIL_IN_USE = {"email": _("A user with that email already exists."), "code": "email_in_use"}
    SECONDARY_EMAIL_REQUIRED = {
        "message": _("You need to setup a secondary email to proceed."),
        "code": "secondary_email_required",
    }
    PASSWORD_ALREADY_SET = {
        "message": _("Password already set for account."),
        "code": "password_already_set",
    }
    INVALID_REGISTRATION_DATA_MESSAGE = _("Invalid registration data.")
    FAILED_SENDING_ACTIVATION_EMAIL = {
        'message': _("User account created but could not send activation email."),
        'code': 'send_activation_email_failed',
    }
    FAILED_PASSWORD_CHANGE_MESSAGE = _("Password change failed.")
    INVALID_EMAIL_ADDRESS_MESSAGE = _("Invalid email address.")


class TokenAction(object):
    ACTIVATION = "activation"
    PASSWORD_RESET = "password_reset"
    ACTIVATION_SECONDARY_EMAIL = "activation_secondary_email"
    PASSWORD_SET = "password_set"
