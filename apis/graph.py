import graphene
from flask import Blueprint
from flask_graphql import GraphQLView
from flask_jwt_extended import get_jwt_identity

from models import *
from schemas import *
from utils.tool import exceptions

bp = Blueprint("graphql", __name__)


class GeneralDelete(graphene.Mutation):
    result = graphene.Boolean()

    class Arguments:
        target = graphene.String()  # 数据库ORM类的名称
        target_id = graphene.String()  # ORM类实例ID

    @exceptions()
    def mutate(self, info, target, target_id):
        return GeneralDelete(result=eval(f"{target}.delete(id)"))


class GraphQuery(graphene.ObjectType):
    """
    用于实现GraphQL对数据的查询操作
    仅提供入口点，其他信息通过入口点字段关联获取
    """
    user = graphene.Field(UserQuery)
    reports = graphene.Field(ReportQuery)
    report = graphene.Field(ReportQuery, rid=graphene.String())

    def resolve_user(self, info):
        uid = get_jwt_identity()
        query = UserQuery.get_query(info)  # SQLAlchemy query
        return query.filter(User.id == uid).first()

    def resolve_reports(self, info):
        uid = get_jwt_identity()
        query = ReportQuery.get_query(info)  # SQLAlchemy query
        return query.filter(Report.uid == uid).all()

    def resolve_report(self, info, rid):
        query = ReportQuery.get_query(info)  # SQLAlchemy query
        return query.filter(Report.id == rid).first()


class GraphMutation(graphene.ObjectType):
    """
    用于实现GraphQL对数据的变更操作
    """
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    create_credential = CreateCredential.Field()
    update_credential = UpdateCredential.Field()
    create_plugin = CreatePlugin.Field()
    update_plugin = UpdatePlugin.Field()
    create_region = CreateRegion.Field()
    update_region = UpdateRegion.Field()
    create_service = CreateService.Field()
    update_service = UpdateService.Field()
    delete = GeneralDelete.Field()


schema = graphene.Schema(query=GraphQuery, mutation=GraphMutation)
bp.add_url_rule("", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))
