from functools import wraps

from flask import make_response, jsonify, request
from sqlalchemy import select, func, asc, desc

from enums import *
from models import *
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


def sql_list(target, parser, args=None):
    """
    对全部数据进行分页返回处理【真分页，根据条件执行SQL查询出对应的数据】
    :param target: ORM类定义
    :param parser: ORM类实例的序列化方法
    :param args: 查询条件
    """
    args = request.args.get
    with Session(engine) as session:
        # 这里考虑到所有的ORM类都应该继承自ModelTemplate，所以也都应该有id列
        if args:
            count = session.execute(select(func.count(target.id)).where(args)).scalar()
        else:
            count = session.execute(select(func.count(target.id))).scalar()
        page = int(args('page', 0))
        limit = int(args('limit', 10))
        pagination = {"page": page, "total": count, 'limit': limit}
        if args:
            sql = select(target).where(args).offset((page - 1) * limit).limit(limit)
        else:
            sql = select(target).offset((page - 1) * limit).limit(limit)
        if order_key := args('order_by', None):
            sql = sql.order_by(asc(order_key) if args('order', 'asc') == 'asc' else desc(order_key))
        result = session.execute(sql).scalars().all()
        return response(ResponseEnum.SUCCESS_200,
                        data=[parser(data) for data in result],
                        pagination=pagination)


def data_list(data: list):
    """
    对全部数据进行分页返回处理【假分页，data为全部数据】
    :param data: 全部数据
    """
    args = request.args.get
    page = int(args('page', 0))
    limit = int(args('limit', 10))
    pagination = {"page": page, "total": len(data), 'limit': limit}
    if (filter_by := args('filter_by', None)) and (filter_value := args('filter', None)):
        if args('fuzzy', None) == 'true':
            data = list(filter(lambda d: d.get(filter_by, '').find(filter_value) > -1, data))
        else:
            data = list(filter(lambda d: str(d.get(filter_by, '')) == str(filter_value), data))
    if order_key := args('order_by', None):
        data.sort(key=lambda d: d.get(order_key, 0), reverse=args('order', 'asc') != 'asc')
    pagination["filtered"] = len(data)
    return response(ResponseEnum.SUCCESS_200,
                    data=data[(page - 1) * limit:page * limit] if page > 0 else data,
                    pagination=pagination)
