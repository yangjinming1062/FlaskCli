"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : base.py
Author      : jinming.yang
Description : model基础信息定义
Model分为两类，
    - OLTP: 联机事务处理
    - OLAP: 联机事务处理
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from secrets import token_urlsafe
from typing import Optional
from typing import Union
from uuid import uuid4

from clickhouse_sqlalchemy import types
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.collections import InstrumentedList

from utils import OLAP_ENGINE
from utils import OLTP_ENGINE
from utils import execute_sql
from utils import logger

_OLTPModelBase = declarative_base(bind=OLTP_ENGINE)
_OLAPModelBase = declarative_base(bind=OLAP_ENGINE)
IdDefine = String(32)


class ModelTemplate:
    """
    TP、AP公共方法
    """

    id = None

    def jsonify(self, excluded: set = None, include_properties=True) -> dict:
        """
        将ORM实例转为可以序列化的dict对象
        Args:
            excluded: 需要忽略的列
            include_properties: 是否包含属性的导出

        Returns:
            dict
        """
        d = dict()
        ignored_fields = excluded or set()
        for property_name in dir(self):
            if property_name.startswith('_') or property_name in ignored_fields:
                continue
            cp = getattr(type(self), property_name)
            value = getattr(self, property_name)
            if isinstance(value, InstrumentedList):
                d[property_name] = [item.id for item in value]  # 只导出ID是为了避免循环调用
            elif isinstance(value, (OLAPModelBase, OLTPModelBase)):
                d[property_name] = {'id': value.id}
            elif isinstance(cp, InstrumentedAttribute) or (isinstance(cp, property) and include_properties):
                d[property_name] = value
        return d

    @classmethod
    def get_columns(cls):
        """
        获取类中的全部数据库列的名称
        Returns:
            列名称列表
        """
        properties = []
        for property_name in dir(cls):
            if property_name.startswith('_'):
                continue
            if isinstance(getattr(cls, property_name), InstrumentedAttribute):
                properties.append(property_name)
        return properties

    @classmethod
    def to_property(cls, columns: Union[str, list, set]):
        """
        根据列名获取对应的列
        """
        if isinstance(columns, str):
            return getattr(cls, columns)
        else:
            return [getattr(cls, name) for name in columns]

    @classmethod
    def create(cls, **kwargs) -> (Optional[str], bool):
        """
        创建数据实例
        Args:
            **kwargs: 参数

        Returns:
            返回元组，第一位可能是新建数据的ID或错误消息，第二位是SQL执行是否成功的标识位
        """
        return execute_sql(insert(cls).values(**kwargs))

    @classmethod
    def read(cls, query_id=None):
        """
        查询数据
        Args:
            query_id: 提供id时返回单一的实例对象，否则查询全部数据列表

        Returns:
            实例对象或列表数据
        """
        if query_id:
            return execute_sql(select(cls).where(cls.id == query_id), many=False)
        else:
            return execute_sql(select(cls), many=True)

    @classmethod
    def update(cls, query_id, data):
        """
        更新数据
        Args:
            query_id: 目标ID
            data: 更新数据

        Returns:
            返回元组，第一位可能是None或错误消息，第二位是SQL执行是否成功的标识位
        """
        return execute_sql(update(cls).where(cls.id == query_id).values(**data))

    @classmethod
    def delete(cls, query_id) -> (Optional[str], bool):
        """
        删除数据
        Args:
            query_id: 目标ID【或ID列表】

        Returns:
            返回元组，第一位可能是None或错误消息，第二位是SQL执行是否成功的标识位
        """
        with Session(cls.bind) as session:
            try:
                if isinstance(query_id, (list, set)):
                    if instances := session.scalars(select(cls).where(cls.id.in_(query_id))).all():
                        for instance in instances:
                            session.delete(instance)
                        return None, True
                else:
                    if instance := session.scalar(select(cls).where(cls.id == query_id)):
                        session.delete(instance)  # 通过该方式可以级联删除子数据
                        return None, True
                return f'未找到资源', False
            except IntegrityError as ex:
                session.rollback()
                logger.exception(ex)
                return ex.orig.args[1], False
            except Exception as exx:
                session.rollback()
                logger.exception(exx)
                return str(exx), False
            finally:
                session.commit()


class OLTPModelBase(_OLTPModelBase, ModelTemplate):
    """
    OLTP模型基类
    """
    __abstract__ = True

    id: Union[Column, str] = Column(IdDefine, primary_key=True, default=lambda: token_urlsafe(24), comment='主键')


class OLAPModelBase(_OLAPModelBase, ModelTemplate):
    """
    OLAP模型基类
    """
    __abstract__ = True

    id: Union[Column, str] = Column(types.UUID, primary_key=True, default=lambda: uuid4(), comment='主键')
