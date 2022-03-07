from functools import wraps

from flask import make_response, jsonify, request

from enums import *
from utils import logger
from utils.tool import is_simple_data, to_dict


def format_json(js):
    """
    将常规JSON转换成Name:Value格式的前端JSON
    """
    result = None
    if js is not None:
        if isinstance(js, list):
            result = [format_json(item) for item in js]
        elif isinstance(js, dict):
            result = [{"name": k, "value": format_json(v)} for k, v in js.items()]
        elif is_simple_data(js):
            result = js
        else:
            result = {}
            if hasattr(js, '__slots__'):
                for name in js.__slots__:
                    if hasattr(js, name):
                        result[name] = to_dict(getattr(js, name))
            elif hasattr(js, '__dict__'):
                for name in js.__dict__:
                    if hasattr(js, name):
                        result[name] = to_dict(getattr(js, name))
    return result


def response(base_response: ResponseEnum, data=None, msg: str = None, pagination: dict = None):
    """
    统一的API响应方法
    :param base_response: 基础响应信息，本次API响应状态
    :param data: 响应内容，默认为None
    :param msg: 响应消息，默认为None
    :param pagination: 分页信息
    :return:[any]
    """
    base_response = base_response.value
    result = {'status': base_response['status'], 'data': data, 'msg': msg or base_response['msg']}
    if pagination is not None:
        result['pagination'] = pagination
    return make_response(jsonify(result), base_response['code'], {'Access-Control-Allow-Origin': '*', 'server': 'CSPM Service'})


def api_wrapper(requires: set = None):
    """
    装饰器：处理API响应异常以及必要参数的校验
    :param requires:当前接口的请求体中必须包含的字段，如果只需要传参数但不强制则传空列表
    :return:[any/SERVER_EXCEPTION_500]无异常则返回方法的返回值，异常返回SERVER_EXCEPTION_500
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                params = None
                if requires is not None:  # 参数获取
                    params = dict(request.args) if request.method in ('GET', 'DELETE') else request.json
                    if missed := requires - set(params.keys()):
                        return response(ResponseEnum.MISSING_PARAMETERS_422, msg=f'缺失{missed}')
                kwargs['params'] = params
                return func(*args, **kwargs)
            except Exception as ex:
                logger.exception(ex, module=func.__module__, func=func.__name__)
                return response(ResponseEnum.SERVER_ERROR_500, msg=f'{ex}')

        return wrapper

    return decorator
