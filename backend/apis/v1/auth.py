"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : auth.py
Author      : jinming.yang
Description : 实现和鉴权相关的API接口
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from random import random

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from models import *
from utils.api import *
from utils.classes import Redis

bp = get_blueprint(__name__)


def search(query_value):
    sql = select(User).where(or_(User.account == query_value, User.phone == query_value, User.email == query_value))
    result, flag = execute_sql(sql, many=False)
    return result if flag else None


@bp.route('/login', methods=['POST'])
@api_wrapper(params={'*account': str, '*password': str})
def post_login(**kwargs):
    if (user := search(kwargs['account'])) is None:
        return response(RespEnum.WrongPassword)
    if user.check_password(kwargs['password']):
        return response(RespEnum.OK, {
            'username': user.username,
            'access_token': create_access_token(identity=user.id),
            'refresh_token': create_refresh_token(user.id),
        })
    else:
        return response(RespEnum.WrongPassword)


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def post_refresh(**kwargs):
    """
    利用refresh token获取新的access token
    """
    return response(RespEnum.OK, {'access_token': create_access_token(identity=get_jwt_identity())})


@bp.route('/captcha', methods=['POST'])
@api_wrapper(params={'*account': str, '*method': str})
def post_captcha(**kwargs):
    """
    忘记密码，进行密码重置
    """
    if (user := search(kwargs['account'])) is None:
        return response(RespEnum.UnRegistered)
    code = str(random())[-6:]  # 生成一个随机的6位数字
    Redis.set(user.id, code, ex=300)
    # TODO 任意合适的方式将验证码发送出去
    return response(RespEnum.NoContent)


@bp.route('/password', methods=['POST'])
@api_wrapper(params={'*account': str, '*captcha': int})
def post_password(**kwargs):
    """
    密码重置
    """
    if user := search(kwargs['account']):
        if kwargs['captcha'] != Redis.read(user.id):
            return response(RespEnum.WrongCaptcha)
        result, flag = execute_sql(update(User).where(user.id).values(password=User.generate_hash(kwargs['password'])))
        if flag:
            return response(RespEnum.OK, {
                'username': user.username,
                'access_token': create_access_token(identity=user.id),
                'refresh_token': create_refresh_token(user.id),
            })
        else:
            return response(RespEnum.ParamsValueError)
    else:
        return response(RespEnum.UnRegistered)
