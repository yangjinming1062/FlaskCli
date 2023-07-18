"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : api.py
Author      : jinming.yang
Description : API接口用到的工具方法实现
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from datetime import datetime
from functools import wraps
from typing import Union

from flask import Blueprint
from flask import jsonify
from flask import request
from sqlalchemy import case
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import Session

from enums import *
from models import OLTPEngine
from utils import execute_sql
from utils import logger


def get_blueprint(name):
    """
    生成API的蓝图：方便统一调整
    """
    tmp = name.split('.')
    version = tmp[-2]
    _name = tmp[-1]
    return Blueprint(_name, __name__, url_prefix=f'/api/{version}/{_name}')


def response(base_response: RespEnum, data=None):
    """
    统一的API响应方法
    Args:
        base_response: 基础响应信息，本次API响应状态
        data: 响应内容，默认为None

    Returns:
        Response
    """
    status, resp = base_response.value
    if data is not None:
        resp = data
    return jsonify(resp), status


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
                    logger.info(missed)
                    return response(RespEnum.ParamsMissed)
                # 4.如果不存在params则直接返回
                if not params:
                    kwargs.update(req_params)
                    return func(*args, **kwargs)
                # 5.检查是否有垃圾参数
                if junk := req_params.keys() - params.keys():
                    logger.info(junk)
                    return response(RespEnum.IllegalParams)
                # 6.检查参数类型，并将对应的参数转成目标类型
                for k, t in params.items():
                    if k in req_params:
                        # GET和DELETE的params默认都是兼容批量的，如果不指定需要列表则获取到单一参数时直接转换成对应类型
                        if request.method in ('GET', 'DELETE') and t is not list and len(req_params[key]) == 1:
                            req_params[key] = req_params[key][0]
                        if t is None:
                            # None为保留情况，此时不对参数类型进行校验
                            continue
                        elif t in (list, dict):
                            # 复杂的嵌套类型暂时不做处理
                            if not isinstance(req_params[k], t):
                                return response(RespEnum.ParamsValueError)
                        elif t is datetime:
                            req_params[k] = datetime.fromisoformat(req_params[k])
                        else:
                            # args类型参数顺便进行类型转换
                            req_params[k] = t(req_params[k])
                kwargs.update(req_params)
                return func(*args, **kwargs)
            except KeyError as ex:
                logger.info(ex)
                return response(RespEnum.ParamsMissed)
            except ValueError as ex:
                logger.info(ex)
                return response(RespEnum.ParamsValueError)
            except Exception as ex:
                logger.exception(str(ex), module=func.__module__, func=func.__name__)
                return response(RespEnum.Error)

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
    result, flag = execute_sql(insert(cls).values(**params))
    if flag:
        return response(RespEnum.Created, result)
    else:
        if result.find('Duplicate') > 0:
            return response(RespEnum.KeyRepeat, result)
        else:
            return response(RespEnum.InvalidInput, result)


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
            return response(RespEnum.ParamsRangeError, data=columns)
        else:
            columns = fields
    sql = select(*cls.to_properties(columns)).select_from(cls).where(cls.id == resource_id)
    if data := execute_sql(sql, many=False, scalar=False):
        return response(RespEnum.OK, data)
    else:
        return response(RespEnum.NotFound)


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
    if not params:
        return response(RespEnum.ParamsMissed)
    result, flag = execute_sql(update(cls).where(cls.id == resource_id).values(**params))
    if flag:
        return response(RespEnum.NoContent)
    else:
        return response(RespEnum.InvalidInput)


def orm_delete(cls, resource_id: Union[str, list, set]):
    """
    删除数据实例
    Args:
        cls: ORM类定义
        resource_id:  资源ID

    Returns:
        Response
    """
    with Session(cls.bind) as session:
        try:
            if isinstance(resource_id, (list, set)):
                for instance in session.scalars(select(cls).where(cls.id.in_(resource_id))).all():
                    session.delete(instance)
                return response(RespEnum.NoContent)
            else:
                if instance := session.query(cls).get(resource_id):
                    session.delete(instance)  # 通过该方式可以级联删除子数据
                    return response(RespEnum.NoContent)
            return response(RespEnum.NotFound)
        except Exception as ex:
            session.rollback()
            logger.exception(ex)
            return response(RespEnum.BadRequest)
        finally:
            session.commit()


def orm_paginate(cls, params):
    """
    统一分分页查询操作
    Args:
        cls: 添加完where条件的SQLAlchemy的查询类
        params: 请求参数

    Returns:
        接口响应
    Example:
        params = {
            'page': 1,
            'size': 10,
            'field': ['id', 'name'],
            'query': {'age': {'op': '=', 'value': 18}, 'name': {'op': 'like', 'value': '%Alice%'}}
        }
    """
    # 先处理查询内容
    columns = set(cls.get_columns())
    if fields := params.get('field'):
        if set(fields) - columns:
            return response(RespEnum.ParamsRangeError, data=columns)
    # 构建查询SQL
    sql = select(*cls.to_property(fields or columns)).select_from(cls)
    # 构建查询条件
    if filters := params.get('query'):
        if filters.keys() - columns:
            return response(RespEnum.ParamsRangeError, data=columns)
        for column_name, value in filters.items():
            if value['op'] == 'like':
                sql = sql.where(getattr(cls, column_name).like(value['value']))
            elif value['op'] == 'in':
                sql = sql.where(getattr(cls, column_name).in_(value['value']))
            elif value['op'] == 'notin':
                sql = sql.where(getattr(cls, column_name).notin_(value['value']))
            elif value['op'] in ('==', '>=', '<=', '!=', '>', '<'):
                eval(f'sql = sql.where(getattr(cls, column_name) {value["op"]} {value["value"]}')
            else:
                logger.warning(filters)
    return paginate_query(sql, params, False)


def paginate_query(sql, params, scalar=False, format_func=None):
    """
    统一分分页查询操作
    Args:
        sql:查询SQL
        params: 请求参数，对应接口的kwargs
        scalar:是否需要scalars
        format_func:直接返回查询后的数据，不进行响应，用于数据结构需要特殊处理的情况

    Returns:
        接口响应
    """
    total_sql = select(func.count()).select_from(sql)
    with Session(OLTPEngine) as session:
        total = execute_sql(total_sql, many=False, scalar=True, session=session)
        sql = sql.limit(params['size']).offset(params['page'] * params['size'])
        for column in params.get('sort', []):
            if column[1] in ('+', '-'):
                direct = 'DESC' if column[1] == '-' else 'ASC'
                column = column[1:]
            else:
                direct = 'ASC'
            sql = sql.order_by(f'{column} {direct}')
        result = {
            'total': total,
            'data': execute_sql(sql, many=True, scalar=scalar, session=session)
        }
        if format_func:
            # 需要按照特定格式对数据进行修改的时候使用format_func
            result['data'] = list(map(format_func, result['data']))
        return response(RespEnum.OK, result)


def safe_column(column, default='-', label=None):
    """
    可为空的列在为空时返回默认值
    Args:
        column: xxx.xx
        default: 为空时的替换值
        label: 变化后的列名，默认保持不变

    Returns:
        case之后的select列
    """
    return case({None: default}, value=column).label(label if label else column.name)
