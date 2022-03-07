from flask import Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token

from models import User
from utils.api import *

bp = Blueprint("auth", __name__)


@bp.route('/login', methods=['POST'])
@api_wrapper(requires={'account', 'password'})
def login(**kwargs):
    data = kwargs['params']
    if (user := User.search(data['account'])) is None:
        return response(ResponseEnum.FORBIDDEN_403, msg='用户名或密码错误，请重试')
    if user.check_password(data['password']):
        return response(ResponseEnum.SUCCESS_200, {
            "username": user.username,
            "access_token": create_access_token(identity=user.id),
            "refresh_token": create_refresh_token(user.id),
        })
    else:
        return response(ResponseEnum.FORBIDDEN_403, msg='用户名或密码错误，请重试')


@bp.route('/password', methods=['POST'])
@api_wrapper(requires={'account', 'captcha'})
def password(**kwargs):
    """
    TODO：忘记密码，进行密码重置
    """
    return response(ResponseEnum.SUCCESS_200)
