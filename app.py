from flask import Flask, request
from flask.json import JSONEncoder
from flask_cors import CORS  # 解决前后端联调的跨域问题
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity

import config
from apis import *
from enums import Enum, ResponseEnum
from models import ModelBase, engine, User
from utils import logger
from utils.api import response

jwt = JWTManager()
cors = CORS()


class ExtensionJSONEncoder(JSONEncoder):
    """
    处理枚举等各种无法JSON序列化的类型
    """

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super(ExtensionJSONEncoder, self).default(obj)


def create_app():
    flask_app = Flask(__name__)
    flask_app.json_encoder = ExtensionJSONEncoder
    flask_app.config.update({
        "JWT_SECRET_KEY": 'cloud',
        "JWT_BLACKLIST_ENABLED": False,
        "JWT_COOKIE_CSRF_PROTECT": True,
        "JWT_ACCESS_TOKEN_EXPIRES": 86400 * 7,
        "JSON_AS_ASCII": False,
    })
    jwt.init_app(flask_app)
    cors.init_app(flask_app, supports_credentials=True)
    register_blueprints(flask_app)  # 注册蓝图
    register_handler(flask_app)  # 注册错误处理函数
    ModelBase.metadata.create_all(engine)
    return flask_app


def register_blueprints(flask_app):
    flask_app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    flask_app.register_blueprint(chart_bp, url_prefix='/api/v1/chart')
    flask_app.register_blueprint(function_bp, url_prefix='/api/v1/function')
    flask_app.register_blueprint(graph_bp, url_prefix='/api/v1/graphql')


def register_handler(flask_app):
    @flask_app.before_request
    def authentication():
        # 0.开发阶段可以访问GraphiQL界面进行调用以及文档查看
        if config.DEVELOP and request.path.startswith("/api/v1/graphql"):
            return None
        # 1.无需鉴权的接口直接返回
        if request.path.startswith("/api/v1/auth") or request.path.startswith("/api/v1/common"):
            return None
        # 2.对接口进行健全
        try:
            _ = verify_jwt_in_request()
        except Exception as ex:
            return response(ResponseEnum.UNAUTHORIZED_401, msg=str(ex))
        if (uid := get_jwt_identity()) is None:  # 获取token中记录的uid信息
            return response(ResponseEnum.FORBIDDEN_403)
        if (user := User.read(uid)) is None:  # 登录的token还有效，但是token内的uid已经不在来（几乎不存在，但有可能）
            return response(ResponseEnum.FORBIDDEN_403, msg='登录无效，请重新登录')

    @flask_app.errorhandler(400)
    def bad_request(e):
        logger.error(e)
        return response(ResponseEnum.BAD_REQUEST_400)

    @flask_app.errorhandler(404)
    def not_found(e):
        logger.info(f'未定义的地址：{request.base_url}')
        return response(ResponseEnum.NOT_FOUND_404, msg='API地址错误，请检查请求地址')

    @flask_app.errorhandler(500)
    def server_error(e):
        logger.error(e)
        return response(ResponseEnum.SERVER_ERROR_500)


app = create_app()
if __name__ == '__main__':  # Debug时使用该方法
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
