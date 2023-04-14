"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
File Name   : base.py
Author      : jinming.yang
Description : model基础信息定义
Model分为两类，
    - OLTP: 联机事务处理
    - OLAP: 联机事务处理
    因ol和01不易区分，因此只保留TP、AP进行定义
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
from secrets import token_urlsafe
from typing import Optional
from typing import Union
from uuid import uuid4

from clickhouse_sqlalchemy import types
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.collections import InstrumentedList

from config import DATABASE_CLICKHOUSE_URI
from config import DATABASE_MYSQL_URI
from utils.classes import logger
from utils.functions import execute_sql

tp_engine = create_engine(DATABASE_MYSQL_URI, pool_size=150, pool_recycle=60)
tp_public_session = scoped_session(sessionmaker(autocommit=True, bind=tp_engine))
_TPModelBase = declarative_base(bind=tp_engine)

ap_engine = create_engine(DATABASE_CLICKHOUSE_URI)
ap_public_session = scoped_session(sessionmaker(autocommit=True, bind=ap_engine))
_APModelBase = declarative_base(bind=ap_engine)

IdDefine = String(32)


class ModelTemplate:
    """
    TP、AP公共方法
    """

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
            elif isinstance(value, _TPModelBase):
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


class TPModelBase(_TPModelBase, ModelTemplate):
    """
    OLTP模型基类
    """
    __abstract__ = True

    id: Union[Column, str] = Column(IdDefine, primary_key=True, default=lambda: token_urlsafe(24), comment='主键')
    query: scoped_session = tp_public_session.query_property()  # GraphQL用到

    @classmethod
    def create(cls, **kwargs) -> (Optional[str], bool):
        """
        创建数据实例
        Args:
            **kwargs: 参数

        Returns:
            返回元组，第一位可能是新建数据的ID或错误消息，第二位是SQL执行是否成功的标识位
        """
        with Session(tp_engine, autocommit=True) as session:
            return execute_sql(insert(cls).values(**kwargs), session)

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
            return execute_sql(select(cls).where(cls.id == query_id), tp_public_session, keyword=0, expect_list=False)
        else:
            return execute_sql(select(cls), tp_public_session, keyword=0, expect_list=True)

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
        with Session(tp_engine, autocommit=True) as session:
            return execute_sql(update(cls).where(cls.id == query_id).values(**data), session)

    @classmethod
    def delete(cls, query_id) -> (Optional[str], bool):
        """
        删除数据
        Args:
            query_id: 目标ID【或ID列表】

        Returns:
            返回元组，第一位可能是None或错误消息，第二位是SQL执行是否成功的标识位
        """
        with Session(tp_engine) as session:
            try:
                if isinstance(query_id, (list, set)):
                    if instances := session.execute(select(cls).where(cls.id.in_(query_id))).scalars().all():
                        for instance in instances:
                            session.delete(instance)
                        session.commit()
                        return None, True
                else:
                    if instance := session.execute(select(cls).where(cls.id == query_id)).scalar():
                        session.delete(instance)  # 通过该方式可以级联删除子数据
                        session.commit()
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


class APModelBase(_APModelBase, ModelTemplate):
    """
    OLAP模型基类
    """
    __abstract__ = True
    id: Union[Column, str] = Column(types.UUID, primary_key=True, default=lambda: uuid4(), comment='主键')
