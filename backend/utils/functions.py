"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : functions.py
Author      : jinming.yang
Description : 基础方法的定义实现
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
import uuid
from functools import wraps

from clickhouse_driver import Client
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config import DATABASE_OLAP_URI
from defines import *
from utils import logger

_OLAP_TABLES = {item.__tablename__ for item in OLAPModelsDict.values()}


def execute_sql(sql, *, many: bool = False, scalar: bool = True, params=None, session=None):
    """
    执行SQL语句
    Args:
        sql: SQLAlchemy SQL语句对象
        many: 是否查询多行数据，默认值为False
        scalar: 查询model时返回model实例，如果指定了查询的列则不需要，默认值为True
        params: 批量插入类操作时插入的数据，默认值为None
        session: 执行SQL的session，默认不需要，会自动创建，但是如果有上下文需要使用相同的也可以传递

    Returns:
        当SQL是查询类语句时：返回列表、实例对象、Row对象
        当SQL是非查询类语句时：返回受影响的行数/错误消息/None, 是否执行成功
    """
    tp_flag = not isinstance(session, Client)
    if sql.is_select:
        if session_flag := session is None:
            if sql.froms[0].name in _OLAP_TABLES:
                tp_flag = False
                session = Client.from_url(DATABASE_OLAP_URI)
            else:
                session = Session(OLTPEngine)
    else:
        if session_flag := session is None:
            if sql.table.name in _OLAP_TABLES:
                tp_flag = False
                session = Client.from_url(DATABASE_OLAP_URI)
            else:
                session = Session(OLTPEngine)
    try:
        if sql.is_select:
            if not tp_flag:
                sql = sql.compile(compile_kwargs={'literal_binds': True}).string
            executed = session.execute(sql)
            if many:
                result = executed.fetchall() if tp_flag else executed
                if scalar:
                    result = [row[0] for row in result]
            else:
                if tp_flag:
                    result = executed.first()
                else:
                    if executed:
                        result = executed[0]
                    else:
                        return None
                if scalar and result:
                    result = result[0]
            if session_flag and tp_flag:
                # 通过expunge使实例可以脱离session访问
                session.expunge_all()
            return result
        elif sql.is_insert:
            # 插入返回新增实例的ID
            if tp_flag:
                result = session.execute(sql, params) if params is not None else session.execute(sql)
                session.flush()
                if hasattr(result, 'inserted_primary_key_rows'):
                    created_id = [key[0] for key in result.inserted_primary_key_rows]
                    return created_id if params else created_id[0], True
                else:
                    return '', True
            else:
                sql = sql.compile(compile_kwargs={'literal_binds': True}).string
                if params:
                    sql = sql.split('VALUES')[0] + 'VALUES'
                    session.execute(sql, params=params)
                else:
                    session.execute(sql)
                return '', True
        else:
            # 更新和删除返回受影响的行数
            result = session.execute(sql)
            session.flush()
            if result:
                return result.rowcount, True
            else:
                return 'SQL执行失败', False
    except IntegrityError as ex:
        if tp_flag:
            session.rollback()
        logger.exception(ex)
        return ex.args[0], False
    except Exception as exx:
        if tp_flag:
            session.rollback()
        logger.exception(exx)
        return str(exx), False
    finally:
        if session_flag:
            if tp_flag:
                session.commit()
                session.close()
            else:
                session.disconnect()


def exceptions(default=None):
    """
    装饰器：异常捕获
    Args:
        default: 当发生异常时返回的内容

    Returns:
        无异常则返回方法的返回值，异常返回default的值
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            try:
                return func(*args, **kw)
            except Exception as ex:
                logger.exception(ex)
                return default

        return wrapper

    return decorator


def generate_key(source: str = None):
    """
    根据特定的输入输出id
    Args:
        source:

    Returns:

    """
    if source:
        tmp = uuid.uuid5(uuid.NAMESPACE_DNS, source)
    else:
        tmp = uuid.uuid4()
    return tmp.hex[-12:]
