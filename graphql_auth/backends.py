from graphql_jwt.backends import JSONWebTokenBackend
from graphql_jwt.exceptions import JSONWebTokenError
from graphql_jwt.shortcuts import get_user_by_token
from graphql_jwt.utils import get_credentials


class GraphQLAuthBackend(JSONWebTokenBackend):
    """
    Only difference from the original backend
    is it does not raise when fail on get_user_by_token
    preventing of raise when client send token to a
    mutation that does not re-query login but is not on
    allow any settings.

    Main advantage is to let the mutation handle the
    authentication error.
    """

    def authenticate(self, request=None, **kwargs):
        if request is None or getattr(request, "_jwt_token_auth", False):
            return None

        token = get_credentials(request, **kwargs)

        try:  # +++
            if token is not None:
                return get_user_by_token(token, request)
        except JSONWebTokenError:  # +++
            pass  # +++

        return None
