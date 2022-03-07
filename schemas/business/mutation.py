import graphene
from flask_jwt_extended import get_jwt_identity

from models import *
from utils.tool import exceptions


class CreateUser(graphene.Mutation):
    result = graphene.String()

    class Arguments:
        email = graphene.String()
        phone = graphene.String()
        account = graphene.String()
        username = graphene.String()
        password = graphene.String()
        valid = graphene.Boolean()

    @exceptions()
    def mutate(self, info, email, phone, account, username, password, valid=True):
        """
        Demo:
        http://127.0.0.1:5000/api/v1/graphql?query=mutation Mutation {
            createUser(email:"test@test.cn",
                        phone:"110",
                        account: "dunnizike",
                        username: "卢甘斯克",
                        password:"ahahaha") {
                result
            }
        }
        """
        if uid := User.create(email=email,
                              phone=phone,
                              account=account,
                              username=username,
                              password=User.generate_hash(password),
                              valid=valid):
            return CreateUser(result=uid)
        else:
            return CreateUser(result="创建失败")


class UpdateUser(graphene.Mutation):
    result = graphene.Boolean()

    class Arguments:
        uid = graphene.ID()
        email = graphene.String()
        phone = graphene.String()
        account = graphene.String()
        username = graphene.String()
        password = graphene.String()
        valid = graphene.Boolean()

    @exceptions()
    def mutate(self, info, uid, email=None, phone=None, account=None, username=None, password=None, valid=None):
        """
        Demo:
        http://127.0.0.1:5000/api/v1/graphql?query=mutation Mutation {
            updateUser(uid:"AXELknl5-oNrn9khWHGZwSuxl32m1e7y",
                        account: "lugansike") {
                result
            }
        }
        """
        params = {}
        if email:
            params['email'] = email
        if phone:
            params['phone'] = phone
        if account:
            params['account'] = account
        if username:
            params['username'] = username
        if password:
            params['password'] = password
        if valid:
            params['valid'] = valid
        if params:
            return UpdateUser(result=User.update(uid, params))
        else:
            return UpdateUser(result=True)


class CreateDemo(graphene.Mutation):
    result = graphene.String()

    class Arguments:
        name = graphene.String()
        plugin = graphene.JSONString()

    @exceptions()
    def mutate(self, info, name, plugin=None):
        params = {"name": name, "uid": get_jwt_identity()}
        if plugin:
            params["plugin"] = plugin
        if cid := Demo.create(**params):
            return CreateDemo(result=cid)
        else:
            return CreateDemo(result="创建失败")


class UpdateDemo(graphene.Mutation):
    result = graphene.Boolean()

    class Arguments:
        cid = graphene.ID()
        name = graphene.String()
        plugin = graphene.JSONString()

    @exceptions()
    def mutate(self, info, rid, name=None, plugin=None):
        params = {}
        if name:
            params["name"] = name
        if plugin:
            params["plugin"] = plugin
        if params:
            return UpdateDemo(result=Demo.update(rid, params))
        else:
            return UpdateDemo(result=True)
