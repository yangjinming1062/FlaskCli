"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : functions.py
Author      : jinming.yang
Description : 工具方法定义实现处
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from functools import wraps

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from utils.classes import logger


def exceptions(flag_text: str = None, default=None):
    """
    装饰器：异常捕获
    Args:
        flag_text: 自定义的附加文本
        default: 当发生异常时返回的内容，默认为None

    Returns:
        无异常则返回方法的返回值，异常返回default
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kw):
            try:
                return func(*args, **kw)
            except Exception as ex:
                logger.exception(str(ex), func=func.__name__, plugin=flag_text)
                return default

        return wrapper

    return decorator


def execute_sql(sql, *,
                many: bool = True,
                scalar: bool = True,
                source: bool = False,
                params=None,
                session=None):
    """
    执行SQL语句
    Args:
        sql: SQL语句
        many: 当需要查询多行数据时返回列表格式的结果，如果查询单一数据返回数据的dict对象
        scalar: 查询model的指定列时传递False
        source: 查询类SQL生效，不做处理直接返回execute的结果
        params: 批量插入类操作时插入的数据
        session: 执行SQL的session，默认不需要，会自动创建，但是如果有上下文需要使用相同的也可以传递
        常见使用场景：
            1.当传入一个model的定义并且想直接返回该model的实例时可以将keyword赋值0
                1.1.同时传递expect_list为False返回model实例， 否则返回的是model的列表
            2.指定了查询的列，并且想返回列表就直接使用默认的参数即可
            3.非查询类操作基本只需要传递sql和session两个参数

    Returns:
        当SQL是查询类语句时：返回列表、实例对象、Row对象
        当SQL是非查询类语句时：返回受影响的行数/错误消息/None, 是否执行成功
    """
    if session_flag := session is None:
        # 如果没提供session则根据查询的对象创建一个
        session = Session(sql.froms[0].bind)
    try:
        if sql.is_select:
            executed = session.execute(sql)
            if source:
                return executed
            if many:
                result = executed.fetchall()
                if scalar:
                    result = [row[0] for row in result]
            else:
                result = executed.first()
                if scalar and result:
                    result = result[0]
            if session_flag:
                # 通过expunge使实例可以脱离session访问
                session.expunge_all()
            return result
        elif sql.is_insert:
            # 插入返回新增实例的ID
            result = session.execute(sql, params) if params is not None else session.execute(sql)
            created_id = [key[0] for key in result.inserted_primary_key_rows]
            session.flush()
            return created_id if params else created_id[0], True
        else:
            # 更新和删除返回受影响的行数
            result = session.execute(sql)
            session.flush()
            if result:
                return result.rowcount, True
            else:
                return 'SQL执行失败', False
    except IntegrityError as ex:
        session.rollback()
        logger.exception(ex)
        return ex.orig.args[1], False
    except Exception as exx:
        session.rollback()
        logger.exception(exx)
        return str(exx), False
    finally:
        if session_flag:
            session.commit()
            session.close()


def shadow_str(source, head=3, tail=2) -> str:
    """
    对敏感信息进行部分隐藏，只暴露头尾
    Args:
        source: 待隐藏字符串
        head: 前面暴露几个字符
        tail: 后面暴露几个字符

    Returns:
        隐藏信息后的字符串
    """
    if source is None:
        return ''
    if len(source) < head + tail:
        return source
    return f'{source[:head]}**{source[-tail:]}'
