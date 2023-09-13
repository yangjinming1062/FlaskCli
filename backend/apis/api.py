"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : api.py
Author      : jinming.yang
Description : API接口用到的工具方法实现
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import json
from datetime import datetime
from functools import partial
from functools import wraps
from time import time
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Union
from uuid import uuid4

from clickhouse_driver import Client
from flask import Blueprint
from flask import make_response
from flask import request
from sqlalchemy import Column
from sqlalchemy import Row
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import update
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from config import DATABASE_OLAP_URI
from defines import *
from utils import *

oltp_session_factory = scoped_session(sessionmaker(bind=OLTPEngine))
_SUCCESSFUL_RESP = [RespEnum.OK, RespEnum.Created, RespEnum.Accepted]


class ParamDefine:
    """
    API接口参数定义类
    """
    __slots__ = ('type', 'required', 'comment', 'default', 'valid', 'key', 'resp')
    type: Any
    required: bool
    comment: str
    default: Any
    valid: Any
    resp: RespEnum

    def __init__(self, type_, required: bool = False, comment: str = '', **kwargs):
        """
        参数定义
        Args:
            type_: 数据类型
            required: 是否必填
            comment: 注释
            valid: 参数校验（一个返回bool值的校验函数）
            resp: 参数不满足时的错误提示
            key: 定义响应参数时序列化数据的key（默认和参数同名）
        """
        self.type = type_
        self.required = required
        self.comment = comment
        self.key = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self, *args, **kwargs):
        """
        确保类是callable的才可以放到List或Dict中
        """
        pass


class ParamSchema:
    """
    接口参数定义
    """
    define: ParamDefine

    @staticmethod
    def is_schema(value) -> bool:
        """
        判断指定数据是否是Schema定义
        Args:
            value:

        Returns:
            是否是ParamSchema
        """
        if isinstance(value, ParamSchema):
            return True
        else:
            return type(value) is type and issubclass(value, ParamSchema)


class APIException(Exception):
    """
    异常响应
    """

    def __init__(self, resp: RespEnum):
        self.resp = resp


def get_blueprint(path, name):
    """
    生成API的蓝图：方便统一调整
    """
    url_prefix = f'/{path.replace(".", "/")}'
    return Blueprint(name, __name__, url_prefix=url_prefix)


def response(base_response: RespEnum, data=None, headers=None):
    """
    统一的API响应方法
    Args:
        base_response: 基础响应信息，本次API响应状态
        data: 响应内容，默认为None
        headers: 响应头

    Returns:
        Response
    """
    status, msg = base_response.value
    if data is None:
        resp = make_response(json.dumps({
            'code': base_response.name,
            'message': msg
        }), status)
    else:
        if isinstance(data, (list, dict)):
            resp = make_response(json.dumps(data, cls=JSONExtensionEncoder), status)
        else:
            resp = make_response(data, status)
    resp.headers['Content-Type'] = 'application/json'
    if headers:
        if ParamSchema.is_schema(headers):
            headers = headers.define
        resp.headers.update(headers.type)
    if request.uid:
        # 记录访问日志，也可以把匿名访问都记录上，看需求
        sql = insert(ApiRequestLogs).values({
            'id': str(uuid4()),
            'user_id': request.uid,
            'created_at': datetime.now(),
            'method': request.method,
            'blueprint': request.blueprint,
            'uri': request.path,
            'status': resp.status_code,
            'duration': int((time() - request.started_at) * 1000),
            'source_ip': request.remote_addr,
        })
        execute_sql(sql)
    return resp


