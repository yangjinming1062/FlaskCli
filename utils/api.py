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
from sqlalchemy import text

from enums import *
from models import tp_public_session
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


def api_wrapper(requires: set = None):
    """
    装饰器：统一处理API响应异常以及必要参数的校验
    Args:
        requires: 当前接口的请求体中必须包含的字段，如果只需要传参数但不强制则传空集合

    Returns:
        无异常则返回方法的返回值，异常返回Error
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                params = {}
                if requires is not None:  # 参数获取
                    # GET和DELETE按照规范是使用url参数
                    if request.method in ('GET', 'DELETE'):
                        for key in dict(request.args).keys():
                            params[key] = request.args.get(key)
                            if len(params[key]) == 1:
                                # 兼容多个key的情况：例如?key=value1&key=value2
                                params[key] = params[key][0]
                    else:
                        params = request.json
                    if missed := requires - set(params.keys()):
                        return response(ResponseEnum.MissingParams, msg=f'缺失{missed}')
                kwargs['params'] = params
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


def orm_delete(cls, resource_id: Union[str, list]):
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


def orm_query(cls, resource_id: str, fields: list = None):
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
    if fields and set(fields) - set(columns):
        return response(ResponseEnum.InvalidInput, data=columns, msg=f'请求列错误,请参考合法列名')
    sql = select(text(f"{','.join(fields)}")).where(cls.id.in_(resource_id))
    if data := execute_sql(sql, tp_public_session, expect_list=False):
        return response(ResponseEnum.OK, data)
    else:
        return response(ResponseEnum.NotFound)


def paginate_query(cls, fields: list = None) -> (list, int):
    """
    统一分分页查询操作
    Args:
        cls: 添加完where条件的SQLAlchemy的查询类
        fields: 查询特定列

    Returns:
        数据列表, 分页信息
    """
    # 1.先处理查询内容
    columns = cls.get_columns()
    if fields:
        if set(fields) - set(columns):
            return response(ResponseEnum.InvalidInput, data=columns, msg=f'请求列错误,请参考合法列名')
    else:
        fields = columns
    # 2.将敏感字段从查询内容中隐藏
    fields = set(fields) - {'password', 'access', 'secret'}
    # 3.分页参数处理
    limit = request.args.get('limit', type=int, default=20)
    if limit < 1 or limit > 100:
        return response(ResponseEnum.InvalidInput, msg=f'limit必须是1-100')
    offset = request.args.get('offset', type=int, default=0)
    if offset < 0:
        offset = 0
    # 4.构建查询SQL
    sql = select(text(f"{','.join(fields)}"))
    if order_by := request.args.getlist('order'):
        for column in order_by:
            if column not in columns:
                return response(ResponseEnum.InvalidInput, data=columns, msg=f'{column}排序无效')
            # 根据列名前面的正负号判断是正序还是倒序
            if column.startswith('-'):
                sql = sql.order_by(desc(column[1:]))
            elif column.startswith('+'):
                sql = sql.order_by(asc(column[1:]))
            else:
                return response(ResponseEnum.InvalidInput, msg=f'以+/-开头进行排序')
    sql = sql.limit(limit).offset(offset)
    # 5.返回响应数据
    return execute_sql(sql, tp_public_session, expect_list=True, default=[])
