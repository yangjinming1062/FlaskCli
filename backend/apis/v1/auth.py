from io import BytesIO

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from ..common import *

bp = get_blueprint(__name__, '鉴权登陆')


@bp.route('/login', methods=['POST'])
@api_wrapper(
    request_param=ParamDefine({
        'account': ParamDefine(str, True, '账号'),
        'password': ParamDefine(str, True, '密码'),
        'random': ParamDefine(str, True, '生成验证码的随机数'),
        'captcha': ParamDefine(str, True, '验证码')
    }, True),
    response_param=ParamDefine({
        'username': ParamDefine(str, True),
        'role': ParamDefine(RoleEnum, True),
        'access_token': ParamDefine(str, True),
        'refresh_token': ParamDefine(str, True),
    }, True),
)
def post_login(**kwargs):
    """
    登陆
    """
    if captcha := Redis.get(f'captcha:{kwargs["random"]}'):
        if captcha == kwargs['captcha'].lower():
            if user := execute_sql(select(User).where(User.account == kwargs['account']), many=False):
                if user.check_password(kwargs['password']):
                    return {
                        'username': user.username,
                        'role': user.role,
                        'access_token': create_access_token(identity=user.id),
                        'refresh_token': create_refresh_token(user.id),
                    }
            raise APIErrorResponse(403, '用户名或密码错误')
    raise APIErrorResponse(403, '验证码错误')


@bp.route('/captcha', methods=['GET'])
@api_wrapper(
    request_param=ParamDefine({
        'random': ParamDefine(str, True, '随机数'),
    }, True),
    response_param=ParamDefine(Any, True, '返回Content-Type为image/png的图片数据'),
    response_header=ParamDefine({'Content-Type': 'image/png'})
)
def get_captcha(**kwargs):
    """
    获取验证码
    """
    img, code = ImageCode().draw_verify_code()
    with BytesIO() as imgio:
        img.save(imgio, 'png')
        Redis.set(f'captcha:{kwargs["random"]}', code.lower(), ex=300)
        return imgio.getvalue()


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@api_wrapper(
    response_param=ParamDefine({'access_token': ParamDefine(str, True)}),
)
def post_refresh(**kwargs):
    """
    利用refresh token获取新的access token
    """
    return {'access_token': create_access_token(identity=get_jwt_identity())}
