from typing import Any

import graphene
from django.contrib.auth import get_user_model
from graphene_django.filter.fields import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from .connection import CountableConnection
from .settings import graphql_auth_settings as app_settings

UserModel = get_user_model()


class UserNode(DjangoObjectType):
    class Meta:
        model = UserModel
        filter_fields = app_settings.USER_NODE_FILTER_FIELDS
        exclude = app_settings.USER_NODE_EXCLUDE_FIELDS
        interfaces = (graphene.relay.Node,)
        connection_class = CountableConnection

    pk = graphene.Int()
    archived = graphene.Boolean()
    verified = graphene.Boolean()
    secondary_email = graphene.String()

    def resolve_pk(self, info):
        return self.pk

    def resolve_archived(self, info):
        return self.status.archived  # type: ignore

    def resolve_verified(self, info):
        return self.status.verified  # type: ignore

    def resolve_secondary_email(self, info):
        return self.status.secondary_email  # type: ignore

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.select_related('status')

    @classmethod
    def get_node(cls, info, id) -> Any:
        """
        Allows only staff users to access the node.
        """
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return super().get_node(info, id)
        return None


class UserQuery(graphene.ObjectType):
    user = graphene.relay.Node.Field(UserNode)
    users = DjangoFilterConnectionField(UserNode)

    def resolve_users(self, info, **kwargs):
        """
        Allows only staff users to get users list.
        """
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return UserModel.objects.all()
        return UserModel.objects.none()


class MeQuery(graphene.ObjectType):
    me = graphene.Field(UserNode)

    def resolve_me(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None
