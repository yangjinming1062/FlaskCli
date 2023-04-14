"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : auth.py
Author      : jinming.yang
Description : 实现和鉴权相关的API接口
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from random import random

from flask import Blueprint
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from models import *
from utils.api import *
from utils.classes import Redis
from . import version

bp = Blueprint('auth', __name__, url_prefix=f'/api/{version}/auth')


@bp.route('/login', methods=['POST'])
@api_wrapper(requires={'account', 'password'})
def post_login(**kwargs):
    data = kwargs['params']
    if (user := User.search(data['account'])) is None:
        return response(ResponseEnum.Forbidden, msg='用户名或密码错误，请重试')
    if user.check_password(data['password']):
        return response(ResponseEnum.OK, {
            'username': user.username,
            'access_token': create_access_token(identity=user.id),
            'refresh_token': create_refresh_token(user.id),
        })
    else:
        return response(ResponseEnum.Forbidden, msg='用户名或密码错误，请重试')


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def post_refresh(**kwargs):
    """
    利用refresh token获取新的access token
    """
    return response(ResponseEnum.OK, {'access_token': create_access_token(identity=get_jwt_identity())})


@bp.route('/captcha', methods=['POST'])
@api_wrapper(requires={'account', 'method'})
def post_captcha(**kwargs):
    """
    忘记密码，进行密码重置
    """
    if (user := User.search(kwargs['params']['account'])) is None:
        return response(ResponseEnum.Forbidden, msg='该账号未注册，请检查后重试')
    code = str(random())[-6:]  # 生成一个随机的6位数字
    Redis.set(user.id, code, ex=300)
    # TODO 任意合适的方式将验证码发送出去
    return response(ResponseEnum.NoContent)


@bp.route('/password', methods=['POST'])
@api_wrapper(requires={'account', 'captcha'})
def post_password(**kwargs):
    """
    密码重置
    """
    if user := User.search(kwargs['params']['account']):
        if kwargs['params']['captcha'] != Redis.read(user.id):
            return response(ResponseEnum.Forbidden, msg='验证码失效或不正确')
        result, flag = User.update(user.id, {'password': User.generate_hash(kwargs['params']['password'])})
        if flag:
            return response(ResponseEnum.OK, {
                'username': user.username,
                'access_token': create_access_token(identity=user.id),
                'refresh_token': create_refresh_token(user.id),
            })
        else:
            return response(ResponseEnum.Forbidden, msg=result)
    else:
        return response(ResponseEnum.Forbidden, msg='该账号未注册，请检查后重试')
