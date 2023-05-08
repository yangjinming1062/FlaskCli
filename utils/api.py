"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : api.py
Author      : jinming.yang
Description : API接口用到的工具方法实现
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from functools import wraps
from typing import Union

from flask import jsonify
from flask import request
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import select

from enums import *
from utils import execute_sql
from utils import logger


def response(base_response: ResponseEnum, data=None, msg: str = None):
    """
    统一的API响应方法
    Args:
        base_response: 基础响应信息，本次API响应状态
        data: 响应内容，默认为None
        msg: 响应消息，默认为None

    Returns:
        Response
    """
    code, status, base_msg = base_response.value
    resp = {'status': status, 'data': data, 'msg': msg or base_msg}
    return jsonify(resp), code


def api_wrapper(params: dict = None):
    """
    装饰器：统一处理API响应异常以及必要参数的校验
    Args:
        params: 当前接口包含的字段（key为字段名称，value为字段类型），如果参数为必填在在名称前添加*

    Returns:
        无异常则返回方法的返回值，异常返回Error
    """

    def decorator(func):

        def get_params():
            req_params = {}
            # GET和DELETE按照规范是使用url参数
            if request.method in ('GET', 'DELETE'):
                for key in dict(request.args).keys():
                    # 兼容多个key的情况：例如?key=value1&key=value2
                    req_params[key] = request.args.getlist(key)
                    if len(params[key]) == 1:
                        params[key] = params[key][0]
            # 其他类型请求默认是JSON参数
            else:
                req_params = request.json
            return req_params

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 如果不存在必填参数和任何参数，直接调用原函数，避免进行不必要的参数校验
                if params is None:
                    return func(*args, **kwargs)
                # 1.先获取参数
                req_params = get_params()
                # 2.提取必填参数
                requires = set()
                for key in {key for key in params.keys() if key.startswith('*')}:
                    requires.add(key[1:])
                    params[key[1:]] = params.pop(key)
                # 3.检查必填参数是否有缺失的
                if requires and (missed := requires - req_params.keys()):
                    return response(ResponseEnum.MissingParams, msg=f'缺失{missed}')
                # 4.如果不存在params则直接返回
                if not params:
                    kwargs.update(req_params)
                    return func(*args, **kwargs)
                # 5.检查是否有垃圾参数
                if junk := req_params.keys() - params.keys():
                    return response(ResponseEnum.InvalidInput, msg=f'存在非法参数{junk}')
                # 6.检查参数类型，并将对应的参数转成目标类型
                for k, t in params.items():
                    if k in req_params:
                        if t is None:
                            # None为保留情况，此时不对参数类型进行校验
                            continue
                        elif t in (list, dict):
                            # 复杂的嵌套类型暂时不做处理
                            if not isinstance(req_params[k], t):
                                return response(ResponseEnum.InvalidInput, msg=f'{k}的类型应该是{t}')
                        else:
                            try:
                                # args类型参数顺便进行类型转换
                                req_params[k] = t(req_params[k])
                            except ValueError:
                                return response(ResponseEnum.InvalidInput, msg=f'{k}的类型应该是{t}')
                kwargs.update(req_params)
                return func(*args, **kwargs)
            except Exception as ex:
                logger.exception(str(ex), module=func.__module__, func=func.__name__)
                return response(ResponseEnum.Error, msg=str(ex))

        return wrapper

    return decorator


def orm_create(cls, params: dict):
    """
    创建数据实例
    Args:
        cls: ORM类定义
        params: 参数

    Returns:
        Response
    """
    result, flag = cls.create(**params)
    return response(ResponseEnum.Created if flag else ResponseEnum.InvalidInput, result)


def orm_read(cls, resource_id: str, fields: list = None):
    """
    ORM数据查询详情
    Args:
        cls: OMR类定义
        resource_id: 资源ID
        fields: 查询指定的列

    Returns:
        Response
    """
    columns = cls.get_columns()
    if fields:
        if set(fields) - set(columns):
            return response(ResponseEnum.InvalidInput, data=columns, msg=f'请求列错误,请参考合法列名')
        else:
            columns = fields
    sql = select(*cls.to_properties(columns)).select_from(cls).where(cls.id == resource_id)
    if data := execute_sql(sql, many=False, scalar=False):
        return response(ResponseEnum.OK, data)
    else:
        return response(ResponseEnum.NotFound)


def orm_update(cls, resource_id: str, params: dict):
    """
    ORM数据的更新
    Args:
        cls: ORM类定义
        resource_id: 资源ID
        params: 更新数据

    Returns:
        Response
    """
    result, flag = cls.update(resource_id, params)
    if flag:
        return response(ResponseEnum.NoContent)
    else:
        return response(ResponseEnum.InvalidInput, msg=result)


def orm_delete(cls, resource_id: Union[str, list, set]):
    """
    删除数据实例
    Args:
        cls: ORM类定义
        resource_id:  资源ID

    Returns:
        Response
    """
    result, flag = cls.delete(resource_id)
    if flag:
        return response(ResponseEnum.NoContent)
    else:
        return response(ResponseEnum.InvalidInput, msg=result)


def orm_paginate(cls, fields: list = None) -> (list, int):
    """
    统一分分页查询操作
    Args:
        cls: 添加完where条件的SQLAlchemy的查询类
        fields: 查询特定列

    Returns:
        数据列表, 分页信息
    """
    # 先处理查询内容
    columns = set(cls.get_columns())
    if fields:
        if set(fields) - columns:
            return response(ResponseEnum.InvalidInput, data=columns, msg=f'请求列错误,请参考合法列名')
    # 构建查询SQL
    sql = select(*cls.to_property(fields or columns)).select_from(cls)
    for column in request.args.getlist('order'):
        if column not in columns:
            return response(ResponseEnum.InvalidInput, data=columns, msg=f'{column}排序无效')
        # 根据列名前面的正负号判断是正序还是倒序
        if column.startswith('-'):
            sql = sql.order_by(desc(column[1:]))
        elif column.startswith('+'):
            sql = sql.order_by(asc(column[1:]))
        else:
            return response(ResponseEnum.InvalidInput, msg=f'以+/-开头进行排序')
    return paginate_query(sql, False)


def paginate_query(sql, scalar=False):
    """
    统一分分页查询操作
    Args:
        sql:查询SQL
        scalar:是否需要scalars

    Returns:
        数据列表, 分页信息
    """
    size = request.args.get('page_size', type=int, default=20)
    if size < 1 or size > 100:
        return response(ResponseEnum.InvalidInput, msg=f'size必须是1-100')
    page = request.args.get('page', type=int, default=1)
    sql = sql.limit(size).offset((page - 1) * size)
    return execute_sql(sql, many=True, scalar=scalar)
