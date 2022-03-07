from graphene_sqlalchemy import SQLAlchemyObjectType

from models import *


class UserQuery(SQLAlchemyObjectType):
    class Meta:
        model = User
        # use `only_fields` to only expose specific fields ie "name"
        # only_fields = ("name",)
        # use `exclude_fields` to exclude specific fields ie "last_name"
        exclude_fields = ("password",)


class DemoQuery(SQLAlchemyObjectType):
    class Meta:
        model = Demo
