"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : app.py
Author      : jinming.yang
Description : 程序的入口位置，通过该文件启动app程序
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from time import time
from uuid import uuid4

from flask import Flask
from flask import Response
from flask_cors import CORS  # 解决前后端联调的跨域问题
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import verify_jwt_in_request
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.exceptions import NotFound

from apis import *
from enums import *
from models import ApiRequestLogs
from utils import ExtensionJSONEncoder
from utils import logger

jwt = JWTManager()
cors = CORS()


def create_app():
    flask_app = Flask(__name__)
    flask_app.json_encoder = ExtensionJSONEncoder
    flask_app.config.update({
        'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY', 'flaskcli'),
        'JWT_ACCESS_TOKEN_EXPIRES': int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400 * 7)),
        'JWT_REFRESH_TOKEN_EXPIRES': int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 86400 * 30)),
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
    """
    注册生命周期函数以及其他错误捕捉函数
    Args:
        flask_app: flask程序

    Returns:
        None
    """

    @flask_app.before_request
    def authentication():
        """
        接口进行响应前的钩子函数：进行统一的接口鉴权
        Returns:
            None
        """
        request.started_at = time()
        # 1.无需鉴权的接口直接返回
        if SKIP_AUTH_REGEX.match(request.path):
            request.uid = None
            return None
        # 2.对接口进行鉴权
        try:
            _ = verify_jwt_in_request()
            if (uid := get_jwt_identity()) is None:
                return response(RespEnum.Forbidden)
            request.uid = uid
        except Exception as ex:
            logger.error(ex)
            return response(RespEnum.UnAuthorized)

    @flask_app.after_request
    def log_record(resp: Response):
        """
        接口进行响应后的钩子函数：进行日志的记录
        Args:
            resp: 接口的响应

        Returns:
            None
        """
        try:
            _ = verify_jwt_in_request()
            sql = insert(ApiRequestLogs).values({
                'id': str(uuid4()),
                'user_id': get_jwt_identity(),
                'created_at': datetime.fromtimestamp(int(time())),
                'method': request.method,
                'blueprint': request.blueprint,
                'uri': request.path,
                'status': resp.status_code,
                'duration': int((time() - request.started_at) * 1000),
                'source_ip': request.remote_addr,
            })
            execute_sql(sql)
            # log = ApiRequestLogs()
            # log.user_id = get_jwt_identity()
            # log.created_at = int(time())
            # log.method = request.method
            # log.blueprint = request.blueprint
            # log.uri = request.path
            # log.status = resp.status_code
            # log.duration = int((time() - request.started_at) * 1000)
            # log.source_ip = request.remote_addr
            # kafka.produce(Constants.Topic_ReqLogs, log.json())  # WARNING！！！ 频率低就直接flush，频率高避免性能影响可以单独开一个线程定时flush
        finally:
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
        logger.error(e)
        return response(RespEnum.DBError)

    @flask_app.errorhandler(Exception)
    def handle_exception(e: Exception):
        logger.error(e)
        return response(RespEnum.Error)


app = create_app()
if __name__ == '__main__':  # Debug时使用该方法
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