def api_wrapper(
        request_header: Union[ParamDefine, ParamSchema] = None,
        request_param: Union[ParamDefine, ParamSchema] = None,
        response_param: Dict[RespEnum, Union[ParamDefine, ParamSchema]] = None,
        response_header: Union[ParamDefine, ParamSchema] = None,
        permission: set = None
):
    """
    装饰器：统一处理API响应异常以及必要参数的校验
    Args:
        request_header: 请求头中的参数
        request_param: 当前接口包含的字段
        response_param: 当前接口的响应数据结构，用于生成接口文档
        response_header: 响应头，用于生成接口文档
        permission: 接口权限

    Returns:
        无异常则返回方法的返回值，异常返回Error
    """

    def _get_params():
        """
        获取请求的参数
            GET、DELETE： query参数
            POST、PUT、PATCH： json参数
        Returns:
            dict
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

    def _req_value(define, value):
        """
        设置请求参数的格式
        Args:
            define: 参数定义
            value: 传入值

        Returns:
            类型转化后的参数
        """
        if define is Any:
            # 参数可以是任意类型
            return value
        elif define is datetime:
            # 时间类型
            return datetime.strptime(value, Constants.DEFINE_DATE_FORMAT)
        elif issubclass(define, ModelTemplate):
            # model定义
            return define(**value)
        elif issubclass(define, Enum):
            tmp = {x.name: x for x in list(define)}
            if value in tmp:
                # 按照枚举的Key去匹配
                return tmp[value]
            else:
                # Key匹配不上则认为传递的是枚举Value
                return define(value)
        else:
            # 其他类型
            return define(value)

    def _resp_value(define: ParamDefine, value, language):
        """
        输出参数的校验及特殊类型的序列化
        Args:
            define: 参数定义
            value: 传入值
            language: 语言类型，可以在这里根据不同语言切换不同的处理

        Returns:
            处理后的参数
        """
        if value is None and hasattr(define, 'default'):
            return define.default
        return value

    def _req_params(define: Union[ParamDefine, ParamSchema], source, flag: bool):
        """
        根据定义生成请求参数
        Args:
            define: 参数定义
            source: 传入参数
            flag: 是否是GET或DELETE请求（影响参数获取方式）

        Returns:
            请求参数
        """
        # 判断传过来是的共用的Schema还是单独定义的dict
        if ParamSchema.is_schema(define):
            define = define.define
        if not isinstance(source, dict):
            raise APIException(RespEnum.ParamsMissed)
        result = {}
        assert isinstance(define.type, dict)
        for field_name, field_define in define.type.items():
            # 1. 每一个属性都需要通过ParamDefine进行定义声明
            assert isinstance(field_define, ParamDefine)
            # 2. 判断是否为必填参数
            if field_define.required and field_name not in source:
                raise APIException(RespEnum.ParamsMissed)
            # 3. 判断非必填的参数是否存在
            if field_name in source:
                # 从这里开始需要对各种类型的参数进行处理
                str_type = str(field_define.type)
                # 3.1 List类型的嵌套
                if str_type.startswith('typing.List'):
                    if isinstance(source[field_name], list):
                        # 获取List中定义的子类型是什么
                        inner_type = field_define.type.__args__[0]
                        if isinstance(inner_type, ParamDefine):
                            # List需要套一层ParamDefine的也就只有dict或ParamSchema，不然普通的类型直接放到List里面就行，所以这里需要按嵌套结构处理
                            result = [_req_params(inner_type.type, row, flag) for row in source[field_name]]
                        else:
                            # 通过偏函数partial将inner_type作为_req_value的第一个参数生成一个新的只需要value参数的函数，使用map高阶函数遍历
                            result[field_name] = list(map(partial(_req_value, inner_type), source[field_name]))
                    else:
                        # 如果入参不是数组则提示参数错误
                        raise APIException(RespEnum.ParamsValueError)
                # 3.2 Dict意味着允许传递对象类型的参数，但是具体有哪些key未作限定
                elif str_type.startswith('typing.Dict'):
                    # TODO： 这里面再嵌套ParamDefine可能需要再完善，但是需要typing.Dict的基本都是动态定义，应该情况极少
                    assert isinstance(source[field_name], dict)
                    key_type = field_define.__args__[0]
                    value_type = field_define.__args__[1]
                    result[field_name] = {
                        _req_value(key_type, k): _req_value(value_type, v)
                        for k, v in source[field_name].items()
                    }
                # 3.3 嵌套结构
                elif isinstance(field_define.type, dict):
                    result[field_name] = _req_params(field_define, source[field_name], flag)
                # 3.4 其他常规情况
                else:
                    # Get、Delete获取的都是list
                    if flag and len(source[field_name]) == 1:
                        # 能到这步定义肯定就不是要的list了，所以直接取出第一个即可
                        result[field_name] = _req_value(field_define.type, source[field_name][0])
                    else:
                        result[field_name] = _req_value(field_define.type, source[field_name])
                # 4. 如果提供了校验函数则校验数据取值
                if hasattr(field_define, 'valid'):
                    try:
                        if isinstance(result[field_name], (list, dict)):
                            # 如果是可遍历的类型则遍历校验所有子项都满足参数要求
                            assert all(map(field_define.valid, result[field_name]))
                        else:
                            assert field_define.valid(result[field_name])
                    except:
                        if hasattr(field_define, 'resp'):
                            # 参数定义的时候定义了校验不通过的响应则优先使用定义的（主要是满足不同的参数校验需要给出不同提示的场景）
                            raise APIException(field_define.resp)
                        else:
                            # 没有提供特定的响应则使用默认的
                            raise APIException(RespEnum.ParamsRangeError)
            else:
                # 3.1 没传参数则看看有没有默认值
                if hasattr(field_define, 'default'):
                    result[field_name] = field_define.default
                    continue
        return result

    def _resp_params(define: Union[ParamDefine, ParamSchema], source, language: LanguageEnum):
        """
        根据参数定义生成响应参数
        Args:
            define: 参数定义
            source: 接口输出
            language: 语言类型

        Returns:
            响应参数
        """
        if ParamSchema.is_schema(define):
            define = define.define
        if define.type is None:
            # 接口不需要响应数据
            return None
        if define.type is Any:
            return source
        # 1 嵌套结构
        if isinstance(define.type, dict):
            result = {}
            for field_name, field_define in define.type.items():
                tmp = None
                if ParamSchema.is_schema(field_define):
                    field_define = field_define.define
                if isinstance(source, (Row, ModelTemplate)):
                    # 如果是查询数据库获得的实例对象则递归处理
                    if field_define.required or hasattr(source, field_define.key or field_name):
                        tmp = _resp_params(field_define, getattr(source, field_define.key or field_name), language)
                elif isinstance(source, dict):
                    # 也是递归，但dict类型是.get，上面是getattr
                    if field_define.required or (field_define.key or field_name in source):
                        tmp = _resp_params(field_define, source[field_define.key or field_name], language)
                if field_define.required or tmp:
                    # 必填参数或者可选参数也有数据则进行赋值
                    result[field_name] = tmp
            return result
        # 2 List类型的嵌套
        elif str(define.type).startswith('typing.List'):
            if isinstance(source, Iterable):
                inner_type = define.type.__args__[0]
                # 这里为什么分开处理见_req_params的List嵌套的处理注释
                if isinstance(inner_type, ParamDefine):
                    return [_resp_params(inner_type, row, language) for row in source]
                else:
                    return list(map(partial(_resp_value, define, language=language), source))
            else:
                logger.debug(source, 'data is not a list')
                return []
        # 3 其他常规情况
        else:
            return _resp_value(define, source, language)

    def decorator(function):
        function.__apispec__ = {
            'request_param': request_param,
            'response_param': response_param,
            'request_header': request_header,
            'response_header': response_header
        }

        @wraps(function)
        def wrapper(*args, **kwargs):
            kwargs['oltp_session'] = oltp_session_factory()
            kwargs['olap_session'] = Client.from_url(DATABASE_OLAP_URI)
            try:
                # 1. 接口的鉴权处理：获取登陆的user
                if request.uid:
                    # 登录的token还有效，但是token内的uid已经不在来（几乎不存在，但有可能）
                    user = execute_sql(select(User).where(User.id == request.uid), session=kwargs['oltp_session'])
                    if not user:
                        return response(RespEnum.Forbidden, headers=response_header)
                    if permission and user.role not in permission:
                        return response(RespEnum.Forbidden, headers=response_header)
                else:
                    user = None
                kwargs['user_id'] = request.uid
                kwargs['user'] = user
                # 2. 请求参数获取
                if request_param:
                    # 定义的请求参数要求
                    kwargs.update(_req_params(request_param, _get_params(), request.method in ('GET', 'DELETE')))
                # 3. 请求头信息获取
                if request_header:
                    kwargs.update(_req_params(request_header, {k: v for k, v in request.headers.items()}, False))
                # 4. API接口调用
                resp = function(*args, **kwargs)
                # 5. 接口响应数据处理
                if response_param:
                    language = kwargs.get('Accept-Language', LanguageEnum.ZH)
                    for key in _SUCCESSFUL_RESP:
                        if key in response_param:
                            data = _resp_params(response_param[key], resp, language)
                            return response(key, data, headers=response_header)
                else:
                    # 只要接口正常运行完了就是成功，没数据就返回204
                    return response(RespEnum.NoContent, headers=response_header)
            except APIException as ex:
                # 接口非正常响应时返回异常状态
                return response(ex.resp, headers=response_header)
            except AssertionError as ex:
                kwargs['oltp_session'].rollback()
                logger.debug(ex)
                return response(RespEnum.InvalidInput, headers=response_header)
            except KeyError as ex:
                kwargs['oltp_session'].rollback()
                logger.debug(ex)
                return response(RespEnum.ParamsMissed, headers=response_header)
            except ValueError as ex:
                kwargs['oltp_session'].rollback()
                logger.debug(ex)
                return response(RespEnum.ParamsValueError, headers=response_header)
            except Exception as ex:
                kwargs['oltp_session'].rollback()
                logger.exception(ex)
                return response(RespEnum.Error, headers=response_header)
            finally:
                kwargs['olap_session'].disconnect()
                kwargs['oltp_session'].commit()

        return wrapper

    return decorator


def orm_create(cls, params: dict, repeat_resp=RespEnum.KeyRepeat):
    """
    创建数据实例
    Args:
        cls: ORM类定义
        params: 参数
        repeat_resp: 新增重复时的响应

    Returns:
        新增数据的ID
    """
    params['updated_at'] = datetime.now()
    _params = {k: v for k, v in params.items() if k in cls.get_columns()}
    result, flag = execute_sql(insert(cls).values(**_params))
    if flag:
        return result
    else:
        if result.lower().find('duplicate') > 0:
            raise APIException(repeat_resp)
        else:
            raise APIException(RespEnum.InvalidInput)


def orm_update(cls, resource_id: str, params: dict, error_resp=RespEnum.InvalidInput):
    """
    ORM数据的更新
    Args:
        cls: ORM类定义
        resource_id: 资源ID
        params: 更新数据
        error_resp: 更新失败时的响应状态

    Returns:
        None
    """
    if not params:
        raise APIException(RespEnum.ParamsMissed)
    params['updated_at'] = datetime.now()
    _params = {k: v for k, v in params.items() if k in cls.get_columns()}
    result, flag = execute_sql(update(cls).where(cls.id == resource_id).values(**_params))
    if flag and not result:
        raise APIException(RespEnum.NotFound)
    elif not flag:
        raise APIException(error_resp)


def orm_delete(cls, resource_id: Union[str, list, set]):
    """
    删除数据实例
    Args:
        cls: ORM类定义
        resource_id:  资源ID

    Returns:
        None
    """
    session = oltp_session_factory()
    try:
        if isinstance(resource_id, (list, set)):
            for instance in session.scalars(select(cls).where(cls.id.in_(resource_id))).all():
                session.delete(instance)
        else:
            if instance := session.query(cls).get(resource_id):
                session.delete(instance)  # 通过该方式可以级联删除子数据
    except Exception as ex:
        session.rollback()
        logger.exception(ex)
        raise APIException(RespEnum.BadRequest)
    finally:
        session.commit()


def paginate_query(sql, params, scalar=False, format_func=None, session=None):
    """
    统一分分页查询操作
    Args:
        sql:查询SQL
        params: 请求参数，对应接口的kwargs
        scalar:是否需要scalars
        format_func:直接返回查询后的数据，不进行响应，用于数据结构需要特殊处理的情况
        session: 特殊OLAP等情况需要方法自己提供session

    Returns:
        {
            'total': int,
            'data': List[Any]
        }
    """

    def _add_sort(_sql):
        for column in params.get('sort', []):
            if column == '':
                continue
            if column[0] in ('+', '-'):
                direct = 'DESC' if column[0] == '-' else 'ASC'
                column = column[1:]
            else:
                direct = 'ASC'
            _sql = _sql.order_by(text(f'{column} {direct}'))
        return _sql

    if params['size'] == 0:
        # 特殊约定的查询全量数据的方式，可以以其他方式，比如size是-1等
        sql = _add_sort(sql)
        data = execute_sql(sql, many=True, scalar=scalar, session=session)
        result = {'total': len(data), 'data': data}
    else:
        total_sql = select(func.count()).select_from(sql)
        total = execute_sql(total_sql, many=False, scalar=True, session=session)
        if params['size'] > 100 or params['size'] < 1:
            raise APIException(RespEnum.ParamsRangeError)
        if params['page'] < 1:
            raise APIException(RespEnum.ParamsRangeError)
        sql = sql.limit(params['size']).offset((params['page'] - 1) * params['size'])
        result = {
            'total': total,
            'data': execute_sql(_add_sort(sql), many=True, scalar=scalar, session=session)
        }
    if format_func:
        # 需要按照特定格式对数据进行修改的时候使用format_func
        result['data'] = list(map(format_func, result['data']))
    return result


def query_condition(sql, params: dict, column: Column, field_name=None, op_func=None, op_type=None):
    """
    添加查询参数
    Args:
        sql: SQL对象
        params: 接口参数
        column: 查询的列
        field_name: 条件名称(默认为空时和查询列同名)
        op_func: 操作函数(op_func优先于op_type)
        op_type: 操作类型(op_func和op_type至少一个不为None)

    Returns:
        添加where条件后的SQL对象
    """
    if (param := params.get(field_name or column.key)) is not None or op_type == 'datetime':
        if op_func:
            return sql.where(op_func(param))
        else:
            assert op_type is not None, 'op_type 和 op_func 至少一个不为None'
            if op_type == 'like':
                if isinstance(param, list):
                    return sql.where(or_(*[column.like(f'%{x}%') for x in param]))
                else:
                    return sql.where(column.like(f'%{param}%'))
            elif op_type == 'in':
                return sql.where(column.in_(param))
            elif op_type == 'notin':
                return sql.where(column.notin_(param))
            elif op_type == 'datetime':
                if start := params.get(f'{field_name or column.key}_start'):
                    sql = sql.where(column >= start)
                if end := params.get(f'{field_name or column.key}_end'):
                    sql = sql.where(column <= end)
                return sql
            else:
                return sql.where(eval(f'column {op_type} param'))
    else:
        return sql
