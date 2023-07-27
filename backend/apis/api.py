"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : api.py
Author      : jinming.yang
Description : API接口用到的工具方法实现
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from datetime import datetime
from functools import partial
from functools import wraps
from typing import Any
from typing import Iterable
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
from models import ModelTemplate
from models import OLTPEngine
from utils import execute_sql
from utils import logger


class ParamDefine:
    """
    API接口参数定义类
    """
    __slots__ = ('type', 'comment', 'default', 'valid', 'message')
    type: Any
    comment: str
    default: Any
    valid: Any
    message: str

    def __init__(self, type_, comment='', **kwargs):
        """
        参数定义
        Args:
            type_: 数据类型
            comment: 注释
            valid: 参数校验（一个返回bool值的校验函数）
            message: 参数不满足时的错误提示
        """
        self.type = type_
        self.comment = comment
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self, *args, **kwargs):
        """
        确保类是callable的才可以放到List或Dict中
        """
        pass


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


def api_wrapper(request_param: dict = None, response_param: dict = None):
    """
    装饰器：统一处理API响应异常以及必要参数的校验
    Args:
        request_param: 当前接口包含的字段（key为字段名称，value为字段类型），如果参数为必填在在名称前添加*
        response_param: 当前接口的响应数据结构，用于生成接口文档

    Returns:
        无异常则返回方法的返回值，异常返回Error
    """

    def get_params():
        """
        获取请求参数
        Returns:
            请求参数
        """
        result = {}
        # GET和DELETE按照规范是使用url参数
        if request.method in ('GET', 'DELETE'):
            for key in dict(request.args).keys():
                # 兼容多个key的情况：例如?key=value1&key=value2
                result[key] = request.args.getlist(key)
        # 其他类型请求默认是JSON参数
        else:
            result = request.json
        return result

    def set_value(define, value):
        """
        根据类型定义调整请求值
        Args:
            define: 类型定义
            value: 参数值

        Returns:
            修改后的参数值
        """
        if define is Any:
            # 参数可以是任意类型
            return value
        elif define is datetime:
            # 时间类型
            return datetime.fromisoformat(value)
        elif issubclass(define, ModelTemplate):
            # model定义
            return define(**value)
        else:
            # 其他类型
            return define(value)

    def set_params(define, source, flag: bool):
        """
        根据参数定义生成请求参数
        Args:
            define: 参数定义
            source: 请求参数
            flag: 是否是GET或DELETE请求

        Returns:
            请求参数
        """
        if not isinstance(source, dict):
            raise Exception(RespEnum.ParamsMissed)
        result = {}
        for key, value in define.items():
            # 1. 判断是否为必填参数
            if key.startswith('*'):
                key = key[1:]
                if key not in source:
                    raise Exception(RespEnum.ParamsMissed)
            # 2. 每一个属性都需要通过ParamDefine进行定义声明
            assert isinstance(value, ParamDefine)
            # 3. 判断非必填的参数是否存在
            if key in source:
                # 从这里开始需要对各种类型的参数进行处理
                str_type = str(value.type)
                # 3.1 List类型的嵌套
                if str_type.startswith('typing.List'):
                    if isinstance(source[key], list):
                        l_type = value.type.__args__[0]
                        if isinstance(l_type, ParamDefine):
                            # List需要套一层ParamDefine的也就只有dict，不然普通的类型直接放到List里面就行，所以这里需要按嵌套结构处理
                            result = [set_params(l_type.type, row, flag) for row in source[key]]
                        else:
                            result[key] = list(map(partial(set_value, l_type), source[key]))
                    else:
                        raise Exception(RespEnum.ParamsValueError)
                # 3.2 Dict意味着允许传递对象类型的参数，但是具体有哪些key未作限定
                elif str_type.startswith('typing.Dict'):
                    assert isinstance(source[key], dict)
                    k_type = value.__args__[0]
                    v_type = value.__args__[1]
                    result[key] = {set_value(k_type, k): set_value(v_type, v) for k, v in source[key].items()}
                # 3.3 嵌套结构
                elif isinstance(value.type, dict):
                    result[key] = set_params(value.type, source[key], flag)
                # 3.4 其他常规情况
                else:
                    if flag and len(source[key]) == 1:  # Get、Delete获取的都是list
                        result[key] = set_value(value.type, source[key][0])
                    else:
                        result[key] = set_value(value.type, source[key])
            else:
                # 3.1 没传参数则看看有没有默认值
                if hasattr(value, 'default'):
                    result[key] = value.default
                    continue
            # 4. 如果提供了校验函数则校验数据取值
            if hasattr(value, 'valid'):
                if isinstance(result[key], Iterable):
                    if all(map(value.valid, result[key])):
                        continue
                else:
                    if value.valid(result[key]):
                        continue
                # 4.1 校验通过就continue了，走到这说明校验没通过
                raise Exception(RespEnum.ParamsRangeError)
        return result

    def decorator(func):
        func.__apispec__ = {'request': request_param, 'response': response_param}

        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['oltp_session'] = Session(OLTPEngine)
            try:
                if request_param is None:
                    # 参数为空说明是不需要参数的接口
                    return func(*args, **kwargs)
                if request_param:
                    # 定义的请求参数要求
                    req_params = set_params(request_param, get_params(), request.method in ('GET', 'DELETE'))
                else:
                    # 这种情况是参数定义为空字典，表示可以接收任意的请求参数
                    req_params = get_params()
                kwargs.update(req_params)
                kwargs['oltp_session'].begin()
                return func(*args, **kwargs)
            except AssertionError as ex:
                kwargs['oltp_session'].rollback()
                logger.info(ex)
                return response(RespEnum.InvalidInput)
            except KeyError as ex:
                kwargs['oltp_session'].rollback()
                logger.info(ex)
                return response(RespEnum.ParamsMissed)
            except ValueError as ex:
                kwargs['oltp_session'].rollback()
                logger.info(ex)
                return response(RespEnum.ParamsValueError)
            except Exception as ex:
                kwargs['oltp_session'].rollback()
                logger.info(ex)
                if isinstance(ex.args[0], RespEnum):
                    return response(ex.args[0])
                else:
                    return response(RespEnum.Error)
            finally:
                kwargs['oltp_session'].close()

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
