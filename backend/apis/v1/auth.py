from io import BytesIO

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from utils import ImageCode
from utils import Redis
from ..api import *

bp = get_blueprint(__name__, '鉴权登陆')


@bp.route('/login', methods=['POST'])
@api_wrapper(
    request_param={
        '*account': ParamDefine(str, '账号'),
        '*password': ParamDefine(str, '密码'),
        '*random': ParamDefine(str, '生成验证码的随机数'),
        '*captcha': ParamDefine(str, '验证码')
    },
    response_param={
        RespEnum.OK: ParamDefine({
            '*username': ParamDefine(str),
            '*role': ParamDefine(RoleEnum),
            '*access_token': ParamDefine(str),
            '*refresh_token': ParamDefine(str),
        }),
    },
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
            raise APIException(RespEnum.WrongPassword)
    raise APIException(RespEnum.WrongCaptcha)


@bp.route('/captcha', methods=['GET'])
@api_wrapper(
    request_param={
        '*random': ParamDefine(str, '随机数'),
    },
    response_param={
        RespEnum.OK: ParamDefine(Any, '返回Content-Type为image/png的图片数据')
    },
    response_header={
        'Content-Type': 'image/png'
    }
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
    response_param={
        RespEnum.OK: ParamDefine({'*access_token': ParamDefine(str)})
    },
)
def post_refresh(**kwargs):
    """
    利用refresh token获取新的access token
    """
    return {'access_token': create_access_token(identity=get_jwt_identity())}
