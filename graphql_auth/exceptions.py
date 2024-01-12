from typing import Any, Collection

from django.utils.translation import gettext as _
from graphql import GraphQLError, GraphQLErrorExtensions
from graphql.language.ast import Node
from graphql.language.source import Source

from graphql_auth.constants import Messages


class GraphQLAuthError(GraphQLError):
    default_message: str = _('Not described message.')
    _extensions: dict[str, Any] = {}

    def __init__(
        self,
        message: str | None = None,
        nodes: Collection[Node] | Node | None = None,
        source: Source | None = None,
        positions: Collection[int] | None = None,
        path: Collection[str | int] | None = None,
        original_error: Exception | None = None,
        extensions: GraphQLErrorExtensions | None = None,
    ) -> None:
        if message is None:
            message = self.default_message
        if not extensions and self._extensions:
            extensions = self._extensions
        super().__init__(message, nodes, source, positions, path, original_error, extensions)


class UserAlreadyVerifiedError(GraphQLAuthError):
    default_message = Messages.ALREADY_VERIFIED['message']
    _extensions = Messages.ALREADY_VERIFIED


class InvalidCredentialsError(GraphQLAuthError):
    default_message = _("Invalid credentials.")
    _extensions = Messages.INVALID_CREDENTIALS


class UserNotVerifiedError(GraphQLAuthError):
    default_message = _("User is not verified.")
    _extensions = Messages.NOT_VERIFIED


class EmailAlreadyInUseError(GraphQLAuthError):
    default_message = _("This email is already in use.")
    _extensions = Messages.EMAIL_IN_USE


class TokenScopeError(GraphQLAuthError):
    default_message = _("This token if for something else.")


class PasswordAlreadySetError(GraphQLAuthError):
    default_message = Messages.PASSWORD_ALREADY_SET['message']
    _extensions = Messages.PASSWORD_ALREADY_SET


class WrongUsageError(GraphQLAuthError):
    """internal exception"""

    default_message = _("Wrong usage, check your code!.")


class InvalidEmailAddressError(GraphQLAuthError):
    default_message = _('Invalid email address')
    _extensions = {'message': default_message, 'code': 'invalid-email-address'}
