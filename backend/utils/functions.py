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

from models import OLAPEngine
from models import OLAPModelsDict
from models import OLTPEngine
from utils import logger

_OLAP_TABLES = {item.__tablename__ for item in OLAPModelsDict.values()}


def exceptions(default=None):
    """
    装饰器：异常捕获
    Args:
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
                logger.exception(ex)
                return default

        return wrapper

    return decorator


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
    tp_flag = True
    if sql.is_select:
        if session_flag := session is None:
            if sql.froms[0].name in _OLAP_TABLES:
                tp_flag = False
                session = OLAPEngine
            else:
                session = Session(OLTPEngine)
    else:
        if session_flag := session is None:
            session = Session(OLTPEngine)
    try:
        if sql.is_select:
            if not tp_flag:
                sql = sql.compile(compile_kwargs={"literal_binds": True}).string
            executed = session.execute(sql)
            if many:
                result = executed.fetchall() if tp_flag else executed
                if scalar:
                    result = [row[0] for row in result]
            else:
                result = executed.first() if tp_flag else executed[0]
                if scalar and result:
                    result = result[0]
            if session_flag and tp_flag:
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
        if session_flag and tp_flag:
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
