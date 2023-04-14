"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : functions.py
Author      : jinming.yang
Description : 工具方法定义实现处
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from functools import wraps
from typing import Union

from sqlalchemy.exc import IntegrityError

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


def execute_sql(sql, session, source_pattern: bool = False, expect_list: bool = True, keyword: Union[str, int] = None,
                default=None, params=None):
    """
    执行SQL语句
    Args:
        sql: SQL语句
        session: 执行SQL的session
        source_pattern: 是否需要对查询结果进行解析成list/dict这种JSON序列化格式（仅限非keyword查询时生效）
        expect_list: 当需要查询多行数据时返回列表格式的结果，如果查询单一数据返回数据的dict对象
        keyword: 只需要查询SQL语句中的某一列结果时传递该参数，允许列名称（str）和列索引（int）两种方式
        default: 当查询识别或者结果不存在时返回的默认值
        params: 批量插入类操作时插入的数据
        常见使用场景：
            1.当传入一个model的定义并且想直接返回该model的实例时可以将keyword赋值0
                1.1.同时传递expect_list为False返回model实例， 否则返回的是model的列表
            2.如果查询作为中间数据不需要解析处理，建议直接将source_pattern赋值为True
            3.指定了查询的列，并且想返回列表就直接使用默认的参数即可
            4.非查询类操作基本只需要传递sql和session两个参数

    Returns:
        当SQL是查询类语句时：
            当 keyword 指定 并且 expect_list 为 True:
                return 指定列的数据格式的列表
            当 keyword 指定 并且 expect_list 为 False:
                return 指定列的数据格式(常见为str或int）
            当 keyword 未指定 并且 expect_list 为 True:
                return 查询的全部列dict对象的列表
            当 keyword 未指定 并且 expect_list 为 False:
                return 全部列的dict对象
        当SQL是非查询类语句时：
            返回受影响的行数/错误消息/None, 是否执行成功
    """
    try:
        if sql.is_select:
            if not expect_list:
                sql = sql.limit(1)
            executed = session.execute(sql)
            # 先判断是否只想查单一列
            if keyword is not None:
                # 防止keyword是0不被命中，显式判断不为None
                if expect_list:
                    return [row[keyword] for row in executed]
                else:
                    result = executed.first()
                    return result[keyword] if result else default
            else:
                if expect_list:
                    if source_pattern:
                        # 源数据模式直接返回查询结果
                        return executed
                    else:
                        return [{key: row[key] for key in executed.keys()} for row in executed]
                else:
                    result = executed.first()
                    if source_pattern:
                        return result or default
                    else:
                        if result is None:
                            return default
                        # 返回一个以查询的列名为key，列内容为value的字典
                        return {key: result[key] for key in executed.keys()}
        elif sql.is_insert:
            result = session.execute(sql, params) if params is not None else session.execute(sql)
            created_id = result.inserted_primary_key[0]
            session.flush()
            return created_id, True
        else:
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
