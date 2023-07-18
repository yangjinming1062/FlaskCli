import os
from time import time

from flask import Flask
from flask import Response
from flask import request
from flask_cors import CORS  # 解决前后端联调的跨域问题
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import verify_jwt_in_request
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.exceptions import NotFound

from apis import Blueprints
from apis import SKIP_AUTH_REGEX
from enums import RespEnum
from models import ApiRequestLogs
from models import User
from utils import Constants
from utils import ExtensionJSONEncoder
from utils import Kafka
from utils import logger
from utils.api import response

jwt = JWTManager()
cors = CORS()
kafka = Kafka()


def create_app():
    flask_app = Flask(__name__)
    flask_app.json_encoder = ExtensionJSONEncoder
    # 通过获取环境变量中的值来完善config
    flask_app.config.update({
        'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY', 'flaskcli'),
        'JWT_ACCESS_TOKEN_EXPIRES': int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)),
        'JWT_REFRESH_TOKEN_EXPIRES': int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 864000)),
        'JWT_BLACKLIST_ENABLED': False,
        'JWT_COOKIE_CSRF_PROTECT': True,
        'JSON_AS_ASCII': False,
    })
    jwt.init_app(flask_app)
    cors.init_app(flask_app, supports_credentials=True)
    for bp in Blueprints:
        # 注册蓝图，只要在apis的__init__.py中导入了即可
        flask_app.register_blueprint(bp)
    register_handler(flask_app)  # 注册错误处理函数
    return flask_app


def register_handler(flask_app):
    @flask_app.before_request
    def authentication():
        """
        接口进行响应前的钩子函数：处理鉴权、访问时间记录等逻辑

        Returns:
            None
        """
        request.start_time = time()
        # 1.无需鉴权的接口直接返回
        if SKIP_AUTH_REGEX.match(request.path):
            return None
        # 2.对接口进行鉴权
        try:
            _ = verify_jwt_in_request()
        except Exception as ex:
            logger.error(ex)
            return response(RespEnum.UnAuthorized)
        if (uid := get_jwt_identity()) is None:  # 获取token中记录的uid信息
            return response(RespEnum.Forbidden)
        # 登录的token还有效，但是token内的uid已经不在来（几乎不存在，但有可能）
        if not User.read(uid):
            return response(RespEnum.Forbidden)

    @flask_app.after_request
    def log_record(resp: Response):
        """
        接口进行响应后的钩子函数：进行日志的记录
        Args:
            resp: 接口的响应

        Returns:
            None
        """
        log = ApiRequestLogs()
        uri_list = request.path.split('/')  # 按照接口的构成反向拆出版本和蓝图信息
        try:
            _ = verify_jwt_in_request()
            log.user_id = get_jwt_identity()
        except:
            log.user_id = 'public'
        log.create_time = int(time())
        log.method = request.method
        log.version = uri_list[1] if len(uri_list) > 1 else 'unknown'
        log.blueprint = request.blueprint
        log.uri = request.path
        log.status_code = resp.status_code
        log.duration = int((time() - request.start_time) * 1000)
        log.source_ip = request.remote_addr
        log.destination_ip = request.server[0]
        kafka.produce(Constants.Topic_ReqLogs, log.json())  # WARNING！！！ 频率低就直接flush，频率高避免性能影响可以单独开一个线程定时flush
        return resp

    @flask_app.errorhandler(AssertionError)
    def handle_assertion_error(e: AssertionError):
        logger.error(e)
        return response(RespEnum.IllegalParams)

    @flask_app.errorhandler(NotFound)
    def handle_path_error(_):
        logger.info(f'未定义的地址：{request.base_url}')
        return response(RespEnum.UriNotFound)

    @flask_app.errorhandler(MethodNotAllowed)
    def handle_method_error(_):
        logger.info(f'未定义的地址：{request.base_url}，方法：{request.method}')
        return response(RespEnum.MethodNotFound)

    @flask_app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(e: SQLAlchemyError):
        logger.exception(e)
        return response(RespEnum.DBError)

    @flask_app.errorhandler(Exception)
    def handle_exception(e: Exception):
        logger.exception(e)
        return response(RespEnum.Error)


app = create_app()
if __name__ == '__main__':  # Debug时使用该方法
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
