"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : app.py
Author      : jinming.yang
Description : 程序的入口位置，通过该文件启动app程序
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import asyncio

from flask import Flask
from flask_cors import CORS  # 解决前后端联调的跨域问题
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import verify_jwt_in_request
from hypercorn.asyncio import serve
from hypercorn.config import Config
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.exceptions import NotFound

import config
from apis import *
from utils import JSONExtensionEncoder
from utils import logger

jwt = JWTManager()
cors = CORS()


def create_app():
    flask_app = Flask(__name__)
    flask_app.json_encoder = JSONExtensionEncoder
    c = {k: v for k, v in config.__dict__.items() if not k.startswith('_')}
    flask_app.config.update(c)
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
                return response(403, msg='未授权进行该操作')
            request.uid = uid
        except Exception as ex:
            logger.exception(ex)
            return response(401, msg='认证失效')

    @flask_app.errorhandler(NotFound)
    def handle_path_error(_):
        logger.debug(f'未定义的地址：{request.base_url}')
        return response(404, msg='请求地址错误')

    @flask_app.errorhandler(MethodNotAllowed)
    def handle_method_error(_):
        logger.debug(f'未定义的地址：{request.base_url}，方法：{request.method}')
        return response(404, msg='请求方法错误')


if __name__ == '__main__':  # Debug时使用该方法
    app_config = Config()
    app_config.bind = ["0.0.0.0:5000"]

    asyncio.run(serve(create_app(), app_config))  # 启动服务器
